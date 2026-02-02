# VisaSight Deployment Guide (Updated)

I have completed the critical code refactoring to ensure your backend works properly. The main issue was that the Machine Learning models were in a separate folder that wasn't being deployed with the backend.

## ✅ Completed Fixes
1.  **Refactored Project Structure**: Moved `visasight/ml` into `visasight/backend/ml_core`.
2.  **Updated Code**: Modified `predictor.py` and `models.py` to point to the new location.
3.  **Verified Imports**: The backend now strictly contains all necessary ML code.

## 🚀 Final Deployment Steps (Required)

You must now perform these steps in your Railway and Vercel dashboards to finalize the fix.

### 1. Railway (Backend)
Navigate to your Railway project settings for the backend service.

*   **Root Directory**: Verify this is set to `/visasight/backend`.
    *   *Why?* The `main.py` file is inside this folder.
*   **Environment Variables**:
    *   `SUPABASE_URL`: (Your Supabase URL)
    *   `SUPABASE_KEY`: (Your Supabase Link/Anon Key)
    *   `FRONTEND_URL`: `https://ai-enabled-visa-status-prediction-visa-sight-fronten-eosfatc1l.vercel.app` (or similar Vercel URL)
    *   `MODEL_TYPE`: `mock` (Start with `mock` to verify the API works, then switch to `hf` or `baseline`)
    *   `LOAD_MODELS_ON_STARTUP`: `false` (Recommended `false` for free tier to prevent "Out of Memory" crashes)

### 2. Vercel (Frontend)
Navigate to your Vercel project settings.

*   **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: **Must match your Railway URL** (e.g., `https://visasight-production.up.railway.app`).
        *   *Note*: Ensure there is NO trailing slash `/`.
    *   `NEXT_PUBLIC_SUPABASE_URL`: (Same as backend)
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (Same as backend)

### 3. Verification
1.  **Deploy**: Commit these changes and wait for Railway to build.
    *   *The build should now verify dependencies verify `ml_core` is present.*
2.  **Check Backend**: Open your Railway URL (e.g., `https://...railway.app/`).
    *   It should show: `{"name":"VisaSight API","version":"1.0.0","status":"operational","docs":"/docs"}`.
    *   Access `/health`: Should return `{"status": "healthy"}`.
3.  **Check Frontend**: Open your Vercel URL.
    *   Go to **Settings**.
    *   "System Health" should show "API Server: Operational".

## Troubleshooting
-   **Still 404?** Your Railway "Root Directory" might still be wrong, or the specific Railway Service "Start Command" is overriding the default. Ensure it is simply `uvicorn main:app --host 0.0.0.0 --port $PORT`.
-   **ML Models Error?** If the settings page shows "ML Models: Error", check the Railway logs. If you are on the free tier, the "Hugging Face" models might be crashing due to memory. Switch `MODEL_TYPE` to `mock` or `baseline` in Railway variables.
