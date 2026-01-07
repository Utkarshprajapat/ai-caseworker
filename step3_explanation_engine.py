"""
STEP 3: EXPLANATION ENGINE (AZURE OPENAI)
==========================================
Generates citizen-friendly explanations for AI decisions.

In production, this would use:
- Azure OpenAI Service (GPT-4 or GPT-3.5-turbo)
- Azure OpenAI Studio for prompt engineering
- Azure Cognitive Services for additional NLP capabilities
"""

import json
from typing import Dict, Any, Optional

class MockAzureOpenAI:
    """
    Mock Azure OpenAI Service for local development.
    
    In production, replace with actual Azure OpenAI SDK:
    from azure.openai import AzureOpenAI
    """
    
    def __init__(self):
        self.api_key = "mock_key"  # In production: Load from Azure Key Vault
        self.endpoint = "https://mock-openai.azure.com"  # In production: Your Azure OpenAI endpoint
        self.deployment_name = "gpt-4"  # In production: Your deployment name
    
    def generate_explanation(self, prompt: str) -> str:
        """
        Generate explanation using Azure OpenAI.
        
        In production:
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=self.endpoint
        )
        response = client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        """
        # Mock response - simulates GPT-4 output
        # In production, this would be a real API call to Azure OpenAI
        
        # Simple rule-based mock for demonstration
        if "high risk" in prompt.lower() or "risk_score" in prompt:
            # Extract risk score from prompt
            risk_score = 0
            if "risk_score" in prompt:
                try:
                    import re
                    match = re.search(r'risk_score[:\s]+(\d+\.?\d*)', prompt)
                    if match:
                        risk_score = float(match.group(1))
                except:
                    pass
            
            if risk_score >= 60:
                return """Based on our review of your welfare case, we've identified some concerns that need attention.

**What we found:**
Your case shows a high risk score ({}), which means there may be discrepancies in your information or documentation that require verification.

**Why this matters:**
This helps ensure that welfare benefits reach those who truly need them and prevents errors in the system.

**What you need to do:**
1. Please update your income documentation within the next 30 days
2. Submit any missing documents through the online portal or your local welfare office
3. If you have questions, contact our helpline at 1800-WELFARE

**Next steps:**
A case officer will review your file and may contact you for additional information. You will receive a decision within 15 business days.

We're here to help ensure you receive the support you're entitled to.""".format(int(risk_score))
            elif risk_score >= 30:
                return """Thank you for your welfare application. We've completed an initial review of your case.

**What we found:**
Your case shows a moderate risk score ({}), which means some information may need clarification or updating.

**Why this matters:**
Regular updates help us ensure you continue to receive the correct benefits based on your current situation.

**What you need to do:**
1. Please verify that your income information is up to date
2. Check that your contact information is current
3. If your circumstances have changed, please notify us within 30 days

**Next steps:**
Your case will be reviewed by a case officer. You should receive an update within 10 business days.

If you have any questions, please don't hesitate to contact us.""".format(int(risk_score))
            else:
                return """Thank you for your welfare application. We've completed an initial review of your case.

**What we found:**
Your case shows a low risk score ({}), which means your information appears to be in good order.

**What happens next:**
Your application will proceed to final review by a case officer. This is a standard process to ensure accuracy.

**Timeline:**
You should receive a decision within 5-7 business days.

**If you need help:**
If you have any questions or need to update your information, please contact us through the online portal or call 1800-WELFARE.

We're committed to processing your application fairly and efficiently.""".format(int(risk_score))
        
        # Default response
        return "We have reviewed your welfare case. A case officer will contact you with further details."

