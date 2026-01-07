# AI Caseworker Backend - Render.com Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- GitHub repository with this code
- Render.com account (free)
- Azure OpenAI Service credentials

### 2. Deploy to Render.com

#### Option A: Using render.yaml (Recommended)
1. Push code to GitHub
2. Connect GitHub repo to Render.com
3. Render will auto-detect `render.yaml` and deploy

#### Option B: Manual Setup
1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ai-caseworker-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon` (or closest to users)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 3. Set Environment Variables
In Render dashboard → Service → Environment:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 4. Verify Deployment
- Health check: `https://your-app.onrender.com/health`
- API docs: `https://your-app.onrender.com/docs`

## 🧪 Testing Your API

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### Analyze a Case
```bash
curl -X POST "https://your-app.onrender.com/analyze_case" \
  -H "Content-Type: application/json" \
  -d '{
    "case": {
      "citizen_id": "CIT001",
      "income": 25000.0,
      "last_document_update_months": 8.5,
      "scheme_type": "pension",
      "past_benefit_interruptions": 2
    }
  }'
```

### Get All Cases
```bash
curl https://your-app.onrender.com/cases
```

## 📁 Final Project Structure

```
backend/
├── main.py                 # FastAPI application
├── models.py              # ML model wrapper
├── explanation.py         # Azure OpenAI integration
├── requirements.txt       # Python dependencies
├── gunicorn.conf.py      # Production server config
└── welfare_risk_model.pkl # Pre-trained ML model

render.yaml                # Render deployment config
DEPLOYMENT.md             # This file
```

## 🔧 Environment Variables Explained

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Your Azure OpenAI resource endpoint | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | ✅ | API key for Azure OpenAI | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | ✅ | Model deployment name | `gpt-4` or `gpt-35-turbo` |
| `PORT` | ❌ | Server port (auto-set by Render) | `8000` |

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check for monitoring |
| `POST` | `/analyze_case` | Analyze welfare case risk |
| `GET` | `/cases` | List all cases (with filters) |
| `GET` | `/cases/{case_id}` | Get specific case |
| `POST` | `/approve_case` | Human approval/rejection |
| `GET` | `/approvals` | Audit trail of decisions |

## 🚨 Troubleshooting

### Common Issues:

1. **Build fails**: Check `requirements.txt` syntax
2. **Health check fails**: Verify ML model file exists
3. **Azure OpenAI errors**: Check environment variables
4. **CORS issues**: Frontend domain not in allowed origins

### Logs:
- View logs in Render dashboard → Service → Logs
- Look for `✅` (success) and `❌` (error) indicators

## 🎉 Demo Tips for Judges

1. **Show the health endpoint** - proves everything is working
2. **Demonstrate Azure OpenAI integration** - key requirement
3. **Test with different risk levels** - show AI explanations
4. **Show human-in-the-loop approval** - governance feature
5. **Highlight real-time API responses** - production ready

## 🔗 Frontend Integration

Your Vercel frontend should call:
```javascript
const API_BASE = 'https://your-app.onrender.com';

// Analyze case
const response = await fetch(`${API_BASE}/analyze_case`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ case: caseData })
});
```

## 📊 Performance Notes

- **Cold starts**: ~10-15 seconds (free tier)
- **Response time**: ~1-3 seconds for analysis
- **Concurrent users**: ~10-20 (free tier)
- **Uptime**: 99%+ (Render SLA)

Perfect for hackathon demos and MVP validation! 🏆