---
description: Deploy VisaSight to Railway and Vercel
---

# VisaSight Deployment Workflow

## Prerequisites Check

1. Ensure you have accounts on:
   - GitHub (already configured ✅)
   - Railway.app
   - Vercel.com

2. Ensure your Supabase database is set up and accessible

## Step 1: Test Local Backend

// turbo
```bash
cd backend
python -m uvicorn main:app --reload
```

Visit http://localhost:8000/docs to verify the API is working.

## Step 2: Test Local Frontend

Open a new terminal and run:

// turbo
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 to verify the frontend is working.

## Step 3: Commit and Push to GitHub

If you have any uncommitted changes:

```bash
git add .
git commit -m "Ready for deployment - VisaSight v1.0"
git push origin main
```

## Step 4: Deploy Backend to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your **visasight** repository
5. Configure the service:
   - Click on the newly created service
   - Go to **Settings**
   - Set **Root Directory:** `backend`
   - Set **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - Go to **Variables** tab
   - Add the following variables (copy from your `backend/.env` file):
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `API_HOST=0.0.0.0`
     - `DEBUG=false`
7. Click **Deploy**
8. Go to **Settings** → **Networking** → **Generate Domain**
9. Copy your Railway URL (e.g., `https://visasight-backend-production.up.railway.app`)

## Step 5: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import your **visasight** repository from GitHub
4. Configure the project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - Click **"Continue"**
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = Your Railway backend URL (from Step 4)
   - `NEXT_PUBLIC_SUPABASE_URL` = Your Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Your Supabase Anon Key
6. Click **"Deploy"**
7. Wait for deployment to complete (~2-3 minutes)
8. Copy your Vercel URL (e.g., `https://visasight.vercel.app`)

## Step 6: Update CORS Settings

After deployment, you need to update your backend's CORS settings to allow requests from your Vercel frontend:

1. In your `backend/main.py` or `backend/app/main.py`, update the CORS origins to include your Vercel URL
2. Commit and push the changes
3. Railway will automatically redeploy

## Step 7: Test Your Deployment

1. Test Backend Health:
```bash
curl https://your-railway-url.railway.app/health
```

2. Visit your Vercel frontend URL in a browser
3. Navigate to the Settings page and verify all indicators are green
4. Try making a visa prediction to ensure end-to-end functionality

## Step 8: Monitor and Verify

1. Check Railway logs for any backend errors
2. Check Vercel deployment logs for any frontend errors
3. Test all major features:
   - Visa status prediction
   - Processing time estimation
   - Settings page
   - Analytics/dashboard

## Post-Deployment

- Your backend is live at: `https://your-app.railway.app`
- Your frontend is live at: `https://your-app.vercel.app`
- Update your README.md with the live URLs
- Share your project! 🎉

## Troubleshooting

- **Backend 500 errors:** Check Railway logs and environment variables
- **Frontend can't connect to backend:** Verify NEXT_PUBLIC_API_URL is set correctly
- **CORS errors:** Update backend CORS settings to include your Vercel domain
- **Model loading errors:** Ensure model files are committed to the repository
