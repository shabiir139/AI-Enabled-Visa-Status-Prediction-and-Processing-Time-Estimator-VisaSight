"""
AI Prediction API Endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import random

from app.models.schemas import (
    PredictRequest,
    PredictionResult,
    StatusProbabilities,
    PredictionExplanation,
    ExplanationFactor,
)
from app.ml.predictor import get_predictor

router = APIRouter()

# Get global predictor
predictor = get_predictor()


@router.post("/status", response_model=PredictionResult)
async def predict_status(request: PredictRequest):
    """
    Predict visa status probabilities.
    
    Uses XGBoost/LightGBM models to predict the probability
    of Approved, RFE, or Denied outcomes.
    """
    # Generate prediction using ML model
    prediction = predictor.predict_status(request.case_id, request.case_data)
    return prediction


@router.post("/processing-time", response_model=PredictionResult)
async def predict_processing_time(request: PredictRequest):
    """
    Estimate visa processing time.
    
    Uses survival analysis models to estimate remaining
    days until decision with confidence intervals.
    """
    prediction = predictor.predict_processing_time(request.case_id, request.case_data)
    return prediction


@router.get("/explain/{case_id}")
async def get_prediction_explanation(case_id: str):
    """
    Get SHAP-based explanation for a prediction.
    
    Returns feature importance and top factors
    influencing the prediction.
    """
    explanation = predictor.get_explanation(case_id)
    return explanation
