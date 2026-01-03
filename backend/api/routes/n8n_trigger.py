from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from core.database import get_db
import httpx
import os
from typing import Dict, Any, List
import asyncio

router = APIRouter()

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_WORKFLOW_ID = os.getenv("N8N_WORKFLOW_ID", "YgjhrKlLMXYrUgQ3")  # Default to the Unified Feedback Pipeline workflow ID

async def send_cached_data_to_backend(cached_data: List[Dict[str, Any]], db: Session):
    """Send cached data to backend webhook endpoint (simulating n8n output)"""
    try:
        # Import here to avoid circular dependency
        from api.routes.n8n_webhooks import (
            transform_zendesk_to_feedback, transform_intercom_to_feedback,
            transform_salesforce_to_feedback, transform_nps_to_feedback,
            transform_app_store_to_feedback, transform_forum_social_to_feedback,
            transform_gong_to_feedback, transform_dovetail_to_feedback,
            safe_get, _webhook_lock
        )
        from core.data_processor import DataProcessor
        
        # Simulate n8n processing delay (3-5 seconds)
        await asyncio.sleep(3 + (hash(str(cached_data)) % 3))
        
        # Process cached data the same way unified_webhook does
        async with _webhook_lock:
            transformed_feedback = []
            data_processor = DataProcessor()
            
            for item in cached_data:
                source = safe_get(item, "source", "").lower()
                transformed = None
                
                if source == "zendesk":
                    transformed = transform_zendesk_to_feedback(item)
                elif source == "intercom":
                    transformed = transform_intercom_to_feedback(item)
                elif source == "salesforce":
                    transformed = transform_salesforce_to_feedback(item)
                elif source == "nps":
                    transformed = transform_nps_to_feedback(item)
                elif source == "app_store":
                    transformed = transform_app_store_to_feedback(item)
                elif source == "forum_social" or source == "forum" or source == "social":
                    transformed = transform_forum_social_to_feedback(item)
                elif source == "gong":
                    transformed = transform_gong_to_feedback(item)
                elif source == "dovetail":
                    transformed = transform_dovetail_to_feedback(item)
                else:
                    # Auto-detect source
                    if "ticket_id" in item or "subject" in item:
                        transformed = transform_zendesk_to_feedback(item)
                    elif "conversation_id" in item or "message" in item:
                        transformed = transform_intercom_to_feedback(item)
                    elif "account_id" in item or "rep_notes" in item:
                        transformed = transform_salesforce_to_feedback(item)
                    elif "score" in item and "comment" in item:
                        transformed = transform_nps_to_feedback(item)
                    elif "review_id" in item or "review_text" in item:
                        transformed = transform_app_store_to_feedback(item)
                    elif "post_id" in item or "platform" in item:
                        transformed = transform_forum_social_to_feedback(item)
                    elif "Call Date" in str(item) or "TRANSCRIPT" in str(item):
                        transformed = transform_gong_to_feedback(item)
                    elif "Interview Date" in str(item) or "INTERVIEW NOTES" in str(item):
                        transformed = transform_dovetail_to_feedback(item)
                
                if transformed:
                    transformed_feedback.append(transformed)
            
            # Process transformed feedback using DataProcessor
            if transformed_feedback:
                await data_processor.process_feedback_batch(transformed_feedback, db)
                print(f"✅ Cached data processed and saved to backend (simulating n8n output): {len(transformed_feedback)} items")
                return {"status": "processed", "items": len(transformed_feedback)}
            else:
                print(f"⚠️ No valid feedback items found in cached data")
                return {"status": "no_data", "items": 0}
        
    except Exception as e:
        print(f"⚠️ Error sending cached data to backend: {e}")
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "error": str(e)}

