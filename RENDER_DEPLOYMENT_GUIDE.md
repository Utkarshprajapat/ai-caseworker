# 🚀 AI Caseworker - Complete Render.com Deployment Guide

## 📋 Project Overview

**AI Caseworker for Government Welfare Leakage** - Imagine Cup 2026 Project
- **Backend**: Production-ready FastAPI with Azure OpenAI integration
- **ML Model**: Pre-trained RandomForest for welfare case risk assessment
- **AI Explanations**: Azure OpenAI Service (mandatory requirement)
- **Deployment**: Render.com (free tier suitable for hackathon demo)

## 🏗️ Final Project Structure

```
project/
├── backend/
│   ├── main.py                 # FastAPI application (production-ready)
│   ├── models.py              # ML model wrapper
│   ├── explanation.py         # Azure OpenAI integration
│   ├── requirements.txt       # Python dependencies
│   ├── gunicorn.conf.py      # Production server config
│   ├── start_local.py        # Local development server
│   ├── welfare_risk_model.pkl # Pre-trained ML model
│   └── README.md             # Backend documentation
├── frontend/                  # Your existing Vercel frontend
├── render.yaml               # Render deployment config
├── test_api.py              # API testing script
├── DEPLOYMENT.md            # Detailed deployment guide
└── RENDER_DEPLOYMENT_GUIDE.md # This file
```

## 🚀 Step-by-Step Deployment

### 1. Prerequisites ✅
- [x] GitHub repository with this code
- [x] Render.com account (free)
- [x] Azure OpenAI Service credentials

### 2. Deploy to Render.com

#### Option A: Automatic Deployment (Recommended)
1. **Push to GitHub**: Commit all files to your repository
2. **Connect to Render**: 
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
3. **Auto-Configuration**: Render will detect `render.yaml` and configure automatically

#### Option B: Manual Configuration
If automatic detection fails:
- **Name**: `ai-caseworker-backend`
- **Environment**: `Python 3`
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- **Root Directory**: Leave empty (not `backend`)

### 3. Configure Environment Variables 🔧

In Render Dashboard → Your Service → Environment, add:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

**⚠️ CRITICAL**: These are mandatory for Imagine Cup judging!

### 4. Verify Deployment ✅

Once deployed, test these endpoints:

```bash
# Replace YOUR_APP_URL with your Render URL
export API_URL="https://your-app.onrender.com"

# Health check
curl $API_URL/health

# API documentation
open $API_URL/docs
```

## 🧪 Testing Your Deployment

### Quick Test Script
```bash
python test_api.py
```

### Manual API Tests

#### 1. Health Check
```bash
curl https://your-app.onrender.com/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "azure_openai_configured": true,
  "cases_count": 0,
  "approvals_count": 0
}
```

#### 2. Analyze a Case
```bash
curl -X POST "https://your-app.onrender.com/analyze_case" \
  -H "Content-Type: application/json" \
  -d '{
    "case": {
      "citizen_id": "DEMO_001",
      "income": 25000.0,
      "last_document_update_months": 8.5,
      "scheme_type": "pension",
      "past_benefit_interruptions": 2
    }
  }'
```

#### 3. Get Cases
```bash
curl https://your-app.onrender.com/cases
```

## 🎯 API Endpoints Summary

| Method | Endpoint | Description | Demo Priority |
|--------|----------|-------------|---------------|
| `GET` | `/health` | System health check | 🔥 High |
| `POST` | `/analyze_case` | AI risk analysis | 🔥 High |
| `GET` | `/cases` | List all cases | 🔥 High |
| `POST` | `/approve_case` | Human oversight | 🔥 High |
| `GET` | `/` | API information | ⭐ Medium |
| `GET` | `/docs` | Interactive API docs | ⭐ Medium |

## 🎪 Demo Script for Judges

### 1. Show System Health (30 seconds)
```bash
curl https://your-app.onrender.com/health
```
**Highlight**: "All systems operational, Azure OpenAI connected"

