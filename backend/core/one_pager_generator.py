from typing import Dict, List, Any
from core.database import Recommendation, Theme, Feedback
from sqlalchemy.orm import Session
import json

class OnePagerGenerator:
    """Generate comprehensive stakeholder one-pagers for features"""
    
    def __init__(self):
        pass  # No dependencies needed
    
    async def generate_one_pager(self, recommendation_id: int, db: Session) -> Dict[str, Any]:
        """Generate comprehensive one-pager with all data"""
        # Get recommendation
        recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not recommendation:
            return None
        
        # Get theme
        theme = db.query(Theme).filter(Theme.name == recommendation.feature).first()
        
        # Get feedback for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all() if theme else []
        
        # Calculate metrics
        total_requests = len(feedback_items)
        total_arr = sum(f.arr for f in feedback_items if f.arr)
        avg_arr = total_arr / total_requests if total_requests > 0 else 0
        
        # Get customer quotes
        customer_quotes = []
        if recommendation.customer_quotes:
            if isinstance(recommendation.customer_quotes, list):
                customer_quotes = recommendation.customer_quotes
            else:
                customer_quotes = [recommendation.customer_quotes]
        
        # Get lost deal info
        lost_deal_info = {}
        if theme and theme.extra_metadata and theme.extra_metadata.get("lost_deal_info"):
            lost_deal_info = theme.extra_metadata["lost_deal_info"]
        
        # Get deliberation data
        deliberation = recommendation.evidence or {}
        evaluations = deliberation.get("evaluations", {})
        unified = deliberation.get("unified_recommendation", {})
        
        # Generate one-pager
        one_pager = {
            "feature": recommendation.feature,
            "title": recommendation.title,
            "description": recommendation.description,
            
            # Key Metrics
            "metrics": {
                "impact_score": recommendation.impact_score,
                "feasibility_score": recommendation.feasibility_score,
                "risk_score": recommendation.risk_score,
                "request_volume": total_requests,
                "total_arr_requested": round(total_arr, 2),
                "avg_customer_arr": round(avg_arr, 2),
                "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0.0),
                "competitor_mentions": lost_deal_info.get("competitor_mentions", [])
            },
            
            # Customer Voice
            "customer_voice": {
                "quotes": customer_quotes[:5],  # Top 5 quotes
                "request_volume": total_requests,
                "customer_segments": list(set(f.user_segment for f in feedback_items if f.user_segment))
            },
            
            # Persona Agent Evaluations
            "persona_evaluations": {
                "pm": {
                    "verdict": evaluations.get("pm", {}).get("verdict", "pending"),
                    "reasoning": evaluations.get("pm", {}).get("reasoning", recommendation.pm_verdict),
                    "business_impact": evaluations.get("pm", {}).get("business_impact", recommendation.business_impact),
                    "initial_thoughts": evaluations.get("pm", {}).get("initial_thoughts"),
                    "key_considerations": evaluations.get("pm", {}).get("key_considerations"),
                    "priority_justification": evaluations.get("pm", {}).get("priority_justification")
                },
                "ux": {
                    "verdict": evaluations.get("ux", {}).get("verdict", "pending"),
                    "reasoning": evaluations.get("ux", {}).get("reasoning", recommendation.ux_verdict),
                    "ux_implications": evaluations.get("ux", {}).get("ux_implications", recommendation.ux_implications),
                    "initial_thoughts": evaluations.get("ux", {}).get("initial_thoughts"),
                    "key_considerations": evaluations.get("ux", {}).get("key_considerations")
                },
                "data_scientist": {
                    "verdict": evaluations.get("data_scientist", {}).get("verdict", "pending"),
                    "reasoning": evaluations.get("data_scientist", {}).get("reasoning", recommendation.data_scientist_verdict),
                    "data_insights": evaluations.get("data_scientist", {}).get("data_insights")
                },
                "engineering": {
                    "verdict": evaluations.get("engineering", {}).get("verdict", "pending"),
                    "reasoning": evaluations.get("engineering", {}).get("reasoning", recommendation.engineering_verdict),
                    "feasibility_score": evaluations.get("engineering", {}).get("feasibility_score", recommendation.feasibility_score),
                    "risk_score": evaluations.get("engineering", {}).get("risk_score", recommendation.risk_score),
                    "technical_assessment": evaluations.get("engineering", {}).get("technical_assessment")
                }
            },
            
            # Team Consensus
            "team_consensus": {
                "final_verdict": unified.get("final_verdict", "approve"),
                "unified_reasoning": unified.get("unified_reasoning", recommendation.unified_recommendation),
                "team_discussion": unified.get("team_discussion"),
                "key_debate_points": unified.get("key_debate_points"),
                "trade_offs": unified.get("trade_offs", []),
                "confidence": unified.get("confidence", 7.0),
                "final_priority": unified.get("final_priority")
            },
            
            # ROI Projection
            "roi_projection": {
                "estimated_impact": f"Addresses {total_requests} customer requests",
                "arr_at_risk": lost_deal_info.get("lost_deal_arr", 0.0),
                "customer_satisfaction_boost": "High" if total_requests > 20 else "Medium" if total_requests > 10 else "Low",
                "competitive_advantage": "Yes" if lost_deal_info.get("has_lost_deals") else "Moderate"
            },
            
            # Implementation Estimate
            "implementation": {
                "feasibility": recommendation.feasibility_score,
                "risk_level": "Low" if recommendation.risk_score < 3 else "Medium" if recommendation.risk_score < 6 else "High",
                "estimated_effort": "Low" if recommendation.feasibility_score > 8 else "Medium" if recommendation.feasibility_score > 6 else "High"
            },
            
            # Action Items
            "action_items": unified.get("action_items", [])
        }
        
        return one_pager

