"""
SHAP-based Explainability Module

Provides explanations for visa predictions using SHAP and feature attribution.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

from config import STATUS_LABELS


@dataclass
class ExplanationFactor:
    """Single factor contributing to a prediction."""
    feature: str
    impact: str  # positive, negative, neutral
    contribution: float
    description: str


@dataclass
class PredictionExplanation:
    """Complete explanation for a prediction."""
    top_factors: List[ExplanationFactor]
    feature_importance: Dict[str, float]
    model_confidence: float
    shap_values: Optional[np.ndarray] = None


class ShapExplainer:
    """
    SHAP-based explainability for visa predictions.
    """
    
    def __init__(self, model, model_type: str = "tree"):
        """
        Args:
            model: Trained model (sklearn, xgboost, etc.)
            model_type: "tree" for tree-based, "kernel" for general
        """
        self.model = model
        self.model_type = model_type
        self.explainer = None
        self.feature_names = None
    
    def fit(
        self,
        X_background: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> 'ShapExplainer':
        """
        Initialize SHAP explainer with background data.
        """
        if not HAS_SHAP:
            print("⚠️ SHAP not available. Using fallback explanations.")
            self.feature_names = feature_names or [f"feature_{i}" for i in range(X_background.shape[1])]
            return self
        
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X_background.shape[1])]
        
        if self.model_type == "tree":
            self.explainer = shap.TreeExplainer(self.model)
        else:
            # Use background sample
            background = shap.sample(X_background, min(100, len(X_background)))
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba if hasattr(self.model, 'predict_proba') else self.model.predict,
                background
            )
        
        return self
    
    def explain(
        self,
        X: np.ndarray,
        top_n: int = 5,
        predicted_class: Optional[int] = None
    ) -> PredictionExplanation:
        """
        Generate explanation for a prediction.
        
        Args:
            X: Single sample or batch
            top_n: Number of top factors to return
            predicted_class: Class index for multiclass explanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        if HAS_SHAP and self.explainer is not None:
            shap_values = self.explainer.shap_values(X)
            
            # Handle multiclass
            if isinstance(shap_values, list):
                if predicted_class is not None:
                    shap_vals = shap_values[predicted_class][0]
                else:
                    # Use class with highest contribution
                    shap_vals = shap_values[np.argmax([sv[0].sum() for sv in shap_values])][0]
            else:
                shap_vals = shap_values[0]
        else:
            # Fallback: use feature importance from model
            shap_vals = self._get_fallback_importance(X)
        
        # Extract top factors
        top_factors = self._extract_top_factors(shap_vals, top_n)
        
        # Feature importance dict
        importance_dict = {
            name: abs(float(val))
            for name, val in zip(self.feature_names, shap_vals)
        }
        importance_dict = dict(sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Confidence based on prediction clarity
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(X)[0]
            confidence = float(np.max(probs))
        else:
            confidence = 0.75  # Default
        
        return PredictionExplanation(
            top_factors=top_factors,
            feature_importance=importance_dict,
            model_confidence=confidence,
            shap_values=shap_vals
        )
    
    def _extract_top_factors(
        self,
        shap_vals: np.ndarray,
        top_n: int
    ) -> List[ExplanationFactor]:
        """Extract top contributing factors."""
        # Sort by absolute value
        sorted_idx = np.argsort(np.abs(shap_vals))[::-1]
        
        factors = []
        for idx in sorted_idx[:top_n]:
            val = shap_vals[idx]
            feature = self.feature_names[idx]
            
            if val > 0.01:
                impact = "positive"
            elif val < -0.01:
                impact = "negative"
            else:
                impact = "neutral"
            
            description = self._generate_description(feature, impact)
            
            factors.append(ExplanationFactor(
                feature=feature,
                impact=impact,
                contribution=float(val),
                description=description
            ))
        
        return factors
    
    def _generate_description(self, feature: str, impact: str) -> str:
        """Generate human-readable description for a factor."""
        descriptions = {
            ("prior_travel", "positive"): "Previous US travel history increases approval likelihood",
            ("prior_travel", "negative"): "No prior travel may require additional documentation",
            ("sponsor_type", "positive"): "Strong sponsorship demonstrates ties and support",
            ("sponsor_type", "negative"): "Sponsorship type may require additional verification",
            ("document_count", "positive"): "Complete documentation submitted",
            ("document_count", "negative"): "Consider submitting additional supporting documents",
            ("nationality", "positive"): "Nationality has favorable processing statistics",
            ("nationality", "negative"): "Nationality may experience longer processing times",
            ("visa_type", "positive"): "Visa category has strong approval rates",
            ("visa_type", "negative"): "Visa category requires thorough documentation",
            ("consulate", "positive"): "Consulate has efficient processing times",
            ("consulate", "negative"): "Consulate may have longer wait times",
            ("days_since_submission", "positive"): "Application timing is favorable",
            ("days_since_submission", "negative"): "Extended processing time expected",
        }
        
        key = (feature, impact)
        default = f"{feature.replace('_', ' ').title()} has {impact} impact on prediction"
        
        return descriptions.get(key, default)
    
    def _get_fallback_importance(self, X: np.ndarray) -> np.ndarray:
        """Fallback when SHAP not available."""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        else:
            # Random importance for demo
            n_features = X.shape[1] if X.ndim > 1 else len(X)
            importance = np.random.random(n_features)
            importance = importance / importance.sum()
        
        # Add sign based on feature values
        signs = np.sign(X[0] - 0.5) if X.ndim > 1 else np.sign(X - 0.5)
        return importance * signs


def generate_user_explanation(
    explanation: PredictionExplanation,
    predicted_status: str,
    estimated_days: int
) -> Dict[str, Any]:
    """
    Generate user-friendly explanation for frontend display.
    """
    # Top factors formatted
    factors_formatted = []
    for factor in explanation.top_factors:
        contribution_pct = abs(factor.contribution) * 100
        sign = "+" if factor.impact == "positive" else ("-" if factor.impact == "negative" else "")
        
        factors_formatted.append({
            "feature": factor.feature,
            "impact": factor.impact,
            "contribution": f"{sign}{contribution_pct:.1f}%",
            "description": factor.description,
        })
    
    # Confidence text
    if explanation.model_confidence >= 0.85:
        confidence_text = "High confidence"
    elif explanation.model_confidence >= 0.70:
        confidence_text = "Moderate confidence"
    else:
        confidence_text = "Lower confidence - consider additional documentation"
    
    return {
        "summary": f"Based on your case details, we predict {predicted_status.upper()} "
                   f"with {explanation.model_confidence*100:.0f}% confidence. "
                   f"Estimated processing time: {estimated_days} days.",
        "top_factors": factors_formatted,
        "confidence_level": confidence_text,
        "model_confidence": round(explanation.model_confidence, 2),
        "recommendation": _generate_recommendation(explanation.top_factors),
    }


def _generate_recommendation(factors: List[ExplanationFactor]) -> str:
    """Generate actionable recommendation based on factors."""
    negative_factors = [f for f in factors if f.impact == "negative"]
    
    if not negative_factors:
        return "Your application looks strong. Ensure all documents are in order and submit promptly."
    
    # Recommendations based on negative factors
    recommendations = []
    
    for factor in negative_factors[:2]:
        if "document" in factor.feature.lower():
            recommendations.append("Consider submitting additional supporting documents")
        elif "sponsor" in factor.feature.lower():
            recommendations.append("Strengthen your sponsorship documentation")
        elif "travel" in factor.feature.lower():
            recommendations.append("Provide any prior travel history documentation")
    
    if not recommendations:
        recommendations.append("Review your application for any missing information")
    
    return ". ".join(set(recommendations)) + "."


if __name__ == "__main__":
    print("🧪 Testing Explainability Module...")
    
    # Mock model for testing
    class MockModel:
        feature_importances_ = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
        
        def predict(self, X):
            return np.zeros(len(X))
        
        def predict_proba(self, X):
            return np.array([[0.7, 0.2, 0.1]] * len(X))
    
    model = MockModel()
    feature_names = ["prior_travel", "sponsor_type", "document_count", "nationality", "consulate"]
    
    explainer = ShapExplainer(model, model_type="kernel")
    X_bg = np.random.random((10, 5))
    explainer.fit(X_bg, feature_names)
    
    # Generate explanation
    X_test = np.array([[0.8, 0.5, 0.9, 0.3, 0.6]])
    explanation = explainer.explain(X_test, top_n=3)
    
    print(f"✅ Top factors: {[f.feature for f in explanation.top_factors]}")
    print(f"   Confidence: {explanation.model_confidence:.2f}")
    
    # User explanation
    user_exp = generate_user_explanation(explanation, "approved", 45)
    print(f"   Summary: {user_exp['summary']}")
