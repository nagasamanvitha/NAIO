from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import (
    Feedback, Theme, Recommendation, Roadmap, Competitor,
    get_db
)
from sqlalchemy import func, delete
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview statistics - ULTRA FAST (no count queries)"""
    # Skip expensive count() queries - use estimates from limited queries
    # Get top themes (already limited)
    top_themes = db.query(Theme).order_by(
        Theme.overall_impact_score.desc()
    ).limit(5).all()
    
    # Get recent feedback for classification breakdown (limited sample)
    recent_feedback_sample = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).limit(100).all()  # Sample 100 items for classification breakdown
    
    # Calculate classification from sample (fast)
    classification_counts = {}
    for item in recent_feedback_sample:
        cls = item.classification or "unknown"
        classification_counts[cls] = classification_counts.get(cls, 0) + 1
    
    # Get recommendations (limited)
    recommendations = db.query(Recommendation).limit(50).all()
    recommendations_by_status = {}
    for rec in recommendations:
        status = rec.status or "pending"
        recommendations_by_status[status] = recommendations_by_status.get(status, 0) + 1
    
    # Recent activity (limit to 5 for speed)
    recent_feedback = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).limit(5).all()
    
    # Estimate totals from limited queries (much faster than count())
    total_themes_estimate = len(db.query(Theme).limit(100).all())
    total_recommendations_estimate = len(recommendations)
    total_competitors_estimate = len(db.query(Competitor).limit(100).all())
    
    return {
        "feedback": {
            "total": len(recent_feedback_sample),  # Sample-based estimate
            "by_classification": classification_counts
        },
        "themes": {
            "total": total_themes_estimate,
            "top_themes": [
                {
                    "id": theme.id,
                    "name": theme.name,
                    "impact_score": theme.overall_impact_score,
                    "request_frequency": theme.request_frequency,
                    # Include ARR and lost deals
                    "lost_deal_count": (theme.extra_metadata or {}).get("lost_deal_info", {}).get("lost_deal_count", 0) if theme.extra_metadata else 0,
                    "lost_deal_arr": (theme.extra_metadata or {}).get("lost_deal_info", {}).get("lost_deal_arr", 0) if theme.extra_metadata else 0,
                    "competitor_mentions": (theme.extra_metadata or {}).get("lost_deal_info", {}).get("competitor_mentions", []) if theme.extra_metadata else []
                }
                for theme in top_themes
            ]
        },
        "recommendations": {
            "total": total_recommendations_estimate,
            "by_status": recommendations_by_status
        },
        "competitors": {
            "total": total_competitors_estimate
        },
        "recent_activity": [
            {
                "id": item.id,
                "type": "feedback",
                "content": item.content[:100],
                "source": item.source,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in recent_feedback
        ]
    }

@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Get key insights for dashboard"""
    # High impact themes
    high_impact_themes = db.query(Theme).filter(
        Theme.overall_impact_score >= 7.0
    ).order_by(Theme.overall_impact_score.desc()).limit(10).all()
    
    # Pending recommendations
    pending_recommendations = db.query(Recommendation).filter(
        Recommendation.status == "pending"
    ).order_by(Recommendation.impact_score.desc()).limit(10).all()
    
    # Recent competitors
    recent_competitors = db.query(Competitor).order_by(
        Competitor.discovered_at.desc()
    ).limit(5).all()
    
    return {
        "high_impact_themes": [
            {
                "id": theme.id,
                "name": theme.name,
                "impact_score": theme.overall_impact_score,
                "customer_value": theme.customer_value,
                "request_frequency": theme.request_frequency
            }
            for theme in high_impact_themes
        ],
        "pending_recommendations": [
            {
                "id": rec.id,
                "title": rec.title,
                "impact_score": rec.impact_score,
                "feasibility_score": rec.feasibility_score,
                "risk_score": rec.risk_score
            }
            for rec in pending_recommendations
        ],
        "recent_competitors": [
            {
                "id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "discovered_at": comp.discovered_at.isoformat() if comp.discovered_at else None
            }
            for comp in recent_competitors
        ]
    }