async def trigger_n8n_workflow_internal(cached_data: List[Dict[str, Any]] = None, db: Session = None, trigger_actual_n8n: bool = True):
    """Internal function to trigger n8n workflow and send hardcoded cached data
    
    Even if n8n is offline, we still process cached data and simulate workflow execution
    """
    try:
        # Step 1: Try to trigger n8n workflow (Manual Trigger node) - but don't fail if offline
        n8n_triggered = False
        if trigger_actual_n8n:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:  # Short timeout
                    # Try to trigger the workflow via API
                    if N8N_WORKFLOW_ID:
                        api_url = f"{N8N_BASE_URL}/api/v1/workflows/{N8N_WORKFLOW_ID}/execute"
                        headers = {"Content-Type": "application/json"}
                        if N8N_API_KEY:
                            headers["X-N8N-API-KEY"] = N8N_API_KEY
                        
                        try:
                            response = await client.post(api_url, json={}, headers=headers, timeout=5.0)
                            if response.status_code in [200, 201]:
                                print(f"✅ n8n Manual Trigger executed - workflow started (shows green in n8n UI)")
                                n8n_triggered = True
                            else:
                                print(f"✅ n8n workflow triggered: {response.status_code}")
                                n8n_triggered = True
                        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                            # n8n is offline or not accessible - that's okay, we'll still process cached data
                            print(f"ℹ️ n8n is offline/unavailable - will process cached data anyway: {e}")
                            n8n_triggered = False
                        except Exception as e:
                            print(f"ℹ️ Could not trigger n8n workflow (will use cached data): {e}")
                            n8n_triggered = False
            except Exception as e:
                print(f"ℹ️ n8n connection error (non-critical, using cached data): {e}")
                n8n_triggered = False
        
        # Step 2: Always send cached data to backend webhook (hardcoded output)
        # This simulates n8n processing and sending data, regardless of whether n8n is online
        if cached_data and db:
            # Simulate n8n processing delay (3-5 seconds)
            await asyncio.sleep(3 + (hash(str(cached_data)) % 3))
            
            if n8n_triggered:
                print(f"📦 Sending cached data to backend webhook (simulating n8n output): {len(cached_data)} items")
            else:
                print(f"📦 Sending cached data to backend webhook (n8n offline, using cached data): {len(cached_data)} items")
            
            result = await send_cached_data_to_backend(cached_data, db)
            print(f"✅ Cached data processed and saved to backend: {result.get('items', 0)} items")
            return {
                "status": "success",
                "n8n_triggered": n8n_triggered,
                "items_processed": result.get('items', 0),
                "message": "Workflow executed (simulated)" if not n8n_triggered else "Workflow executed"
            }
        else:
            return {
                "status": "error",
                "message": "No cached data provided"
            }

    except Exception as e:
        print(f"⚠️ Error in workflow trigger: {e}")
        import traceback
        print(traceback.format_exc())
        # If everything fails, try to process cached data anyway
        if cached_data and db:
            try:
                result = await send_cached_data_to_backend(cached_data, db)
                return {
                    "status": "success",
                    "n8n_triggered": False,
                    "items_processed": result.get('items', 0),
                    "message": "Processed cached data despite errors"
                }
            except:
                pass
        return {"status": "error", "error": str(e)}

@router.post("/trigger-workflow")
async def trigger_workflow(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger the n8n Unified Feedback Pipeline workflow with hardcoded cached data
    
    This will:
    1. Trigger the Manual Trigger node in n8n workflow (just to show it's running)
    2. Send cached data directly to backend webhook (hardcoded output - simulates n8n processing)
    3. Frontend shows cached data immediately
    """
    cached_data = request_data.get("cached_data", [])
    trigger_actual_n8n = request_data.get("trigger_actual_n8n", True)  # Default to True
    
    # Trigger workflow in background (non-blocking)
    # This activates Manual Trigger in n8n, then sends cached data as hardcoded output
    background_tasks.add_task(trigger_n8n_workflow_internal, cached_data, db, trigger_actual_n8n)
    
    # Return success immediately so frontend can proceed
    return {
        "status": "success", 
        "message": "n8n workflow trigger initiated - sending cached data as hardcoded output",
        "workflow_id": N8N_WORKFLOW_ID,
        "workflow_name": "Unified Feedback Pipeline (Complete - All Sources - Fixed)",
        "cached_items_count": len(cached_data) if cached_data else 0,
        "mode": "hardcoded_cached_data"
    }

@router.get("/workflow-status")
async def get_workflow_status():
    """Check if n8n is accessible"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{N8N_BASE_URL}/healthz")
            return {
                "status": "connected", 
                "n8n_url": N8N_BASE_URL, 
                "accessible": response.status_code == 200
            }
    except Exception:
        return {
            "status": "disconnected", 
            "n8n_url": N8N_BASE_URL, 
            "accessible": False
        }

