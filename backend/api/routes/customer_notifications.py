from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, Recommendation
from core.customer_notifier import CustomerNotifier
from typing import Optional

router = APIRouter()
notifier = CustomerNotifier()

@router.post("/notify/{recommendation_id}")
async def notify_customers_about_feature(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Notify all customers who requested this feature that it's been shipped"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if recommendation.status != "shipped":
        raise HTTPException(
            status_code=400, 
            detail=f"Feature status is '{recommendation.status}', not 'shipped'. Only shipped features can trigger notifications."
        )
    
    result = notifier.notify_customers(recommendation, db)
    return {
        "status": "success",
        "notifications_sent": result["customers_notified"],
        "feature": result["feature"],
        "notifications": result["notifications"]
    }

@router.get("/customers/{recommendation_id}")
async def get_customers_to_notify(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get list of customers who requested this feature (preview before sending)"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    customers = notifier.get_customers_to_notify(recommendation, db)
    return {
        "recommendation_id": recommendation_id,
        "feature": recommendation.feature,
        "customers": customers,
        "count": len(customers)
    }