@router.get("/recommendations")
async def get_recommendations(
    status: str = None,
    limit: int = 20,
    quarter: str = None,  # Q1, Q2, Q3, Q4
    year: int = None,  # 2024, 2025, etc.
    db: Session = Depends(get_db)
):
    """Get recommendations - ONLY returns real recommendations from n8n data (NO AUTO-GENERATION)"""
    from datetime import datetime
    from sqlalchemy import and_
    
    query = db.query(Recommendation)
    
    if status:
        query = query.filter(Recommendation.status == status)
    
    # Filter by quarter/year if provided
    if quarter and year:
        quarter_map = {
            'Q1': (1, 3),
            'Q2': (4, 6),
            'Q3': (7, 9),
            'Q4': (10, 12)
        }
        if quarter in quarter_map:
            start_month, end_month = quarter_map[quarter]
            start_dt = datetime(year, start_month, 1)
            if end_month == 12:
                end_dt = datetime(year + 1, 1, 1)
            else:
                end_dt = datetime(year, end_month + 1, 1)
            query = query.filter(
                and_(
                    Recommendation.created_at >= start_dt,
                    Recommendation.created_at < end_dt
                )
            )
    
    recommendations = query.order_by(
        Recommendation.impact_score.desc()
    ).limit(limit).all()
    
    # NO AUTO-GENERATION - Only return real recommendations from n8n processed data
    # If no recommendations exist, return empty array (frontend will show empty state)
    
    # Get theme data for each recommendation to include ARR, lost deals, etc.
    from core.database import Theme, Feedback
    
    recommendations_data = []
    for rec in recommendations:
        # Find theme for this recommendation
        theme = db.query(Theme).filter(Theme.name == rec.feature).first()
        
        # Get ARR and lost deal data
        arr_data = {}
        lost_deal_info = {}
        competitor_info = []
        mock_competitor_info = []
        
        if theme:
            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
            total_arr = sum([f.arr for f in theme_feedback if f.arr]) if theme_feedback else 0
            avg_arr = total_arr / len(theme_feedback) if theme_feedback else 0
            
            if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
            
            arr_data = {
                "avg_arr": avg_arr,
                "total_arr": total_arr,
                "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),
                "competitor_mentions": lost_deal_info.get("competitor_mentions", [])
            }
            
            # Get detailed competitor information from database (like themes do)
            if lost_deal_info.get("competitor_mentions"):
                from core.database import Competitor
                mentioned_competitors = lost_deal_info.get("competitor_mentions", [])
                competitors = db.query(Competitor).filter(
                    Competitor.name.in_(mentioned_competitors)
                ).all()
                competitor_info = [
                    {
                        "name": c.name,
                        "description": c.description,
                        "strengths": c.strengths or [],
                        "weaknesses": c.weaknesses or [],
                        "opportunities": c.opportunities or [],
                        "market_gaps": c.market_gaps or [],
                        "positioning": c.positioning,
                        "competitive_pressure": "high"  # Default, can be enhanced
                    }
                    for c in competitors
                ]
            
            # Get mock competitor data details (like themes get from mock enrichment)
            from core.mock_competitor_enrichment import MOCK_COMPETITORS
            theme_lower = (theme.name + ' ' + (theme.description or '')).lower()
            for comp in MOCK_COMPETITORS:
                # Check if this competitor matches the theme
                comp_name_lower = comp['name'].lower()
                if comp['name'] in lost_deal_info.get("competitor_mentions", []):
                    # Also check feature comparison keywords
                    feature_match = any(
                        keyword in theme_lower 
                        for keyword in comp.get('feature_comparison', {}).keys()
                    )
                    if feature_match or comp_name_lower in theme_lower:
                        mock_competitor_info.append({
                            "name": comp['name'],
                            "lost_deals_attributed": comp.get('lost_deals_attributed', 0),
                            "total_arr_lost": comp.get('total_arr_lost', 0),
                            "mentioned_in_feedback": comp.get('mentioned_in_feedback', 0),
                            "competitive_pressure": comp.get('competitive_pressure', 'medium'),
                            "strengths": comp.get('strengths', []),
                            "weaknesses": comp.get('weaknesses', []),
                            "feature_comparison": comp.get('feature_comparison', {})
                        })
        
        # Format customer quotes properly
        customer_quotes_formatted = []
        if rec.customer_quotes:
            if isinstance(rec.customer_quotes, list):
                for quote_item in rec.customer_quotes:
                    if isinstance(quote_item, dict):
                        customer_quotes_formatted.append(quote_item.get("quote", quote_item.get("content", str(quote_item))))
                    else:
                        customer_quotes_formatted.append(str(quote_item))
            else:
                customer_quotes_formatted = [str(rec.customer_quotes)]
        
        # Get priority level and competitor info from extra_metadata
        priority_level = "P2/Medium"
        if rec.extra_metadata and isinstance(rec.extra_metadata, dict):
            priority_level = rec.extra_metadata.get("priority_level", "P2/Medium")
            # Merge ARR data from extra_metadata if available
            if "arr_data" in rec.extra_metadata:
                arr_data.update(rec.extra_metadata["arr_data"])
            # Get competitor info from extra_metadata if stored there
            if "competitor_info" in rec.extra_metadata and rec.extra_metadata["competitor_info"]:
                competitor_info = rec.extra_metadata["competitor_info"]
            if "mock_competitor_info" in rec.extra_metadata and rec.extra_metadata["mock_competitor_info"]:
                mock_competitor_info = rec.extra_metadata["mock_competitor_info"]
        
        recommendations_data.append({
            "id": rec.id,
            "title": rec.title,
            "description": rec.description,
            "feature": rec.feature,
            "impact_score": rec.impact_score,
            "feasibility_score": rec.feasibility_score,
            "risk_score": rec.risk_score,
            "status": rec.status,
            "unified_recommendation": rec.unified_recommendation,
            "pm_verdict": rec.pm_verdict,
            "ux_verdict": rec.ux_verdict,
            "engineering_verdict": rec.engineering_verdict,
            "data_scientist_verdict": rec.data_scientist_verdict,
            "business_impact": rec.business_impact,
            "ux_implications": rec.ux_implications,
            "customer_quotes": customer_quotes_formatted,  # Properly formatted customer quotes
            "evidence": rec.evidence,  # Full deliberation data with all persona agent conversations
            "priority_level": priority_level,  # Explicit priority level
            "arr_data": arr_data,  # ARR, lost deals, competitor mentions
            "arr_at_risk": arr_data.get("lost_deal_arr", 0),  # For frontend compatibility
            "total_arr_requesting": arr_data.get("total_arr", 0),  # For frontend compatibility
            "lost_deal_count": arr_data.get("lost_deal_count", 0),  # For frontend compatibility
            "competitors_mentioned": arr_data.get("competitor_mentions", []),  # For frontend compatibility
            "competitors": competitor_info,  # Detailed competitor info (strengths, weaknesses, opportunities) - like themes
            "mock_competitors": mock_competitor_info,  # Mock competitor data with full details
            "created_at": rec.created_at.isoformat() if rec.created_at else None
        })
    
    return {
        "recommendations": recommendations_data
    }

