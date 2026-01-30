"""
Hugging Face MiniLM-based Time Estimator

Uses sentence-transformers for embedding generation
with a regression head for processing time prediction.
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from config import MINILM_CONFIG, MODELS_DIR


class RegressionHead(nn.Module):
    """
    Regression head for processing time prediction.
    
    Outputs: median prediction and quantiles (P10, P90) for confidence intervals.
    """
    
    def __init__(self, input_dim: int = 384, hidden_dim: int = 128):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
        )
        
        # Separate heads for median and quantiles
        self.median_head = nn.Linear(hidden_dim // 2, 1)
        self.lower_head = nn.Linear(hidden_dim // 2, 1)  # P10
        self.upper_head = nn.Linear(hidden_dim // 2, 1)  # P90
    
    def forward(self, x):
        features = self.network(x)
        
        median = self.median_head(features)
        lower = self.lower_head(features)
        upper = self.upper_head(features)
        
        # Ensure proper ordering: lower <= median <= upper
        # Use softplus to ensure positive outputs
        median = nn.functional.softplus(median)
        lower = median - nn.functional.softplus(lower - median + 1)
        upper = median + nn.functional.softplus(upper - median + 1)
        
        return median, lower, upper


class QuantileLoss(nn.Module):
    """
    Quantile (pinball) loss for uncertainty estimation.
    """
    
    def __init__(self, quantiles: List[float] = [0.10, 0.50, 0.90]):
        super().__init__()
        self.quantiles = quantiles
    
    def forward(self, preds: Tuple[torch.Tensor, ...], targets: torch.Tensor):
        """
        Args:
            preds: (median, lower, upper) predictions
            targets: true values
        """
        median, lower, upper = preds
        targets = targets.unsqueeze(1)
        
        losses = []
        
        for pred, q in zip([lower, median, upper], self.quantiles):
            errors = targets - pred
            loss = torch.max(q * errors, (q - 1) * errors)
            losses.append(loss.mean())
        
        return sum(losses) / len(losses)


class MiniLMTimeEstimator:
    """
    MiniLM-based time estimation model.
    
    Uses sentence embeddings + regression head for
    processing time prediction with uncertainty.
    """
    
    def __init__(self, device: Optional[str] = None):
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError(
                "sentence-transformers required. Install with: pip install sentence-transformers"
            )
        
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = MINILM_CONFIG["model_name"]
        self.embedding_dim = MINILM_CONFIG["embedding_dim"]
        
        self.encoder = None
        self.regression_head = None
        self.metrics = {}
    
    def load_pretrained(self):
        """Load pretrained sentence transformer."""
        print(f"📥 Loading {self.model_name}...")
        
        self.encoder = SentenceTransformer(self.model_name)
        self.encoder.to(self.device)
        
        self.regression_head = RegressionHead(
            input_dim=self.embedding_dim
        ).to(self.device)
        
        print(f"✅ Model loaded on {self.device}")
        return self
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for texts."""
        return self.encoder.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
    
    def train(
        self,
        train_texts: List[str],
        train_times: np.ndarray,
        val_texts: Optional[List[str]] = None,
        val_times: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 1e-3
    ):
        """
        Train regression head on embedded visa cases.
        """
        if self.encoder is None:
            self.load_pretrained()
        
        print("🔢 Encoding training texts...")
        train_embeddings = self.encode(train_texts)
        
        val_embeddings = None
        if val_texts:
            val_embeddings = self.encode(val_texts)
        
        # Create data loaders
        train_dataset = torch.utils.data.TensorDataset(
            torch.tensor(train_embeddings, dtype=torch.float32),
            torch.tensor(train_times, dtype=torch.float32)
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizer
        optimizer = torch.optim.Adam(
            self.regression_head.parameters(),
            lr=learning_rate
        )
        
        loss_fn = QuantileLoss()
        
        print(f"🎯 Training regression head for {epochs} epochs...")
        
        best_val_mae = float("inf")
        
        for epoch in range(epochs):
            self.regression_head.train()
            total_loss = 0
            
            for embeddings, targets in train_loader:
                embeddings = embeddings.to(self.device)
                targets = targets.to(self.device)
                
                optimizer.zero_grad()
                
                preds = self.regression_head(embeddings)
                loss = loss_fn(preds, targets)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            # Validation
            if val_embeddings is not None and (epoch + 1) % 10 == 0:
                val_metrics = self._evaluate(val_embeddings, val_times)
                val_mae = val_metrics["mae"]
                
                print(f"   Epoch {epoch+1}/{epochs}: loss={avg_loss:.4f}, val_mae={val_mae:.2f}")
                
                if val_mae < best_val_mae:
                    best_val_mae = val_mae
                    self.metrics["best_val_mae"] = val_mae
        
        self.metrics["train_complete"] = True
        return self
    
    def _evaluate(self, embeddings: np.ndarray, targets: np.ndarray) -> Dict[str, float]:
        """Evaluate on embeddings."""
        self.regression_head.eval()
        
        with torch.no_grad():
            emb_tensor = torch.tensor(embeddings, dtype=torch.float32).to(self.device)
            median, lower, upper = self.regression_head(emb_tensor)
            
            median = median.cpu().numpy().squeeze()
            lower = lower.cpu().numpy().squeeze()
            upper = upper.cpu().numpy().squeeze()
        
        from sklearn.metrics import mean_absolute_error
        
        mae = mean_absolute_error(targets, median)
        
        # Coverage
        in_interval = (targets >= lower) & (targets <= upper)
        coverage = np.mean(in_interval)
        
        return {
            "mae": mae,
            "coverage": coverage,
            "avg_interval_width": np.mean(upper - lower),
        }
    
    def predict(self, texts: List[str]) -> np.ndarray:
        """Predict median processing time."""
        median, _, _ = self.predict_with_interval(texts)
        return median
    
    def predict_with_interval(
        self,
        texts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict processing time with confidence interval.
        
        Returns:
            (median, lower_bound, upper_bound)
        """
        if self.encoder is None or self.regression_head is None:
            raise ValueError("Model not loaded. Call load_pretrained() first.")
        
        self.regression_head.eval()
        
        embeddings = self.encode(texts)
        
        with torch.no_grad():
            emb_tensor = torch.tensor(embeddings, dtype=torch.float32).to(self.device)
            median, lower, upper = self.regression_head(emb_tensor)
            
            median = median.cpu().numpy().squeeze()
            lower = lower.cpu().numpy().squeeze()
            upper = upper.cpu().numpy().squeeze()
        
        # Ensure positive values
        median = np.maximum(1, median)
        lower = np.maximum(1, lower)
        upper = np.maximum(lower + 1, upper)
        
        return median, lower, upper
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text."""
        return self.encode([text])[0]
    
    def save(self, path: Optional[Path] = None):
        """Save model to disk."""
        if path is None:
            path = MODELS_DIR / "minilm_time_model"
        
        path.mkdir(parents=True, exist_ok=True)
        
        # Save regression head
        torch.save(
            self.regression_head.state_dict(),
            path / "regression_head.pt"
        )
        
        # Save metrics
        with open(path / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"💾 Model saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'MiniLMTimeEstimator':
        """Load model from disk."""
        estimator = cls()
        estimator.load_pretrained()
        
        # Load regression head
        head_path = path / "regression_head.pt"
        if head_path.exists():
            estimator.regression_head.load_state_dict(
                torch.load(head_path, map_location=estimator.device)
            )
        
        metrics_path = path / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                estimator.metrics = json.load(f)
        
        return estimator


if __name__ == "__main__":
    if HAS_SENTENCE_TRANSFORMERS:
        print("🧪 Testing MiniLM Time Estimator...")
        
        # Quick test
        texts = [
            "Nationality: India\nVisa Type: H-1B\nDocuments: Complete",
            "Nationality: China\nVisa Type: F-1\nDocuments: Incomplete",
        ]
        
        estimator = MiniLMTimeEstimator()
        estimator.load_pretrained()
        
        # Get embeddings
        emb = estimator.encode(texts)
        print(f"✅ Embedding shape: {emb.shape}")
        
        # Predict (untrained, just testing)
        median, lower, upper = estimator.predict_with_interval(texts)
        print(f"   Predictions: median={median}, interval=[{lower}, {upper}]")
    else:
        print("⚠️ sentence-transformers not installed. Skipping test.")
