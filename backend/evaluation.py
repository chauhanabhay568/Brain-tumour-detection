# evaluation.py
#
# Evaluation metrics and reporting for the brain tumor classifier.
# Used by evaluate.py (pre-trained model) and train.py (full pipeline).
#
# The current model is a binary classifier (single sigmoid output:
# Tumor vs No Tumor), so binary metrics are computed by default.
# If the model ever outputs more than one unit (multi-class softmax),
# the functions below detect that automatically and switch to
# *weighted* averaging — chosen over macro because medical imaging
# datasets are typically class-imbalanced, and weighted averaging
# reflects per-class support in the final score.

import json
import os

import matplotlib

matplotlib.use("Agg")  # headless backend: scripts run without a display
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from preprocessing import CLASS_NAMES

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def predict_labels(model, X, batch_size=32):
    """Run the model and return (predicted labels, probability scores).

    Handles both a single-sigmoid binary head and a multi-class
    softmax head transparently.
    """
    probs = model.predict(X, batch_size=batch_size, verbose=0)
    if probs.ndim == 2 and probs.shape[1] > 1:  # multi-class softmax
        return np.argmax(probs, axis=1), probs
    probs = probs.ravel()  # binary sigmoid
    return (probs > 0.5).astype(int), probs


def compute_metrics(y_true, y_pred, y_prob=None):
    """Compute the full metric suite as a plain dict.

    Binary case: precision/recall/F1 are reported for the positive
    (Tumor) class, plus specificity (true-negative rate) and ROC-AUC.
    Multi-class case: weighted averaging, specificity as the mean of
    per-class true-negative rates, ROC-AUC one-vs-rest weighted.
    """
    labels = sorted(set(np.unique(y_true)) | set(np.unique(y_pred)))
    n_classes = len(labels)
    binary = n_classes <= 2
    average = "binary" if binary else "weighted"

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    metrics = {
        "problem_type": "binary" if binary else "multi-class",
        "averaging": average,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "recall_sensitivity": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        "confusion_matrix": cm.tolist(),
    }

    # Specificity = TN / (TN + FP); per-class one-vs-rest, averaged for multi-class
    specificities = []
    for i in range(n_classes):
        tn = cm.sum() - cm[i, :].sum() - cm[:, i].sum() + cm[i, i]
        fp = cm[:, i].sum() - cm[i, i]
        specificities.append(tn / (tn + fp) if (tn + fp) > 0 else 0.0)
    metrics["specificity"] = float(specificities[1] if binary else np.mean(specificities))

    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            if binary:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
            else:
                metrics["roc_auc"] = float(
                    roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
                )
        except ValueError as exc:
            print(f"[WARN] ROC-AUC could not be computed: {exc}")

    return metrics


def save_confusion_matrix_plot(y_true, y_pred, output_dir, class_names=None):
    class_names = class_names or CLASS_NAMES
    labels = list(range(len(class_names)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    fig.colorbar(im, ax=ax)
    ax.set_xticks(labels, class_names)
    ax.set_yticks(labels, class_names)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title("Confusion Matrix")
    threshold = cm.max() / 2 if cm.max() else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > threshold else "black")
    fig.tight_layout()
    path = os.path.join(output_dir, "confusion_matrix.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[INFO] Saved {path}")


def save_classification_report(y_true, y_pred, output_dir, class_names=None):
    class_names = class_names or CLASS_NAMES
    report = classification_report(
        y_true, y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        zero_division=0,
    )
    path = os.path.join(output_dir, "classification_report.txt")
    with open(path, "w") as f:
        f.write(report)
    print(f"[INFO] Saved {path}")
    return report


def save_metrics_json(metrics, output_dir):
    path = os.path.join(output_dir, "metrics.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Saved {path}")


def save_history_curves(history, output_dir):
    """Save accuracy_curve.png and loss_curve.png from a Keras History
    object (or its .history dict)."""
    hist = history.history if hasattr(history, "history") else history
    epochs = range(1, len(hist["loss"]) + 1)

    for metric, fname, title in (
        ("accuracy", "accuracy_curve.png", "Model Accuracy"),
        ("loss", "loss_curve.png", "Model Loss"),
    ):
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(epochs, hist[metric], label=f"Training {metric}")
        if f"val_{metric}" in hist:
            ax.plot(epochs, hist[f"val_{metric}"], label=f"Validation {metric}")
        ax.set_xlabel("Epoch")
        ax.set_ylabel(metric.capitalize())
        ax.set_title(title)
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        path = os.path.join(output_dir, fname)
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[INFO] Saved {path}")


def evaluate_model(model, X, y, output_dir=DEFAULT_OUTPUT_DIR, split_name="test",
                   save_artifacts=True):
    """Evaluate `model` on (X, y); optionally save all report artifacts.

    Returns the metrics dict. `split_name` labels the metrics when
    multiple splits are evaluated (train/val/test).
    """
    os.makedirs(output_dir, exist_ok=True)
    y_pred, y_prob = predict_labels(model, X)
    metrics = compute_metrics(y, y_pred, y_prob)

    print(f"\n===== {split_name.upper()} METRICS =====")
    for key, value in metrics.items():
        if key == "confusion_matrix":
            continue
        print(f"{key:>20}: {value if isinstance(value, str) else f'{value:.4f}'}")

    if save_artifacts:
        save_confusion_matrix_plot(y, y_pred, output_dir)
        report = save_classification_report(y, y_pred, output_dir)
        print("\n" + report)

    return metrics
