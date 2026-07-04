# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from keras.models import load_model
from PIL import Image
import io

from preprocessing import preprocess

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

