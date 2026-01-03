from typing import Dict, List, Any
from core.database import Recommendation, Feedback, Theme
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class FeatureAdoptionTracker:
    """Track feature adoption after shipping"""
    
    def track_adoption(self, recommendation: Recommendation, db: Session) -> Dict[str, Any]:
        """Track adoption metrics for a shipped feature"""
        # Get theme for this recommendation
        theme = db.query(Theme).filter(Theme.name == recommendation.feature).first()
        
        if not theme:
            return {
                "feature": recommendation.feature,
                "status": "no_theme_found",
                "adoption_rate": 0.0
            }
        
        # Get original request volume
        original_requests = db.query(Feedback).filter(Feedback.theme_id == theme.id).count()
        
        # Get feedback after feature shipped (if recommendation has shipped_at date)
        shipped_at = None
        if recommendation.extra_metadata and recommendation.extra_metadata.get("shipped_at"):
            shipped_at = datetime.fromisoformat(recommendation.extra_metadata["shipped_at"])
        
        # For now, estimate adoption based on:
        # 1. Request volume vs. typical adoption rates
        # 2. Time since shipping
        # 3. User segment distribution
        
        # Get user segments
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        segments = {}
        total_arr = 0.0
        
        for feedback in feedback_items:
            segment = feedback.user_segment or "unknown"
            segments[segment] = segments.get(segment, 0) + 1
            if feedback.arr:
                total_arr += feedback.arr
        
        # Estimate adoption rate (in production, would track actual usage)
        # Higher request volume + higher ARR = higher expected adoption
        estimated_adoption = min(100.0, 
            (original_requests * 2.0) +  # Base: 2% per request
            min(30.0, total_arr / 10000)  # Up to 30% for high ARR customers
        )
        
        return {
            "feature": recommendation.feature,
            "recommendation_id": recommendation.id,
            "original_request_volume": original_requests,
            "estimated_adoption_rate": round(estimated_adoption, 1),
            "user_segments": segments,
            "total_arr_requested": round(total_arr, 2),
            "shipped_at": shipped_at.isoformat() if shipped_at else None,
            "status": "shipped" if recommendation.status == "shipped" else "pending"
        }
    
    def compare_request_vs_adoption(self, recommendation: Recommendation, db: Session) -> Dict[str, Any]:
        """Compare request volume vs adoption to validate prioritization"""
        adoption_data = self.track_adoption(recommendation, db)
        
        request_volume = adoption_data["original_request_volume"]
        adoption_rate = adoption_data["estimated_adoption_rate"]
        
        # Calculate success score
        # High adoption on high request volume = success
        success_score = (adoption_rate / 100.0) * (request_volume / 10.0)
        success_score = min(10.0, success_score)
        
        return {
            **adoption_data,
            "success_score": round(success_score, 2),
            "validation": "success" if success_score >= 7.0 else "needs_review" if success_score >= 4.0 else "low_adoption"
        }







