# Brain Tumour Detection

A full-stack web application that detects brain tumours in MRI scans. Upload an MRI image and the app returns a diagnosis ("Tumor is present" / "Tumor is not present") with a probability score.

## Architecture

- **Frontend** — React + TypeScript (Vite, shadcn-ui, Tailwind CSS), in the project root.
- **Backend** — FastAPI server (`backend/main.py`) that loads a pre-trained Keras CNN (`backend/bestm.h5`) and exposes a `POST /predict/` endpoint.
- **Model** — Binary classifier with a single sigmoid output, trained on 240×240 brain MRI images. Preprocessing (`backend/preprocessing.py`) crops the brain region via contour detection before resizing.

## Requirements

- Node.js & npm (frontend)
- [uv](https://docs.astral.sh/uv/) (backend Python environment)
- Python 3.11 (installed automatically by uv)

> **Note:** TensorFlow is pinned to `2.15.1` in `backend/requirements.txt`. This is the last release bundled with Keras 2, which is required to load `bestm.h5` — newer TensorFlow ships Keras 3 and cannot deserialize this model.

## Backend setup

```sh
cd backend

# Create a Python 3.11 virtual environment
uv venv --python 3.11 .venv

# Install dependencies
uv pip install --python .venv/bin/python -r requirements.txt

# Start the API server
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

Test the endpoint:

```sh
curl -X POST -F "file=@path/to/mri.jpg" http://127.0.0.1:8001/predict/
# → {"prediction": "Tumor is present", "probability": 0.99}
```

## Frontend setup

```sh
npm i
npm run dev
```

## API

| Method | Endpoint | Body | Response |
|---|---|---|---|
| POST | `/predict/` | multipart form, `file` = MRI image (jpg/png) | `{"prediction": string, "probability": float}` |

## Model evaluation

`backend/evaluate.py` evaluates the model on a labelled dataset laid out as `yes/` (tumour) and `no/` (no tumour) subfolders, using the same preprocessing as the serving pipeline:

```sh
cd backend
.venv/bin/python evaluate.py --data-dir path/to/dataset
```

Artifacts (`metrics.json`, `classification_report.txt`, `confusion_matrix.png`) are written to `backend/outputs/`.

### Results

Evaluated on the standard Brain MRI dataset (253 images: 155 tumour, 98 no-tumour):

| Metric | Value |
|---|---|
| Accuracy | 92.5% |
| Precision (Tumour) | 98.6% |
| Recall / Sensitivity | 89.0% |
| Specificity | 98.0% |
| F1-score | 93.6% |
| ROC-AUC | 0.977 |

The model correctly identified 138/155 tumour scans and 96/98 healthy scans. Note that the model was likely trained on part of this dataset, so these numbers are optimistic relative to fully unseen data.

## Project structure

```
├── src/                    # React frontend
├── backend/
│   ├── main.py             # FastAPI server (POST /predict/)
│   ├── preprocessing.py    # Contour-crop + resize pipeline, dataset loading
│   ├── evaluate.py         # Evaluate bestm.h5 on a labelled dataset
│   ├── evaluation.py       # Metrics, confusion matrix, reports
│   ├── train.py            # Training pipeline
│   ├── bestm.h5            # Pre-trained Keras model (240×240×3 input)
│   └── requirements.txt    # Python dependencies (TensorFlow 2.15.1)
└── package.json            # Frontend dependencies
```

## Disclaimer

This project is for educational purposes only and must not be used for actual medical diagnosis.
