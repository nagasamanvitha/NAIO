from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db, Feedback, Theme, Recommendation
from core.mock_data import MockDataGenerator
from core.data_processor import DataProcessor
from core.roadmap_generator import RoadmapGenerator
from core.agents.competitor_agent import CompetitorAgent

router = APIRouter()
data_processor = DataProcessor()
roadmap_generator = RoadmapGenerator()
competitor_agent = CompetitorAgent()

@router.post("/full-demo")
async def run_full_demo(db: Session = Depends(get_db)):
    """Run a complete end-to-end demo of the system"""
    try:
        results = {
            "step1_data_generation": {},
            "step2_feedback_processing": {},
            "step3_theme_clustering": {},
            "step4_competitor_analysis": {},
            "step5_recommendations": {},
            "step6_roadmap": {}
        }
        
        # Step 1: Generate mock data
        print("Step 1: Generating mock data...")
        mock_data = MockDataGenerator.generate_all_mock_data()
        all_feedback = MockDataGenerator.get_all_feedback_flat()
        results["step1_data_generation"] = {
            "total_items": len(all_feedback),
            "by_source": {k: len(v) for k, v in mock_data.items()}
        }
        
        # Step 2: Process feedback
        print("Step 2: Processing feedback...")
        feedback_results = await data_processor.process_feedback_batch(all_feedback, db)
        results["step2_feedback_processing"] = feedback_results
        
        # Step 3: Get themes
        print("Step 3: Retrieving themes...")
        themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).limit(10).all()
        results["step3_theme_clustering"] = {
            "themes_count": len(themes),
            "top_themes": [
                {
                    "id": t.id,
                    "name": t.name,
                    "impact_score": t.overall_impact_score,
                    "request_frequency": t.request_frequency
                }
                for t in themes[:5]
            ]
        }
        
        # Step 4: Competitor analysis
        print("Step 4: Running competitor analysis...")
        competitor_results = await competitor_agent.analyze({
            "product_info": {
                "name": "Sample Product",
                "description": "A comprehensive business intelligence platform",
                "category": "SaaS"
            },
            "market_context": {}
        })
        results["step4_competitor_analysis"] = {
            "competitors_found": len(competitor_results.get("competitors", [])),
            "market_gaps": len(competitor_results.get("market_gaps", [])),
            "opportunities": len(competitor_results.get("opportunities", []))
        }
        
        # Step 5: Generate recommendations
        print("Step 5: Generating recommendations...")
        if themes:
            theme_data = [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "impact_score": t.overall_impact_score,
                    "customer_value": t.customer_value
                }
                for t in themes[:5]
            ]
            recommendations = await roadmap_generator.generate_recommendations(
                theme_data,
                competitor_results,
                db
            )
            results["step5_recommendations"] = {
                "recommendations_count": len(recommendations),
                "top_recommendations": [
                    {
                        "title": r.get("title"),
                        "impact_score": r.get("impact_score")
                    }
                    for r in recommendations[:3]
                ]
            }
        
        # Step 6: Generate roadmap
        print("Step 6: Generating roadmap...")
        if themes and recommendations:
            roadmap = await roadmap_generator.generate_quarterly_roadmap(
                "Q1",
                2024,
                recommendations,
                db
            )
            results["step6_roadmap"] = {
                "roadmap_id": roadmap.get("roadmap_id"),
                "quarter": roadmap.get("quarter"),
                "items_count": len(roadmap.get("items", []))
            }
        
        return {
            "status": "success",
            "message": "Full demo completed successfully!",
            "results": results,
            "summary": {
                "total_feedback": len(all_feedback),
                "themes_created": feedback_results.get("themes_created", 0),
                "recommendations": len(recommendations) if themes else 0,
                "roadmap_generated": "roadmap_id" in results["step6_roadmap"]
            }
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }








