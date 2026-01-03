from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from core.database import Recommendation, Theme, Feedback, get_db
from datetime import datetime
import json

router = APIRouter()

def generate_fast_recommendation(theme: Theme, feedback_count: int, db: Session = None) -> Dict[str, Any]:
    """Generate recommendation instantly without LLM calls"""
    # Determine classification and scores based on theme name and metrics
    theme_lower = theme.name.lower()
    
    # Quick classification
    if any(word in theme_lower for word in ["bug", "error", "crash", "broken"]):
        classification = "bug_fix"
        feasibility = 8.0
        risk = 3.0
        business_impact = "Critical for user satisfaction and retention"
    elif any(word in theme_lower for word in ["export", "data", "download", "csv"]):
        classification = "feature_enhancement"
        feasibility = 7.0
        risk = 2.0
        business_impact = "High customer demand for data portability"
    elif any(word in theme_lower for word in ["mobile", "app", "ios", "android"]):
        classification = "platform_expansion"
        feasibility = 6.0
        risk = 4.0
        business_impact = "Expands market reach and user accessibility"
    elif any(word in theme_lower for word in ["integrate", "api", "webhook", "zapier"]):
        classification = "integration"
        feasibility = 7.5
        risk = 3.5
        business_impact = "Increases product stickiness and workflow efficiency"
    elif any(word in theme_lower for word in ["performance", "speed", "slow", "loading"]):
        classification = "performance"
        feasibility = 8.5
        risk = 2.0
        business_impact = "Improves user experience and reduces churn"
    elif any(word in theme_lower for word in ["ui", "interface", "design", "dashboard"]):
        classification = "ux_improvement"
        feasibility = 7.0
        risk = 3.0
        business_impact = "Enhances user satisfaction and adoption"
    else:
        classification = "feature_request"
        feasibility = 6.5
        risk = 4.0
        business_impact = "Addresses customer needs and competitive gaps"
    
    # Generate verdicts based on metrics - use theme's impact score (not 0.0)
    impact_score = theme.overall_impact_score or 0.0
    # Note: If impact_score is 0.0, it will be recalculated when recommendations are created/updated
    # We don't recalculate here to avoid modifying the theme object unnecessarily
    
    pm_verdict = f"High priority feature with impact score of {impact_score:.1f}. {business_impact}. Requested by {feedback_count} customers."
    ux_verdict = f"Improves user experience for {feedback_count} users. Customer value score: {theme.customer_value:.1f}/10."
    engineering_verdict = f"Feasibility: {feasibility}/10. Risk: {risk}/10. Estimated effort: {'Low' if feasibility > 7 else 'Medium' if feasibility > 5 else 'High'}."
    data_scientist_verdict = f"Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: {theme.request_frequency}."
    
    unified_recommendation = f"Team consensus: {'Approve' if impact_score > 7 and feasibility > 6 else 'Consider'}. {business_impact} Recommended for roadmap."
    
    return {
        "title": f"Enhance {theme.name}",
        "description": theme.description or f"Address customer feedback related to {theme.name}. {feedback_count} customer requests.",
        "impact_score": impact_score,
        "feasibility_score": feasibility,
        "risk_score": risk,
        "business_impact": business_impact,
        "pm_verdict": pm_verdict,
        "ux_verdict": ux_verdict,
        "engineering_verdict": engineering_verdict,
        "data_scientist_verdict": data_scientist_verdict,
        "unified_recommendation": unified_recommendation,
        "ux_implications": f"Improves usability and user satisfaction for {theme.name} related features."
    }

