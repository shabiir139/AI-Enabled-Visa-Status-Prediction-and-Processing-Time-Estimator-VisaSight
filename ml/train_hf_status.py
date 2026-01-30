"""
Training Script for Hugging Face Status Model (BERT)

Fine-tunes BERT for visa status classification.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

from config import DATASET_CONFIG, MODELS_DIR, DATA_DIR, BERT_CONFIG, EVAL_THRESHOLDS
from dataset_generator import generate_dataset, split_dataset
from feature_engineering import CaseTextEncoder, encode_labels
from hf_status_model import BertStatusClassifier


def train_bert_status_model(
    n_samples: int = 10000,
    epochs: int = None,
    quick: bool = False
):
    """
    Train BERT model for status prediction.
    """
    print("=" * 60)
    print("🤖 VisaSight BERT Status Model Training")
    print("=" * 60)
    
    if quick:
        n_samples = 500
        epochs = 2
        print(f"⚡ Quick mode: {n_samples} samples, {epochs} epochs")
    
    epochs = epochs or BERT_CONFIG["epochs"]
    
    # Step 1: Load dataset
    print("\n📊 Step 1: Loading dataset...")
    csv_path = DATA_DIR / "synthetic_visa_cases.csv"
    
    if csv_path.exists() and not quick:
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} cases from {csv_path}")
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
    
    print(f"   Sample prompt:\n{train_texts[0][:200]}...")
    
    # Labels
    train_labels = encode_labels(train_df).tolist()
    val_labels = encode_labels(val_df).tolist()
    test_labels = encode_labels(test_df).tolist()
    
    # Step 4: Compute class weights
    print("\n⚖️ Step 4: Computing class weights...")
    class_counts = np.bincount(train_labels, minlength=3)
    total = len(train_labels)
    class_weights = [total / (3 * count) if count > 0 else 1.0 for count in class_counts]
    print(f"   Class distribution: {class_counts}")
    print(f"   Class weights: {class_weights}")
    
    # Step 5: Train BERT
    print("\n🎯 Step 5: Training BERT classifier...")
    classifier = BertStatusClassifier()
    classifier.load_pretrained()
    
    classifier.train(
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=val_texts,
        val_labels=val_labels,
        epochs=epochs,
        batch_size=BERT_CONFIG["batch_size"],
        class_weights=class_weights
    )
    
    # Step 6: Final evaluation
    print("\n📈 Step 6: Final evaluation on test set...")
    test_preds = classifier.predict(test_texts)
    test_probs = classifier.predict_proba(test_texts)
    
    from sklearn.metrics import f1_score, accuracy_score, classification_report
    
    test_f1 = f1_score(test_labels, test_preds, average="macro")
    test_acc = accuracy_score(test_labels, test_preds)
    
    print(f"   Test F1 (macro): {test_f1:.4f}")
    print(f"   Test Accuracy: {test_acc:.4f}")
    print("\n   Classification Report:")
    print(classification_report(test_labels, test_preds, target_names=["approved", "rfe", "denied"]))
    
    # Step 7: Check acceptance
    print("\n✅ Step 7: Acceptance criteria...")
    passed = test_f1 >= EVAL_THRESHOLDS["min_macro_f1"]
    print(f"   F1 ≥ {EVAL_THRESHOLDS['min_macro_f1']}: {'✅ PASS' if passed else '❌ FAIL'}")
    
    # Step 8: Save model
    if not quick:
        print("\n💾 Step 8: Saving model...")
        classifier.save()
        
        # Save report
        report = {
            "model": "bert-base-uncased",
            "trained_at": datetime.now().isoformat(),
            "epochs": epochs,
            "samples": len(train_df),
            "test_f1_macro": test_f1,
            "test_accuracy": test_acc,
            "class_weights": class_weights,
            "acceptance_passed": passed,
        }
        
        report_path = MODELS_DIR / "bert_training_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"   Report saved to {report_path}")
    
    print("\n" + "=" * 60)
    print("🎉 BERT training complete!")
    print("=" * 60)
    
    return classifier


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train BERT status model")
    parser.add_argument("--samples", type=int, default=10000, help="Number of samples")
    parser.add_argument("--epochs", type=int, default=None, help="Training epochs")
    parser.add_argument("--quick", action="store_true", help="Quick mode for testing")
    
    args = parser.parse_args()
    
    train_bert_status_model(
        n_samples=args.samples,
        epochs=args.epochs,
        quick=args.quick
    )
