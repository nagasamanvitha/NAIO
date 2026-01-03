from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import get_db
from core.feedback_loop import FeedbackLoop

router = APIRouter()
feedback_loop = FeedbackLoop()

@router.post("/notify/{recommendation_id}")
async def notify_customers(
    recommendation_id: int,
    request_data: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Notify customers when a feature ships and generate email templates"""
    try:
        generate_emails = request_data.get("generate_emails", True) if request_data else True
        result = feedback_loop.notify_customers_on_ship(recommendation_id, db, generate_emails=generate_emails)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email-template/{recommendation_id}/{customer_id}")
async def get_email_template(
    recommendation_id: int,
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get email template for a specific customer"""
    try:
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Get customer's feedback
        customer_feedback = db.query(Feedback).filter(
            Feedback.feature == recommendation.feature,
            Feedback.account_id == customer_id
        ).all()
        
        email_template = feedback_loop.generate_email_template(
            recommendation,
            customer_id,
            customer_feedback
        )
        
        return {"status": "success", **email_template}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-adoption")
async def track_adoption(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Track feature adoption"""
    try:
        recommendation_id = request_data.get("recommendation_id")
        customer_id = request_data.get("customer_id")
        adopted = request_data.get("adopted", False)
        
        result = feedback_loop.track_adoption(recommendation_id, customer_id, adopted, db)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adoption-stats/{recommendation_id}")
async def get_adoption_stats(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get adoption statistics"""
    try:
        stats = feedback_loop.get_adoption_stats(recommendation_id, db)
        return {"status": "success", **stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

