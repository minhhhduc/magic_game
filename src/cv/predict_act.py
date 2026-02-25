import numpy as np
import cv2
import joblib
import os

__current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(__current_dir, "character_classifier.pkl"))

def parse_shape(img):
    w, h = 28, 28
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)

    return img.flatten()

def transform_image(img):
    __current_dir = os.path.dirname(os.path.abspath(__file__))
    mean = np.load(os.path.join(__current_dir, "mean.npy"))
    std = np.load(os.path.join(__current_dir, "std.npy"))
    W = np.load(os.path.join(__current_dir, "pca_components.npy"))
    img = img/255.0
    img = (img - mean) / std
    img = img @ W
    return img

def predict_action(image, model=model):
    img = parse_shape(image)
    img = transform_image(img)
    pred = model.predict([img])
    return pred[0]

if __name__ == '__main__':
    print(predict_action(cv2.imread(os.path.join(__current_dir, "hasy-data/v2-00149.png"), cv2.IMREAD_GRAYSCALE)))