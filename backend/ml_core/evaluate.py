"""
Evaluation Utilities for VisaSight ML Models

Metrics computation, error analysis, and reporting.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)

from config import STATUS_LABELS, EVAL_THRESHOLDS


def evaluate_classifier(
    model,
    X: np.ndarray,
    y_true: np.ndarray,
    class_names: List[str] = STATUS_LABELS
) -> Dict[str, Any]:
    """
    Comprehensive classifier evaluation.
    
    Returns:
        Dict with accuracy, F1, precision, recall, confusion matrix
    """
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X) if hasattr(model, 'predict_proba') else None
    
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "f1_per_class": f1_score(y_true, y_pred, average=None).tolist(),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_per_class": recall_score(y_true, y_pred, average=None, zero_division=0).tolist(),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    
    # Per-class metrics
    for i, class_name in enumerate(class_names):
        metrics[f"f1_{class_name}"] = metrics["f1_per_class"][i] if i < len(metrics["f1_per_class"]) else 0
        metrics[f"recall_{class_name}"] = metrics["recall_per_class"][i] if i < len(metrics["recall_per_class"]) else 0
    
    return metrics


def evaluate_regressor(
    model,
    X: np.ndarray,
    y_true: np.ndarray
) -> Dict[str, float]:
    """
    Comprehensive regressor evaluation.
    
    Returns:
        Dict with MAE, RMSE, R², MAPE
    """
    y_pred = model.predict(X)
    
    metrics = {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mse": mean_squared_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
    
    # MAPE (avoid division by zero)
    mask = y_true != 0
    if mask.sum() > 0:
        metrics["mape"] = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        metrics["mape"] = 0.0
    
    # Percentile errors
    errors = np.abs(y_true - y_pred)
    metrics["p50_error"] = np.percentile(errors, 50)
    metrics["p90_error"] = np.percentile(errors, 90)
    metrics["p95_error"] = np.percentile(errors, 95)
    
    return metrics


def compute_baseline_metrics(
    y_train_status: np.ndarray,
    y_val_status: np.ndarray,
    y_train_time: np.ndarray,
    y_val_time: np.ndarray
) -> Dict[str, float]:
    """
    Compute naive baseline metrics for comparison.
    """
    # Majority class baseline for classification
    majority_class = np.argmax(np.bincount(y_train_status))
    majority_pred = np.full_like(y_val_status, majority_class)
    majority_f1 = f1_score(y_val_status, majority_pred, average="macro")
    
    # Median baseline for regression
    median_time = np.median(y_train_time)
    median_pred = np.full_like(y_val_time, median_time, dtype=float)
    median_mae = mean_absolute_error(y_val_time, median_pred)
    
    return {
        "majority_class": int(majority_class),
        "majority_f1": majority_f1,
        "median_time": float(median_time),
        "median_mae": median_mae,
    }


def analyze_errors(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    df: pd.DataFrame,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Analyze prediction errors.
    
    Returns:
        Dict with error distribution and worst cases
    """
    errors = np.abs(y_true - y_pred)
    
    # Error distribution
    error_stats = {
        "mean": float(np.mean(errors)),
        "std": float(np.std(errors)),
        "min": float(np.min(errors)),
        "max": float(np.max(errors)),
        "median": float(np.median(errors)),
    }
    
    # Worst cases
    worst_indices = np.argsort(errors)[-top_n:][::-1]
    worst_cases = []
    for idx in worst_indices:
        case = {
            "index": int(idx),
            "true": float(y_true[idx]),
            "pred": float(y_pred[idx]),
            "error": float(errors[idx]),
        }
        # Add case details if available
        if idx < len(df):
            row = df.iloc[idx]
            case["visa_type"] = row.get("visa_type", "unknown")
            case["nationality"] = row.get("nationality", "unknown")
            case["consulate"] = row.get("consulate", "unknown")
        worst_cases.append(case)
    
    return {
        "error_stats": error_stats,
        "worst_cases": worst_cases,
    }


