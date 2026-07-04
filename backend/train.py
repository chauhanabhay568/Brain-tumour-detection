# train.py
#
# Training pipeline for the brain tumor classifier.
#
# Loads the existing bestm.h5 architecture+weights (the architecture is
# NOT changed), splits the dataset into stratified train/validation/test
# sets, trains with early stopping, and produces the full evaluation
# report: accuracy/loss curves, confusion matrix, classification report
# and metrics.json (with train/val/test accuracy).
#
# The retrained model is saved to bestm_retrained.h5 so the model
# currently served by main.py is never overwritten. Replace bestm.h5
# with it manually once you are happy with the metrics.
#
# Usage:
#     python train.py --data-dir dataset --epochs 25

import argparse
import os

import numpy as np
import tensorflow as tf
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import load_model
from sklearn.model_selection import train_test_split

from evaluation import (
    DEFAULT_OUTPUT_DIR,
    compute_metrics,
    evaluate_model,
    predict_labels,
    save_history_curves,
    save_metrics_json,
)
from preprocessing import load_dataset

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


def split_dataset(X, y, val_size, test_size, seed):
    """Stratified train/val/test split."""
    X_train, X_tmp, y_train, y_tmp = train_test_split(
        X, y, test_size=val_size + test_size, stratify=y, random_state=seed
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp, test_size=test_size / (val_size + test_size),
        stratify=y_tmp, random_state=seed,
    )
    print(f"[INFO] Split sizes -> train: {len(y_train)}, "
          f"val: {len(y_val)}, test: {len(y_test)}")
    return X_train, y_train, X_val, y_val, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description="Train/fine-tune the brain tumor classifier.")
    parser.add_argument("--data-dir", default=os.path.join(BACKEND_DIR, "dataset"),
                        help="Dataset directory containing yes/ and no/ subfolders.")
    parser.add_argument("--model", default=os.path.join(BACKEND_DIR, "bestm.h5"),
                        help="Model to start from (architecture is kept as-is).")
    parser.add_argument("--output-model", default=os.path.join(BACKEND_DIR, "bestm_retrained.h5"),
                        help="Where to save the best retrained model.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Where to write evaluation artifacts.")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--val-size", type=float, default=0.15)
    parser.add_argument("--test-size", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"[INFO] Loading dataset: {args.data_dir}")
    X, y = load_dataset(args.data_dir)
    X_train, y_train, X_val, y_val, X_test, y_test = split_dataset(
        X, y, args.val_size, args.test_size, args.seed
    )

    print(f"[INFO] Loading model: {args.model} (architecture unchanged)")
    model = load_model(args.model)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        ModelCheckpoint(args.output_model, monitor="val_accuracy", save_best_only=True),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
    )

    # Curves (training + validation accuracy/loss per epoch)
    save_history_curves(history, args.output_dir)

    # Test split gets the full artifact set (confusion matrix, report);
    # train/val metrics are computed without overwriting those files.
    test_metrics = evaluate_model(model, X_test, y_test,
                                  output_dir=args.output_dir, split_name="test")
    all_metrics = {"test": test_metrics}
    for split_name, X_s, y_s in (("train", X_train, y_train), ("val", X_val, y_val)):
        y_pred, y_prob = predict_labels(model, X_s)
        all_metrics[split_name] = compute_metrics(y_s, y_pred, y_prob)
        print(f"[INFO] {split_name} accuracy: {all_metrics[split_name]['accuracy']:.4f}")

    all_metrics["summary"] = {
        "train_accuracy": all_metrics["train"]["accuracy"],
        "validation_accuracy": all_metrics["val"]["accuracy"],
        "test_accuracy": all_metrics["test"]["accuracy"],
    }
    save_metrics_json(all_metrics, args.output_dir)
    print(f"\n[INFO] Best model saved to {args.output_model}")
    print(f"[INFO] All evaluation artifacts saved to {args.output_dir}")


if __name__ == "__main__":
    main()
