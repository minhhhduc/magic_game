import numpy as np
import cv2
import joblib
import os

from config.iconfig import CHARACTER_CLASSIFIER_PATH, MEAN_PATH, STD_PATH, PCA_COMPONENTS_PATH

# Globals to avoid repeated disk I/O
_MODELS_LOADED = False
_model = None
_mean = None
_std = None
_pca_components = None

def _load_resources():
    global _MODELS_LOADED, _model, _mean, _std, _pca_components
    if not _MODELS_LOADED:
        _model = joblib.load(CHARACTER_CLASSIFIER_PATH)
        _mean = np.load(MEAN_PATH)
        _std = np.load(STD_PATH)
        _pca_components = np.load(PCA_COMPONENTS_PATH)
        _MODELS_LOADED = True

# Model class → game spell character mapping
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
    
    # Ensure it's a binary image for bounding box finding
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to ensure pure black/white
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # Find bounding box of non-zero pixels (the white strokes)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, bw, bh = cv2.boundingRect(coords)
        # Add a tiny bit of internal margin before we add the padding
        # to ensure the stroke isn't touching the edge during resize
        img = thresh[y:y+bh, x:x+bw]
    else:
        # Return empty white canvas if no drawing found
        return np.full((target_size * target_size,), 255, dtype=np.float32)

    # Invert: white-on-black → black-on-white (to match HASYv2 training data)
    img = 255 - img

    # Pad to square while preserving aspect ratio
    h, w = img.shape[:2]
    max_side = max(h, w)
    
    # HASYv2 symbols are typically centered with a decent margin
    # Let's target the symbol taking up ~70% of the canvas
    padding = int(max_side * 0.2) 
    canvas_size = max_side + 2 * padding
    
    # Create white canvas
    canvas = np.full((canvas_size, canvas_size), 255, dtype=np.uint8)
    
    # Paste centered
    y_off = (canvas_size - h) // 2
    x_off = (canvas_size - w) // 2
    canvas[y_off:y_off+h, x_off:x_off+w] = img
    
    # Resize to 28x28 using INTER_AREA for downsampling (as used in training script)
    result = cv2.resize(canvas, (target_size, target_size), interpolation=cv2.INTER_AREA)
    
    return result.flatten().astype(np.float32)

def transform_image(flat_img):
    """Apply the same normalization + PCA used during training."""
    _load_resources()
    
    img = flat_img / 255.0
    img = (img - _mean) / _std
    img = img @ _pca_components
    return img

def predict_action(image, model=None):
    """
    Takes a canvas image (white drawing on black bg),
    returns (spell_char, debug_img_28x28, raw_class_int).
    """
    _load_resources()
    target_model = model if model is not None else _model
    
    flat = parse_shape(image)
    debug_img = flat.reshape(28, 28).astype(np.uint8)
    
    # Handle empty canvas case
    if np.all(flat == 255):
        return None, debug_img, -1
        
    transformed = transform_image(flat)
    raw_pred = target_model.predict([transformed])[0]

    spell = CLASS_TO_SPELL.get(int(raw_pred), None)
    return spell, debug_img, raw_pred


if __name__ == '__main__':
    # Test with a HASYv2 image (already black-on-white)
    # So we invert it first to simulate game canvas input (white-on-black)
    test_img = cv2.imread(os.path.join(__current_dir, "hasy-data/v2-00149.png"), cv2.IMREAD_GRAYSCALE)
    test_img = 255 - test_img  # simulate canvas format
    spell, img, raw = predict_action(test_img)
    print(f"Spell: {spell}, Raw: {raw}")