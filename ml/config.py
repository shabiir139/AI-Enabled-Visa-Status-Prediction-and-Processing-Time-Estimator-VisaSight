"""
ML Configuration - Hyperparameters and Settings
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Dataset Configuration
DATASET_CONFIG = {
    "synthetic_size": 10000,
    "random_seed": 42,
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
}

# Visa Types and their weights (for synthetic data generation)
VISA_TYPES = ["F-1", "H-1B", "B1/B2", "L-1", "O-1", "J-1"]
VISA_TYPE_WEIGHTS = [0.30, 0.35, 0.20, 0.08, 0.04, 0.03]

# Nationalities (top countries by visa applications)
NATIONALITIES = [
    "India", "China", "Mexico", "Philippines", "Vietnam",
    "Brazil", "South Korea", "Nigeria", "United Kingdom", "Canada",
    "Germany", "Japan", "Taiwan", "Pakistan", "Bangladesh"
]

# US Consulates
CONSULATES = [
    "New Delhi", "Mumbai", "Chennai", "Hyderabad", "Kolkata",
    "Beijing", "Shanghai", "Guangzhou", "Shenyang",
    "Mexico City", "Guadalajara", "Ciudad Juarez",
    "Manila", "London", "Toronto", "Frankfurt", "Tokyo", "Seoul"
]

# Sponsor Types
SPONSOR_TYPES = ["employer", "university", "self", "family", "government"]

# Documents
COMMON_DOCUMENTS = [
    "Passport", "DS-160", "Photo", "Fee Receipt",
    "I-20", "I-797", "Employment Letter", "Financial Docs",
    "Transcripts", "Resume", "Invitation Letter", "Travel Itinerary"
]

# Status Labels
STATUS_LABELS = ["approved", "rfe", "denied"]
STATUS_MAPPING = {"approved": 0, "rfe": 1, "denied": 2}

# Random Forest Configuration
RF_CONFIG = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [5, 10, 15, 20, 30, None],
    "min_samples_leaf": [1, 5, 10, 20],
    "max_features": ["sqrt", "log2"],
    "random_state": 42,
}

# XGBoost Configuration
XGB_CONFIG = {
    "n_estimators": [200, 400, 600, 800],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "max_depth": [3, 5, 7, 10],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
    "reg_alpha": [0, 0.1, 0.5, 1],
    "reg_lambda": [1, 2, 5, 10],
    "random_state": 42,
}

# BERT Configuration
BERT_CONFIG = {
    "model_name": "bert-base-uncased",
    "max_length": 256,
    "batch_size": 16,
    "epochs": 5,
    "learning_rate": 2e-5,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01,
}

# MiniLM Configuration
MINILM_CONFIG = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dim": 384,
    "batch_size": 32,
}

# Evaluation Thresholds
EVAL_THRESHOLDS = {
    "min_macro_f1": 0.70,
    "min_rfe_recall": 0.60,
    "min_denied_recall": 0.60,
    "max_mae_ratio": 0.20,  # 20% of median
    "min_ci_coverage": 0.80,
    "max_inference_ms": 500,
}

# Model Versioning
MODEL_VERSIONS = {
    "baseline_rf": "rf-visasight-v1.0",
    "baseline_xgb": "xgb-visasight-v1.0",
    "bert_status": "bert-visasight-status-v1.0",
    "minilm_time": "minilm-visasight-time-v1.0",
}
