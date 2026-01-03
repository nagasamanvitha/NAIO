from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from core.llm_client import openrouter_client

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm_client = openrouter_client
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method to be implemented by each agent"""
        pass
    
    async def classify_feedback(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Classify feedback into categories"""
        prompt = f"""Analyze the following feedback and classify it. Return a JSON object with:
- classification: one of "bug", "feature_request", "usability_issue", "integration_request"
- sentiment_score: float between -1 and 1
- pain_level: float between 0 and 10
- urgency: one of "low", "medium", "high", "critical"
- feature: the main feature/product area mentioned
- reason: brief explanation of the feedback

Feedback: {content}
"""
        if context:
            prompt += f"\nContext: {context}"
        
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are an expert at analyzing customer feedback. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.3)
        
        try:
            import json
            return json.loads(response)
        except:
            # Fallback parsing
            return {
                "classification": "feature_request",
                "sentiment_score": 0.0,
                "pain_level": 5.0,
                "urgency": "medium",
                "feature": "general",
                "reason": response[:200]
            }
    
    async def extract_metadata(
        self,
        content: str,
        source: str
    ) -> Dict[str, Any]:
        """Extract metadata from feedback"""
        prompt = f"""Extract metadata from this feedback. Return JSON with:
- user_segment: customer segment (enterprise, smb, individual, etc.)
- account_id: if mentioned
- arr: estimated ARR if available
- churn_risk: float 0-1 if indicators present
- additional_metadata: any other relevant info

Source: {source}
Content: {content}
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "Extract structured metadata from feedback. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.2)
        
        try:
            import json
            return json.loads(response)
        except:
            return {
                "user_segment": "unknown",
                "account_id": None,
                "arr": None,
                "churn_risk": 0.5,
                "additional_metadata": {}
            }








