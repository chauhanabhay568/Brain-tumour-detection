# evaluate.py
#
# Evaluate the pre-trained model (bestm.h5) on a labelled dataset,
# using the exact same preprocessing as the FastAPI serving pipeline.
#
# Usage:
#     python evaluate.py --data-dir dataset            # evaluate whole dataset
#     python evaluate.py --data-dir dataset --test-split 0.2 --seed 42
#
# The dataset directory must contain 'yes/' (tumor) and 'no/' (no tumor)
# subfolders. Outputs (confusion_matrix.png, classification_report.txt,
# metrics.json) are written to backend/outputs/.
#
# Note: accuracy/loss curves require training history and are produced
# by train.py, not by this script.

import argparse
import os

from keras.models import load_model
from sklearn.model_selection import train_test_split

from evaluation import DEFAULT_OUTPUT_DIR, evaluate_model, save_metrics_json
from preprocessing import load_dataset

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="Evaluate the brain tumor classifier.")
    parser.add_argument("--data-dir", default=os.path.join(BACKEND_DIR, "dataset"),
                        help="Dataset directory containing yes/ and no/ subfolders.")
    parser.add_argument("--model", default=os.path.join(BACKEND_DIR, "bestm.h5"),
                        help="Path to the trained Keras model.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Where to write evaluation artifacts.")
    parser.add_argument("--test-split", type=float, default=None,
                        help="If set (e.g. 0.2), evaluate only a stratified held-out "
                             "fraction instead of the full dataset.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for the held-out split.")
    args = parser.parse_args()

    print(f"[INFO] Loading model: {args.model}")
    model = load_model(args.model)

    print(f"[INFO] Loading dataset: {args.data_dir}")
    X, y = load_dataset(args.data_dir)

    if args.test_split:
        _, X, _, y = train_test_split(
            X, y, test_size=args.test_split, stratify=y, random_state=args.seed
        )
        print(f"[INFO] Evaluating on stratified held-out split of {len(y)} images.")

    metrics = evaluate_model(model, X, y, output_dir=args.output_dir, split_name="test")
    save_metrics_json({"test": metrics}, args.output_dir)


if __name__ == "__main__":
    main()
