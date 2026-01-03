from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from core.database import get_db
from core.data_processor import DataProcessor
from core.websocket_manager import ConnectionManager
import json

router = APIRouter()
data_processor = DataProcessor()
manager = ConnectionManager()

@router.post("/analyze")
async def analyze_with_agents(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run analysis with all agents"""
    try:
        product_info = request_data.get("product_info", {})
        feedback_data = request_data.get("feedback_data", [])
        social_data = request_data.get("social_data", [])
        documents = request_data.get("documents", [])
        
        # Run full analysis
        results = await data_processor.run_full_analysis(
            product_info,
            feedback_data,
            social_data,
            documents,
            db
        )
        
        # Notify via WebSocket
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "results": results
        }))
        
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agent_status():
    """Get status of all agents"""
    return {
        "market_agent": "active",
        "social_agent": "active",
        "competitor_agent": "active",
        "persona_agents": "active"
    }








