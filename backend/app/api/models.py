"""
Model Management API Endpoints

List, switch, and manage ML model versions.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import json
from pathlib import Path

router = APIRouter()


class ModelInfo(BaseModel):
    """Information about a model version."""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    version: str
    type: str  # baseline, hf, mock
    trained_at: Optional[str] = None
    metrics: dict = {}
    is_active: bool = False


class ModelSwitchRequest(BaseModel):
    """Request to switch active model."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_type: str  # mock, baseline, hf


# Models directory
MODELS_DIR = Path(__file__).parent.parent.parent / "ml_core" / "models"

# Active model state
_active_model_type = "mock"


@router.get("", response_model=List[ModelInfo])
async def list_models():
    """List all available model versions."""
    models = [
        ModelInfo(
            name="Mock Predictor",
            version="v1.0.0-mock",
            type="mock",
            trained_at=None,
            metrics={},
            is_active=_active_model_type == "mock"
        )
    ]
    
    # Check for baseline models
    rf_status_path = MODELS_DIR / "status_rf_model.pkl"
    if rf_status_path.exists():
        report_path = MODELS_DIR / "training_report_rf.json"
        metrics = {}
        trained_at = None
        
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                metrics = {
                    "f1_macro": report.get("status_metrics", {}).get("test", {}).get("f1_macro"),
                    "mae": report.get("time_metrics", {}).get("test", {}).get("mae"),
                }
                trained_at = report.get("report_generated_at")
        
        models.append(ModelInfo(
            name="Random Forest Baseline",
            version="v1.0.0-baseline-rf",
            type="baseline",
            trained_at=trained_at,
            metrics=metrics,
            is_active=_active_model_type == "baseline"
        ))
    
    # Check for XGBoost models
    xgb_status_path = MODELS_DIR / "status_xgb_model.pkl"
    if xgb_status_path.exists():
        report_path = MODELS_DIR / "training_report_xgb.json"
        metrics = {}
        trained_at = None
        
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                metrics = {
                    "f1_macro": report.get("status_metrics", {}).get("test", {}).get("f1_macro"),
                    "mae": report.get("time_metrics", {}).get("test", {}).get("mae"),
                }
                trained_at = report.get("report_generated_at")
        
        models.append(ModelInfo(
            name="XGBoost Baseline",
            version="v1.0.0-baseline-xgb",
            type="baseline-xgb",
            trained_at=trained_at,
            metrics=metrics,
            is_active=_active_model_type == "baseline-xgb"
        ))
    
    # Check for BERT model
    bert_path = MODELS_DIR / "bert_status_model"
    if bert_path.exists():
        report_path = MODELS_DIR / "bert_training_report.json"
        metrics = {}
        trained_at = None
        
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                metrics = {
                    "f1_macro": report.get("test_f1_macro"),
                    "accuracy": report.get("test_accuracy"),
                }
                trained_at = report.get("trained_at")
        
        models.append(ModelInfo(
            name="BERT Status Classifier",
            version="v1.0.0-hf-bert",
            type="hf",
            trained_at=trained_at,
            metrics=metrics,
            is_active=_active_model_type == "hf"
        ))
    
    # Check for MiniLM model
    minilm_path = MODELS_DIR / "minilm_time_model"
    if minilm_path.exists():
        report_path = MODELS_DIR / "minilm_training_report.json"
        metrics = {}
        trained_at = None
        
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                metrics = {
                    "mae": report.get("test_mae"),
                    "coverage": report.get("ci_coverage"),
                }
                trained_at = report.get("trained_at")
        
        models.append(ModelInfo(
            name="MiniLM Time Estimator",
            version="v1.0.0-hf-minilm",
            type="hf",
            trained_at=trained_at,
            metrics=metrics,
            is_active=_active_model_type == "hf"
        ))
    
    return models


@router.get("/active")
async def get_active_model():
    """Get the currently active model."""
    return {
        "model_type": _active_model_type,
        "version": f"v1.0.0-{_active_model_type}",
    }


@router.post("/switch")
async def switch_model(request: ModelSwitchRequest):
    """
    Switch to a different model type.
    
    Requires model to be available.
    """
    global _active_model_type
    
    valid_types = ["mock", "baseline", "baseline-xgb", "hf"]
    if request.model_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model type. Must be one of: {valid_types}"
        )
    
    # Check if model is available
    if request.model_type == "baseline":
        rf_path = MODELS_DIR / "status_rf_model.pkl"
        if not rf_path.exists():
            raise HTTPException(
                status_code=400,
                detail="Baseline model not trained. Run `python ml/train_baseline.py` first."
            )
    
    if request.model_type == "hf":
        bert_path = MODELS_DIR / "bert_status_model"
        if not bert_path.exists():
            # Will use pretrained
            pass
    
    _active_model_type = request.model_type
    
    # Reload predictor
    from app.ml.predictor import get_predictor
    predictor = get_predictor(request.model_type)
    
    return {
        "message": f"Switched to {request.model_type} model",
        "model_type": _active_model_type,
        "model_version": f"v1.0.0-{_active_model_type}",
    }


@router.get("/metrics/{model_type}")
async def get_model_metrics(model_type: str):
    """Get detailed metrics for a model type."""
    report_paths = {
        "baseline": MODELS_DIR / "training_report_rf.json",
        "hf-bert": MODELS_DIR / "bert_training_report.json",
        "hf-minilm": MODELS_DIR / "minilm_training_report.json",
    }
    
    if model_type not in report_paths and model_type != "mock":
        raise HTTPException(status_code=404, detail="Model type not found")
    
    if model_type == "mock":
        return {"message": "Mock model has no metrics"}
    
    report_path = report_paths.get(model_type)
    if not report_path or not report_path.exists():
        raise HTTPException(status_code=404, detail="Metrics not available")
    
    with open(report_path) as f:
        return json.load(f)
