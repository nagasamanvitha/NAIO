from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import Recommendation, Roadmap, Theme, Feedback, get_db
from core.roadmap_generator import RoadmapGenerator
from core.websocket_manager import ConnectionManager
from datetime import datetime
import json

router = APIRouter()
roadmap_generator = RoadmapGenerator()
manager = ConnectionManager()

def generate_fast_roadmap(quarter: str, year: int, db: Session) -> Dict[str, Any]:
    """Generate roadmap FAST without LLM calls"""
    # Get top themes by impact
    themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).limit(10).all()
    
    if not themes:
        return {
            "roadmap_id": None,
            "quarter": quarter,
            "year": year,
            "items": [],
            "summary": f"No themes found in database. Run n8n workflow to generate themes first.",
            "debate_process": {
                "themes_analyzed": 0,
                "recommendations_created": 0,
                "top_candidates_debated": 0,
                "final_selected": 0,
                "final_debate_summary": "No themes available - please run n8n workflow to generate themes"
            },
            "error": "No themes found"
        }
    
    roadmap_items = []
    
    for idx, theme in enumerate(themes):
        # Get feedback count
        feedback_count = db.query(Feedback).filter(Feedback.theme_id == theme.id).count()
        
        # Check if recommendation exists
        existing_rec = db.query(Recommendation).filter(Recommendation.feature == theme.name).first()
        
        if not existing_rec:
            # Create fast recommendation
            from api.routes.recommendations import generate_fast_recommendation
            rec_data = generate_fast_recommendation(theme, feedback_count)
            
            recommendation = Recommendation(
                title=rec_data["title"],
                description=rec_data["description"],
                feature=theme.name,
                impact_score=rec_data["impact_score"],
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
            existing_rec = recommendation
        
        # Theme is already available from the loop
        
        # Get feedback items for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        total_requests = len(feedback_items)
        total_arr = sum([f.arr for f in feedback_items if f.arr and f.arr > 0])
        avg_arr = total_arr / len([f for f in feedback_items if f.arr and f.arr > 0]) if len([f for f in feedback_items if f.arr and f.arr > 0]) > 0 else 0
        
        # Get lost deal info
        lost_deal_info = {}
        if theme and theme.extra_metadata and theme.extra_metadata.get("lost_deal_info"):
            lost_deal_info = theme.extra_metadata["lost_deal_info"]
        
        # Get customer quotes
        customer_quotes = []
        if existing_rec.customer_quotes:
            if isinstance(existing_rec.customer_quotes, list):
                customer_quotes = existing_rec.customer_quotes[:5]
            else:
                customer_quotes = [existing_rec.customer_quotes]
        
        # Determine which teams benefit
        teams_benefit = []
        if lost_deal_info.get("lost_deal_count", 0) > 0:
            teams_benefit.append("Sales")
        if total_requests > 10:
            teams_benefit.append("Customer Success")
        if existing_rec.feasibility_score and existing_rec.feasibility_score > 7:
            teams_benefit.append("Engineering")
        if not teams_benefit:
            teams_benefit = ["Product", "All Teams"]
        
        # Risk of not doing it
        risk_level = "high"
        risk_reasons = []
        if lost_deal_info.get("lost_deal_count", 0) > 0:
            risk_level = "critical"
            risk_reasons.append(f"{lost_deal_info.get('lost_deal_count', 0)} lost deals (${lost_deal_info.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk)")
        elif lost_deal_info.get("competitor_mentions"):
            risk_level = "high"
            risk_reasons.append(f"Competitive pressure from {', '.join(lost_deal_info.get('competitor_mentions', [])[:2])}")
        elif total_requests > 20:
            risk_level = "high"
            risk_reasons.append(f"High demand ({total_requests} requests)")
        else:
            risk_level = "medium"
            risk_reasons.append("Moderate customer demand")
        
        # Estimated timeline
        if existing_rec.feasibility_score:
            if existing_rec.feasibility_score >= 8:
                estimated_weeks = "6-8 weeks"
            elif existing_rec.feasibility_score >= 6:
                estimated_weeks = "8-12 weeks"
            else:
                estimated_weeks = "12+ weeks"
        else:
            estimated_weeks = "8-10 weeks"
        
        # Generate why this matters now
        why_matters = []
        if lost_deal_info.get("lost_deal_count", 0) > 0:
            why_matters.append(f"🚨 {lost_deal_info.get('lost_deal_count', 0)} lost deals (${lost_deal_info.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk)")
        if total_requests > 0:
            why_matters.append(f"📊 {total_requests} customer requests")
        if lost_deal_info.get("competitor_mentions"):
            why_matters.append(f"⚔️ Competitive pressure from {', '.join(lost_deal_info.get('competitor_mentions', [])[:2])}")
        if avg_arr > 50000:
            why_matters.append(f"💰 High-value customers affected (${avg_arr/1000:.0f}K avg ARR)")
        if theme and theme.customer_value and theme.customer_value > 7:
            why_matters.append(f"😰 High pain score ({theme.customer_value:.1f}/10)")
        if not why_matters:
            why_matters.append("📈 Growing customer demand")
        
        # Generate alternatives considered
        alternatives = []
        if existing_rec.evidence and isinstance(existing_rec.evidence, dict):
            evaluations = existing_rec.evidence.get("evaluations", {})
            engineering = evaluations.get("engineering", {})
            if engineering.get("alternatives"):
                alternatives.extend(engineering.get("alternatives", []))
        if not alternatives:
            alternatives = [
                "Do nothing (not recommended - high risk)",
                "Partial implementation (may not address core need)",
                "Third-party integration (evaluation needed)"
            ]
        
        # Include existing evidence/deliberation data if available (for full AI roadmap display)
        evidence_data = None
        if existing_rec.evidence and isinstance(existing_rec.evidence, dict):
            evidence_data = existing_rec.evidence
        
        roadmap_item = {
            "id": existing_rec.id,
            "title": existing_rec.title,
            "feature": existing_rec.feature,
            "summary": existing_rec.description[:200] + "..." if len(existing_rec.description) > 200 else existing_rec.description,
            "why_this_matters_now": " | ".join(why_matters),
            "top_customer_quotes": customer_quotes,
            "arr_impact_potential": {
                "total_arr_requested": round(total_arr, 2),
                "avg_customer_arr": round(avg_arr, 2),
                "lost_deal_arr": round(lost_deal_info.get("lost_deal_arr", 0), 2),
                "customers_affected": total_requests
            },
            "teams_benefit": teams_benefit,
            "risk_of_not_doing_it": {
                "level": risk_level,
                "reasons": risk_reasons,
                "impact": f"${lost_deal_info.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk" if lost_deal_info.get("lost_deal_arr", 0) > 0 else "Customer satisfaction impact"
            },
            "estimated_timeline": {
                "quarter": quarter,
                "weeks": estimated_weeks,
                "feasibility_score": existing_rec.feasibility_score or 0
            },
            "alternatives_considered": alternatives[:3],
            "impact_score": existing_rec.impact_score,
            "feasibility_score": existing_rec.feasibility_score,
            "risk_score": existing_rec.risk_score,
            "consensus_score": 8.0,
            "final_ranking": idx + 1,
            "priority": "P0" if risk_level == "critical" else "P1" if risk_level == "high" else "P2",
            "status": existing_rec.status
        }
        
        # Include full evidence/deliberation data if available (for detailed AI roadmap view)
        if evidence_data:
            roadmap_item["evidence"] = evidence_data
            roadmap_item["persona_debate"] = evidence_data.get("evaluations", {})
            roadmap_item["unified_recommendation"] = evidence_data.get("unified_recommendation", {})
            roadmap_item["data_justification"] = evidence_data.get("data_justification", {})
            # Calculate consensus score from evidence if available
            if evidence_data.get("unified_recommendation", {}).get("confidence"):
                roadmap_item["consensus_score"] = evidence_data["unified_recommendation"]["confidence"]
        
        roadmap_items.append(roadmap_item)
    
    # Create roadmap
    roadmap = Roadmap(
        quarter=quarter,
        year=year,
        items=[item["id"] for item in roadmap_items],
        extra_metadata={
            "total_themes_considered": len(themes),
            "top_candidates_evaluated": len(themes),
            "final_selected": len(roadmap_items),
            "debate_summary": "Fast generation: Selected top themes by impact score",
            "consensus_reasoning": "Top features selected based on impact scores and customer demand"
        }
    )
    
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    
    return {
        "roadmap_id": roadmap.id,
        "quarter": quarter,
        "year": year,
        "items": roadmap_items,
        "summary": f"Q{quarter[-1]} {year} Roadmap: {len(roadmap_items)} high-impact features selected based on customer feedback and impact scores.",
        "debate_process": {
            "themes_analyzed": len(themes),
            "recommendations_created": len(roadmap_items),
            "top_candidates_debated": len(themes),
            "final_selected": len(roadmap_items),
            "final_debate_summary": "Fast generation completed - top features by impact"
        }
    }

@router.post("/generate")
async def generate_roadmap(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a quarterly roadmap - Uses existing recommendations when available (fast) or generates new ones (slower)"""
    try:
        quarter = request_data.get("quarter", "Q1")
        year = request_data.get("year", datetime.now().year)
        use_fast = request_data.get("fast", True)  # Default to fast (uses existing data)
        
        if use_fast:
            # Fast generation using existing recommendations (under 1 second if data exists)
            roadmap = generate_fast_roadmap(quarter, year, db)
            return {"status": "success", "roadmap": roadmap}
        else:
            # Slow LLM-based generation (for when you need full deliberation)
            async def send_progress(step: str, message: str, data: Any = None):
                progress = {
                    "step": step,
                    "message": message,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast(json.dumps({
                    "type": "roadmap_progress",
                    **progress
                }))
            
            await send_progress("start", "Starting roadmap generation...")
            roadmap = await roadmap_generator.generate_roadmap_from_all_data(
                quarter, 
                year, 
                db,
                progress_callback=send_progress
            )
            await send_progress("complete", "Roadmap generation complete!", {"roadmap_id": roadmap.get("roadmap_id")})
            return {"status": "success", "roadmap": roadmap}
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        await manager.broadcast(json.dumps({
            "type": "roadmap_error",
            "error": str(e)
        }))
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/generate-from-data")
async def generate_roadmap_from_data(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Generate roadmap from provided themes and competitor insights (legacy method)"""
    try:
        quarter = request_data.get("quarter", "Q1")
        year = request_data.get("year", datetime.now().year)
        themes = request_data.get("themes", [])
        competitor_insights = request_data.get("competitor_insights", {})
        
        # Generate recommendations from themes
        recommendations = await roadmap_generator.generate_recommendations(
            themes,
            competitor_insights,
            db
        )
        
        # Generate roadmap
        roadmap = await roadmap_generator.generate_quarterly_roadmap(
            quarter,
            year,
            recommendations,
            db
        )
        
        return {"status": "success", "roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/one-pager/{recommendation_id}")
async def get_one_pager(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive one-pager for a recommendation with all stakeholder data"""
    try:
        one_pager = await roadmap_generator.generate_one_pager(recommendation_id, db)
        if not one_pager:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        return {"status": "success", "one_pager": one_pager}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
