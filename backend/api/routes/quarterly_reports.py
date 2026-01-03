from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from core.database import get_db
from core.quarterly_report_generator import QuarterlyReportGenerator
from datetime import datetime

router = APIRouter()
report_generator = QuarterlyReportGenerator()

@router.get("/{quarter}/{year}")
async def get_quarterly_report(
    quarter: str,
    year: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive quarterly report for a specific quarter
    
    Quarter format: Q1, Q2, Q3, or Q4
    Year: 2024, 2025, etc.
    
    Returns:
    - Executive Summary
    - Feedback Summary for the Quarter
    - Top Themes of the Quarter
    - Top Feature Requests This Quarter
    - Roadmap Recommendation for Next Quarter
    - Customer Quote Digest (This Quarter)
    - Deal Impact (This Quarter)
    - Shipped Feature Impact (This Quarter)
    - "New This Quarter" Highlights
    """
    try:
        if quarter not in ['Q1', 'Q2', 'Q3', 'Q4']:
            raise HTTPException(status_code=400, detail="Quarter must be Q1, Q2, Q3, or Q4")
        
        if year < 2020 or year > 2100:
            raise HTTPException(status_code=400, detail="Year must be between 2020 and 2100")
        
        report = await report_generator.generate_quarterly_report(quarter, year, db)
        return {"status": "success", "report": report}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quarterly report: {str(e)}")

@router.get("/")
async def list_available_quarters(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List all available quarters with data"""
    from core.database import Feedback
    
    # Get all feedback to determine available quarters
    all_feedback = db.query(Feedback).order_by(Feedback.created_at).all()
    
    if not all_feedback:
        return {
            "status": "success",
            "available_quarters": [],
            "message": "No feedback data available. Run n8n workflow to generate data."
        }
    
    # Group by quarter
    quarters = {}
    for feedback in all_feedback:
        if not feedback.created_at:
            continue
        
        year = feedback.created_at.year
        month = feedback.created_at.month
        
        if month <= 3:
            quarter = 'Q1'
        elif month <= 6:
            quarter = 'Q2'
        elif month <= 9:
            quarter = 'Q3'
        else:
            quarter = 'Q4'
        
        key = f"{quarter}_{year}"
        if key not in quarters:
            quarters[key] = {
                "quarter": quarter,
                "year": year,
                "feedback_count": 0
            }
        quarters[key]["feedback_count"] += 1
    
    available_quarters = sorted(
        [q for q in quarters.values()],
        key=lambda x: (x["year"], x["quarter"]),
        reverse=True
    )
    
    return {
        "status": "success",
        "available_quarters": available_quarters,
        "total_quarters": len(available_quarters)
    }

@router.get("/current")
async def get_current_quarter_report(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get quarterly report for the current quarter"""
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month <= 3:
        quarter = 'Q1'
    elif month <= 6:
        quarter = 'Q2'
    elif month <= 9:
        quarter = 'Q3'
    else:
        quarter = 'Q4'
    
    return await get_quarterly_report(quarter, year, db)




