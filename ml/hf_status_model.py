"""
Hugging Face BERT-based Status Classifier

Fine-tuned BERT model for visa status prediction (Approved/RFE/Denied).
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

try:
    from transformers import (
        BertTokenizer, BertForSequenceClassification,
        AdamW, get_linear_schedule_with_warmup
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from config import BERT_CONFIG, STATUS_LABELS, MODELS_DIR


class VisaCaseDataset(Dataset):
    """PyTorch Dataset for visa case text data."""
    
    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[int]] = None,
        tokenizer=None,
        max_length: int = 256
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        item = {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
        }
        
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return item


class BertStatusClassifier:
    """
    BERT-based classifier for visa status prediction.
    
    Uses bert-base-uncased fine-tuned for multiclass classification.
    """
    
    def __init__(self, num_labels: int = 3, device: Optional[str] = None):
        if not HAS_TRANSFORMERS:
            raise ImportError("transformers library required. Install with: pip install transformers")
        
        self.num_labels = num_labels
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model_name = BERT_CONFIG["model_name"]
        self.max_length = BERT_CONFIG["max_length"]
        
        self.tokenizer = None
        self.model = None
        self.metrics = {}
    
    def load_pretrained(self):
        """Load pretrained BERT model and tokenizer."""
        print(f"📥 Loading {self.model_name}...")
        
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        self.model.to(self.device)
        
        print(f"✅ Model loaded on {self.device}")
        return self
    
    def train(
        self,
        train_texts: List[str],
        train_labels: List[int],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[int]] = None,
        epochs: int = None,
        batch_size: int = None,
        learning_rate: float = None,
        class_weights: Optional[List[float]] = None
    ):
        """
        Fine-tune BERT on visa case data.
        """
        if self.model is None:
            self.load_pretrained()
        
        epochs = epochs or BERT_CONFIG["epochs"]
        batch_size = batch_size or BERT_CONFIG["batch_size"]
        learning_rate = learning_rate or BERT_CONFIG["learning_rate"]
        
        # Create datasets
        train_dataset = VisaCaseDataset(
            train_texts, train_labels, self.tokenizer, self.max_length
        )
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True
        )
        
        val_loader = None
        if val_texts and val_labels:
            val_dataset = VisaCaseDataset(
                val_texts, val_labels, self.tokenizer, self.max_length
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Optimizer and scheduler
        optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=BERT_CONFIG["weight_decay"]
        )
        
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(total_steps * BERT_CONFIG["warmup_ratio"]),
            num_training_steps=total_steps
        )
        
        # Class weights for imbalanced data
        if class_weights:
            loss_weights = torch.tensor(class_weights, dtype=torch.float).to(self.device)
            loss_fn = nn.CrossEntropyLoss(weight=loss_weights)
        else:
            loss_fn = nn.CrossEntropyLoss()
        
        # Training loop
        print(f"🎯 Training for {epochs} epochs...")
        best_val_f1 = 0
        
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                loss = loss_fn(outputs.logits, labels)
                loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            # Validation
            if val_loader:
                val_metrics = self._evaluate(val_loader)
                val_f1 = val_metrics["f1_macro"]
                
                print(f"   Epoch {epoch+1}/{epochs}: loss={avg_loss:.4f}, val_f1={val_f1:.4f}")
                
                if val_f1 > best_val_f1:
                    best_val_f1 = val_f1
                    self.metrics["best_val_f1"] = val_f1
            else:
                print(f"   Epoch {epoch+1}/{epochs}: loss={avg_loss:.4f}")
        
        self.metrics["train_complete"] = True
        return self
    
    def _evaluate(self, data_loader: DataLoader) -> Dict[str, float]:
        """Evaluate on a data loader."""
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"]
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        
        from sklearn.metrics import f1_score, accuracy_score
        
        return {
            "accuracy": accuracy_score(all_labels, all_preds),
            "f1_macro": f1_score(all_labels, all_preds, average="macro"),
            "f1_per_class": f1_score(all_labels, all_preds, average=None).tolist(),
        }
    
    def predict(self, texts: List[str]) -> np.ndarray:
        """Predict class labels."""
        probs = self.predict_proba(texts)
        return np.argmax(probs, axis=1)
    
    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict class probabilities."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_pretrained() first.")
        
        self.model.eval()
        
        dataset = VisaCaseDataset(texts, None, self.tokenizer, self.max_length)
        loader = DataLoader(dataset, batch_size=BERT_CONFIG["batch_size"])
        
        all_probs = []
        
        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
                all_probs.extend(probs)
        
        return np.array(all_probs)
    
    def get_attention_weights(self, text: str) -> Dict[str, np.ndarray]:
        """
        Get attention weights for explainability.
        """
        self.model.eval()
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True
            )
        
        # Average attention across heads and layers
        attentions = outputs.attentions  # List of tensors
        avg_attention = torch.mean(torch.stack(attentions), dim=0)
        avg_attention = torch.mean(avg_attention, dim=1).squeeze()  # Average across heads
        
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])
        
        return {
            "tokens": tokens,
            "attention": avg_attention.cpu().numpy(),
        }
    
    def save(self, path: Optional[Path] = None):
        """Save model to disk."""
        if path is None:
            path = MODELS_DIR / "bert_status_model"
        
        path.mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save metrics
        with open(path / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"💾 Model saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'BertStatusClassifier':
        """Load model from disk."""
        classifier = cls()
        
        classifier.tokenizer = BertTokenizer.from_pretrained(path)
        classifier.model = BertForSequenceClassification.from_pretrained(path)
        classifier.model.to(classifier.device)
        
        metrics_path = path / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                classifier.metrics = json.load(f)
        
        return classifier


if __name__ == "__main__":
    if HAS_TRANSFORMERS:
        print("🧪 Testing BERT Status Classifier...")
        
        # Quick test with dummy data
        texts = [
            "Nationality: India\nVisa Type: H-1B\nDocuments: Complete",
            "Nationality: China\nVisa Type: F-1\nDocuments: Incomplete",
        ]
        labels = [0, 1]  # approved, rfe
        
        classifier = BertStatusClassifier()
        classifier.load_pretrained()
        
        # Test prediction (without training)
        probs = classifier.predict_proba(texts)
        print(f"✅ Prediction shape: {probs.shape}")
        print(f"   Sample probs: {probs[0]}")
    else:
        print("⚠️ transformers not installed. Skipping test.")
