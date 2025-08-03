import os


# suppress TensorFlow logs:
# 2: Filters out INFO and WARNING messages,
# 1: Filters out INFO messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
# fully suppress the oneDNN warning message as well as general INFO logs.
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img


# Define the base directory and load the model once
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "notebook", "model_100.keras")
model = load_model(MODEL_PATH)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "jfif"}

# Class labels
CLASSES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]


def allowed_file(filename):
    """Check if the filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(filename):
    """Load and preprocess the image for model prediction."""
    img = load_img(filename, target_size=(32, 32))  # Resize to 32x32
    img = img_to_array(img) / 255.0  # Normalize pixel values
    img = preprocess_input(img)  # EfficientNet-specific preprocessing
    return np.expand_dims(img, axis=0)  # Reshape for model input


def predict(filename):
    """Predict the top 4 classes for the given image."""
    img = preprocess_image(filename)
    predictions = model.predict(img)[0]  # Get the first result from batch

    # Get top 4 predictions
    top_indices = np.argsort(predictions)[::-1][:4]  # Get top 4 predictions
    # top_indices = np.argsort(predictions)[-4:][::-1]  # Sort and get top 4 indices
    top_classes = [CLASSES[i] for i in top_indices]
    top_probs = [float(f"{predictions[i] * 100:.2f}") for i in top_indices]
    return top_classes, top_probs
