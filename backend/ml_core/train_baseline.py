"""
Training Script for Baseline Models

Trains Random Forest and XGBoost models on synthetic visa case data.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

from config import DATASET_CONFIG, MODELS_DIR, DATA_DIR, EVAL_THRESHOLDS
from dataset_generator import generate_dataset, split_dataset
from feature_engineering import TabularFeatureExtractor, encode_labels
from baseline_models import BaselineStatusClassifier, BaselineTimeRegressor
from evaluate import (
    evaluate_classifier, evaluate_regressor,
    compute_baseline_metrics, generate_evaluation_report
)


def train_baseline_models(
    n_samples: int = 10000,
    model_type: str = "rf",
    tune: bool = False,
    quick: bool = False
):
    """
    Train baseline models for status prediction and time estimation.
    
    Args:
        n_samples: Number of samples to generate
        model_type: "rf" or "xgb"
        tune: Whether to tune hyperparameters
        quick: Quick mode with fewer samples
    """
    print("=" * 60)
    print("🚀 VisaSight Baseline Model Training")
    print("=" * 60)
    
    if quick:
        n_samples = 500
        print(f"⚡ Quick mode: using {n_samples} samples")
    
    # Step 1: Generate or load dataset
    print("\n📊 Step 1: Preparing dataset...")
    csv_path = DATA_DIR / "synthetic_visa_cases.csv"
    
    if csv_path.exists() and not quick:
        print(f"   Loading existing dataset from {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        print(f"   Generating {n_samples} synthetic cases...")
        df = generate_dataset(n_samples=n_samples, save=not quick)
    
    # Step 2: Split dataset
    print("\n📊 Step 2: Splitting dataset (time-based)...")
    train_df, val_df, test_df = split_dataset(df)
    
    # Step 3: Feature extraction
    print("\n🔧 Step 3: Extracting features...")
    reference_date = datetime(2026, 1, 29)
    
    extractor = TabularFeatureExtractor()
    X_train = extractor.fit_transform(train_df, reference_date)
    X_val = extractor.transform(val_df, reference_date)
    X_test = extractor.transform(test_df, reference_date)
    
    # Labels
    y_train_status = encode_labels(train_df)
    y_val_status = encode_labels(val_df)
    y_test_status = encode_labels(test_df)
    
    y_train_time = train_df["processing_days"].values
    y_val_time = val_df["processing_days"].values
    y_test_time = test_df["processing_days"].values
    
    print(f"   Feature shape: {X_train.shape}")
    print(f"   Feature names: {extractor.get_feature_names()}")
    
    # Step 4: Compute baselines
    print("\n📏 Step 4: Computing naive baselines...")
    baseline_metrics = compute_baseline_metrics(
        y_train_status, y_val_status,
        y_train_time, y_val_time
    )
    print(f"   Majority class baseline F1: {baseline_metrics['majority_f1']:.4f}")
    print(f"   Median time baseline MAE: {baseline_metrics['median_mae']:.2f} days")
    
    # Step 5: Train status classifier
    print(f"\n🎯 Step 5: Training {model_type.upper()} status classifier...")
    status_clf = BaselineStatusClassifier(model_type=model_type)
    status_clf.train(
        X_train, y_train_status,
        X_val, y_val_status,
        tune_hyperparams=tune,
        n_iter=10 if quick else 20
    )
    
    print(f"   Train F1 (macro): {status_clf.metrics['train_f1_macro']:.4f}")
    print(f"   Val F1 (macro): {status_clf.metrics['val_f1_macro']:.4f}")
    
    # Feature importance
    importance = status_clf.get_feature_importance(extractor.get_feature_names())
    print("   Top 5 features:")
    for i, (feat, imp) in enumerate(list(importance.items())[:5]):
        print(f"      {i+1}. {feat}: {imp:.4f}")
    
    # Step 6: Train time regressor
    print(f"\n⏱️ Step 6: Training {model_type.upper()} time regressor...")
    time_reg = BaselineTimeRegressor(model_type=model_type)
    time_reg.train(X_train, y_train_time, X_val, y_val_time)
    
    print(f"   Train MAE: {time_reg.metrics['train_mae']:.2f} days")
    print(f"   Val MAE: {time_reg.metrics['val_mae']:.2f} days")
    print(f"   Val R²: {time_reg.metrics['val_r2']:.4f}")
    
    # Step 7: Final evaluation on test set
    print("\n📈 Step 7: Final evaluation on test set...")
    
    # Status evaluation
    test_status_metrics = evaluate_classifier(
        status_clf, X_test, y_test_status
    )
    print(f"   Test F1 (macro): {test_status_metrics['f1_macro']:.4f}")
    print(f"   Test Accuracy: {test_status_metrics['accuracy']:.4f}")
    
    # Time evaluation
    test_time_metrics = evaluate_regressor(
        time_reg, X_test, y_test_time
    )
    print(f"   Test MAE: {test_time_metrics['mae']:.2f} days")
    print(f"   Test RMSE: {test_time_metrics['rmse']:.2f} days")
    
    # Step 8: Check acceptance criteria
    print("\n✅ Step 8: Checking acceptance criteria...")
    
    status_passed = test_status_metrics['f1_macro'] >= EVAL_THRESHOLDS['min_macro_f1']
    median_time = np.median(y_test_time)
    time_passed = (test_time_metrics['mae'] / median_time) <= EVAL_THRESHOLDS['max_mae_ratio']
    
    print(f"   Status F1 ≥ {EVAL_THRESHOLDS['min_macro_f1']}: {'✅ PASS' if status_passed else '❌ FAIL'}")
    print(f"   Time MAE ≤ {EVAL_THRESHOLDS['max_mae_ratio']*100}% of median: {'✅ PASS' if time_passed else '❌ FAIL'}")
    
    # Step 9: Save models and report
    print("\n💾 Step 9: Saving models and report...")
    
    if not quick:
        status_clf.save()
        time_reg.save()
        
        # Save feature extractor
        import joblib
        joblib.dump(extractor, MODELS_DIR / "feature_extractor.pkl")
        
        # Generate and save report
        report = generate_evaluation_report(
            model_type=model_type,
            baseline_metrics=baseline_metrics,
            status_metrics={
                "train": status_clf.metrics,
                "test": test_status_metrics
            },
            time_metrics={
                "train": time_reg.metrics,
                "test": test_time_metrics
            },
            feature_importance=importance,
            acceptance_passed={
                "status": status_passed,
                "time": time_passed
            }
        )
        
        report_path = MODELS_DIR / f"training_report_{model_type}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"   Report saved to {report_path}")
    
    print("\n" + "=" * 60)
    print("🎉 Training complete!")
    print("=" * 60)
    
    return status_clf, time_reg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train baseline models")
    parser.add_argument("--samples", type=int, default=10000, help="Number of samples")
    parser.add_argument("--model", type=str, default="rf", choices=["rf", "xgb"], help="Model type")
    parser.add_argument("--tune", action="store_true", help="Tune hyperparameters")
    parser.add_argument("--quick", action="store_true", help="Quick mode for testing")
    
    args = parser.parse_args()
    
    train_baseline_models(
        n_samples=args.samples,
        model_type=args.model,
        tune=args.tune,
        quick=args.quick
    )
