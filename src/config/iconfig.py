import os

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(BASE_DIR, 'src')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sound')

# Vision System Paths
VISION_DIR = os.path.join(SRC_DIR, 'vision')
CV_DIR = os.path.join(VISION_DIR, 'cv')
MODEL_PATH = os.path.join(ASSETS_DIR, 'hand_landmarker.task')

# CV Model Paths
CHARACTER_CLASSIFIER_PATH = os.path.join(CV_DIR, 'character_classifier.pkl')
MEAN_PATH = os.path.join(CV_DIR, 'mean.npy')
STD_PATH = os.path.join(CV_DIR, 'std.npy')
PCA_COMPONENTS_PATH = os.path.join(CV_DIR, 'pca_components.npy')
