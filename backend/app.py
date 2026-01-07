"""
AI Caseworker Backend API
Deployed on Azure Web App
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Import local modules
from models import WelfareRiskModel
from explanation import ExplanationEngine

# Global variables
risk_model = None
explanation_engine = None
cases_db = []
approvals_db = []

# Lifespan handler for Azure Web App
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global risk_model, explanation_engine
    try:
        risk_model = WelfareRiskModel()
        model_path = os.getenv('MODEL_PATH', 'welfare_risk_model.pkl')
        if os.path.exists(model_path):
            risk_model.load_model(model_path)
        else:
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        explanation_engine = ExplanationEngine()
        print("[OK] Models loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading models: {e}")
        raise
    
    yield
    
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(
    title="AI Caseworker API",
    description="API for welfare case risk analysis with human-in-the-loop approval",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow frontend domain
frontend_url = os.getenv('FRONTEND_URL', '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url] if frontend_url != '*' else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CitizenCase(BaseModel):
    citizen_id: str
    income: float = Field(..., gt=0)
    last_document_update_months: float = Field(..., ge=0)
    scheme_type: str = Field(..., pattern="^(pension|subsidy|ration)$")
    past_benefit_interruptions: int = Field(..., ge=0, le=10)

class CaseAnalysisRequest(BaseModel):
    case: CitizenCase

class CaseAnalysisResponse(BaseModel):
    case_id: str
    citizen_id: str
    risk_score: float
    risk_level: str
    explanation: str
    recommended_action: str
    action_description: str
    model_reasons: Dict[str, Any]
    timestamp: str
    status: str = "PENDING_APPROVAL"

class ApprovalRequest(BaseModel):
    case_id: str
    officer_id: str
    decision: str = Field(..., pattern="^(APPROVE|REJECT)$")
    officer_notes: Optional[str] = None

class ApprovalResponse(BaseModel):
    case_id: str
    decision: str
    officer_id: str
    timestamp: str
    officer_notes: Optional[str] = None

# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Caseworker API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure."""
    return {
        "status": "healthy",
        "models_loaded": risk_model is not None and explanation_engine is not None,
        "cases_count": len(cases_db),
        "approvals_count": len(approvals_db)
    }

@app.post("/analyze_case", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """Analyze welfare case and generate risk score with explanation."""
    global risk_model, explanation_engine, cases_db
    
    if risk_model is None or explanation_engine is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        case_data = request.case.dict()
        df = pd.DataFrame([case_data])
        X = risk_model.prepare_features(df)
        
        risk_levels, risk_scores, _ = risk_model.predict_risk(X)
        risk_level = risk_levels[0]
        risk_score = float(risk_scores[0])
        
        model_reasons = risk_model.get_model_reasons(X, risk_model.feature_names)
        
        explanation_result = explanation_engine.generate_explanation(
            risk_score=risk_score,
            risk_level=risk_level,
            model_reasons=model_reasons,
            citizen_data=case_data
        )
        
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(cases_db)}"
        
        response = CaseAnalysisResponse(
            case_id=case_id,
            citizen_id=case_data['citizen_id'],
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation_result['explanation'],
            recommended_action=explanation_result['recommended_action'],
            action_description=explanation_result['action_description'],
            model_reasons=model_reasons,
            timestamp=datetime.now().isoformat(),
            status="PENDING_APPROVAL"
        )
        
        cases_db.append(response.dict())
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing case: {str(e)}")

@app.get("/cases", response_model=List[CaseAnalysisResponse])
async def get_cases(
    status: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get all cases with optional filtering."""
    global cases_db
    filtered_cases = cases_db
    
    if status:
        filtered_cases = [c for c in filtered_cases if c['status'] == status]
    if risk_level:
        filtered_cases = [c for c in filtered_cases if c['risk_level'] == risk_level]
    
    return filtered_cases

@app.get("/cases/{case_id}", response_model=CaseAnalysisResponse)
async def get_case(case_id: str):
    """Get a specific case by ID."""
    global cases_db
    
    case = next((c for c in cases_db if c['case_id'] == case_id), None)
    
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case

@app.post("/approve_case", response_model=ApprovalResponse)
async def approve_case(request: ApprovalRequest):
    """Human-in-the-loop approval endpoint."""
    global cases_db, approvals_db
    
    case = next((c for c in cases_db if c['case_id'] == request.case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case['status'] != 'PENDING_APPROVAL':
        raise HTTPException(
            status_code=400,
            detail=f"Case already processed. Current status: {case['status']}"
        )
    
    case['status'] = request.decision
    case['officer_id'] = request.officer_id
    case['officer_notes'] = request.officer_notes
    case['approval_timestamp'] = datetime.now().isoformat()
    
    approval_record = {
        'case_id': request.case_id,
        'officer_id': request.officer_id,
        'decision': request.decision,
        'officer_notes': request.officer_notes,
        'timestamp': datetime.now().isoformat(),
        'ai_recommendation': case['recommended_action'],
        'ai_risk_score': case['risk_score']
    }
    approvals_db.append(approval_record)
    
    return ApprovalResponse(
        case_id=request.case_id,
        decision=request.decision,
        officer_id=request.officer_id,
        timestamp=approval_record['timestamp'],
        officer_notes=request.officer_notes
    )

@app.get("/approvals")
async def get_approvals():
    """Get all approval records for audit trail."""
    global approvals_db
    return approvals_db

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


