# Quick Deployment Commands for VisaSight

## Step 1: Initialize Git and Push to GitHub

```bash
# Navigate to project root
cd c:\Users\shabbir7\Desktop\ai\visasight

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - VisaSight v1.0 ready for deployment"

# Create main branch
git branch -M main

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/visasight.git

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy Backend to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select "visasight" repository
5. Configure:
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (copy from backend/.env):
   - `SUPABASE_URL=...`
   - `SUPABASE_KEY=...`
7. Click "Deploy"
8. Copy your Railway URL (e.g., `https://visasight-backend.railway.app`)

## Step 3: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import "visasight" from GitHub
4. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend.railway.app` (use your Railway URL)
   - `NEXT_PUBLIC_SUPABASE_URL=...` (copy from backend/.env)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY=...` (copy from backend/.env)
6. Update `frontend/vercel.json` with your Railway URL
7. Click "Deploy"
8. Your site is live at `https://your-project.vercel.app`

## Step 4: Test Deployment

```bash
# Test backend
curl https://your-backend.railway.app/health

# Test frontend
# Visit: https://your-project.vercel.app
# Check Settings page - all should be green!
```

## That's it! 🎉

Your VisaSight app is now live and accessible worldwide!
