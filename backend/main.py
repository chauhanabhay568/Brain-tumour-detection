# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import imutils
from keras.models import load_model
from PIL import Image
import io

# Initialize the FastAPI app
app = FastAPI()

# CORS setup: allow all origins during development (frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model once when the server starts
model = load_model("bestm.h5")

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
    image = cv2.resize(image, dsize=(240, 240), interpolation=cv2.INTER_CUBIC)
    image = image / 255.0  # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    return image

# Prediction route: receives image, preprocesses it, and returns diagnosis
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Read uploaded image file
    contents = await file.read()

    # Open it as a PIL image and convert to RGB
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    img_array = np.array(image)

    try:
        # Preprocess and run prediction
        preprocessed_image = preprocess(img_array)
        pred = model.predict(preprocessed_image)

        # Interpret prediction
        result = "Tumor is present" if pred[0][0] > 0.5 else "Tumor is not present"
        probability = float(pred[0][0])

        return {"prediction": result, "probability": probability}

    except Exception as e:
        return {"error": str(e)}
