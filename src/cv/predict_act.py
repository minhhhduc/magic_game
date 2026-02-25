import numpy as np
import cv2
import joblib
import os

__current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(__current_dir, "character_classifier.pkl"))

# Model class → game spell character mapping
# From training data: 1→O, 2→/, 3→|, 4→\backslash
CLASS_TO_SPELL = {
    1: "O",
    2: "/",
    3: "|",
    4: "\\",
}


def parse_shape(img):
    """
    Preprocess a canvas image (WHITE drawing on BLACK background)
    to match HASYv2 training format (BLACK symbol on WHITE background, 28x28).
    """
    target_size = 28

    # Find bounding box of non-zero pixels (the white strokes)
    coords = cv2.findNonZero(img)
    if coords is not None:
        x, y, bw, bh = cv2.boundingRect(coords)
        img = img[y:y+bh, x:x+bw]

    # Invert: white-on-black → black-on-white (to match HASYv2 training data)
    img = 255 - img

    # Pad to square while preserving aspect ratio
    crop_h, crop_w = img.shape[:2]
    max_side = max(crop_h, crop_w)

    # Add padding (~15%) to mimic HASYv2's natural margin around symbols
    padding = max(int(max_side * 0.15), 2)
    canvas_size = max_side + 2 * padding

    # Create a WHITE square canvas (background = 255, like HASYv2)
    square = np.full((canvas_size, canvas_size), 255, dtype=np.uint8)

    # Center the (now inverted) symbol on the canvas
    y_offset = (canvas_size - crop_h) // 2
    x_offset = (canvas_size - crop_w) // 2
    square[y_offset:y_offset + crop_h, x_offset:x_offset + crop_w] = img

    # Resize to 28x28 (training resized 32x32 → 28x28)
    result = cv2.resize(square, (target_size, target_size), interpolation=cv2.INTER_AREA)

    return result.flatten()


def transform_image(img):
    """Apply the same normalization + PCA used during training."""
    mean = np.load(os.path.join(__current_dir, "mean.npy"))
    std = np.load(os.path.join(__current_dir, "std.npy"))
    W = np.load(os.path.join(__current_dir, "pca_components.npy"))

    img = img / 255.0
    img = (img - mean) / std
    img = img @ W
    return img


def predict_action(image, model=model):
    """
    Takes a canvas image (white drawing on black bg),
    returns (spell_char, debug_img_28x28, raw_class_int).
    """
    flat = parse_shape(image)
    debug_img = flat.reshape(28, 28).astype(np.uint8)
    transformed = transform_image(flat)
    raw_pred = model.predict([transformed])[0]

    spell = CLASS_TO_SPELL.get(int(raw_pred), None)
    return spell, debug_img, raw_pred


if __name__ == '__main__':
    # Test with a HASYv2 image (already black-on-white)
    # So we invert it first to simulate game canvas input (white-on-black)
    test_img = cv2.imread(os.path.join(__current_dir, "hasy-data/v2-00149.png"), cv2.IMREAD_GRAYSCALE)
    test_img = 255 - test_img  # simulate canvas format
    spell, img, raw = predict_action(test_img)
    print(f"Spell: {spell}, Raw: {raw}")