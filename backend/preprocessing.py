# preprocessing.py
#
# Shared image preprocessing and dataset loading, used by the FastAPI
# server (main.py), the evaluation script (evaluate.py) and the
# training pipeline (train.py).

import os

import cv2
import imutils
import numpy as np

# Model input size (must match the network's expected input shape)
IMAGE_SIZE = (240, 240)

# Class label conventions for the yes/no dataset layout
CLASS_NAMES = ["No Tumor", "Tumor"]  # index 0 -> negative, index 1 -> positive
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")


# Preprocessing function: crops and prepares the MRI image for prediction
def preprocess(img_array):
    # Convert image to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Thresholding to highlight the tumor region
    thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours and get the largest one (tumor area)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)

    # Get bounding box around the largest contour
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])

    # Crop the tumor region and resize to model input shape
    image = img_array[extTop[1]:extBot[1], extLeft[0]:extRight[0]]
    image = cv2.resize(image, dsize=IMAGE_SIZE, interpolation=cv2.INTER_CUBIC)
    image = image / 255.0  # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    return image


def load_dataset(data_dir):
    """Load and preprocess a yes/no image dataset.

    Expects the layout used by the Br35H-style brain MRI datasets:

        data_dir/
            yes/   <- images containing a tumor  (label 1)
            no/    <- images without a tumor     (label 0)

    Every image goes through the same `preprocess()` used at inference
    time, so evaluation numbers reflect the real serving pipeline.
    Images the crop step cannot handle (no contour found) are skipped
    with a warning.

    Returns:
        X: float array of shape (n, 240, 240, 3)
        y: int array of shape (n,) with 0 = no tumor, 1 = tumor
    """
    folders = {"no": 0, "yes": 1}
    images, labels = [], []
    skipped = 0

    for folder, label in folders.items():
        folder_path = os.path.join(data_dir, folder)
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(
                f"Expected folder '{folder_path}' not found. The dataset "
                f"directory must contain 'yes/' and 'no/' subfolders."
            )
        for fname in sorted(os.listdir(folder_path)):
            if not fname.lower().endswith(VALID_EXTENSIONS):
                continue
            path = os.path.join(folder_path, fname)
            img = cv2.imread(path)  # BGR, matching preprocess()'s expectation
            if img is None:
                print(f"[WARN] Could not read image, skipping: {path}")
                skipped += 1
                continue
            try:
                images.append(preprocess(img)[0])  # drop batch dimension
                labels.append(label)
            except Exception as exc:  # e.g. no contour found on blank images
                print(f"[WARN] Preprocessing failed, skipping {path}: {exc}")
                skipped += 1

    if not images:
        raise RuntimeError(f"No usable images found under '{data_dir}'.")

    if skipped:
        print(f"[INFO] Skipped {skipped} unreadable/unprocessable image(s).")

    X = np.asarray(images, dtype=np.float32)
    y = np.asarray(labels, dtype=np.int64)
    print(f"[INFO] Loaded {len(y)} images "
          f"({int((y == 1).sum())} tumor, {int((y == 0).sum())} no-tumor).")
    return X, y
