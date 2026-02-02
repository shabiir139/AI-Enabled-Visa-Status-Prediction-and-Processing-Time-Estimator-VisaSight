"""
Baseline Models for VisaSight

Random Forest and XGBoost implementations for status prediction and time estimation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)
import joblib
from pathlib import Path

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from config import RF_CONFIG, XGB_CONFIG, MODELS_DIR, STATUS_LABELS


class BaselineStatusClassifier:
    """
    Baseline classifier for visa status prediction.
    Supports Random Forest and XGBoost.
    """
    
    def __init__(self, model_type: str = "rf"):
        """
        Args:
            model_type: "rf" for Random Forest, "xgb" for XGBoost
        """
        self.model_type = model_type
        self.model = None
        self.best_params = None
        self.metrics = {}
        
        if model_type == "xgb" and not HAS_XGBOOST:
            print("⚠️ XGBoost not available, falling back to Random Forest")
            self.model_type = "rf"
    
    def _create_base_model(self):
        """Create base model with default params."""
        if self.model_type == "rf":
            return RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
        else:
            return xgb.XGBClassifier(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                use_label_encoder=False,
                eval_metric="mlogloss"
            )
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        tune_hyperparams: bool = False,
        n_iter: int = 20
    ) -> 'BaselineStatusClassifier':
        """
        Train the classifier.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            tune_hyperparams: Whether to run hyperparameter tuning
            n_iter: Number of random search iterations
        """
        if tune_hyperparams:
            print(f"🔧 Tuning {self.model_type.upper()} hyperparameters...")
            self.model = self._tune_hyperparams(X_train, y_train, n_iter)
        else:
            self.model = self._create_base_model()
            self.model.fit(X_train, y_train)
        
        # Evaluate on training set
        train_pred = self.model.predict(X_train)
        self.metrics["train_accuracy"] = accuracy_score(y_train, train_pred)
        self.metrics["train_f1_macro"] = f1_score(y_train, train_pred, average="macro")
        
        # Evaluate on validation set if provided
        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            self.metrics["val_accuracy"] = accuracy_score(y_val, val_pred)
            self.metrics["val_f1_macro"] = f1_score(y_val, val_pred, average="macro")
            self.metrics["val_f1_per_class"] = f1_score(y_val, val_pred, average=None).tolist()
        
        return self
    
    def _tune_hyperparams(self, X: np.ndarray, y: np.ndarray, n_iter: int):
        """Run randomized hyperparameter search."""
        if self.model_type == "rf":
            base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
            param_dist = {
                "n_estimators": RF_CONFIG["n_estimators"],
                "max_depth": RF_CONFIG["max_depth"],
                "min_samples_leaf": RF_CONFIG["min_samples_leaf"],
                "max_features": RF_CONFIG["max_features"],
            }
        else:
            base_model = xgb.XGBClassifier(
                random_state=42, use_label_encoder=False, eval_metric="mlogloss"
            )
            param_dist = {
                "n_estimators": XGB_CONFIG["n_estimators"],
                "max_depth": XGB_CONFIG["max_depth"],
                "learning_rate": XGB_CONFIG["learning_rate"],
                "subsample": XGB_CONFIG["subsample"],
                "colsample_bytree": XGB_CONFIG["colsample_bytree"],
            }
        
        search = RandomizedSearchCV(
            base_model,
            param_dist,
            n_iter=n_iter,
            cv=5,
            scoring="f1_macro",
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        search.fit(X, y)
        self.best_params = search.best_params_
        print(f"✅ Best params: {self.best_params}")
        
        return search.best_estimator_
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        return self.model.predict_proba(X)
    
    def get_feature_importance(self, feature_names: Optional[list] = None) -> Dict[str, float]:
        """Get feature importance scores."""
        importances = self.model.feature_importances_
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        return dict(sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def save(self, path: Optional[Path] = None):
        """Save model to disk."""
        if path is None:
            path = MODELS_DIR / f"status_{self.model_type}_model.pkl"
        
        joblib.dump({
            "model": self.model,
            "model_type": self.model_type,
            "best_params": self.best_params,
            "metrics": self.metrics,
        }, path)
        print(f"💾 Model saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'BaselineStatusClassifier':
        """Load model from disk."""
        data = joblib.load(path)
        classifier = cls(model_type=data["model_type"])
        classifier.model = data["model"]
        classifier.best_params = data["best_params"]
        classifier.metrics = data["metrics"]
        return classifier


class BaselineTimeRegressor:
    """
    Baseline regressor for processing time estimation.
    """
    
    def __init__(self, model_type: str = "rf"):
        self.model_type = model_type
        self.model = None
        self.metrics = {}
        
        if model_type == "xgb" and not HAS_XGBOOST:
            self.model_type = "rf"
    
    def _create_base_model(self):
        if self.model_type == "rf":
            return RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
        else:
            return xgb.XGBRegressor(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> 'BaselineTimeRegressor':
        """Train the regressor."""
        self.model = self._create_base_model()
        self.model.fit(X_train, y_train)
        
        # Training metrics
        train_pred = self.model.predict(X_train)
        self.metrics["train_mae"] = mean_absolute_error(y_train, train_pred)
        self.metrics["train_rmse"] = np.sqrt(mean_squared_error(y_train, train_pred))
        
        # Validation metrics
        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            self.metrics["val_mae"] = mean_absolute_error(y_val, val_pred)
            self.metrics["val_rmse"] = np.sqrt(mean_squared_error(y_val, val_pred))
            self.metrics["val_r2"] = r2_score(y_val, val_pred)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict processing time."""
        return self.model.predict(X)
    
    def predict_with_interval(
        self,
        X: np.ndarray,
        confidence: float = 0.80
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict with confidence interval using quantile estimation.
        
        Returns:
            (median_pred, lower_bound, upper_bound)
        """
        if self.model_type == "rf":
            # Use individual tree predictions for uncertainty
            all_preds = np.array([
                tree.predict(X) for tree in self.model.estimators_
            ])
            
            lower_q = (1 - confidence) / 2
            upper_q = 1 - lower_q
            
            median_pred = np.median(all_preds, axis=0)
            lower_bound = np.quantile(all_preds, lower_q, axis=0)
            upper_bound = np.quantile(all_preds, upper_q, axis=0)
        else:
            # Simple heuristic for XGBoost
            pred = self.model.predict(X)
            std = np.std(X, axis=1) * 10  # Rough uncertainty estimate
            median_pred = pred
            lower_bound = pred - std
            upper_bound = pred + std
        
        return median_pred, np.maximum(0, lower_bound), upper_bound
    
    def save(self, path: Optional[Path] = None):
        if path is None:
            path = MODELS_DIR / f"time_{self.model_type}_model.pkl"
        
        joblib.dump({
            "model": self.model,
            "model_type": self.model_type,
            "metrics": self.metrics,
        }, path)
        print(f"💾 Model saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'BaselineTimeRegressor':
        data = joblib.load(path)
        regressor = cls(model_type=data["model_type"])
        regressor.model = data["model"]
        regressor.metrics = data["metrics"]
        return regressor


if __name__ == "__main__":
    # Quick test with dummy data
    print("🧪 Testing baseline models with dummy data...")
    
    X = np.random.randn(100, 10)
    y_class = np.random.randint(0, 3, 100)
    y_reg = np.random.randint(20, 100, 100)
    
    # Test classifier
    clf = BaselineStatusClassifier(model_type="rf")
    clf.train(X[:80], y_class[:80], X[80:], y_class[80:])
    print(f"✅ Classifier metrics: {clf.metrics}")
    
    # Test regressor
    reg = BaselineTimeRegressor(model_type="rf")
    reg.train(X[:80], y_reg[:80], X[80:], y_reg[80:])
    print(f"✅ Regressor metrics: {reg.metrics}")
    
    # Test prediction with interval
    median, lower, upper = reg.predict_with_interval(X[80:])
    print(f"✅ Predictions with CI: median={median[:3]}, range=[{lower[:3]}, {upper[:3]}]")
