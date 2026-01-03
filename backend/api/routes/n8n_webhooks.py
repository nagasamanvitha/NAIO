from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from core.database import get_db
from core.data_processor import DataProcessor
from datetime import datetime
import re
import asyncio

router = APIRouter()
data_processor = DataProcessor()

# Global lock to prevent concurrent webhook processing
# This prevents multiple simultaneous webhook calls from overwhelming file descriptors
_webhook_lock = asyncio.Lock()

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dict"""
    try:
        return data.get(key, default)
    except:
        return default

def transform_zendesk_to_feedback(zendesk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Zendesk ticket to feedback format"""
    try:
        content = safe_get(zendesk_data, "description") or safe_get(zendesk_data, "subject") or ""
        if not content or not content.strip():
            return None
        
        return {
            "source": "zendesk",
            "source_id": str(safe_get(zendesk_data, "ticket_id") or safe_get(zendesk_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(zendesk_data, "created_at"),
            "extra_metadata": {
                "subject": safe_get(zendesk_data, "subject"),
                "status": safe_get(zendesk_data, "status"),
                "priority": safe_get(zendesk_data, "priority"),
                "customer_id": safe_get(zendesk_data, "customer_id")
            }
        }
    except Exception as e:
        print(f"Error transforming Zendesk data: {e}")
        return None

def transform_intercom_to_feedback(intercom_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Intercom conversation to feedback format"""
    try:
        content = safe_get(intercom_data, "message") or safe_get(intercom_data, "content") or ""
        if not content or not content.strip():
            return None
        
        return {
            "source": "intercom",
            "source_id": str(safe_get(intercom_data, "conversation_id") or safe_get(intercom_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(intercom_data, "created_at"),
            "extra_metadata": {
                "user_id": safe_get(intercom_data, "user_id"),
                "channel": safe_get(intercom_data, "channel"),
                "priority": safe_get(intercom_data, "priority")
            }
        }
    except Exception as e:
        print(f"Error transforming Intercom data: {e}")
        return None

def transform_salesforce_to_feedback(salesforce_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Salesforce deal/note to feedback format"""
    try:
        content = safe_get(salesforce_data, "rep_notes") or safe_get(salesforce_data, "notes") or ""
        if not content or not content.strip():
            return None
        
        # Extract ARR from deal_value or arr field
        arr = safe_get(salesforce_data, "arr") or safe_get(salesforce_data, "deal_value") or 0
        try:
            arr = float(arr) if arr else 0
        except:
            arr = 0
        
        return {
            "source": "salesforce",
            "source_id": str(safe_get(salesforce_data, "account_id") or safe_get(salesforce_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(salesforce_data, "created_at"),
            "arr": arr,
            "extra_metadata": {
                "deal_value": safe_get(salesforce_data, "deal_value"),
                "stage": safe_get(salesforce_data, "stage"),
                "lost_reason": safe_get(salesforce_data, "lost_reason"),
                "account_id": safe_get(salesforce_data, "account_id")
            }
        }
    except Exception as e:
        print(f"Error transforming Salesforce data: {e}")
        return None

def transform_nps_to_feedback(nps_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform NPS survey response to feedback format"""
    try:
        content = safe_get(nps_data, "comment") or safe_get(nps_data, "feedback") or ""
        if not content or not content.strip():
            return None
        
        return {
            "source": "nps",
            "source_id": str(safe_get(nps_data, "user_id") or safe_get(nps_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(nps_data, "timestamp") or safe_get(nps_data, "created_at"),
            "extra_metadata": {
                "score": safe_get(nps_data, "score"),
                "segment": safe_get(nps_data, "segment"),
                "user_id": safe_get(nps_data, "user_id")
            }
        }
    except Exception as e:
        print(f"Error transforming NPS data: {e}")
        return None

def transform_app_store_to_feedback(app_store_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform App Store review to feedback format"""
    try:
        content = safe_get(app_store_data, "review_text") or safe_get(app_store_data, "review") or ""
        if not content or not content.strip():
            return None
        
        return {
            "source": "app_store",
            "source_id": str(safe_get(app_store_data, "review_id") or safe_get(app_store_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(app_store_data, "date") or safe_get(app_store_data, "created_at"),
            "extra_metadata": {
                "rating": safe_get(app_store_data, "rating"),
                "user_name": safe_get(app_store_data, "user_name"),
                "version": safe_get(app_store_data, "version")
            }
        }
    except Exception as e:
        print(f"Error transforming App Store data: {e}")
        return None

def transform_forum_social_to_feedback(forum_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Forum/Social media post to feedback format"""
    try:
        content = safe_get(forum_data, "content") or safe_get(forum_data, "post") or safe_get(forum_data, "text") or ""
        
        if not content or not content.strip():
            return None  # Skip if no content
        
        return {
            "source": "forum_social",
            "source_id": str(safe_get(forum_data, "post_id") or safe_get(forum_data, "id") or ""),
            "content": content.strip(),
            "created_at": safe_get(forum_data, "created_at") or safe_get(forum_data, "date"),
            "extra_metadata": {
                "platform": safe_get(forum_data, "platform"),
                "author": safe_get(forum_data, "author"),
                "engagement": safe_get(forum_data, "engagement")
            }
        }
    except Exception as e:
        print(f"Error transforming Forum/Social data: {e}")
        return None

def transform_gong_to_feedback(gong_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Gong call transcript to feedback format"""
    try:
        # Gong data can come as text or structured
        if isinstance(gong_data, str):
            # Parse text format
            text = gong_data
        else:
            text = safe_get(gong_data, "transcript") or safe_get(gong_data, "content") or safe_get(gong_data, "text") or ""
        
        if not text or not text.strip():
            return None
        
        # Extract date from text if present
        date_match = re.search(r'Call Date:\s*(\d{4}-\d{2}-\d{2})', text)
        call_date = date_match.group(1) if date_match else None
        
        # Extract customer/account info
        customer_match = re.search(r'Customer:\s*([^\n]+)', text)
        customer = customer_match.group(1).strip() if customer_match else None
        
        # Extract deal value
        deal_value_match = re.search(r'Deal Value:\s*\$?([\d,]+)', text)
        deal_value = deal_value_match.group(1).replace(',', '') if deal_value_match else None
        arr = float(deal_value) if deal_value else 0
        
        # Extract key insights section
        insights_match = re.search(r'KEY INSIGHTS:\s*\n(.*?)(?=\n\n|\Z)', text, re.DOTALL)
        insights = insights_match.group(1).strip() if insights_match else ""
        
        # Combine transcript and insights for content
        content = text.strip()
        
        return {
            "source": "gong",
            "source_id": str(safe_get(gong_data, "call_id") or safe_get(gong_data, "id") or f"gong_{datetime.now().timestamp()}"),
            "content": content,
            "created_at": call_date or safe_get(gong_data, "created_at") or safe_get(gong_data, "call_date"),
            "arr": arr,
            "extra_metadata": {
                "customer": customer,
                "deal_value": deal_value,
                "insights": insights,
                "duration": safe_get(gong_data, "duration"),
                "rep": safe_get(gong_data, "rep")
            }
        }
    except Exception as e:
        print(f"Error transforming Gong data: {e}")
        return None

def transform_dovetail_to_feedback(dovetail_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform Dovetail interview to feedback format"""
    try:
        # Dovetail data can come as text or structured
        if isinstance(dovetail_data, str):
            text = dovetail_data
        else:
            text = safe_get(dovetail_data, "interview_notes") or safe_get(dovetail_data, "content") or safe_get(dovetail_data, "text") or ""
        
        if not text or not text.strip():
            return None
        
        # Extract date from text if present
        date_match = re.search(r'Interview Date:\s*(\d{4}-\d{2}-\d{2})', text)
        interview_date = date_match.group(1) if date_match else None
        
        # Extract user/account info
        user_match = re.search(r'User:\s*([^\n]+)', text)
        user = user_match.group(1).strip() if user_match else None
        
        # Extract pain level
        pain_match = re.search(r'PAIN LEVEL:\s*(\d+)/10', text)
        pain_level = float(pain_match.group(1)) if pain_match else None
        
        # Extract urgency
        urgency_match = re.search(r'URGENCY:\s*(\w+)', text)
        urgency = urgency_match.group(1).lower() if urgency_match else "medium"
        
        # Extract key insights
        insights_match = re.search(r'KEY INSIGHTS:\s*\n(.*?)(?=\n\nPAIN|URGENCY|\Z)', text, re.DOTALL)
        insights = insights_match.group(1).strip() if insights_match else ""
        
        # Combine interview notes and insights for content
        content = text.strip()
        
        return {
            "source": "dovetail",
            "source_id": str(safe_get(dovetail_data, "interview_id") or safe_get(dovetail_data, "id") or f"dovetail_{datetime.now().timestamp()}"),
            "content": content,
            "created_at": interview_date or safe_get(dovetail_data, "created_at") or safe_get(dovetail_data, "interview_date"),
            "pain_level": pain_level,
            "urgency": urgency,
            "extra_metadata": {
                "user": user,
                "user_persona": safe_get(dovetail_data, "user_persona"),
                "segment": safe_get(dovetail_data, "segment"),
                "tags": safe_get(dovetail_data, "tags"),
                "insights": insights
            }
        }
    except Exception as e:
        print(f"Error transforming Dovetail data: {e}")
        return None

@router.post("/webhook/unified")
async def unified_webhook(
    data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Unified webhook endpoint that processes feedback from all sources"""
    # Use lock to prevent concurrent processing (prevents file descriptor overflow)
    async with _webhook_lock:
        try:
            transformed_feedback = []
            
            for item in data:
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
                    # Try to auto-detect source from data structure
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
            
            # Process all transformed feedback
            if transformed_feedback:
                results = await data_processor.process_feedback_batch(transformed_feedback, db)
                return {
                    "status": "success",
                    "processed": len(transformed_feedback),
                    "total_received": len(data),
                    **results
                }
            else:
                return {
                    "status": "success",
                    "processed": 0,
                    "total_received": len(data),
                    "message": "No valid feedback items found"
                }
        
        except Exception as e:
            print(f"Error in unified webhook: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