def slice_analysis(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    df: pd.DataFrame,
    slice_columns: List[str] = ["visa_type", "nationality", "consulate"]
) -> Dict[str, Dict[str, float]]:
    """
    Compute metrics sliced by categorical variables.
    
    Useful for detecting bias and per-group performance.
    """
    results = {}
    
    for col in slice_columns:
        if col not in df.columns:
            continue
        
        col_results = {}
        for value in df[col].unique():
            mask = df[col] == value
            if mask.sum() < 10:  # Skip small groups
                continue
            
            slice_true = y_true[mask]
            slice_pred = y_pred[mask]
            
            col_results[value] = {
                "count": int(mask.sum()),
                "mae": float(mean_absolute_error(slice_true, slice_pred)),
            }
        
        results[col] = col_results
    
    return results


def check_bias_thresholds(
    slice_results: Dict[str, Dict[str, float]],
    max_mae_diff: float = 0.20
) -> Dict[str, List[str]]:
    """
    Check for bias by comparing slice metrics.
    
    Returns:
        Dict with flagged groups per slice column
    """
    flags = {}
    
    for col, groups in slice_results.items():
        if not groups:
            continue
        
        maes = [g["mae"] for g in groups.values()]
        mean_mae = np.mean(maes)
        
        flagged = []
        for group_name, metrics in groups.items():
            if abs(metrics["mae"] - mean_mae) / mean_mae > max_mae_diff:
                flagged.append(group_name)
        
        if flagged:
            flags[col] = flagged
    
    return flags


def evaluate_confidence_intervals(
    y_true: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    target_coverage: float = 0.80
) -> Dict[str, float]:
    """
    Evaluate prediction interval quality.
    """
    in_interval = (y_true >= lower) & (y_true <= upper)
    coverage = np.mean(in_interval)
    
    # Average interval width
    avg_width = np.mean(upper - lower)
    
    return {
        "coverage": coverage,
        "target_coverage": target_coverage,
        "coverage_met": coverage >= target_coverage,
        "avg_interval_width": avg_width,
    }


def generate_evaluation_report(
    model_type: str,
    baseline_metrics: Dict,
    status_metrics: Dict,
    time_metrics: Dict,
    feature_importance: Dict,
    acceptance_passed: Dict
) -> Dict[str, Any]:
    """
    Generate comprehensive evaluation report.
    """
    return {
        "report_generated_at": datetime.now().isoformat(),
        "model_type": model_type,
        "baseline_comparison": baseline_metrics,
        "status_prediction": status_metrics,
        "time_estimation": time_metrics,
        "feature_importance": feature_importance,
        "acceptance_criteria": {
            "thresholds": EVAL_THRESHOLDS,
            "results": acceptance_passed,
        },
        "improvement_over_baseline": {
            "status_f1_improvement": (
                status_metrics.get("test", {}).get("f1_macro", 0) - 
                baseline_metrics.get("majority_f1", 0)
            ),
            "time_mae_improvement": (
                baseline_metrics.get("median_mae", 0) - 
                time_metrics.get("test", {}).get("mae", 0)
            ),
        }
    }


if __name__ == "__main__":
    # Test with dummy data
    print("🧪 Testing evaluation utilities...")
    
    y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
    y_pred = np.array([0, 1, 1, 0, 2, 2, 0, 1, 2, 1])
    
    # Mock model
    class MockClassifier:
        def predict(self, X):
            return y_pred
        def predict_proba(self, X):
            return np.eye(3)[y_pred]
    
    clf_metrics = evaluate_classifier(MockClassifier(), None, y_true)
    print(f"✅ Classifier metrics: F1={clf_metrics['f1_macro']:.4f}")
    
    # Regressor test
    y_true_reg = np.array([30, 45, 60, 35, 50])
    y_pred_reg = np.array([32, 40, 65, 38, 48])
    
    class MockRegressor:
        def predict(self, X):
            return y_pred_reg
    
    reg_metrics = evaluate_regressor(MockRegressor(), None, y_true_reg)
    print(f"✅ Regressor metrics: MAE={reg_metrics['mae']:.2f}")
