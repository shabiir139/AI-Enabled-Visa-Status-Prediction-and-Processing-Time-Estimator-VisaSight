"""
VisaSight Backend - FastAPI Application
AI-Enabled Visa Status Prediction & Processing Time Estimator
"""

from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import cases, predict, rules, dashboard, models, external


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    import os
    model_type = os.getenv("MODEL_TYPE", "mock")
    low_memory = os.getenv("LOW_MEMORY_MODE", "false").lower() == "true"
    
    print(f"🚀 VisaSight API starting up (Mode: {model_type})...")
    
    if low_memory:
        print("💡 Low memory mode enabled - skipping heavy model pre-loading")
    else:
        print(f"📊 Pre-loading {model_type} models...")
        from app.ml.predictor import get_predictor
        try:
            get_predictor(model_type).load_models()
            print(f"✅ {model_type.capitalize()} models loaded and ready.")
        except Exception as e:
            print(f"⚠️ Warning: Could not pre-load {model_type} models: {e}")
        
    yield
    # Shutdown
    print("👋 VisaSight API shutting down...")


app = FastAPI(
    title="VisaSight API",
    description="AI-Enabled Visa Status Prediction & Processing Time Estimator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware - Production Ready
import os
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Add Vercel production URL
vercel_prod_url = "https://ai-enabled-visa-status-prediction-visa-sight-fronten-eosfatc1l.vercel.app"
allowed_origins.append(vercel_prod_url)

# Add Vercel preview URLs from environment
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
    # Also add the root domain if it's a vercel URL
    if ".vercel.app" in vercel_url:
        root_domain = vercel_url.split(".vercel.app")[0]
        allowed_origins.append(f"https://{root_domain}.vercel.app")
        
# Allow all Vercel domains for development/preview flexibility
# This is safe for public APIs, adjust carefully for private ones
allowed_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex="https://.*\\.vercel\\.app", # Support for Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router, prefix="/api/cases", tags=["Visa Cases"])
app.include_router(predict.router, prefix="/api/predict", tags=["Predictions"])
app.include_router(rules.router, prefix="/api/rules", tags=["Visa Rules"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(models.router, prefix="/api/models", tags=["Model Management"])
app.include_router(external.router, prefix="/api", tags=["External Data"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "VisaSight API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    print("💓 Health check requested - Status: Healthy")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": os.getenv("MODEL_TYPE", "unknown")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
