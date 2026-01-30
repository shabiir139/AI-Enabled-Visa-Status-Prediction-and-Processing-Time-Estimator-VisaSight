# VisaSight Deployment Guide - Vercel & Railway
**Complete Production Deployment Instructions**

---

## 📋 Deployment Overview

Your VisaSight application has two parts:
1. **Frontend (Next.js)** → Deploy to **Vercel** ✅
2. **Backend (FastAPI)** → Deploy to **Railway** or **Render** 🚂

---

## 🎯 Prerequisites

Before deploying, ensure you have:
- [ ] GitHub account
- [ ] Vercel account (sign up at vercel.com)
- [ ] Railway account (sign up at railway.app) OR Render account
- [ ] Git installed on your computer
- [ ] All code committed to Git repository

---

## Part 1: Setup Git Repository 📦

### Step 1: Initialize Git (if not already done)

```bash
cd c:\Users\shabbir7\Desktop\ai\visasight
git init
```

### Step 2: Create .gitignore

Make sure you have a `.gitignore` file in the root:

```
# See https://help.github.com/articles/ignoring-files/ for more

# dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# testing
coverage/
*.log

# next.js
frontend/.next/
frontend/out/
frontend/build/

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*

# local env files
.env
.env.local
.env.development
.env.production.local
backend/.env

# IDE
.vscode/
.idea/
*.swp

# ML models (too large for git)
backend/ml/models/*.pkl
backend/ml/models/*.json

# Test files
frontend/test_page.html
backend/test_*.py
backend/*_output.txt
backend/test_results_*.json
backend/ab_test_results_*.json
```

### Step 3: Commit Your Code

```bash
git add .
git commit -m "Initial commit - VisaSight v1.0"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named "visasight"
3. DON'T initialize with README (you already have code)
4. Click "Create repository"

### Step 5: Push to GitHub

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/visasight.git
git push -u origin main
```

---

## Part 2: Deploy Backend to Railway 🚂

### Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Authorize Railway to access your GitHub

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your "visasight" repository
4. Railway will detect it's a monorepo

### Step 3: Configure Backend Service

1. Click "Add Service" → "GitHub Repo"
2. Select "visasight" repo
3. **Root Directory:** Set to `backend`
4. **Build Command:** Leave empty (uses requirements.txt automatically)
5. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

In Railway dashboard, go to Variables tab and add:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
PORT=8000
PYTHON_VERSION=3.11
```

### Step 5: Deploy Backend

1. Click "Deploy"
2. Wait for build to complete (~5 minutes)
3. Once deployed, copy your Railway URL (e.g., `https://your-app.railway.app`)

### Step 6: Test Backend

```bash
curl https://your-app.railway.app/health
# Should return: {"status":"healthy"}
```

---

## Part 3: Deploy Frontend to Vercel ✅

### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### Step 2: Deploy via Vercel Dashboard (Recommended)

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository "visasight"
4. Vercel will detect Next.js automatically

### Step 3: Configure Project Settings

**Framework Preset:** Next.js  
**Root Directory:** `frontend`  
**Build Command:** `npm run build`  
**Output Directory:** `.next`  
**Install Command:** `npm install`

### Step 4: Add Environment Variables

In Vercel dashboard, go to Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Important:** Replace `https://your-backend.railway.app` with your actual Railway URL from Part 2!

### Step 5: Update vercel.json

Make sure your `frontend/vercel.json` has the correct backend URL:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend.railway.app/api/:path*"
    },
    {
      "source": "/health",
      "destination": "https://your-backend.railway.app/health"
    }
  ]
}
```

### Step 6: Deploy Frontend

1. Click "Deploy"
2. Wait for build (~2-3 minutes)
3. Your site will be live at `https://your-project.vercel.app`

### Step 7: Test Deployment

Visit your Vercel URL and test:
- ✅ Home page loads
- ✅ Navigate to Dashboard
- ✅ Check Settings page - all systems should be green
- ✅ Try making a prediction

---

## Part 4: Update Backend CORS 🔒

### Important: Update CORS for Production

Edit `backend/main.py` and update CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-project.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then commit and push:

```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Railway will automatically redeploy with the new CORS settings.

---

## Part 5: Alternative - Deploy Backend to Render

If you prefer Render over Railway:

### Step 1: Sign Up for Render

1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Create Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. **Root Directory:** `backend`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure

- **Environment:** Python 3
- **Plan:** Free
- Add environment variables (same as Railway)

### Step 4: Deploy

Click "Create Web Service" and wait for deployment.

---

## 🎉 Post-Deployment Checklist

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads without errors
- [ ] API calls work from frontend to backend
- [ ] Settings page shows all systems operational
- [ ] Prediction feature works
- [ ] Dashboard displays charts correctly
- [ ] Custom domain configured (optional)

---

## 🔧 Troubleshooting

### Frontend can't connect to backend

**Problem:** API calls failing  
**Solution:**
1. Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
2. Verify `vercel.json` has correct backend URL
3. Check backend CORS allows your Vercel domain
4. Redeploy frontend after fixing

### Backend build fails

**Problem:** Railway/Render can't build  
**Solution:**
1. Ensure `requirements.txt` is in `backend/` directory
2. Check Python version compatibility
3. Remove ML model files from git (they're too large)
4. Check logs in Railway/Render dashboard

### 500 errors on backend

**Problem:** Backend crashes  
**Solution:**
1. Check environment variables are set correctly
2. Verify Supabase credentials
3. Check Railway/Render logs for error messages
4. Ensure ML models are optional (app should work without them)

### Database connection fails

**Problem:** Can't connect to Supabase  
**Solution:**
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Check Supabase dashboard that project is active
3. Whitelist Railway/Render IP in Supabase if needed

---

##  🚀 Next Steps After Deployment

1. **Custom Domain:**
   - Vercel: Settings → Domains → Add domain
   - Railway: Settings → Networking → Custom domain

2. **SSL Certificates:**
   - Both Vercel and Railway provide free SSL automatically ✅

3. **Monitoring:**
   - Set up error tracking (Sentry)
   - Enable analytics (Google Analytics)
   - Monitor uptime (UptimeRobot)

4. **Performance:**
   - Enable Vercel Edge Functions for faster API routes
   - Use Vercel ISR for static pages
   - Implement caching strategies

5. **Security:**
   - Set up environment-specific API keys
   - Enable rate limiting on backend
   - Add authentication middleware
   - Regular security audits

---

## 📊 Cost Breakdown

### Free Tier Limits:

**Vercel:**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Preview deployments

**Railway:**
- ✅ $5 free credit/month
- ✅ Automatic deployments
- ✅ ~500 hours/month

**Render:**
- ✅ Free tier available
- ⚠️ May sleep after inactivity
- ✅ Auto-wake on request

---

## 🎯 Success! Your App is Live! 🎉

Your VisaSight application is now deployed and accessible worldwide!

**Frontend:** `https://your-project.vercel.app`  
**Backend:** `https://your-backend.railway.app`  
**Status:** Production-ready ✅

Share your deployed app and get feedback!

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Next.js Docs: https://nextjs.org/docs
- FastAPI Docs: https://fastapi.tiangolo.com
