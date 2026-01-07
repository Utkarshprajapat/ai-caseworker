"""
STEP 4: BACKEND API (FASTAPI / AZURE APP SERVICE)
===================================================
RESTful API for welfare case analysis.

In production, this would be deployed using:
- Azure App Service (for containerized Python apps)
- Azure Functions (for serverless architecture)
- Azure API Management (for API gateway)
- Azure Application Insights (for monitoring)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import json

# Import our modules
from step2_ml_risk_model import WelfareRiskModel
from step3_explanation_engine import ExplanationEngine

# Initialize FastAPI app
app = FastAPI(
    title="AI Caseworker API",
    description="API for welfare case risk analysis with human-in-the-loop approval",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: Specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
risk_model = None
explanation_engine = None
cases_db = []  # In production: Use Azure SQL Database or Cosmos DB
approvals_db = []  # In production: Use Azure SQL Database

# Pydantic models for request/response
class CitizenCase(BaseModel):
    citizen_id: str
    income: float = Field(..., gt=0, description="Monthly income in rupees")
    last_document_update_months: float = Field(..., ge=0, description="Months since last document update")
    scheme_type: str = Field(..., pattern="^(pension|subsidy|ration)$", description="Type of welfare scheme")
    past_benefit_interruptions: int = Field(..., ge=0, le=10, description="Number of past benefit interruptions")

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
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED

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

def load_models():
    """Load ML models on startup."""
    global risk_model, explanation_engine
    
    try:
        # Load risk model
        risk_model = WelfareRiskModel()
        if os.path.exists('welfare_risk_model.pkl'):
            risk_model.load_model()
        else:
            raise FileNotFoundError("Model not found. Please train the model first.")
        
        # Initialize explanation engine
        explanation_engine = ExplanationEngine()
        
        print("[OK] Models loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading models: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize models on application startup."""
    load_models()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Caseworker API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "analyze_case": "POST /analyze_case",
            "get_cases": "GET /cases",
            "approve_case": "POST /approve_case",
            "get_case": "GET /cases/{case_id}"
        }
    }

@app.post("/analyze_case", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """
    Analyze a welfare case and generate risk score with explanation.
    
    This endpoint:
    1. Runs ML risk model
    2. Generates explanation using Azure OpenAI (mocked)
    3. Returns analysis results
    4. Stores case for officer approval (human-in-the-loop)
    
    In production:
    - Deployed on Azure App Service or Azure Functions
    - Uses Azure OpenAI Service for explanations
    - Stores data in Azure SQL Database or Cosmos DB
    """
    global risk_model, explanation_engine, cases_db
    
    if risk_model is None or explanation_engine is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Prepare case data
        case_data = request.case.dict()
        
        # Convert to DataFrame for model input
        df = pd.DataFrame([case_data])
        
        # Prepare features
        X = risk_model.prepare_features(df)
        
        # Predict risk
        risk_levels, risk_scores, _ = risk_model.predict_risk(X)
        risk_level = risk_levels[0]
        risk_score = float(risk_scores[0])
        
        # Get model reasons
        model_reasons = risk_model.get_model_reasons(X, risk_model.feature_names)
        
        # Generate explanation
        explanation_result = explanation_engine.generate_explanation(
            risk_score=risk_score,
            risk_level=risk_level,
            model_reasons=model_reasons,
            citizen_data=case_data
        )
        
        # Create case ID
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(cases_db)}"
        
        # Create response
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
        
        # Store case for approval (human-in-the-loop)
        cases_db.append(response.dict())
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing case: {str(e)}")

@app.get("/cases", response_model=List[CaseAnalysisResponse])
async def get_cases(
    status: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """
    Get all cases with optional filtering.
    
    In production:
    - Queries Azure SQL Database or Cosmos DB
    - Supports pagination
    - Includes caching with Azure Redis Cache
    """
    global cases_db
    
    filtered_cases = cases_db
    
    if status:
        filtered_cases = [c for c in filtered_cases if c['status'] == status]
    
    if risk_level:
        filtered_cases = [c for c in filtered_cases if c['risk_level'] == risk_level]
    
    return filtered_cases

@app.get("/cases/{case_id}", response_model=CaseAnalysisResponse)
async def get_case(case_id: str):
    """
    Get a specific case by ID.
    
    In production:
    - Queries Azure SQL Database or Cosmos DB
    """
    global cases_db
    
    case = next((c for c in cases_db if c['case_id'] == case_id), None)
    
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case

@app.post("/approve_case", response_model=ApprovalResponse)
async def approve_case(request: ApprovalRequest):
    """
    Human-in-the-loop approval endpoint.
    
    This endpoint:
    1. Records officer decision (APPROVE/REJECT)
    2. Updates case status
    3. Logs approval for audit trail
    
    RESPONSIBLE AI COMPLIANCE:
    - AI cannot make final decisions
    - Human approval is mandatory
    - All decisions are logged for transparency
    
    In production:
    - Stores approvals in Azure SQL Database
    - Logs to Azure Monitor for audit
    - Sends notifications via Azure Service Bus
    """
    global cases_db, approvals_db
    
    # Find case
    case = next((c for c in cases_db if c['case_id'] == request.case_id), None)
    
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case['status'] != 'PENDING_APPROVAL':
        raise HTTPException(
            status_code=400,
            detail=f"Case already processed. Current status: {case['status']}"
        )
    
    # Update case status
    case['status'] = request.decision
    case['officer_id'] = request.officer_id
    case['officer_notes'] = request.officer_notes
    case['approval_timestamp'] = datetime.now().isoformat()
    
    # Log approval
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
    
    # Create response
    response = ApprovalResponse(
        case_id=request.case_id,
        decision=request.decision,
        officer_id=request.officer_id,
        timestamp=approval_record['timestamp'],
        officer_notes=request.officer_notes
    )
    
    return response

@app.get("/approvals")
async def get_approvals():
    """
    Get all approval records for audit trail.
    
    In production:
    - Queries Azure SQL Database
    - Used for compliance and audit purposes
    """
    global approvals_db
    return approvals_db

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": risk_model is not None and explanation_engine is not None,
        "cases_count": len(cases_db),
        "approvals_count": len(approvals_db)
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("STARTING AI CASEWORKER API SERVER")
    print("=" * 60)
    print("\nNOTE: In production, this would be deployed on:")
    print("  - Azure App Service (for containerized apps)")
    print("  - Azure Functions (for serverless)")
    print("  - Azure API Management (for API gateway)")
    print("  - Azure Application Insights (for monitoring)")
    print("\nStarting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

