"""
Azure OpenAI Explanation Engine - Production Ready
Generates human-readable explanations for welfare case decisions using Azure OpenAI.
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
    logger.warning("⚠️  Azure OpenAI SDK not installed. Using fallback explanations.")

class ExplanationEngine:
    """
    Engine for generating citizen-friendly explanations.
    Uses Azure OpenAI Service when available, falls back to mock.
    """
    
    def __init__(self):
        self.client = None
        self.deployment_name = None
        
        # Initialize Azure OpenAI if credentials are available
        if AZURE_OPENAI_AVAILABLE:
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
            
            if endpoint and api_key:
                try:
                    self.client = AzureOpenAI(
                        api_key=api_key,
                        api_version="2024-02-15-preview",
                        azure_endpoint=endpoint
                    )
                    logger.info("✅ Azure OpenAI client initialized successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Azure OpenAI: {e}")
                    self.client = None
            else:
                logger.warning("⚠️  Azure OpenAI credentials not found in environment variables")
        else:
            logger.warning("⚠️  Azure OpenAI SDK not available, using fallback explanations")
    
    def create_explanation_prompt(
        self,
        risk_score: float,
        risk_level: str,
        model_reasons: Dict[str, Any],
        citizen_data: Dict[str, Any]
    ) -> str:
        """Create a prompt for Azure OpenAI to generate explanation."""
        prompt = f"""Generate a clear, empathetic explanation for a welfare case decision.

Risk Score: {risk_score:.1f}/100
Risk Level: {risk_level.upper()}
Income: ₹{citizen_data.get('income', 'N/A'):,.2f}
Last Document Update: {citizen_data.get('last_document_update_months', 'N/A'):.1f} months ago
Scheme Type: {citizen_data.get('scheme_type', 'N/A')}
Past Interruptions: {citizen_data.get('past_benefit_interruptions', 'N/A')}

Write a brief, citizen-friendly explanation (2-3 sentences) that:
1. Explains what the risk score means in simple terms
2. Provides clear next steps
3. Uses respectful, helpful tone
Avoid technical jargon."""
        
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
        Uses Azure OpenAI if available, otherwise falls back to mock.
        """
        
        # Try Azure OpenAI first
        if self.client and self.deployment_name:
            try:
                prompt = self.create_explanation_prompt(
                    risk_score, risk_level, model_reasons, citizen_data
                )
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant explaining welfare case decisions in simple, clear language."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                explanation_text = response.choices[0].message.content.strip()
                logger.info("✅ Generated explanation using Azure OpenAI")
            except Exception as e:
                logger.error(f"❌ Azure OpenAI error: {e}. Using fallback explanation.")
                explanation_text = self._generate_mock_explanation(risk_score, risk_level)
        else:
            # Fallback to mock
            explanation_text = self._generate_mock_explanation(risk_score, risk_level)
        
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
    
    def _generate_mock_explanation(self, risk_score: float, risk_level: str) -> str:
        """Fallback mock explanation when Azure OpenAI is not available."""
        if risk_score >= 60:
            return f"Your welfare case shows a high risk score ({int(risk_score)}). Please update your documentation within 30 days. A case officer will review your file and contact you within 15 business days."
        elif risk_score >= 30:
            return f"Your case shows a moderate risk score ({int(risk_score)}). Please verify your income information is up to date. A case officer will review your application within 10 business days."
        else:
            return f"Your case shows a low risk score ({int(risk_score)}). Your application will proceed to final review. You should receive a decision within 5-7 business days."


