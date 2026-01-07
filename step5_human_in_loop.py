"""
STEP 5: HUMAN-IN-THE-LOOP LOGIC
=================================
Implements Responsible AI principles with mandatory human approval.

RESPONSIBLE AI COMPLIANCE:
- No fully automated decisions
- Human approval is mandatory
- All AI recommendations are logged
- Human decisions override AI recommendations
- Full audit trail maintained

In production:
- Azure Logic Apps for workflow orchestration
- Azure Service Bus for notifications
- Azure Monitor for audit logging
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DecisionStatus(str, Enum):
    """Decision status enumeration."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ApprovalWorkflow:
    """
    Manages human-in-the-loop approval workflow.
    
    Ensures Responsible AI compliance:
    1. AI provides recommendation only
    2. Human officer must approve/reject
    3. All decisions are logged
    4. Audit trail is maintained
    """
    
    def __init__(self):
        self.approval_log = []  # In production: Azure SQL Database
    
    def create_approval_request(
        self,
        case_id: str,
        ai_recommendation: str,
        ai_risk_score: float,
        ai_explanation: str
    ) -> Dict[str, Any]:
        """
        Create an approval request after AI analysis.
        
        Parameters:
        -----------
        case_id : str
            Unique case identifier
        ai_recommendation : str
            AI's recommended action
        ai_risk_score : float
            AI's risk score (0-100)
        ai_explanation : str
            AI's explanation for the citizen
        
        Returns:
        --------
        dict
            Approval request record
        """
        approval_request = {
            'case_id': case_id,
            'ai_recommendation': ai_recommendation,
            'ai_risk_score': ai_risk_score,
            'ai_explanation': ai_explanation,
            'status': DecisionStatus.PENDING_APPROVAL,
            'created_at': datetime.now().isoformat(),
            'human_decision': None,
            'officer_id': None,
            'officer_notes': None,
            'approved_at': None
        }
        
        self.approval_log.append(approval_request)
        return approval_request
    
    def process_human_approval(
        self,
        case_id: str,
        officer_id: str,
        decision: str,
        officer_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process human officer approval/rejection.
        
        Parameters:
        -----------
        case_id : str
            Case identifier
        officer_id : str
            Officer who made the decision
        decision : str
            "APPROVE" or "REJECT"
        officer_notes : str, optional
            Officer's notes explaining the decision
        
        Returns:
        --------
        dict
            Updated approval record
        
        Raises:
        -------
        ValueError
            If case not found or already processed
        """
        # Find approval request
        approval = next(
            (a for a in self.approval_log if a['case_id'] == case_id),
            None
        )
        
        if approval is None:
            raise ValueError(f"Approval request not found for case: {case_id}")
        
        if approval['status'] != DecisionStatus.PENDING_APPROVAL:
            raise ValueError(
                f"Case {case_id} already processed. Status: {approval['status']}"
            )
        
        # Validate decision
        if decision not in ['APPROVE', 'REJECT']:
            raise ValueError("Decision must be 'APPROVE' or 'REJECT'")
        
        # Update approval record
        approval['human_decision'] = decision
        approval['officer_id'] = officer_id
        approval['officer_notes'] = officer_notes
        approval['status'] = DecisionStatus.APPROVED if decision == 'APPROVE' else DecisionStatus.REJECTED
        approval['approved_at'] = datetime.now().isoformat()
        
        # Log for audit trail
        self._log_approval(approval)
        
        return approval
    
    def _log_approval(self, approval: Dict[str, Any]):
        """
        Log approval for audit trail.
        
        In production:
        - Logs to Azure Monitor
        - Stores in Azure SQL Database
        - Sends to Azure Service Bus for downstream processing
        """
        audit_log = {
            'timestamp': datetime.now().isoformat(),
            'case_id': approval['case_id'],
            'officer_id': approval['officer_id'],
            'ai_recommendation': approval['ai_recommendation'],
            'ai_risk_score': approval['ai_risk_score'],
            'human_decision': approval['human_decision'],
            'officer_notes': approval['officer_notes'],
            'decision_alignment': self._check_decision_alignment(approval)
        }
        
        # In production: Send to Azure Monitor / Log Analytics
        print(f"[AUDIT LOG] {audit_log}")
    
    def _check_decision_alignment(self, approval: Dict[str, Any]) -> str:
        """
        Check if human decision aligns with AI recommendation.
        
        Returns:
        --------
        str
            "ALIGNED" or "OVERRIDE"
        """
        ai_rec = approval['ai_recommendation']
        human_dec = approval['human_decision']
        
        # Simple alignment check
        # In practice, this would be more sophisticated
        if ai_rec == 'URGENT_REVIEW' and human_dec == 'APPROVE':
            return "OVERRIDE"  # Human approved despite high risk
        elif ai_rec == 'ROUTINE_REVIEW' and human_dec == 'REJECT':
            return "OVERRIDE"  # Human rejected despite low risk
        else:
            return "ALIGNED"
    
    def get_pending_approvals(self) -> list:
        """Get all pending approval requests."""
        return [
            a for a in self.approval_log
            if a['status'] == DecisionStatus.PENDING_APPROVAL
        ]
    
    def get_approval_history(self, case_id: Optional[str] = None) -> list:
        """
        Get approval history.
        
        Parameters:
        -----------
        case_id : str, optional
            Filter by case ID
        
        Returns:
        --------
        list
            Approval records
        """
        if case_id:
            return [a for a in self.approval_log if a['case_id'] == case_id]
        return self.approval_log

def demonstrate_workflow():
    """
    Demonstrate the human-in-the-loop workflow.
    """
    print("=" * 60)
    print("STEP 5: HUMAN-IN-THE-LOOP WORKFLOW DEMONSTRATION")
    print("=" * 60)
    
    workflow = ApprovalWorkflow()
    
    # Simulate AI analysis
    print("\n1. AI analyzes case and creates approval request...")
    approval_req = workflow.create_approval_request(
        case_id="CASE_001",
        ai_recommendation="URGENT_REVIEW",
        ai_risk_score=75.5,
        ai_explanation="High risk case requiring immediate review"
    )
    print(f"   [OK] Approval request created: {approval_req['case_id']}")
    print(f"   [OK] Status: {approval_req['status']}")
    print(f"   [OK] AI Recommendation: {approval_req['ai_recommendation']}")
    print(f"   [OK] AI Risk Score: {approval_req['ai_risk_score']}")
    
    # Simulate human approval
    print("\n2. Human officer reviews and makes decision...")
    try:
        approval_result = workflow.process_human_approval(
            case_id="CASE_001",
            officer_id="OFFICER_123",
            decision="APPROVE",
            officer_notes="Verified documents, case is legitimate despite high risk score"
        )
        print(f"   [OK] Human Decision: {approval_result['human_decision']}")
        print(f"   [OK] Officer ID: {approval_result['officer_id']}")
        print(f"   [OK] Officer Notes: {approval_result['officer_notes']}")
        print(f"   [OK] Final Status: {approval_result['status']}")
    except ValueError as e:
        print(f"   [ERROR] Error: {e}")
    
    # Show audit trail
    print("\n3. Audit Trail:")
    history = workflow.get_approval_history("CASE_001")
    for record in history:
        print(f"   - Case: {record['case_id']}, Status: {record['status']}")
    
    print("\n" + "=" * 60)
    print("RESPONSIBLE AI COMPLIANCE:")
    print("=" * 60)
    print("[OK] No fully automated decisions")
    print("[OK] Human approval is mandatory")
    print("[OK] All AI recommendations are logged")
    print("[OK] Human decisions override AI recommendations")
    print("[OK] Full audit trail maintained")
    print("\nNOTE: In production, this would use:")
    print("  - Azure Logic Apps for workflow orchestration")
    print("  - Azure Service Bus for notifications")
    print("  - Azure Monitor for audit logging")
    print("  - Azure SQL Database for persistent storage")

if __name__ == "__main__":
    demonstrate_workflow()

