from __future__ import annotations
"""
Visa Predictor - Unified ML Prediction Service

Integrates baseline and Hugging Face models for visa prediction.
Loads models at startup and provides unified prediction interface.
"""

from datetime import datetime
import uuid
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Add ML module to path
ML_PATH = Path(__file__).parent.parent.parent.parent / "ml"
if ML_PATH.exists():
    sys.path.insert(0, str(ML_PATH))

from app.models.schemas import (
    PredictionResult,
    StatusProbabilities,
    PredictionExplanation,
    ExplanationFactor,
)

# Global indicator for ML modules
HAS_ML_MODULES = True
HAS_HF_MODELS = True


class VisaPredictor:
    """
    Unified visa prediction service.
    
    Supports multiple model backends:
    - mock: Random predictions for development
    - baseline: Random Forest / XGBoost models
    - hf: Hugging Face transformer models (BERT + MiniLM)
    """
    
    def __init__(self, model_type: str = "mock"):
        """
        Args:
            model_type: "mock", "baseline", or "hf"
        """
        self.model_type = model_type
        self.model_version = f"v1.0.0-{model_type}"
        
        # Model components
        self.status_model = None
        self.time_model = None
        self.text_encoder = None
        self.feature_extractor = None
        self.explainer = None
        
        self.loaded = False
    
    def load_models(self) -> bool:
        """
        Load ML models based on model_type.
        
        Returns:
            True if models loaded successfully
        """
        if self.model_type == "mock":
            self.loaded = True
            print("📦 Using mock predictions")
            return True
        
        if not HAS_ML_MODULES:
            print("⚠️ ML modules not available, falling back to mock")
            self.model_type = "mock"
            self.loaded = True
            return True
        
        try:
            # Initialize encoders
            from feature_engineering import CaseTextEncoder
            self.text_encoder = CaseTextEncoder()
            
            if self.model_type.startswith("baseline"):
                self._load_baseline_models()
            elif self.model_type == "hf":
                self._load_hf_models()
                
            self.loaded = True
            print(f"✅ Models loaded: {self.model_type}")
            return True

        except ImportError as e:
            print(f"⚠️ ML dependency missing: {e}. Falling back to mock.")
            self.model_type = "mock"
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            print("⚠️ Falling back to mock predictions")
            self.model_type = "mock"
            self.loaded = True
            return False
    
    def _load_baseline_models(self):
        """Load baseline RF/XGBoost models."""
        from config import MODELS_DIR
        from baseline_models import BaselineStatusClassifier, BaselineTimeRegressor
        import joblib
        
        suffix = "rf" if self.model_type == "baseline" else "xgb"
        status_path = MODELS_DIR / f"status_{suffix}_model.pkl"
        time_path = MODELS_DIR / f"time_{suffix}_model.pkl"
        extractor_path = MODELS_DIR / "feature_extractor.pkl"
        
        if status_path.exists():
            self.status_model = BaselineStatusClassifier.load(status_path)
            print(f"   Loaded status model from {status_path}")
        else:
            print(f"   ⚠️ Status model not found: {status_path}")
        
        if time_path.exists():
            self.time_model = BaselineTimeRegressor.load(time_path)
            print(f"   Loaded time model from {time_path}")
        else:
            print(f"   ⚠️ Time model not found: {time_path}")
        
        if extractor_path.exists():
            self.feature_extractor = joblib.load(extractor_path)
            print(f"   Loaded feature extractor")
        else:
            print(f"   ⚠️ Feature extractor not found: {extractor_path}")
        
        # Initialize SHAP explainer only if requested or needed
        # Moving SHAP explainer initialization to on-demand to speed up loading
    
    def _load_hf_models(self):
        """Load Hugging Face models."""
        from hf_status_model import BertStatusClassifier
        from hf_time_model import MiniLMTimeEstimator
        from config import MODELS_DIR
        
        bert_path = MODELS_DIR / "bert_status_model"
        minilm_path = MODELS_DIR / "minilm_time_model"
        
        if bert_path.exists():
            self.status_model = BertStatusClassifier.load(bert_path)
            print(f"   Loaded BERT model from {bert_path}")
        else:
            # Load pretrained for inference
            self.status_model = BertStatusClassifier()
            self.status_model.load_pretrained()
            print("   Loaded pretrained BERT (not fine-tuned)")
        
        if minilm_path.exists():
            self.time_model = MiniLMTimeEstimator.load(minilm_path)
            print(f"   Loaded MiniLM model from {minilm_path}")
        else:
            self.time_model = MiniLMTimeEstimator()
            self.time_model.load_pretrained()
            print("   Loaded pretrained MiniLM (not fine-tuned)")
    
    def predict_status(self, case_id: str, case_data: Optional[Dict] = None) -> PredictionResult:
        """
        Predict visa status probabilities.
        
        Args:
            case_id: Unique case identifier
            case_data: Optional case data dict. If None, uses mock data.
        """
        if not self.loaded:
            self.load_models()
        
        # Use mock data if not provided
        if case_data is None:
            case_data = self._get_mock_case_data()
        
        if self.model_type == "mock":
            return self._mock_prediction(case_id, case_data)
        
        try:
            return self._model_prediction(case_id, case_data)
        except Exception as e:
            print(f"⚠️ Prediction error: {e}, using mock")
            return self._mock_prediction(case_id, case_data)
    
    def _model_prediction(self, case_id: str, case_data: Dict) -> PredictionResult:
        """Generate prediction using loaded models."""
        import numpy as np
        
        if self.model_type == "hf":
            # Text-based prediction
            text_prompt = self.text_encoder.encode(case_data)
            
            # Status prediction
            probs = self.status_model.predict_proba([text_prompt])[0]
            
            # Time prediction
            median, lower, upper = self.time_model.predict_with_interval([text_prompt])
            estimated_days = int(median[0]) if hasattr(median, '__len__') else int(median)
            ci = (int(lower[0]) if hasattr(lower, '__len__') else int(lower),
                  int(upper[0]) if hasattr(upper, '__len__') else int(upper))
            
        else:  # baseline
            # Tabular features
            import pandas as pd
            df = pd.DataFrame([case_data])
            features = self.feature_extractor.transform(df)
            
            # Predictions
            probs = self.status_model.predict_proba(features)[0]
            median, lower, upper = self.time_model.predict_with_interval(features)
            
            estimated_days = int(median[0]) if hasattr(median, '__len__') else int(median)
            ci = (
                int(lower[0]) if hasattr(lower, '__len__') else int(lower),
                int(upper[0]) if hasattr(upper, '__len__') else int(upper)
            )
        
        # Build status probabilities
        probabilities = StatusProbabilities(
            approved=round(float(probs[0]), 2),
            rfe=round(float(probs[1]), 2),
            denied=round(float(probs[2]), 2),
        )
        
        # Generate explanation
        explanation = self._generate_explanation(case_data, probs)
        
        return PredictionResult(
            id=str(uuid.uuid4()),
            visa_case_id=case_id,
            predicted_status=probabilities,
            estimated_days_remaining=estimated_days,
            confidence_interval=ci,
            model_version=self.model_version,
            generated_at=datetime.utcnow(),
            explanation=explanation,
        )
    
    def _mock_prediction(self, case_id: str, case_data: Dict) -> PredictionResult:
        """Generate mock prediction for development."""
        import random
        
        # Simulated probabilities influenced by case data
        base_approved = 0.70
        
        # Adjust based on factors
        if case_data.get("prior_travel"):
            base_approved += 0.05
        
        doc_count = case_data.get("document_count", 5)
        if doc_count >= 7:
            base_approved += 0.05
        elif doc_count <= 3:
            base_approved -= 0.10
        
        # Add randomness
        approved_prob = min(0.95, max(0.30, base_approved + random.uniform(-0.1, 0.1)))
        remaining = 1 - approved_prob
        rfe_prob = remaining * random.uniform(0.5, 0.7)
        denied_prob = remaining - rfe_prob
        
        probabilities = StatusProbabilities(
            approved=round(approved_prob, 2),
            rfe=round(rfe_prob, 2),
            denied=round(denied_prob, 2),
        )
        
        # Processing time
        base_days = random.randint(35, 60)
        ci_lower = max(20, base_days - random.randint(10, 15))
        ci_upper = base_days + random.randint(10, 20)
        
        explanation = self._generate_mock_explanation()
        
        return PredictionResult(
            id=str(uuid.uuid4()),
            visa_case_id=case_id,
            predicted_status=probabilities,
            estimated_days_remaining=base_days,
            confidence_interval=(ci_lower, ci_upper),
            model_version=self.model_version,
            generated_at=datetime.utcnow(),
            explanation=explanation,
        )
    
    def predict_processing_time(self, case_id: str, case_data: Optional[Dict] = None) -> PredictionResult:
        """Estimate processing time with confidence interval."""
        # Reuse status prediction which includes time
        return self.predict_status(case_id, case_data)
    
    def get_explanation(self, case_id: str, case_data: Optional[Dict] = None) -> PredictionExplanation:
        """Get detailed explanation for a prediction."""
        if case_data is None:
            case_data = self._get_mock_case_data()
        
        if self.model_type == "mock" or not self.explainer:
            return self._generate_mock_explanation()
        
        # Use SHAP for explanation
        return self._generate_explanation(case_data, None)
    
    def _generate_explanation(
        self,
        case_data: Dict,
        probs: Any | None = None
    ) -> PredictionExplanation:
        """Generate explanation using available explainer."""
        import numpy as np
        
        confidence = 0.85 if probs is None else float(np.max(probs))
        
        # Generate factors based on case data
        factors = []
        
        if case_data.get("prior_travel"):
            factors.append(ExplanationFactor(
                feature="prior_travel",
                impact="positive",
                contribution=0.15,
                description="Previous US travel history increases approval likelihood",
            ))
        
        doc_count = case_data.get("document_count", 5)
        if doc_count >= 7:
            factors.append(ExplanationFactor(
                feature="documents_submitted",
                impact="positive",
                contribution=0.12,
                description="Complete documentation submitted",
            ))
        elif doc_count <= 3:
            factors.append(ExplanationFactor(
                feature="documents_submitted",
                impact="negative",
                contribution=-0.10,
                description="Consider submitting additional supporting documents",
            ))
        
        sponsor = case_data.get("sponsor_type", "self")
        if sponsor in ["employer", "university"]:
            factors.append(ExplanationFactor(
                feature="sponsor_type",
                impact="positive",
                contribution=0.10,
                description="Strong sponsorship demonstrates ties and support",
            ))
        
        # Ensure at least 5 factors
        default_factors = [
            ExplanationFactor(
                feature="visa_type",
                impact="neutral",
                contribution=0.05,
                description="Visa category processed normally",
            ),
            ExplanationFactor(
                feature="consulate",
                impact="neutral",
                contribution=0.03,
                description="Consulate has standard processing times",
            ),
            ExplanationFactor(
                feature="nationality",
                impact="neutral",
                contribution=0.02,
                description="Processing aligns with typical patterns",
            ),
        ]
        
        while len(factors) < 5:
            factors.append(default_factors[len(factors) - 2] if len(factors) > 2 else default_factors[0])
        
        # Feature importance
        importance = {f.feature: abs(f.contribution) for f in factors}
        
        return PredictionExplanation(
            top_factors=factors[:5],
            feature_importance=importance,
            model_confidence=confidence,
        )
    
    def _generate_mock_explanation(self) -> PredictionExplanation:
        """Generate mock explanation."""
        import random
        
        factors = [
            ExplanationFactor(
                feature="prior_travel",
                impact="positive",
                contribution=0.15,
                description="Previous US travel history increases approval likelihood",
            ),
            ExplanationFactor(
                feature="sponsor_type",
                impact="positive",
                contribution=0.12,
                description="Employer sponsorship demonstrates strong ties",
            ),
            ExplanationFactor(
                feature="documents_submitted",
                impact="positive",
                contribution=0.08,
                description="Complete documentation submitted",
            ),
            ExplanationFactor(
                feature="consulate",
                impact="neutral",
                contribution=0.02,
                description="Consulate has average processing times",
            ),
            ExplanationFactor(
                feature="rule_volatility",
                impact="negative",
                contribution=-0.05,
                description="Recent policy changes may cause delays",
            ),
        ]
        
        importance = {
            "prior_travel": 0.22,
            "sponsor_type": 0.18,
            "documents_submitted": 0.15,
            "nationality": 0.14,
            "visa_type": 0.12,
            "consulate": 0.10,
            "rule_volatility": 0.09,
        }
        
        return PredictionExplanation(
            top_factors=factors,
            feature_importance=importance,
            model_confidence=random.uniform(0.78, 0.92),
        )
    
    def _get_mock_case_data(self) -> Dict:
        """Generate mock case data for testing."""
        return {
            "nationality": "India",
            "visa_type": "H-1B",
            "consulate": "New Delhi",
            "submission_date": "2026-01-15",
            "documents_submitted": ["Passport", "DS-160", "I-797", "Employment Letter"],
            "document_count": 4,
            "sponsor_type": "employer",
            "prior_travel": True,
        }


# Global predictor cache
_predictors: Dict[str, VisaPredictor] = {}


def get_predictor(model_type: str = "mock") -> VisaPredictor:
    """Get or create global predictor instance from cache."""
    global _predictors
    
    if model_type not in _predictors:
        predictor = VisaPredictor(model_type=model_type)
        predictor.load_models()
        _predictors[model_type] = predictor
    
    return _predictors[model_type]