@router.post("/generate-from-themes")
async def generate_recommendations_from_themes(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate recommendations from all existing themes - FAST (no LLM calls)"""
    try:
        # Get all themes
        themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).limit(15).all()
        
        if not themes:
            return {"status": "error", "message": "No themes found. Please generate feedback data first."}
        
        recommendations_created = []
        
        # Generate recommendations instantly (no LLM calls)
        for theme in themes:
            # Get feedback count for this theme
            feedback_count = db.query(Feedback).filter(Feedback.theme_id == theme.id).count()
            
            # Generate fast recommendation with updated impact score
            rec_data = generate_fast_recommendation(theme, feedback_count, db)
            
            # Check if recommendation already exists
            existing = db.query(Recommendation).filter(Recommendation.feature == theme.name).first()
            
            if existing:
                # Update existing - use theme's actual impact score
                existing.title = rec_data["title"]
                existing.description = rec_data["description"]
                existing.impact_score = theme.overall_impact_score or 0.0  # Use theme's impact score, not 0.0
                existing.feasibility_score = rec_data["feasibility_score"]
                existing.risk_score = rec_data["risk_score"]
                existing.business_impact = rec_data["business_impact"]
                existing.pm_verdict = rec_data["pm_verdict"]
                existing.ux_verdict = rec_data["ux_verdict"]
                existing.engineering_verdict = rec_data["engineering_verdict"]
                existing.data_scientist_verdict = rec_data["data_scientist_verdict"]
                existing.unified_recommendation = rec_data["unified_recommendation"]
                existing.ux_implications = rec_data["ux_implications"]
                db.commit()
                db.refresh(existing)
                recommendations_created.append({
                    "id": existing.id,
                    "title": existing.title,
                    "impact_score": existing.impact_score,
                    "status": existing.status
                })
            else:
                # Create new - use theme's actual impact score
                recommendation = Recommendation(
                    title=rec_data["title"],
                    description=rec_data["description"],
                    feature=theme.name,
                    impact_score=theme.overall_impact_score or 0.0,  # Use theme's impact score, not 0.0
                    feasibility_score=rec_data["feasibility_score"],
                    risk_score=rec_data["risk_score"],
                    business_impact=rec_data["business_impact"],
                    pm_verdict=rec_data["pm_verdict"],
                    ux_verdict=rec_data["ux_verdict"],
                    engineering_verdict=rec_data["engineering_verdict"],
                    data_scientist_verdict=rec_data["data_scientist_verdict"],
                    unified_recommendation=rec_data["unified_recommendation"],
                    ux_implications=rec_data["ux_implications"],
                    status="pending"
                )
                
                db.add(recommendation)
                db.commit()
                db.refresh(recommendation)
                
                recommendations_created.append({
                    "id": recommendation.id,
                    "title": recommendation.title,
                    "impact_score": recommendation.impact_score,
                    "status": recommendation.status
                })
        
        return {
            "status": "success",
            "recommendations_created": len(recommendations_created),
            "recommendations": recommendations_created
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

@router.patch("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update recommendation status (e.g., mark as shipped) and auto-notify customers"""
    try:
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        new_status = request_data.get("status")
        if new_status not in ["pending", "approved", "rejected", "in_progress", "shipped"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        old_status = recommendation.status
        recommendation.status = new_status
        
        # If marking as shipped, add shipped_at timestamp and auto-notify customers
        if new_status == "shipped" and old_status != "shipped":
            # Add shipped_at timestamp to extra_metadata
            # Use provided shipped_at date or current date
            if not recommendation.extra_metadata:
                recommendation.extra_metadata = {}
            
            # Allow specifying shipped_at date, or use current date
            shipped_at_date = request_data.get("shipped_at")
            if shipped_at_date:
                # Validate and use provided date
                try:
                    shipped_date = datetime.fromisoformat(shipped_at_date.replace('Z', '+00:00'))
                    recommendation.extra_metadata["shipped_at"] = shipped_date.isoformat()
                except:
                    recommendation.extra_metadata["shipped_at"] = datetime.now().isoformat()
            else:
                recommendation.extra_metadata["shipped_at"] = datetime.now().isoformat()
            
            # Auto-notify customers in background and create FeatureNotification records
            from core.customer_notifier import CustomerNotifier
            from core.database import FeatureNotification, Theme, Feedback
            
            def notify_customers_background():
                try:
                    # Create a new database session for background task
                    from core.database import SessionLocal
                    bg_db = SessionLocal()
                    try:
                        # Refresh recommendation in new session
                        bg_rec = bg_db.query(Recommendation).filter(Recommendation.id == recommendation.id).first()
                        if not bg_rec:
                            return
                        
                        notifier = CustomerNotifier()
                        customers = notifier.get_customers_to_notify(bg_rec, bg_db)
                        
                        # Create FeatureNotification records for each customer
                        for customer in customers:
                            # Check if notification already exists
                            existing = bg_db.query(FeatureNotification).filter(
                                FeatureNotification.feature_id == bg_rec.id,
                                FeatureNotification.customer_id == customer.get("account_id", "unknown")
                            ).first()
                            
                            if not existing:
                                notification = FeatureNotification(
                                    feature_id=bg_rec.id,
                                    customer_id=customer.get("account_id", "unknown"),
                                    notified_at=datetime.now(),
                                    adoption_tracked=False
                                )
                                bg_db.add(notification)
                        
                        bg_db.commit()
                        print(f"✅ Auto-notified {len(customers)} customers about shipped feature: {bg_rec.title}")
                    finally:
                        bg_db.close()
                except Exception as e:
                    print(f"⚠️ Error auto-notifying customers: {e}")
                    import traceback
                    traceback.print_exc()
            
            background_tasks.add_task(notify_customers_background)
        
        db.commit()
        db.refresh(recommendation)
        
        notification_count = 0
        if new_status == "shipped" and old_status != "shipped":
            # Count how many customers will be notified
            from core.customer_notifier import CustomerNotifier
            notifier = CustomerNotifier()
            customers = notifier.get_customers_to_notify(recommendation, db)
            notification_count = len(customers)
        
        return {
            "status": "success",
            "recommendation": {
                "id": recommendation.id,
                "title": recommendation.title,
                "status": recommendation.status
            },
            "customers_notified": notification_count if new_status == "shipped" else 0,
            "message": f"Feature marked as {new_status}. {notification_count} customers will be notified." if new_status == "shipped" else f"Feature status updated to {new_status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