### 2. Analyze High-Risk Case (60 seconds)
```bash
curl -X POST "https://your-app.onrender.com/analyze_case" \
  -H "Content-Type: application/json" \
  -d '{
    "case": {
      "citizen_id": "HIGH_RISK_DEMO",
      "income": 15000.0,
      "last_document_update_months": 18.0,
      "scheme_type": "pension",
      "past_benefit_interruptions": 5
    }
  }'
```
**Highlight**: "AI detects high risk, Azure OpenAI explains in plain language"

### 3. Show Human Oversight (30 seconds)
```bash
curl -X POST "https://your-app.onrender.com/approve_case" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "CASE_20260107_123456_000",
    "officer_id": "JUDGE_DEMO",
    "decision": "APPROVE",
    "officer_notes": "Reviewed during Imagine Cup demo"
  }'
```
**Highlight**: "Human-in-the-loop governance ensures accountability"

### 4. Show Audit Trail (30 seconds)
```bash
curl https://your-app.onrender.com/approvals
```
**Highlight**: "Complete audit trail for transparency and compliance"

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Build Fails** | Deployment error | Check `requirements.txt` syntax |
| **Health Check Fails** | `/health` returns unhealthy | Verify ML model file exists |
| **Azure OpenAI Errors** | Explanations are generic | Check environment variables |
| **CORS Issues** | Frontend can't connect | Update CORS origins in `main.py` |
| **Cold Start Delays** | First request slow | Normal for free tier (~15 seconds) |

### Debug Commands
```bash
# Check logs in Render dashboard
# Or use Render CLI:
render logs -s your-service-name

# Test locally:
cd backend
python start_local.py
```

## 🏆 Imagine Cup Judging Criteria

### ✅ Technical Excellence
- [x] **Azure OpenAI Integration**: Mandatory requirement met
- [x] **Production Ready**: FastAPI with proper error handling
- [x] **Scalable Architecture**: Stateless design, ready for database
- [x] **API Documentation**: Auto-generated with FastAPI

### ✅ Innovation & Impact
- [x] **AI-Powered Risk Assessment**: ML model + Azure OpenAI explanations
- [x] **Human-in-the-Loop**: Governance and accountability
- [x] **Real-World Problem**: Government welfare leakage prevention
- [x] **Citizen-Friendly**: Plain language explanations

### ✅ Implementation Quality
- [x] **Working Demo**: Fully functional API
- [x] **Error Handling**: Graceful failures and logging
- [x] **Testing**: Comprehensive test suite included
- [x] **Documentation**: Clear deployment and usage guides

## 🌐 Frontend Integration

Update your Vercel frontend to use the Render backend:

```javascript
// In your frontend code
const API_BASE = 'https://your-app.onrender.com';

// Example: Analyze a case
const analyzeCase = async (caseData) => {
  const response = await fetch(`${API_BASE}/analyze_case`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ case: caseData })
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
};
```

## 📊 Performance Expectations

### Render.com Free Tier
- **Cold Start**: ~10-15 seconds (first request after idle)
- **Response Time**: ~1-3 seconds for analysis
- **Concurrent Users**: ~10-20 (sufficient for demo)
- **Uptime**: 99%+ (Render SLA)
- **Monthly Hours**: 750 hours free

### Optimization Tips
- Keep the service "warm" by pinging `/health` every 10 minutes
- Use caching for repeated requests (future enhancement)
- Consider upgrading to paid tier for production use

## 🎉 Success Checklist

Before your demo, verify:

- [ ] **Health endpoint** returns `"status": "healthy"`
- [ ] **Azure OpenAI** shows `"azure_openai_configured": true`
- [ ] **Case analysis** returns AI-generated explanations
- [ ] **Human approval** workflow functions correctly
- [ ] **API documentation** accessible at `/docs`
- [ ] **Frontend integration** working with CORS
- [ ] **Test script** passes all checks

## 🚀 You're Ready!

Your AI Caseworker backend is now production-ready and deployed on Render.com with full Azure OpenAI integration. The system demonstrates:

1. **AI-powered risk assessment** using machine learning
2. **Human-readable explanations** via Azure OpenAI
3. **Human-in-the-loop governance** for accountability
4. **Production-grade architecture** ready for scale
5. **Complete audit trail** for transparency

**Perfect for Imagine Cup 2026 judging!** 🏆

---

**Need help?** Check the logs in Render dashboard or run the test script locally.