@router.get("/roadmaps")
async def get_roadmaps(db: Session = Depends(get_db)):
    """Get all roadmaps"""
    roadmaps = db.query(Roadmap).order_by(
        Roadmap.year.desc(), Roadmap.quarter.desc()
    ).all()
    
    return {
        "roadmaps": [
            {
                "id": roadmap.id,
                "quarter": roadmap.quarter,
                "year": roadmap.year,
                "items": roadmap.items,
                "created_at": roadmap.created_at.isoformat() if roadmap.created_at else None
            }
            for roadmap in roadmaps
        ]
    }

@router.post("/clear-database")
async def clear_database(db: Session = Depends(get_db)):
    """Clear all feedback, themes, and recommendations from database"""
    try:
        # Count before deletion
        feedback_count = db.query(Feedback).count()
        themes_count = db.query(Theme).count()
        recommendations_count = db.query(Recommendation).count()
        
        # Delete all feedback
        db.execute(delete(Feedback))
        
        # Delete all themes
        db.execute(delete(Theme))
        
        # Delete all recommendations
        db.execute(delete(Recommendation))
        
        # Commit changes
        db.commit()
        
        return {
            "status": "success",
            "message": "Database cleared successfully",
            "deleted": {
                "feedback": feedback_count,
                "themes": themes_count,
                "recommendations": recommendations_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")

