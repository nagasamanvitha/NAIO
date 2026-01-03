from typing import Dict, List, Any
from core.database import Theme, Feedback
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from collections import defaultdict

class TimeSeriesTracker:
    """Track theme volume over time and identify trends"""
    
    def get_theme_trends(self, theme: Theme, db: Session, months: int = 6) -> Dict[str, Any]:
        """Get time-series data for a theme over the last N months"""
        # Get all feedback for this theme
        feedback_items = db.query(Feedback).filter(
            Feedback.theme_id == theme.id
        ).order_by(Feedback.created_at.desc()).all()
        
        if not feedback_items:
            return {
                "trend": "no_data",
                "volume_by_month": {},
                "growth_rate": 0.0,
                "trending": False,
                "declining": False
            }
        
        # Group by month
        volume_by_month = defaultdict(int)
        for feedback in feedback_items:
            if feedback.created_at:
                month_key = feedback.created_at.strftime("%Y-%m")
                volume_by_month[month_key] += 1
        
        # Sort months chronologically
        sorted_months = sorted(volume_by_month.keys())
        
        # Calculate growth rate
        growth_rate = 0.0
        if len(sorted_months) >= 2:
            recent_volume = volume_by_month[sorted_months[-1]]
            previous_volume = volume_by_month[sorted_months[-2]]
            if previous_volume > 0:
                growth_rate = ((recent_volume - previous_volume) / previous_volume) * 100
        
        # Determine trend
        if len(sorted_months) >= 3:
            recent_avg = sum(volume_by_month[m] for m in sorted_months[-3:]) / 3
            older_avg = sum(volume_by_month[m] for m in sorted_months[:-3]) / max(1, len(sorted_months) - 3)
            
            if recent_avg > older_avg * 1.2:  # 20% increase
                trend = "trending_up"
                trending = True
                declining = False
            elif recent_avg < older_avg * 0.8:  # 20% decrease
                trend = "trending_down"
                trending = False
                declining = True
            else:
                trend = "stable"
                trending = False
                declining = False
        else:
            trend = "insufficient_data"
            trending = False
            declining = False
        
        return {
            "trend": trend,
            "volume_by_month": dict(volume_by_month),
            "growth_rate": round(growth_rate, 1),
            "trending": trending,
            "declining": declining,
            "total_volume": len(feedback_items),
            "recent_volume": volume_by_month.get(sorted_months[-1] if sorted_months else "", 0)
        }
    
    def get_all_theme_trends(self, db: Session, months: int = 6) -> Dict[int, Dict[str, Any]]:
        """Get trends for all themes"""
        themes = db.query(Theme).all()
        trends = {}
        
        for theme in themes:
            trends[theme.id] = self.get_theme_trends(theme, db, months)
        
        return trends
    
    def identify_trending_themes(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify themes that are trending up"""
        themes = db.query(Theme).all()
        trending_themes = []
        
        for theme in themes:
            trend_data = self.get_theme_trends(theme, db)
            if trend_data["trending"]:
                trending_themes.append({
                    "theme_id": theme.id,
                    "theme_name": theme.name,
                    "growth_rate": trend_data["growth_rate"],
                    "recent_volume": trend_data["recent_volume"],
                    "trend_data": trend_data
                })
        
        # Sort by growth rate
        trending_themes.sort(key=lambda x: x["growth_rate"], reverse=True)
        return trending_themes[:limit]
    
    def identify_declining_themes(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify themes that are declining"""
        themes = db.query(Theme).all()
        declining_themes = []
        
        for theme in themes:
            trend_data = self.get_theme_trends(theme, db)
            if trend_data["declining"]:
                declining_themes.append({
                    "theme_id": theme.id,
                    "theme_name": theme.name,
                    "growth_rate": trend_data["growth_rate"],
                    "recent_volume": trend_data["recent_volume"],
                    "trend_data": trend_data
                })
        
        # Sort by decline rate (most negative first)
        declining_themes.sort(key=lambda x: x["growth_rate"])
        return declining_themes[:limit]







