"""
Generate recommendations with FULL LLM-based persona agent deliberation
This creates recommendations with detailed debates, competitor data, lost deals, etc.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, Theme, Recommendation, Feedback, Competitor
from core.roadmap_generator import RoadmapGenerator
from typing import Dict, Any

router = APIRouter()
roadmap_generator = RoadmapGenerator()

@router.post("/clear-and-regenerate")
async def clear_and_regenerate_all_recommendations(
    db: Session = Depends(get_db)
):
    """Clear all recommendations and regenerate with FULL details"""
    try:
        # Delete all existing recommendations
        db.query(Recommendation).delete()
        db.commit()
        
        # Now generate new ones
        return await generate_full_recommendations_with_deliberation(db)
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

@router.post("/generate-full-recommendations")
async def generate_full_recommendations_with_deliberation(
    db: Session = Depends(get_db)
):
    """Generate recommendations with FULL LLM-based persona agent deliberation including competitor data, lost deals, and detailed debates"""
    try:
        # Get all themes sorted by impact score
        themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).limit(15).all()
        
        if not themes:
            return {"status": "error", "message": "No themes found. Please generate feedback data first."}
        
        # Get competitor insights
        competitors = db.query(Competitor).all()
        competitor_insights = {
            "competitors": [
                {
                    "name": c.name,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses,
                    "opportunities": c.opportunities
                }
                for c in competitors
            ],
            "market_gaps": [c.market_gaps for c in competitors if c.market_gaps],
            "opportunities": [c.opportunities for c in competitors if c.opportunities]
        }
        
        recommendations_created = []
        
        for idx, theme in enumerate(themes):
            print(f"Processing theme {idx+1}/{len(themes)}: {theme.name}")
            
            # Get feedback for this theme
            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
            
            # Prepare full theme data including extra_metadata
            theme_data_dict = {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "impact_score": theme.overall_impact_score,
                "customer_value": theme.customer_value,
                "request_frequency": theme.request_frequency,
                "feedback_count": len(theme_feedback),
                "extra_metadata": theme.extra_metadata or {}
            }
            
            # Create recommendation from theme (with LLM)
            recommendation_data = await roadmap_generator.create_recommendation_from_theme(
                theme_data_dict,
                competitor_insights,
                db
            )
            
            # Run FULL persona agent deliberation with competitor data, lost deals, etc.
            deliberation = await roadmap_generator.deliberation_system.deliberate(
                recommendation_data,
                {
                    "theme": theme_data_dict,
                    "competitor_insights": competitor_insights
                }
            )
            
            # Get data justification (includes strategic_rationale, customer_demand, prioritization_recommendation)
            from core.impact_scoring import ImpactScorer
            impact_scorer = ImpactScorer()
            data_justification = await impact_scorer.get_data_justification_for_theme(theme.id, db)
            
            # Check if recommendation already exists
            existing = db.query(Recommendation).filter(Recommendation.feature == theme.name).first()
            
            if existing:
                # Update existing with full deliberation
                existing.title = recommendation_data.get("title", f"Enhance {theme.name}")
                existing.description = recommendation_data.get("description", theme.description)
                existing.impact_score = theme.overall_impact_score  # Use theme's impact score
                existing.feasibility_score = deliberation["evaluations"]["engineering"].get("feasibility_score", 5.0)
                existing.risk_score = deliberation["evaluations"]["engineering"].get("risk_score", 5.0)
                existing.ux_implications = deliberation["evaluations"]["ux"].get("ux_implications", "")
                existing.business_impact = deliberation["evaluations"]["pm"].get("business_impact", "")
                existing.pm_verdict = deliberation["evaluations"]["pm"].get("reasoning", "")
                existing.ux_verdict = deliberation["evaluations"]["ux"].get("reasoning", "")
                existing.data_scientist_verdict = deliberation["evaluations"]["data_scientist"].get("reasoning", "")
                existing.engineering_verdict = deliberation["evaluations"]["engineering"].get("reasoning", "")
                existing.unified_recommendation = deliberation["unified_recommendation"].get("unified_reasoning", "")
                existing.customer_quotes = await roadmap_generator.extract_customer_quotes(theme.id, db)
                existing.evidence = {
                    **deliberation,  # Includes evaluations, unified_recommendation with team_discussion, key_debate_points, action_items
                    "data_justification": data_justification  # Includes strategic_rationale, customer_demand, prioritization_recommendation
                }
                db.commit()
                db.refresh(existing)
                recommendations_created.append({
                    "id": existing.id,
                    "title": existing.title,
                    "impact_score": existing.impact_score,
                    "status": existing.status
                })
            else:
                # Create new with full deliberation
                recommendation = Recommendation(
                    title=recommendation_data.get("title", f"Enhance {theme.name}"),
                    description=recommendation_data.get("description", theme.description),
                    feature=theme.name,
                    impact_score=theme.overall_impact_score,  # Use theme's impact score
                    feasibility_score=deliberation["evaluations"]["engineering"].get("feasibility_score", 5.0),
                    risk_score=deliberation["evaluations"]["engineering"].get("risk_score", 5.0),
                    ux_implications=deliberation["evaluations"]["ux"].get("ux_implications", ""),
                    business_impact=deliberation["evaluations"]["pm"].get("business_impact", ""),
                    pm_verdict=deliberation["evaluations"]["pm"].get("reasoning", ""),
                    ux_verdict=deliberation["evaluations"]["ux"].get("reasoning", ""),
                    data_scientist_verdict=deliberation["evaluations"]["data_scientist"].get("reasoning", ""),
                    engineering_verdict=deliberation["evaluations"]["engineering"].get("reasoning", ""),
                    unified_recommendation=deliberation["unified_recommendation"].get("unified_reasoning", ""),
                    customer_quotes=await roadmap_generator.extract_customer_quotes(theme.id, db),
                    evidence={
                        **deliberation,  # Includes evaluations, unified_recommendation with team_discussion, key_debate_points, action_items
                        "data_justification": data_justification  # Includes strategic_rationale, customer_demand, prioritization_recommendation
                    },
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
            "recommendations": recommendations_created,
            "message": "Recommendations generated with FULL LLM-based persona agent deliberation including competitor data, lost deals, and detailed debates"
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

