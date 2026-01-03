from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.mock_data import MockDataGenerator
from core.data_processor import DataProcessor

router = APIRouter()
data_processor = DataProcessor()

@router.post("/generate")
async def generate_mock_data(db: Session = Depends(get_db)):
    """Generate and process comprehensive mock data from all sources"""
    try:
        # Generate all mock data
        mock_data = MockDataGenerator.generate_all_mock_data()
        
        # Get all feedback as flat list
        all_feedback = MockDataGenerator.get_all_feedback_flat()
        
        # Process feedback through the pipeline
        results = await data_processor.process_feedback_batch(all_feedback, db)
        
        return {
            "status": "success",
            "generated": {
                "app_store_reviews": len(mock_data["app_store_reviews"]),
                "support_tickets": len(mock_data["support_tickets"]),
                "sales_notes": len(mock_data["sales_notes"]),
                "user_interviews": len(mock_data["user_interviews"]),
                "social_media": len(mock_data["social_media"]),
                "nps_feedback": len(mock_data["nps_feedback"]),
                "crm_feedback": len(mock_data["crm_feedback"]),
                "in_app_feedback": len(mock_data["in_app_feedback"]),
                "forum_posts": len(mock_data["forum_posts"]),
                "total": len(all_feedback)
            },
            "processed": results,
            "summary": {
                "total_feedback_items": len(all_feedback),
                "themes_created": results.get("themes_created", 0),
                "feedback_processed": results.get("processed_count", 0)
            }
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/preview")
async def preview_mock_data():
    """Preview mock data without saving to database"""
    try:
        mock_data = MockDataGenerator.generate_all_mock_data()
        
        # Return sample from each source
        preview = {}
        for source_type, items in mock_data.items():
            preview[source_type] = items[:3] if len(items) >= 3 else items
        
        return {
            "status": "success",
            "preview": preview,
            "counts": {k: len(v) for k, v in mock_data.items()}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

