# 🎯 VisaSight - Production Ready

## AI-Enabled Visa Status Prediction & Processing Time Estimator

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.0-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Connected-3FCF8E)](https://supabase.com/)

---

## ✅ Production Build Status

```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (11/11)
✓ Finalizing page optimization
```

**All pages verified and production-ready!**

---

## 🏗️ Project Structure

```
visasight/
├── frontend/                    # Next.js 14 App Router
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   │   ├── page.tsx         # Homepage
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── error.tsx        # Error boundary
│   │   │   ├── not-found.tsx    # 404 page
│   │   │   ├── loading.tsx      # Loading state
│   │   │   ├── global-error.tsx # Global error handler
│   │   │   ├── auth/            # Login/Signup pages
│   │   │   ├── dashboard/       # Analytics dashboard
│   │   │   ├── predict/         # AI prediction form
│   │   │   ├── cases/           # Case management
│   │   │   ├── rules/           # Policy monitoring
│   │   │   └── settings/        # System settings
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utilities & API
│   │   └── styles/              # Global CSS
│   ├── package.json
│   ├── next.config.js
│   └── vercel.json
│
├── backend/                     # FastAPI Python Backend
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── ml/                  # ML models
│   │   ├── services/            # Business logic
│   │   └── models/              # Data models
│   ├── main.py                  # Entry point
│   └── requirements.txt
│
├── Procfile                     # Railway deployment
├── railway.json                 # Railway config
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 18+
- Python 3.10+
- npm or yarn

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/your-username/visasight.git
cd visasight

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 2. Configure Environment

**Frontend (.env.local):**
```env
NEXT_PUBLIC_SUPABASE_URL=https://wrzvcytxueeppukahhdk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env):**
```env
SUPABASE_URL=https://wrzvcytxueeppukahhdk.supabase.co
SUPABASE_KEY=your_key_here
PORT=8000
```

### 3. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Open Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🌐 Production Deployment

### Deploy Backend to Railway

1. Go to [Railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Set root directory to `/backend`
4. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `FRONTEND_URL` (your Vercel URL)
5. Deploy!

### Deploy Frontend to Vercel

1. Go to [Vercel.com](https://vercel.com)
2. Import GitHub repository
3. Set root directory to `frontend`
4. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL` (your Railway URL)
5. Deploy!

---

## 📱 Features

### 🎯 Core Features
- **AI Visa Prediction** - Multiclass classification (Approved/RFE/Denied)
- **Processing Time Estimation** - Survival analysis models
- **Explainable AI** - SHAP-based feature importance
- **Real-time Policy Monitoring** - Track visa rule changes

### 🎨 Premium UI
- Dark mode with gradient mesh backgrounds
- Glassmorphism card effects
- Smooth micro-animations
- Responsive design
- Modern typography (Inter, Space Grotesk)

### 🔐 Authentication
- Supabase Auth integration
- Email/password sign up
- Protected routes
- Session management

### 📊 Dashboard
- Visa approval trends
- Processing time analytics
- Case status distribution
- Real-time statistics

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.0 | React framework |
| React | 18.2.0 | UI library |
| TypeScript | 5.3.0 | Type safety |
| Framer Motion | 11.0.0 | Animations |
| Recharts | 2.12.0 | Data visualization |
| Supabase JS | 2.93.3 | Auth & Database |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109.0 | API framework |
| Uvicorn | 0.27.0 | ASGI server |
| Supabase | 2.3.0 | Database client |
| Scikit-learn | 1.4.0 | ML models |
| XGBoost | 2.0.3 | Gradient boosting |
| SHAP | 0.44.1 | Explainability |

---

## 📁 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/cases` | List visa cases |
| POST | `/api/cases` | Create new case |
| GET | `/api/cases/{id}` | Get case details |
| POST | `/api/predict` | Get AI prediction |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/rules` | List visa rules |
| GET | `/api/models` | List ML models |

---

## 🧪 Testing

### Run Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

### Run Backend Tests
```bash
cd backend
python -m pytest
```

### Test API Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## 📝 Environment Variables

### Frontend (Vercel)
| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase anon key |
| `NEXT_PUBLIC_API_URL` | ✅ | Backend API URL |

### Backend (Railway)
| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase service key |
| `FRONTEND_URL` | ✅ | Frontend URL (CORS) |
| `PORT` | ⚪ | Server port (auto-set) |

---

## 🛡️ Security

- ✅ CORS configured for production domains
- ✅ Environment variables for secrets
- ✅ Supabase Row Level Security
- ✅ HTTPS enforced in production
- ✅ API rate limiting

---

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

## 🤝 Support

For issues or questions:
1. Check the `/docs` endpoint for API documentation
2. Review the error logs in Railway/Vercel dashboards
3. Open an issue on GitHub

---

**Built with ❤️ by the VisaSight Team**
