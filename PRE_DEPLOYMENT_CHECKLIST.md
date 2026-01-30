# ✅ Pre-Deployment Checklist for VisaSight

Before deploying to Vercel, complete this checklist:

---

## 📋 Code Preparation

- [ ] **All files are saved**
- [ ] **Frontend builds successfully** (`cd frontend && npm run build`)
- [ ] **Backend runs without errors** (`cd backend && python -m uvicorn main:app`)
- [ ] **Tests pass** (Model A/B testing completed)
- [ ] **Environment files ready** (.env files contain correct values)

---

## 🔑 Information You'll Need

Gather these before starting deployment:

### From Supabase (backend/.env):
- [ ] `SUPABASE_URL` = ________________________________
- [ ] `SUPABASE_KEY` = ________________________________

### Accounts to Create:
- [ ] GitHub account: ________________________________
- [ ] Vercel account: ________________________________  
- [ ] Railway account: ________________________________

### Repository Name:
- [ ] GitHub repo name: **visasight** (or your choice)

---

## 📦 Git Setup Checklist

- [ ] Git installed on computer
- [ ] Navigate to project folder
- [ ] Run `git init`
- [ ] Create .gitignore file (already created ✅)
- [ ] Add all files: `git add .`
- [ ] Commit: `git commit -m "Initial commit"`
- [ ] Create GitHub repository
- [ ] Push to GitHub

---

## 🚂 Backend Deployment (Railway/Render)

- [ ] Sign up for Railway.app
- [ ] Create new project from GitHub
- [ ] Set root directory to `backend`
- [ ] Add environment variables:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `PORT=8000`
- [ ] Copy Railway URL (save it!): ________________________________
- [ ] Test backend health: `curl https://your-url.railway.app/health`

---

## ⚡ Frontend Deployment (Vercel)

- [ ] Sign up for Vercel.com
- [ ] Import GitHub repository
- [ ] Set root directory to `frontend`
- [ ] Framework auto-detected as Next.js
- [ ] Add environment variables:
  - `NEXT_PUBLIC_API_URL` = (your Railway URL)
  - `NEXT_PUBLIC_SUPABASE_URL` = (from backend/.env)
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = (from backend/.env)
- [ ] Update `frontend/vercel.json` with Railway URL
- [ ] Click Deploy
- [ ] Copy Vercel URL: ________________________________

---

## 🔒 CORS Configuration

- [ ] Update `backend/main.py` CORS with Vercel URL
- [ ] Commit change: `git commit -am "Update CORS"`
- [ ] Push to GitHub: `git push`
- [ ] Railway auto-redeploys

---

## 🧪 Post-Deployment Testing

### Backend Tests:
- [ ] Health check: `curl https://your-backend.railway.app/health`
- [ ] Models API: `curl https://your-backend.railway.app/api/models`
- [ ] Prediction: Test via Postman or curl

### Frontend Tests:
- [ ] Home page loads correctly
- [ ] Navigate to all pages (Dashboard, Predict, Cases, Rules, Settings)
- [ ] Settings page shows all systems operational ✅
- [ ] Make a test prediction
- [ ] Check browser console - no errors
- [ ] Test on mobile device

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ Backend health endpoint returns `{"status": "healthy"}`  
✅ Frontend loads without errors  
✅ All pages navigate correctly  
✅ Settings page shows green status for API, Database, ML Models  
✅ Predictions can be generated  
✅ Dashboard displays charts  
✅ No console errors in browser  
✅ Mobile responsive design works  

---

## 📊 Deployment URLs

Save these for your records:

**Production URLs:**
- Frontend: https://________________________________.vercel.app
- Backend: https://________________________________.railway.app

**GitHub Repository:**
- Repo: https://github.com/________________________________/visasight

**Dashboards:**
- Vercel: https://vercel.com/dashboard
- Railway: https://railway.app/dashboard
- Supabase: https://supabase.com/dashboard

---

## 🆘 Quick Troubleshooting

### Issue: Frontend can't connect to backend
**Fix:** Check `NEXT_PUBLIC_API_URL` in Vercel environment variables

### Issue: 500 errors on backend
**Fix:** Check Railway logs, verify environment variables

### Issue: Database connection fails
**Fix:** Verify Supabase credentials are correct

### Issue: Build fails
**Fix:** Check logs in Vercel/Railway dashboard for specific error

---

## 🚀 Ready to Deploy?

If all checkboxes are complete, you're ready!

### Quick Start:
1. Open `QUICK_DEPLOY.md` for fast command reference
2. Open `DEPLOYMENT_GUIDE.md` for detailed step-by-step
3. Follow the steps in order
4. Test thoroughly after deployment

---

**Estimated Time:** 30-45 minutes for complete deployment

**Cost:** $0 (Free tier for all services)

**Difficulty:** ⭐⭐⭐ (Intermediate - follow guide carefully)

---

Good luck with your deployment! 🎉

**Files Created for You:**
- ✅ `.gitignore` - Excludes unnecessary files
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.production` - Production environment template
- ✅ `DEPLOYMENT_GUIDE.md` - Complete guide
- ✅ `QUICK_DEPLOY.md` - Fast reference
- ✅ This checklist

**Next Command to Run:**
```bash
git init
```

Then follow `QUICK_DEPLOY.md` or `DEPLOYMENT_GUIDE.md`!
