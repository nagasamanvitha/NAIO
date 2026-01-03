from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import Competitor, get_db
from core.agents.competitor_agent import CompetitorAgent

router = APIRouter()
competitor_agent = CompetitorAgent()

@router.post("/analyze")
async def analyze_competitors(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Run competitor analysis"""
    try:
        product_info = request_data.get("product_info", {})
        market_context = request_data.get("market_context", {})
        
        results = await competitor_agent.analyze({
            "product_info": product_info,
            "market_context": market_context
        })
        
        # Save competitors to database
        for competitor_data in results.get("competitors", []):
            competitor = Competitor(
                name=competitor_data.get("name", ""),
                description=competitor_data.get("brief_description", ""),
                positioning=competitor_data.get("positioning", ""),
                strengths=competitor_data.get("strengths", []),
                weaknesses=competitor_data.get("weaknesses", []),
                website_url=competitor_data.get("website"),
                customer_reviews_sentiment=competitor_data.get("sentiment_score", 0),
                complaints=competitor_data.get("complaints", []),
                market_gaps=results.get("market_gaps", []),
                opportunities=results.get("opportunities", []),
                extra_metadata=competitor_data
            )
            db.add(competitor)
        
        db.commit()
        
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_competitors(db: Session = Depends(get_db)):
    """List all discovered competitors"""
    competitors = db.query(Competitor).order_by(Competitor.discovered_at.desc()).all()
    
    return {
        "competitors": [
            {
                "id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "positioning": comp.positioning,
                "strengths": comp.strengths,
                "weaknesses": comp.weaknesses,
                "sentiment_score": comp.customer_reviews_sentiment,
                "discovered_at": comp.discovered_at.isoformat() if comp.discovered_at else None
            }
            for comp in competitors
        ]
    }

@router.get("/{competitor_id}")
async def get_competitor(competitor_id: int, db: Session = Depends(get_db)):
    """Get detailed competitor information"""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return {
        "id": competitor.id,
        "name": competitor.name,
        "description": competitor.description,
        "positioning": competitor.positioning,
        "strengths": competitor.strengths,
        "weaknesses": competitor.weaknesses,
        "website_url": competitor.website_url,
        "pricing_info": competitor.pricing_info,
        "funding_info": competitor.funding_info,
        "customer_reviews_sentiment": competitor.customer_reviews_sentiment,
        "social_sentiment": competitor.social_sentiment,
        "product_updates": competitor.product_updates,
        "complaints": competitor.complaints,
        "market_gaps": competitor.market_gaps,
        "opportunities": competitor.opportunities,
        "discovered_at": competitor.discovered_at.isoformat() if competitor.discovered_at else None,
        "updated_at": competitor.updated_at.isoformat() if competitor.updated_at else None
    }

