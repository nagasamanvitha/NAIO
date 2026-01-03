from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, Recommendation
from core.feature_adoption_tracker import FeatureAdoptionTracker
from typing import Optional

router = APIRouter()
tracker = FeatureAdoptionTracker()

@router.get("/adoption/{recommendation_id}")
async def get_feature_adoption(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get adoption metrics for a shipped feature"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    adoption_data = tracker.track_adoption(recommendation, db)
    return {
        "status": "success",
        "adoption": adoption_data
    }

@router.get("/adoption/{recommendation_id}/validation")
async def validate_prioritization(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Compare request volume vs adoption to validate prioritization decision"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    validation = tracker.compare_request_vs_adoption(recommendation, db)
    return {
        "status": "success",
        "validation": validation
    }

@router.get("/adoption/all")
async def get_all_adoption_metrics(
    db: Session = Depends(get_db)
):
    """Get adoption metrics for all shipped features"""
    shipped_recommendations = db.query(Recommendation).filter(Recommendation.status == "shipped").all()
    
    adoption_metrics = []
    for rec in shipped_recommendations:
        adoption_data = tracker.track_adoption(rec, db)
        validation = tracker.compare_request_vs_adoption(rec, db)
        adoption_metrics.append({
            "recommendation_id": rec.id,
            "feature": rec.feature,
            "adoption": adoption_data,
            "validation": validation
        })
    
    return {
        "status": "success",
        "features": adoption_metrics,
        "count": len(adoption_metrics)
    }







