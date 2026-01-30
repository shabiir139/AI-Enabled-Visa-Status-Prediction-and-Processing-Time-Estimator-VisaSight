"""
VisaSight Backend - FastAPI Application
AI-Enabled Visa Status Prediction & Processing Time Estimator
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import cases, predict, rules, dashboard, models, external


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Load ML models
    print("🚀 VisaSight API starting up...")
    print("📊 Pre-loading ML models for better performance...")
    
    # Pre-warm the predictor
    from app.ml.predictor import get_predictor
    # Initialize both mock and baseline to warm up caches
    get_predictor("mock").load_models()
    try:
        get_predictor("baseline").load_models()
        print("✅ Models loaded and ready.")
    except Exception as e:
        print(f"⚠️ Warning: Could not pre-load baseline models: {e}")
        
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
# Add Vercel preview URLs
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
