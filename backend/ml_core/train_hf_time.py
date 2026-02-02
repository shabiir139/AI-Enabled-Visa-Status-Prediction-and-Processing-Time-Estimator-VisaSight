"""
Training Script for Hugging Face Time Model (MiniLM)

Trains MiniLM embeddings + regression head for processing time prediction.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

from config import DATASET_CONFIG, MODELS_DIR, DATA_DIR, MINILM_CONFIG, EVAL_THRESHOLDS
from dataset_generator import generate_dataset, split_dataset
from feature_engineering import CaseTextEncoder
from hf_time_model import MiniLMTimeEstimator


def train_minilm_time_model(
    n_samples: int = 10000,
    epochs: int = 50,
    quick: bool = False
):
    """
    Train MiniLM model for processing time estimation.
    """
    print("=" * 60)
    print("⏱️ VisaSight MiniLM Time Model Training")
    print("=" * 60)
    
    if quick:
        n_samples = 500
        epochs = 10
        print(f"⚡ Quick mode: {n_samples} samples, {epochs} epochs")
    
    # Step 1: Load dataset
    print("\n📊 Step 1: Loading dataset...")
    csv_path = DATA_DIR / "synthetic_visa_cases.csv"
    
    if csv_path.exists() and not quick:
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} cases")
    else:
        df = generate_dataset(n_samples=n_samples, save=not quick)
    
    # Step 2: Split dataset
    print("\n📊 Step 2: Time-based split...")
    train_df, val_df, test_df = split_dataset(df)
    
    # Step 3: Convert to text prompts
    print("\n📝 Step 3: Converting to text prompts...")
    text_encoder = CaseTextEncoder()
    
    train_texts = [text_encoder.encode(row.to_dict()) for _, row in train_df.iterrows()]
    val_texts = [text_encoder.encode(row.to_dict()) for _, row in val_df.iterrows()]
    test_texts = [text_encoder.encode(row.to_dict()) for _, row in test_df.iterrows()]
    
    # Targets
    train_times = train_df["processing_days"].values
    val_times = val_df["processing_days"].values
    test_times = test_df["processing_days"].values
    
    print(f"   Processing time stats: mean={train_times.mean():.1f}, median={np.median(train_times):.1f}")
    
    # Step 4: Train MiniLM
    print("\n🎯 Step 4: Training MiniLM time estimator...")
    estimator = MiniLMTimeEstimator()
    estimator.load_pretrained()
    
    estimator.train(
        train_texts=train_texts,
        train_times=train_times,
        val_texts=val_texts,
        val_times=val_times,
        epochs=epochs,
        batch_size=MINILM_CONFIG["batch_size"]
    )
    
    # Step 5: Final evaluation
    print("\n📈 Step 5: Final evaluation on test set...")
    test_median, test_lower, test_upper = estimator.predict_with_interval(test_texts)
    
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    test_mae = mean_absolute_error(test_times, test_median)
    test_rmse = np.sqrt(mean_squared_error(test_times, test_median))
    
    # Coverage
    in_interval = (test_times >= test_lower) & (test_times <= test_upper)
    coverage = np.mean(in_interval)
    avg_width = np.mean(test_upper - test_lower)
    
    print(f"   Test MAE: {test_mae:.2f} days")
    print(f"   Test RMSE: {test_rmse:.2f} days")
    print(f"   80% CI Coverage: {coverage:.2%}")
    print(f"   Avg Interval Width: {avg_width:.1f} days")
    
    # Step 6: Check acceptance
    print("\n✅ Step 6: Acceptance criteria...")
    median_time = np.median(test_times)
    mae_ratio = test_mae / median_time
    
    mae_passed = mae_ratio <= EVAL_THRESHOLDS["max_mae_ratio"]
    coverage_passed = coverage >= EVAL_THRESHOLDS["min_ci_coverage"]
    
    print(f"   MAE ≤ {EVAL_THRESHOLDS['max_mae_ratio']*100}% of median ({median_time:.0f} days): {'✅ PASS' if mae_passed else '❌ FAIL'}")
    print(f"   Coverage ≥ {EVAL_THRESHOLDS['min_ci_coverage']*100}%: {'✅ PASS' if coverage_passed else '❌ FAIL'}")
    
    # Step 7: Save model
    if not quick:
        print("\n💾 Step 7: Saving model...")
        estimator.save()
        
        # Save report
        report = {
            "model": MINILM_CONFIG["model_name"],
            "trained_at": datetime.now().isoformat(),
            "epochs": epochs,
            "samples": len(train_df),
            "test_mae": test_mae,
            "test_rmse": test_rmse,
            "ci_coverage": coverage,
            "avg_interval_width": avg_width,
            "acceptance_passed": {
                "mae": mae_passed,
                "coverage": coverage_passed,
            },
        }
        
        report_path = MODELS_DIR / "minilm_training_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"   Report saved to {report_path}")
    
    print("\n" + "=" * 60)
    print("🎉 MiniLM training complete!")
    print("=" * 60)
    
    return estimator


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MiniLM time model")
    parser.add_argument("--samples", type=int, default=10000, help="Number of samples")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--quick", action="store_true", help="Quick mode for testing")
    
    args = parser.parse_args()
    
    train_minilm_time_model(
        n_samples=args.samples,
        epochs=args.epochs,
        quick=args.quick
    )