class ExplanationEngine:
    """
    Engine for generating citizen-friendly explanations.
    """
    
    def __init__(self):
        self.openai_client = MockAzureOpenAI()
    
    def create_explanation_prompt(
        self,
        risk_score: float,
        risk_level: str,
        model_reasons: Dict[str, Any],
        citizen_data: Dict[str, Any]
    ) -> str:
        """
        Create a prompt for Azure OpenAI to generate explanation.
        
        Parameters:
        -----------
        risk_score : float
            Predicted risk score (0-100)
        risk_level : str
            Predicted risk level (low/medium/high)
        model_reasons : dict
            Feature importance and values from model
        citizen_data : dict
            Original citizen case data
        
        Returns:
        --------
        str
            Formatted prompt for Azure OpenAI
        """
        prompt = f"""You are a helpful AI assistant explaining welfare case decisions to citizens in simple, clear language.

CASE INFORMATION:
- Risk Score: {risk_score:.1f} (out of 100)
- Risk Level: {risk_level.upper()}
- Income: ₹{citizen_data.get('income', 'N/A'):,.2f}
- Last Document Update: {citizen_data.get('last_document_update_months', 'N/A'):.1f} months ago
- Scheme Type: {citizen_data.get('scheme_type', 'N/A')}
- Past Benefit Interruptions: {citizen_data.get('past_benefit_interruptions', 'N/A')}

MODEL REASONING:
"""
        
        # Add feature importance information
        for feature, info in model_reasons.items():
            prompt += f"- {feature}: value={info['value']:.2f}, importance={info['importance']:.3f}\n"
        
        prompt += """
TASK:
Generate a clear, empathetic, and actionable explanation for the citizen that:
1. Explains what the risk score means in simple terms
2. Identifies the main factors contributing to the risk
3. Provides clear next steps the citizen should take
4. Uses a respectful, helpful tone
5. Avoids technical jargon
6. Includes contact information for support

Format the response as a clear, well-structured message suitable for sending to a citizen.
"""
        
        return prompt
    
    def generate_explanation(
        self,
        risk_score: float,
        risk_level: str,
        model_reasons: Dict[str, Any],
        citizen_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanation for a welfare case.
        
        Parameters:
        -----------
        risk_score : float
            Predicted risk score
        risk_level : str
            Predicted risk level
        model_reasons : dict
            Model reasoning information
        citizen_data : dict
            Citizen case data
        
        Returns:
        --------
        dict
            Explanation with text and recommended actions
        """
        # Create prompt
        prompt = self.create_explanation_prompt(
            risk_score, risk_level, model_reasons, citizen_data
        )
        
        # Generate explanation using Azure OpenAI (mocked here)
        explanation_text = self.openai_client.generate_explanation(prompt)
        
        # Determine recommended action based on risk level
        if risk_level == 'high':
            recommended_action = "URGENT_REVIEW"
            action_description = "Case requires immediate officer review and citizen contact"
        elif risk_level == 'medium':
            recommended_action = "STANDARD_REVIEW"
            action_description = "Case requires standard officer review and documentation update request"
        else:
            recommended_action = "ROUTINE_REVIEW"
            action_description = "Case can proceed with routine officer verification"
        
        return {
            'explanation': explanation_text,
            'recommended_action': recommended_action,
            'action_description': action_description,
            'risk_score': risk_score,
            'risk_level': risk_level
        }

def test_explanation_engine():
    """
    Test the explanation engine with sample data.
    """
    print("=" * 60)
    print("STEP 3: TESTING EXPLANATION ENGINE")
    print("=" * 60)
    
    engine = ExplanationEngine()
    
    # Test case 1: High risk
    print("\n" + "=" * 60)
    print("TEST CASE 1: HIGH RISK")
    print("=" * 60)
    
    citizen_data_1 = {
        'income': 35000,
        'last_document_update_months': 18,
        'scheme_type': 'pension',
        'past_benefit_interruptions': 3
    }
    
    model_reasons_1 = {
        'income': {'value': 35000, 'importance': 0.35},
        'last_document_update_months': {'value': 18, 'importance': 0.30},
        'scheme_type_encoded': {'value': 0, 'importance': 0.20},
        'past_benefit_interruptions': {'value': 3, 'importance': 0.15}
    }
    
    explanation_1 = engine.generate_explanation(
        risk_score=75.5,
        risk_level='high',
        model_reasons=model_reasons_1,
        citizen_data=citizen_data_1
    )
    
    print(f"\nRisk Score: {explanation_1['risk_score']}")
    print(f"Risk Level: {explanation_1['risk_level']}")
    print(f"Recommended Action: {explanation_1['recommended_action']}")
    print(f"\nExplanation:\n{explanation_1['explanation']}")
    
    # Test case 2: Low risk
    print("\n" + "=" * 60)
    print("TEST CASE 2: LOW RISK")
    print("=" * 60)
    
    citizen_data_2 = {
        'income': 12000,
        'last_document_update_months': 3,
        'scheme_type': 'subsidy',
        'past_benefit_interruptions': 0
    }
    
    model_reasons_2 = {
        'income': {'value': 12000, 'importance': 0.25},
        'last_document_update_months': {'value': 3, 'importance': 0.30},
        'scheme_type_encoded': {'value': 1, 'importance': 0.20},
        'past_benefit_interruptions': {'value': 0, 'importance': 0.25}
    }
    
    explanation_2 = engine.generate_explanation(
        risk_score=15.2,
        risk_level='low',
        model_reasons=model_reasons_2,
        citizen_data=citizen_data_2
    )
    
    print(f"\nRisk Score: {explanation_2['risk_score']}")
    print(f"Risk Level: {explanation_2['risk_level']}")
    print(f"Recommended Action: {explanation_2['recommended_action']}")
    print(f"\nExplanation:\n{explanation_2['explanation']}")
    
    print("\n" + "=" * 60)
    print("[OK] Explanation engine test complete!")
    print("=" * 60)
    print("\nNOTE: In production, this would use:")
    print("  - Azure OpenAI Service (GPT-4 or GPT-3.5-turbo)")
    print("  - Azure OpenAI Studio for prompt engineering")
    print("  - Azure Key Vault for API key management")
    print("  - Azure Application Insights for monitoring")

if __name__ == "__main__":
    test_explanation_engine()

