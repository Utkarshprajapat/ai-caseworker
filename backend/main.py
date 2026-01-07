"""
AI Caseworker Backend API - Production Ready for Render.com
Imagine Cup 2026 Project
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import WelfareRiskModel
from explanation import ExplanationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model instances and in-memory storage
risk_model = None
explanation_engine = None
cases_db = []
approvals_db = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for model loading."""
    global risk_model, explanation_engine
    
    try:
        logger.info("Loading ML model and explanation engine...")
        
        # Load ML model
        risk_model = WelfareRiskModel()
        model_path = os.path.join(os.path.dirname(__file__), 'welfare_risk_model.pkl')
        if os.path.exists(model_path):
            risk_model.load_model(model_path)
            logger.info("✅ ML model loaded successfully")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Initialize explanation engine with Azure OpenAI
        explanation_engine = ExplanationEngine()
        logger.info("✅ Explanation engine initialized")
        
        logger.info("🚀 Backend ready for requests")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}")
        raise
    
    yield
    
    # Cleanup (if needed)
    logger.info("🔄 Shutting down backend")

# Initialize FastAPI app
app = FastAPI(
    title="AI Caseworker API",
    description="AI-powered welfare case risk analysis with human oversight",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models
class CitizenCase(BaseModel):
    """Input model for citizen welfare case data."""
    citizen_id: str = Field(..., description="Unique citizen identifier")
    income: float = Field(..., gt=0, description="Monthly income in currency")
    last_document_update_months: float = Field(..., ge=0, description="Months since last document update")
    scheme_type: str = Field(..., pattern="^(pension|subsidy|ration)$", description="Type of welfare scheme")
    past_benefit_interruptions: int = Field(..., ge=0, le=10, description="Number of past benefit interruptions")

class CaseAnalysisRequest(BaseModel):
    """Request model for case analysis."""
    case: CitizenCase

class CaseAnalysisResponse(BaseModel):
    """Response model for case analysis results."""
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
    """Request model for case approval/rejection."""
    case_id: str
    officer_id: str
    decision: str = Field(..., pattern="^(APPROVE|REJECT)$")
    officer_notes: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Caseworker API - Imagine Cup 2026",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze_case": "/analyze_case",
            "get_cases": "/cases",
            "approve_case": "/approve_case"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render.com monitoring."""
    models_loaded = risk_model is not None and explanation_engine is not None
    
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded,
        "azure_openai_configured": explanation_engine.client is not None if explanation_engine else False,
        "cases_count": len(cases_db),
        "approvals_count": len(approvals_db),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze_case", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """
    Analyze a welfare case and generate risk assessment with AI explanation.
    
    This endpoint:
    1. Processes citizen data through ML model
    2. Generates risk score and level
    3. Creates human-readable explanation via Azure OpenAI
    4. Returns actionable recommendations
    """
    global risk_model, explanation_engine, cases_db
    
    if risk_model is None or explanation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail="Backend services not ready. Please try again in a moment."
        )
    
    try:
        # Prepare data for ML model
        case_data = request.case.dict()
        df = pd.DataFrame([case_data])
        X = risk_model.prepare_features(df)
        
        # Get ML predictions
        risk_levels, risk_scores, _ = risk_model.predict_risk(X)
        risk_level = risk_levels[0]
        risk_score = float(risk_scores[0])
        
        # Extract model reasoning
        model_reasons = risk_model.get_model_reasons(X, risk_model.feature_names)
        
        # Generate AI explanation using Azure OpenAI
        explanation_result = explanation_engine.generate_explanation(
            risk_score=risk_score,
            risk_level=risk_level,
            model_reasons=model_reasons,
            citizen_data=case_data
        )
        
        # Create unique case ID
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(cases_db):03d}"
        
        # Build response
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
        
        # Store in memory (in production, use a database)
        cases_db.append(response.dict())
        
        logger.info(f"✅ Analyzed case {case_id} - Risk: {risk_level} ({risk_score:.1f})")
        return response
    
    except Exception as e:
        logger.error(f"❌ Error analyzing case: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze case: {str(e)}"
        )

@app.get("/cases", response_model=List[CaseAnalysisResponse])
async def get_cases(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Retrieve welfare cases with optional filtering.
    
    Query parameters:
    - status: Filter by approval status (PENDING_APPROVAL, APPROVE, REJECT)
    - risk_level: Filter by risk level (low, medium, high)
    - limit: Maximum number of cases to return (default: 100)
    """
    global cases_db
    
    filtered_cases = cases_db.copy()
    
    # Apply filters
    if status:
        filtered_cases = [c for c in filtered_cases if c.get('status') == status]
    if risk_level:
        filtered_cases = [c for c in filtered_cases if c.get('risk_level') == risk_level]
    
    # Apply limit and sort by timestamp (newest first)
    filtered_cases = sorted(
        filtered_cases, 
        key=lambda x: x.get('timestamp', ''), 
        reverse=True
    )[:limit]
    
    return filtered_cases

@app.get("/cases/{case_id}", response_model=CaseAnalysisResponse)
async def get_case(case_id: str):
    """Retrieve a specific case by ID."""
    global cases_db
    
    case = next((c for c in cases_db if c['case_id'] == case_id), None)
    
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    return case

@app.post("/approve_case")
async def approve_case(request: ApprovalRequest):
    """
    Human-in-the-loop approval endpoint for case decisions.
    
    Allows welfare officers to approve or reject AI recommendations.
    """
    global cases_db, approvals_db
    
    # Find the case
    case = next((c for c in cases_db if c['case_id'] == request.case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {request.case_id} not found")
    
    # Check if already processed
    if case.get('status') not in ['PENDING_APPROVAL']:
        raise HTTPException(
            status_code=400,
            detail=f"Case already processed with status: {case.get('status')}"
        )
    
    # Update case status
    case['status'] = request.decision
    case['officer_id'] = request.officer_id
    case['officer_notes'] = request.officer_notes
    case['approval_timestamp'] = datetime.now().isoformat()
    
    # Create approval record for audit trail
    approval_record = {
        'case_id': request.case_id,
        'officer_id': request.officer_id,
        'decision': request.decision,
        'officer_notes': request.officer_notes,
        'timestamp': datetime.now().isoformat(),
        'ai_recommendation': case.get('recommended_action'),
        'ai_risk_score': case.get('risk_score'),
        'citizen_id': case.get('citizen_id')
    }
    approvals_db.append(approval_record)
    
    logger.info(f"✅ Case {request.case_id} {request.decision} by {request.officer_id}")
    
    return {
        "message": f"Case {request.case_id} successfully {request.decision.lower()}d",
        "case_id": request.case_id,
        "decision": request.decision,
        "officer_id": request.officer_id,
        "timestamp": approval_record['timestamp']
    }

@app.get("/approvals")
async def get_approvals(limit: Optional[int] = 100):
    """Get approval records for audit trail."""
    global approvals_db
    
    # Sort by timestamp (newest first) and apply limit
    sorted_approvals = sorted(
        approvals_db, 
        key=lambda x: x.get('timestamp', ''), 
        reverse=True
    )[:limit]
    
    return {
        "approvals": sorted_approvals,
        "total_count": len(approvals_db)
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )