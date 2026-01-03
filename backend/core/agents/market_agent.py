from typing import Dict, List, Any
from core.agents.base_agent import BaseAgent
from core.database import Feedback, Theme
from sqlalchemy.orm import Session
import json

class MarketAgent(BaseAgent):
    """Market Agent - Analyzes market signals, user feedback, and market trends"""
    
    def __init__(self):
        super().__init__("Market Agent")
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and feedback"""
        feedback_items = data.get("feedback", [])
        documents = data.get("documents", [])
        
        results = {
            "analyzed_count": len(feedback_items),
            "classifications": {},
            "themes": [],
            "trends": {},
            "insights": []
        }
        
        # Process each feedback item
        for item in feedback_items:
            classification = await self.classify_feedback(
                item.get("content", ""),
                item.get("context", {})
            )
            
            metadata = await self.extract_metadata(
                item.get("content", ""),
                item.get("source", "unknown")
            )
            
            # Update classification counts
            cls = classification.get("classification", "unknown")
            results["classifications"][cls] = results["classifications"].get(cls, 0) + 1
            
            # Store processed feedback
            item["classification"] = classification
            item["metadata"] = metadata
        
        # Generate market insights
        insights = await self.generate_market_insights(feedback_items, documents)
        results["insights"] = insights
        
        return results
    
    async def generate_market_insights(
        self,
        feedback_items: List[Dict[str, Any]],
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate market insights from feedback and documents"""
        prompt = f"""Analyze the following market data and generate insights. Consider:
- Emerging feature requests and their frequency
- Pain points across different segments
- Market trends and opportunities
- Competitive positioning signals

Feedback items: {len(feedback_items)} items
Documents: {len(documents)} documents

Return a JSON array of insights, each with:
- title: insight title
- description: detailed description
- evidence: supporting evidence
- impact: potential impact level (low, medium, high)
- category: market category
"""
        
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a market intelligence expert. Return valid JSON arrays."},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        
        try:
            return json.loads(response)
        except:
            return [{
                "title": "Market Analysis Complete",
                "description": f"Analyzed {len(feedback_items)} feedback items",
                "evidence": [],
                "impact": "medium",
                "category": "general"
            }]








