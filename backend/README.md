# AI Caseworker Backend

Production-ready FastAPI backend for welfare case risk analysis using Azure OpenAI.

## 🚀 Quick Start

### Local Development
```bash
cd backend
pip install -r requirements.txt
python start_local.py
```

### Production Deployment
See [DEPLOYMENT.md](../DEPLOYMENT.md) for Render.com deployment instructions.

## 📁 File Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models.py              # ML model wrapper and prediction logic
├── explanation.py         # Azure OpenAI integration for explanations
├── requirements.txt       # Python dependencies
├── gunicorn.conf.py      # Production server configuration
├── start_local.py        # Local development server
├── welfare_risk_model.pkl # Pre-trained ML model (RandomForest)
└── README.md             # This file
```

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | ✅ | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | ✅ | Model deployment name (e.g., gpt-4) |
| `PORT` | ❌ | Server port (default: 8000) |

## 🎯 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze_case` - Analyze welfare case
- `GET /cases` - List cases with filtering
- `POST /approve_case` - Human-in-the-loop approval
- `GET /approvals` - Audit trail

## 🧪 Testing

Run the test suite:
```bash
python ../test_api.py
```

## 🏗️ Architecture

1. **FastAPI** - Modern, fast web framework
2. **ML Model** - Pre-trained RandomForest for risk prediction
3. **Azure OpenAI** - Human-readable explanations
4. **In-memory storage** - Simple demo-safe data persistence
5. **CORS enabled** - Works with Vercel frontend

## 🔒 Security Notes

- No authentication (demo/hackathon MVP)
- CORS allows all origins (restrict in production)
- In-memory storage (use database in production)
- Environment variables for sensitive data