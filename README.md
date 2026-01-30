# VisaSight – AI-Enabled Visa Status Prediction & Processing Time Estimator

<div align="center">

![VisaSight Logo](https://img.shields.io/badge/VisaSight-AI%20Visa%20Predictor-3373FF?style=for-the-badge&logo=passport&logoColor=white)

**Predict visa outcomes and processing times with AI-powered insights**

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![BERT](https://img.shields.io/badge/BERT-Transformers-orange?style=flat-square&logo=huggingface)](https://huggingface.co/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com/)

</div>

---

## 🎯 Overview

VisaSight is an AI-powered platform that predicts visa decision outcomes and estimates processing times for US visa applications. It uses state-of-the-art machine learning models to provide explainable predictions with confidence intervals.

### Key Features

- **🔮 Status Prediction**: Predict visa outcomes (Approved/RFE/Denied) with probabilities
- **⏱️ Time Estimation**: Estimate processing time with 80% confidence intervals
- **📊 Explainable AI**: Understand what factors influence your prediction (SHAP-based)
- **📜 Rule Monitoring**: Track real-time visa policy changes
- **📈 Analytics Dashboard**: Visualize trends and statistics

---

## 🏗️ Architecture

```
visasight/
├── frontend/                 # Next.js 14 Application
│   ├── src/
│   │   ├── app/             # Pages (App Router)
│   │   ├── components/      # React Components
│   │   ├── lib/             # API client, types
│   │   └── styles/          # Global CSS
│   └── package.json
│
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/             # REST Endpoints
│   │   ├── ml/              # Prediction service
│   │   └── models/          # Pydantic schemas
│   ├── main.py
│   └── requirements.txt
│
├── ml/                       # ML Training Pipeline
│   ├── config.py            # Hyperparameters
│   ├── dataset_generator.py # Synthetic data
│   ├── feature_engineering.py
│   ├── baseline_models.py   # RF, XGBoost
│   ├── hf_status_model.py   # BERT classifier
│   ├── hf_time_model.py     # MiniLM estimator
│   ├── explainability.py    # SHAP explanations
│   ├── evaluate.py          # Metrics
│   ├── train_baseline.py    # Baseline training
│   ├── train_hf_status.py   # BERT training
│   └── train_hf_time.py     # MiniLM training
│
└── supabase/                 # Database
    └── migrations/           # SQL schemas
```

---

## 🧠 ML Models

### Status Prediction

| Model | Type | Accuracy Target |
|-------|------|-----------------|
| **BERT** (bert-base-uncased) | Transformer | F1 ≥ 0.70 |
| Random Forest | Baseline | F1 ≥ 0.65 |
| XGBoost | Baseline | F1 ≥ 0.68 |

### Time Estimation

| Model | Type | Accuracy Target |
|-------|------|-----------------|
| **MiniLM** (all-MiniLM-L6-v2) | Transformer | MAE ≤ 20% median |
| Random Forest | Baseline | MAE ≤ 25% median |
| XGBoost | Baseline | MAE ≤ 22% median |

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- (Optional) CUDA for GPU training

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/visasight.git
cd visasight
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 4. Train Models (Optional)

```bash
cd ml

# Generate synthetic dataset
python dataset_generator.py

# Train baseline models
python train_baseline.py --model rf

# Train BERT (requires GPU)
python train_hf_status.py

# Train MiniLM
python train_hf_time.py
```

---

## 📡 API Endpoints

### Predictions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predict/status` | POST | Predict visa status probabilities |
| `/api/predict/processing-time` | POST | Estimate processing time |
| `/api/predict/explain/{case_id}` | GET | Get SHAP explanation |

### Cases

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cases` | GET | List user's cases |
| `/api/cases` | POST | Create new case |
| `/api/cases/{id}` | GET | Get case by ID |

### Models

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | List available models |
| `/api/models/switch` | POST | Switch active model |
| `/api/models/metrics/{type}` | GET | Get model metrics |

---

## 📊 MVP Scope

- **Country**: United States only
- **Visa Types**: F-1, H-1B, B1/B2
- **Architecture**: Web application (Next.js + FastAPI)
- **Data**: Synthetic dataset for MVP

---

## 🎯 Acceptance Criteria

| Metric | Threshold |
|--------|-----------|
| Status F1 (macro) | ≥ 0.70 |
| Time MAE | ≤ 20% of median |
| 80% CI Coverage | ≥ 80% |
| Inference p95 | ≤ 500ms |

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

> **IMPORTANT**: VisaSight provides AI-generated predictions for informational purposes only. Predictions are **not legal advice** and should not replace consultation with qualified immigration attorneys. Visa decisions are ultimately made by government officials. Past performance of the model does not guarantee future accuracy.

---

<div align="center">

**Built with ❤️ for the visa applicant community**

</div>
