from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, Theme
from core.time_series_tracker import TimeSeriesTracker
from typing import Optional

router = APIRouter()
tracker = TimeSeriesTracker()

@router.get("/themes/{theme_id}/trends")
async def get_theme_trends(
    theme_id: int,
    months: int = 6,
    db: Session = Depends(get_db)
):
    """Get time-series trends for a specific theme"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    trend_data = tracker.get_theme_trends(theme, db, months)
    return {
        "theme_id": theme_id,
        "theme_name": theme.name,
        "trend_data": trend_data
    }

@router.get("/themes/trending")
async def get_trending_themes(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get themes that are trending up"""
    trending = tracker.identify_trending_themes(db, limit)
    return {
        "trending_themes": trending,
        "count": len(trending)
    }

@router.get("/themes/declining")
async def get_declining_themes(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get themes that are declining"""
    declining = tracker.identify_declining_themes(db, limit)
    return {
        "declining_themes": declining,
        "count": len(declining)
    }

@router.get("/themes/all-trends")
async def get_all_theme_trends(
    months: int = 6,
    db: Session = Depends(get_db)
):
    """Get trends for all themes"""
    trends = tracker.get_all_theme_trends(db, months)
    return {
        "themes": trends,
        "count": len(trends)
    }







