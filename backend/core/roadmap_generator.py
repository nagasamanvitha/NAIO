from typing import Dict, List, Any
from core.agents.persona_agents import PersonaDeliberationSystem
from core.impact_scoring import ImpactScorer
from core.database import Recommendation, Roadmap, Theme, Feedback
from core.one_pager_generator import OnePagerGenerator
from sqlalchemy.orm import Session
from datetime import datetime
import json

class RoadmapGenerator:
    """Generate quarterly roadmaps with persona agent deliberation"""
    
    def __init__(self):
        self.deliberation_system = PersonaDeliberationSystem()
        self.impact_scorer = ImpactScorer()
        self.one_pager_generator = OnePagerGenerator()
    
    async def generate_roadmap_from_all_data(
        self,
        quarter: str,
        year: int,
        db: Session,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Generate roadmap based on ALL feedback, themes, and impact scores"""
        
        async def send_progress(step: str, message: str, data: Any = None):
            if progress_callback:
                await progress_callback(step, message, data)
            print(f"[{step}] {message}")
        
        # Step 1: Get all themes sorted by impact score
        await send_progress("gathering", "Gathering all themes by impact score...")
        themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).all()
        await send_progress("gathering", f"Found {len(themes)} themes", {"count": len(themes)})
        
        if not themes:
            return {"error": "No themes found. Please generate feedback data first."}
        
        # Step 2: Get top features based on impact scoring
        await send_progress("analyzing", f"Analyzing top themes from {len(themes)} total...")
        top_themes = themes[:15]  # Top 15 by impact
        await send_progress("analyzing", f"Selected top {len(top_themes)} themes", {"count": len(top_themes)})
        
        # Step 3: Get competitor insights
        await send_progress("competitors", "Gathering competitor insights...")
        from core.database import Competitor
        competitors = db.query(Competitor).all()
        await send_progress("competitors", f"Found {len(competitors)} competitors", {"count": len(competitors)})
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
        
        # Step 4: Create recommendations from top themes (FAST: Use existing recommendations when available)
        await send_progress("recommendations", f"Creating recommendations from {len(top_themes)} themes...", {"total": len(top_themes)})
        recommendations = []
        
        # First, check for existing recommendations to avoid LLM calls
        existing_recommendations = {}
        for theme in top_themes:
            existing_rec = db.query(Recommendation).filter(Recommendation.feature == theme.name).first()
            if existing_rec:
                existing_recommendations[theme.id] = existing_rec
        
        await send_progress("recommendations", f"Found {len(existing_recommendations)} existing recommendations, creating {len(top_themes) - len(existing_recommendations)} new ones...")
        
        for idx, theme in enumerate(top_themes):
            await send_progress("recommendations", f"Processing {idx+1}/{len(top_themes)}: {theme.name}", {
                "current": idx + 1,
                "total": len(top_themes),
                "theme": theme.name
            })
            # Get feedback for this theme
            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
            
            # Prepare full theme data including extra_metadata for deliberation
            theme_data_dict = {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "impact_score": theme.overall_impact_score,
                "customer_value": theme.customer_value,
                "request_frequency": theme.request_frequency,
                "feedback_count": len(theme_feedback),
                "extra_metadata": theme.extra_metadata or {}  # Include lost_deal_info, etc.
            }
            
            # Use existing recommendation if available (FAST PATH - no LLM call)
            if theme.id in existing_recommendations:
                existing_rec = existing_recommendations[theme.id]
                recommendation_data = {
                    "id": existing_rec.id,
                    "title": existing_rec.title,
                    "description": existing_rec.description,
                    "feature": existing_rec.feature,
                    "impact_score": existing_rec.impact_score,
                    "feasibility_score": existing_rec.feasibility_score,
                    "risk_score": existing_rec.risk_score,
                    "customer_quotes": existing_rec.customer_quotes,
                    "status": existing_rec.status
                }
                await send_progress("recommendations", f"Using existing recommendation for: {theme.name} (skipped LLM call)")
            else:
                # Create new recommendation (SLOW PATH - requires LLM call)
                recommendation_data = await self.create_recommendation_from_theme(
                    theme_data_dict,
                    competitor_insights,
                    db
                )
            
            recommendations.append({
                "theme_id": theme.id,
                "theme_name": theme.name,
                "recommendation": recommendation_data,
                "impact_score": theme.overall_impact_score,
                "feedback_count": len(theme_feedback),
                "theme_data": theme_data_dict  # Include full theme data for deliberation
            })
        
        # Step 5: Persona agents debate and evaluate ALL recommendations (FAST: Use existing evidence when available)
        await send_progress("evaluations", f"Persona agents evaluating {len(recommendations)} recommendations...", {"total": len(recommendations)})
        debated_recommendations = []
        
        for idx, rec in enumerate(recommendations):
            await send_progress("evaluations", f"Evaluating {idx+1}/{len(recommendations)}: {rec['theme_name']}", {
                "current": idx + 1,
                "total": len(recommendations),
                "theme": rec['theme_name']
            })
            
            # Check if recommendation already has full deliberation data (FAST PATH - skip LLM calls)
            existing_rec = db.query(Recommendation).filter(Recommendation.feature == rec['theme_name']).first()
            if existing_rec and existing_rec.evidence and isinstance(existing_rec.evidence, dict) and existing_rec.evidence.get('evaluations'):
                # Use existing deliberation data (skip all LLM calls - instant!)
                deliberation = {
                    "evaluations": existing_rec.evidence.get('evaluations', {}),
                    "unified_recommendation": existing_rec.evidence.get('unified_recommendation', {}),
                    "consensus_score": existing_rec.impact_score or rec["impact_score"]
                }
                await send_progress("evaluations", f"✅ Using existing deliberation for: {rec['theme_name']} (skipped LLM calls - instant!)")
            else:
                # SLOW PATH - Run full deliberation with LLM calls
                # Use theme_data from recommendations if available, otherwise fetch
                if "theme_data" in rec:
                    theme_data = rec["theme_data"]
                else:
                    # Fallback: Get full theme object with all data including extra_metadata
                    theme_obj = db.query(Theme).filter(Theme.id == rec["theme_id"]).first()
                    theme_data = {
                        "id": rec["theme_id"],
                        "name": rec["theme_name"],
                        "description": theme_obj.description if theme_obj else "",
                        "impact_score": rec["impact_score"],
                        "customer_value": theme_obj.customer_value if theme_obj else 0,
                        "request_frequency": rec["feedback_count"],
                        "feedback_count": rec["feedback_count"],
                        "extra_metadata": theme_obj.extra_metadata if theme_obj else {}
                    }
                
                # Get mock competitor data for this theme
                from core.mock_competitor_enrichment import enrich_theme_with_mock_competitor_data, MOCK_COMPETITORS
                mock_enrichment = enrich_theme_with_mock_competitor_data(
                    theme_data.get('name', ''),
                    theme_data.get('description', ''),
                    theme_data.get('feedback_count', 0)
                )
                
                # Find matching mock competitors
                matched_mock_competitors = []
                theme_lower = (theme_data.get('name', '') + ' ' + (theme_data.get('description', '') or '')).lower()
                for comp in MOCK_COMPETITORS:
                    if comp['name'] in mock_enrichment.get('competitor_mentions', []) or any(
                        keyword in theme_lower 
                        for keyword in comp.get('feature_comparison', {}).keys()
                    ):
                        matched_mock_competitors.append(comp)
                
                # Internal company data
                internal_company_data = {
                    "current_focus": "Customer retention and competitive positioning",
                    "strategic_priorities": ["Reduce churn", "Close feature gaps", "Win back lost deals"],
                    "resource_constraints": "Engineering capacity limited, need to prioritize high-impact features",
                    "quarterly_goals": "Increase ARR retention, reduce lost deals to competitors",
                    "engineering_capacity": "Limited - must prioritize P0/P1 features",
                    "market_position": "Competitive pressure increasing, need to close feature gaps"
                }
                
                # Run deliberation - agents debate with FULL context including ALL data (SLOW - requires LLM calls)
                deliberation = await self.deliberation_system.deliberate(
                    rec["recommendation"],
                    {
                        "theme": theme_data,
                        "competitor_insights": competitor_insights,
                        "mock_competitor_data": {
                            "enrichment": mock_enrichment,
                            "matched_competitors": matched_mock_competitors,
                            "all_competitors": MOCK_COMPETITORS
                        },
                        "internal_company_data": internal_company_data
                    }
                )
            
            debated_recommendations.append({
                **rec,
                "deliberation": deliberation,
                "final_score": deliberation.get("consensus_score", rec["impact_score"]) * rec["impact_score"] / 10
            })
        
        # Step 6: Sort by final score (consensus + impact)
        await send_progress("ranking", "Ranking recommendations by consensus and impact...")
        debated_recommendations.sort(key=lambda x: x["final_score"], reverse=True)
        await send_progress("ranking", "Ranking complete", {"ranked": len(debated_recommendations)})
        
        # Step 7: Agents have final debate on top candidates
        await send_progress("debate", "Final team debate on top candidates...")
        top_candidates = debated_recommendations[:10]
        final_debate = await self.final_agent_debate(top_candidates, competitor_insights)
        await send_progress("debate", f"Team reached consensus! Selected {len(final_debate['selected_features'])} features", {
            "selected": len(final_debate["selected_features"])
        })
        
        # Step 8: Create roadmap from final consensus
        await send_progress("roadmap", "Generating final roadmap...")
        roadmap_items = []
        
        for candidate in final_debate["selected_features"]:
            # Create recommendation record
            rec_data = candidate["recommendation"]
            deliberation = candidate["deliberation"]
            
            # Get theme for comprehensive data
            theme = db.query(Theme).filter(Theme.id == candidate["theme_id"]).first()
            
            # Extract customer quotes with data justification
            customer_quotes = await self.extract_customer_quotes(candidate["theme_id"], db)
            
            # Build comprehensive data justification
            feedback_items = db.query(Feedback).filter(Feedback.theme_id == candidate["theme_id"]).all()
            total_requests = len(feedback_items)
            total_arr = sum([f.arr for f in feedback_items if f.arr and f.arr > 0])
            avg_arr = total_arr / len([f for f in feedback_items if f.arr and f.arr > 0]) if len([f for f in feedback_items if f.arr and f.arr > 0]) > 0 else 0
            
            # Get lost deal info
            lost_deal_info = {}
            if theme and theme.extra_metadata and theme.extra_metadata.get("lost_deal_info"):
                lost_deal_info = theme.extra_metadata["lost_deal_info"]
            
            # Build data justification summary
            data_justification = {
                "request_volume": total_requests,
                "total_arr_requested": round(total_arr, 2),
                "avg_customer_arr": round(avg_arr, 2),
                "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                "lost_deal_arr": round(lost_deal_info.get("lost_deal_arr", 0), 2),
                "competitor_mentions": lost_deal_info.get("competitor_mentions", []),
                "customer_quotes_count": len(customer_quotes),
                "top_customer_quotes": customer_quotes[:3],  # Top 3 quotes for summary
                "impact_score_breakdown": theme.extra_metadata.get("impact_score_breakdown", {}) if theme and theme.extra_metadata else {}
            }
            
            # Enhanced description with data justification
            enhanced_description = rec_data.get("description", "")
            if data_justification["request_volume"] > 0:
                enhanced_description += f"\n\n📊 Data Justification:\n"
                enhanced_description += f"• {data_justification['request_volume']} customer requests\n"
                if data_justification["total_arr_requested"] > 0:
                    enhanced_description += f"• ${data_justification['total_arr_requested']/1000:.0f}K total ARR from requesters\n"
                if data_justification["lost_deal_count"] > 0:
                    enhanced_description += f"• {data_justification['lost_deal_count']} lost deals (${data_justification['lost_deal_arr']/1000:.0f}K ARR at risk)\n"
                if data_justification["competitor_mentions"]:
                    enhanced_description += f"• Competitors mentioned: {', '.join(data_justification['competitor_mentions'][:3])}\n"
            
            recommendation = Recommendation(
                title=rec_data.get("title", candidate["theme_name"]),
                description=enhanced_description,
                feature=candidate["theme_name"],
                impact_score=candidate["impact_score"],
                feasibility_score=deliberation["evaluations"]["engineering"].get("feasibility_score", 5.0),
                risk_score=deliberation["evaluations"]["engineering"].get("risk_score", 5.0),
                ux_implications=deliberation["evaluations"]["ux"].get("ux_implications", ""),
                business_impact=deliberation["evaluations"]["pm"].get("business_impact", ""),
                pm_verdict=deliberation["evaluations"]["pm"].get("reasoning", ""),
                ux_verdict=deliberation["evaluations"]["ux"].get("reasoning", ""),
                data_scientist_verdict=deliberation["evaluations"]["data_scientist"].get("reasoning", ""),
                engineering_verdict=deliberation["evaluations"]["engineering"].get("reasoning", ""),
                unified_recommendation=deliberation["unified_recommendation"].get("unified_reasoning", ""),
                customer_quotes=customer_quotes,
                evidence={
                    **deliberation,
                    "data_justification": data_justification  # Add comprehensive data justification
                },
                status="pending"
            )
            
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            # Determine which teams benefit
            teams_benefit = []
            if lost_deal_info.get("lost_deal_count", 0) > 0:
                teams_benefit.append("Sales")
            if total_requests > 10:
                teams_benefit.append("Customer Success")
            if recommendation.feasibility_score and recommendation.feasibility_score > 7:
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
            if recommendation.feasibility_score:
                if recommendation.feasibility_score >= 8:
                    estimated_weeks = "6-8 weeks"
                elif recommendation.feasibility_score >= 6:
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
            if recommendation.evidence and isinstance(recommendation.evidence, dict):
                evaluations = recommendation.evidence.get("evaluations", {})
                engineering = evaluations.get("engineering", {})
                if engineering.get("alternatives"):
                    alternatives.extend(engineering.get("alternatives", []))
            if not alternatives:
                alternatives = [
                    "Do nothing (not recommended - high risk)",
                    "Partial implementation (may not address core need)",
                    "Third-party integration (evaluation needed)"
                ]
            
            roadmap_items.append({
                "id": recommendation.id,
                "title": recommendation.title,
                "feature": recommendation.feature,
                "summary": enhanced_description[:200] + "..." if len(enhanced_description) > 200 else enhanced_description,
                "why_this_matters_now": " | ".join(why_matters),
                "top_customer_quotes": customer_quotes[:5],  # Top 5 quotes
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
                    "feasibility_score": recommendation.feasibility_score or 0
                },
                "alternatives_considered": alternatives[:3],  # Top 3 alternatives
                "impact_score": recommendation.impact_score,
                "consensus_score": candidate["deliberation"].get("consensus_score", 0),
                "final_ranking": candidate.get("final_ranking", 0),
                "priority": "P0" if risk_level == "critical" else "P1" if risk_level == "high" else "P2"
            })
        
        # Step 9: Create roadmap
        roadmap = Roadmap(
            quarter=quarter,
            year=year,
            items=[item["id"] for item in roadmap_items],
            extra_metadata={
                "total_themes_considered": len(themes),
                "top_candidates_evaluated": len(top_candidates),
                "final_selected": len(roadmap_items),
                "debate_summary": final_debate.get("debate_summary", ""),
                "consensus_reasoning": final_debate.get("consensus_reasoning", "")
            }
        )
        
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)
        
        await send_progress("complete", "Roadmap saved successfully!", {"roadmap_id": roadmap.id})
        
        return {
            "roadmap_id": roadmap.id,
            "quarter": quarter,
            "year": year,
            "items": roadmap_items,
            "summary": await self.generate_roadmap_summary(roadmap_items),
            "debate_process": {
                "themes_analyzed": len(themes),
                "recommendations_created": len(recommendations),
                "top_candidates_debated": len(top_candidates),
                "final_selected": len(roadmap_items),
                "final_debate_summary": final_debate.get("debate_summary", "")
            }
        }
    
    async def final_agent_debate(
        self,
        top_candidates: List[Dict[str, Any]],
        competitor_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Final debate where all persona agents discuss top candidates together"""
        
        candidates_summary = []
        for idx, candidate in enumerate(top_candidates):
            candidates_summary.append({
                "rank": idx + 1,
                "name": candidate["theme_name"],
                "impact_score": candidate["impact_score"],
                "feedback_count": candidate["feedback_count"],
                "pm_verdict": candidate["deliberation"]["evaluations"]["pm"].get("verdict", ""),
                "ux_verdict": candidate["deliberation"]["evaluations"]["ux"].get("verdict", ""),
                "engineering_verdict": candidate["deliberation"]["evaluations"]["engineering"].get("verdict", ""),
                "consensus_score": candidate["deliberation"].get("consensus_score", 0)
            })
        
        prompt = f"""As a team of experts (PM, UX Designer, Data Scientist, Engineering Lead), you need to have a FINAL STRATEGIC DEBATE to select the top features for the quarterly roadmap.

CONTEXT:
You have analyzed {len(top_candidates)} top candidates based on:
- Impact scores from customer feedback
- Request frequency and customer demand
- Customer value and pain points
- Competitive pressure and market gaps
- Strategic importance and alignment
- Technical feasibility (from engineering)
- UX implications (from UX designer)
- Data insights (from data scientist)
- Business impact (from PM)

TOP CANDIDATES WITH FULL DELIBERATION:
{json.dumps(candidates_summary, indent=2)[:3000]}

COMPETITOR INSIGHTS:
{json.dumps(competitor_insights.get("opportunities", [])[:5], indent=2)[:800]}

TEAM DEBATE PROCESS:
This is a REAL strategic planning meeting. Each team member should:
1. Present their top priorities and WHY (based on their expertise)
2. Explain what matters most from their perspective
3. Challenge other perspectives constructively
4. Discuss trade-offs and resource constraints
5. Consider the full picture: themes, impact scores, competitor data, customer feedback
6. Reach consensus on the final roadmap priorities

CONSIDERATIONS:
- Business impact and revenue potential (PM perspective)
- Customer demand and urgency (Data Scientist perspective)
- Technical feasibility and risk (Engineering perspective)
- UX implications and user experience (UX perspective)
- Strategic alignment with company goals
- Competitive positioning and market gaps
- Resource constraints and dependencies
- Quick wins vs. long-term investments

Provide the team's final strategic decision as JSON with:
- selected_features: array of selected feature names/IDs (top 8-10) in priority order
- debate_summary: DETAILED summary of the team's strategic discussion, including actual conversation
- consensus_reasoning: WHY these features were selected, what the team agreed on, and what matters most
- rejected_features: features that were discussed but not selected, with specific reasons why
- priority_order: final priority ranking with justification for each priority level
- strategic_rationale: overall strategic reasoning for the roadmap selection
- key_decisions: major decisions made during the debate and why
- trade_offs_discussed: what trade-offs were considered and how they were resolved
- resource_allocation: how resources should be allocated based on priorities
- success_metrics: how success will be measured for each priority
"""
        
        response = await self.deliberation_system.pm_agent.llm_client.chat_completion([
            {"role": "system", "content": "You facilitate strategic team debates on product roadmap decisions. Multiple experts (PM, UX, Data Scientist, Engineering) discuss, debate, challenge each other, and converge on the best features. Show real conversations and detailed reasoning. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.7, max_tokens=3000)
        
        try:
            debate_result = json.loads(response)
            
            # Map selected features back to candidates
            selected_features = []
            for selected in debate_result.get("selected_features", []):
                # Find matching candidate
                for candidate in top_candidates:
                    if (selected.lower() in candidate["theme_name"].lower() or 
                        str(selected) == str(candidate["theme_id"])):
                        selected_features.append(candidate)
                        break
            
            # If not enough found, take top by score
            if len(selected_features) < 8:
                selected_features = top_candidates[:8]
            
            return {
                "selected_features": selected_features[:10],  # Max 10
                "debate_summary": debate_result.get("debate_summary", "Team discussed top candidates and selected based on impact and feasibility"),
                "consensus_reasoning": debate_result.get("consensus_reasoning", ""),
                "rejected_features": debate_result.get("rejected_features", []),
                "priority_order": debate_result.get("priority_order", [])
            }
        except:
            # Fallback: select top 8 by final score
            return {
                "selected_features": top_candidates[:8],
                "debate_summary": "Team selected top features based on impact scores and consensus",
                "consensus_reasoning": "Selected features with highest impact scores and team consensus",
                "rejected_features": [],
                "priority_order": [c["theme_name"] for c in top_candidates[:8]]
            }
    
    async def create_recommendation_from_theme(
        self,
        theme: Dict[str, Any],
        competitor_insights: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Create a recommendation from a theme with FULL context (ARR, lost deals, competitor info, mock data)"""
        # Extract lost deal info
        lost_deal_info = theme.get('lost_deal_info', {}) or theme.get('extra_metadata', {}).get('lost_deal_info', {})
        avg_arr = lost_deal_info.get('estimated_avg_arr', 0) or theme.get('avg_arr', 0)
        total_arr = lost_deal_info.get('total_arr', 0) or theme.get('total_arr', 0)
        lost_deal_count = lost_deal_info.get('lost_deal_count', 0)
        lost_deal_arr = lost_deal_info.get('lost_deal_arr', 0)
        competitor_mentions = lost_deal_info.get('competitor_mentions', [])
        
        # Get mock competitor data for this theme
        from core.mock_competitor_enrichment import enrich_theme_with_mock_competitor_data, MOCK_COMPETITORS
        mock_data = enrich_theme_with_mock_competitor_data(
            theme.get('name', ''),
            theme.get('description', ''),
            theme.get('feedback_count', 0)
        )
        
        # Find matching mock competitors
        matched_mock_competitors = []
        theme_lower = (theme.get('name', '') + ' ' + (theme.get('description', '') or '')).lower()
        for comp in MOCK_COMPETITORS:
            if comp['name'] in competitor_mentions or any(
                keyword in theme_lower 
                for keyword in comp.get('feature_comparison', {}).keys()
            ):
                matched_mock_competitors.append(comp)
        
        # Internal company data (can be expanded)
        internal_company_data = {
            "current_focus": "Customer retention and competitive positioning",
            "strategic_priorities": ["Reduce churn", "Close feature gaps", "Win back lost deals"],
            "resource_constraints": "Engineering capacity limited, need to prioritize high-impact features",
            "quarterly_goals": "Increase ARR retention, reduce lost deals to competitors"
        }
        
        # Build comprehensive prompt with ALL data
        prompt = f"""Based on this theme and comprehensive business data, create a detailed product recommendation with PRIORITIZATION:

THEME INFORMATION:
- Name: {theme.get('name', '')}
- Description: {theme.get('description', '')}
- Impact Score: {theme.get('impact_score', 0)}/10
- Customer Value: {theme.get('customer_value', 0)}/10
- Request Frequency: {theme.get('request_frequency', 0)} requests
- Feedback Count: {theme.get('feedback_count', 0)} customer feedback items

CRITICAL BUSINESS METRICS (USE THESE FOR PRIORITIZATION):
- Average Customer ARR: ${avg_arr:,.0f} per customer
- Total ARR at Stake: ${total_arr:,.0f} across all affected customers
- Lost Deals: {lost_deal_count} deals lost to competitors
- Lost ARR: ${lost_deal_arr:,.0f} in revenue at risk
- Competitors Mentioned: {', '.join(competitor_mentions) if competitor_mentions else 'None'}
- Has Lost Deals: {lost_deal_info.get('has_lost_deals', False)}

COMPETITOR INTELLIGENCE (FROM DATABASE):
{json.dumps(competitor_insights.get('competitors', [])[:5], indent=2)[:1500]}
Market Gaps: {json.dumps(competitor_insights.get('market_gaps', [])[:5], indent=2)[:800]}
Opportunities: {json.dumps(competitor_insights.get('opportunities', [])[:5], indent=2)[:800]}

MOCK COMPETITOR DATA (STATIC MARKET INTELLIGENCE):
{json.dumps(matched_mock_competitors, indent=2)[:1000] if matched_mock_competitors else 'No matching mock competitors'}
Mock Enrichment Data: {json.dumps(mock_data, indent=2)[:800]}

INTERNAL COMPANY DATA:
{json.dumps(internal_company_data, indent=2)}

Create a COMPREHENSIVE product recommendation with EXPLICIT PRIORITIZATION that:
1. Addresses the customer pain point with specific details
2. References ALL business metrics (ARR, lost deals, competitor pressure, impact score)
3. Explains why this is strategically important using the data
4. Provides explicit prioritization recommendation (P0/P1/P2/P3) with reasoning
5. References competitor intelligence and market gaps
6. Provides concrete next steps and implementation guidance

Return JSON with:
- title: specific, actionable recommendation title (not generic, reference the business impact)
- description: detailed description (300+ words) that references:
  * ARR data (${avg_arr:,.0f} avg, ${total_arr:,.0f} total)
  * Lost deals ({lost_deal_count}) and lost ARR (${lost_deal_arr:,.0f})
  * Competitor mentions ({', '.join(competitor_mentions) if competitor_mentions else 'None'})
  * Impact score ({theme.get('impact_score', 0)}/10)
  * Customer demand and feedback count
- impact_score: use the provided impact score ({theme.get('impact_score', 0)})
- priority_level: explicit priority (P0/Critical, P1/High, P2/Medium, P3/Low) with detailed justification
- strategic_rationale: detailed reasoning (400+ words) that mentions:
  * Lost deals ({lost_deal_count}) and lost ARR (${lost_deal_arr:,.0f})
  * ARR impact (${avg_arr:,.0f} avg, ${total_arr:,.0f} total)
  * Competitive pressure from {', '.join(competitor_mentions) if competitor_mentions else 'competitors'}
  * Market gaps and opportunities
  * Why this is strategically important
- customer_demand: specific evidence including feedback count ({theme.get('feedback_count', 0)}), ARR impact, and lost deals
- business_impact: specific revenue/retention impact (200+ words) based on ALL the data provided:
  * ARR at stake (${total_arr:,.0f})
  * Lost deals impact (${lost_deal_arr:,.0f})
  * Competitive threat
  * Customer retention implications
- prioritization_recommendation: when to build this (Q1/Q2/Q3/Q4/Backlog) with detailed reasoning based on:
  * Lost deals urgency
  * ARR at risk
  * Competitive pressure
  * Impact score
  * Resource constraints
"""
        
        response = await self.deliberation_system.pm_agent.llm_client.chat_completion([
            {"role": "system", "content": "You create detailed, data-driven product recommendations. Reference specific metrics (ARR, lost deals, competitor data) in your recommendations. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.6, max_tokens=1500)
        
        try:
            recommendation = json.loads(response)
            # Ensure impact score is from theme data
            recommendation["impact_score"] = theme.get('impact_score', 0)
            return recommendation
        except Exception as e:
            # Fallback with rich data
            lost_deal_text = ""
            if lost_deal_info.get('has_lost_deals'):
                lost_deal_text = f" We've lost {lost_deal_info.get('lost_deal_count', 0)} deals worth ${lost_deal_info.get('lost_deal_arr', 0):,.0f} ARR due to this gap."
            
            competitor_text = ""
            if lost_deal_info.get('competitor_mentions'):
                competitor_text = f" Competitors like {', '.join(lost_deal_info.get('competitor_mentions', [])[:2])} are winning deals because they have this feature."
            
            arr_text = ""
            if avg_arr > 0:
                arr_text = f" This affects customers with average ARR of ${avg_arr:,.0f}."
            
            return {
                "title": f"Fix {theme.get('name', 'Theme')} - Critical for Customer Retention",
                "description": f"{theme.get('description', '')}{lost_deal_text}{competitor_text}{arr_text}",
                "impact_score": theme.get("impact_score", 0),
                "strategic_rationale": f"High impact ({theme.get('impact_score', 0)}/10) with {theme.get('feedback_count', 0)} customer requests.{lost_deal_text}",
                "customer_demand": f"{theme.get('feedback_count', 0)} customer requests, {lost_deal_info.get('lost_deal_count', 0)} lost deals, ${lost_deal_info.get('lost_deal_arr', 0):,.0f} ARR at risk",
                "business_impact": f"Addressing this could prevent ${lost_deal_info.get('lost_deal_arr', 0):,.0f} in lost ARR and improve retention for customers with ${avg_arr:,.0f} average ARR"
            }
    
    async def extract_customer_quotes(self, theme_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Extract professional customer quotes with data justification
        
        Returns quotes sorted by:
        1. High ARR customers first
        2. Strong sentiment (positive or negative)
        3. Most detailed/insightful quotes
        """
        from core.database import Theme
        
        # Get theme for context
        theme = db.query(Theme).filter(Theme.id == theme_id).first()
        
        # Get all feedback for this theme, sorted by ARR and sentiment
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme_id).all()
        
        if not feedback_items:
            return []
        
        # Score and sort quotes by quality and impact
        scored_quotes = []
        for item in feedback_items:
            if not item.content or len(item.content.strip()) < 10:
                continue  # Skip empty or very short feedback
            
            # Calculate quote quality score
            quality_score = 0.0
            
            # ARR weight (higher ARR = more valuable quote)
            if item.arr and item.arr > 0:
                if item.arr >= 100000:  # Enterprise
                    quality_score += 30
                elif item.arr >= 10000:  # Mid-market
                    quality_score += 15
                else:  # SMB
                    quality_score += 5
            
            # Sentiment weight (strong sentiment = more impactful)
            if item.sentiment_score:
                sentiment_abs = abs(item.sentiment_score)
                quality_score += sentiment_abs * 10  # Scale sentiment to 0-10
            
            # Quote length weight (detailed quotes are more valuable)
            quote_length = len(item.content)
            if quote_length > 200:
                quality_score += 10  # Detailed quote
            elif quote_length > 100:
                quality_score += 5   # Medium quote
            
            # Pain level weight (high pain = urgent need)
            if item.pain_level and item.pain_level > 0:
                quality_score += item.pain_level * 2
            
            # Urgency weight
            if item.urgency:
                urgency_map = {"critical": 15, "high": 10, "medium": 5, "low": 1}
                quality_score += urgency_map.get(item.urgency.lower(), 0)
            
            scored_quotes.append({
                "quote": item.content[:500] if len(item.content) > 500 else item.content,  # Up to 500 chars
                "content": item.content[:500] if len(item.content) > 500 else item.content,
                "source": item.source or "Unknown",
                "sentiment": item.sentiment_score or 0,
                "arr": item.arr or 0,
                "account_id": item.account_id,
                "user_segment": item.user_segment,
                "pain_level": item.pain_level or 0,
                "urgency": item.urgency,
                "classification": item.classification,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "quality_score": quality_score
            })
        
        # Sort by quality score (highest first) and take top 10
        scored_quotes.sort(key=lambda x: x["quality_score"], reverse=True)
        top_quotes = scored_quotes[:10]
        
        # Format for frontend with data justification
        formatted_quotes = []
        for quote_data in top_quotes:
            # Build data justification string
            justification_parts = []
            
            if quote_data["arr"] > 0:
                if quote_data["arr"] >= 100000:
                    justification_parts.append(f"Enterprise customer (${quote_data['arr']/1000:.0f}K ARR)")
                elif quote_data["arr"] >= 10000:
                    justification_parts.append(f"Mid-market customer (${quote_data['arr']/1000:.0f}K ARR)")
                else:
                    justification_parts.append(f"${quote_data['arr']/1000:.0f}K ARR customer")
            
            if quote_data["user_segment"]:
                justification_parts.append(quote_data["user_segment"])
            
            if quote_data["pain_level"] and quote_data["pain_level"] >= 7:
                justification_parts.append(f"High pain ({quote_data['pain_level']}/10)")
            
            if quote_data["urgency"]:
                justification_parts.append(f"{quote_data['urgency'].title()} urgency")
            
            justification = " • ".join(justification_parts) if justification_parts else "Customer feedback"
            
            formatted_quotes.append({
                "quote": quote_data["quote"],
                "content": quote_data["content"],
                "source": quote_data["source"],
                "sentiment": quote_data["sentiment"],
                "arr": quote_data["arr"],
                "account_id": quote_data["account_id"],
                "user_segment": quote_data["user_segment"],
                "pain_level": quote_data["pain_level"],
                "urgency": quote_data["urgency"],
                "classification": quote_data["classification"],
                "created_at": quote_data["created_at"],
                "data_justification": justification,  # Professional justification string
                "quality_score": quote_data["quality_score"]
            })
        
        return formatted_quotes
    
    async def generate_quarterly_roadmap(
        self,
        quarter: str,
        year: int,
        recommendations: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Generate quarterly roadmap (legacy method - use generate_roadmap_from_all_data instead)"""
        # Sort by impact score
        sorted_recs = sorted(recommendations, key=lambda x: x.get("impact_score", 0), reverse=True)
        
        # Select top items for roadmap
        roadmap_items = sorted_recs[:10]
        
        # Create roadmap record
        roadmap = Roadmap(
            quarter=quarter,
            year=year,
            items=[r["id"] for r in roadmap_items],
            extra_metadata={
                "total_recommendations": len(recommendations),
                "selected_count": len(roadmap_items)
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
            "summary": await self.generate_roadmap_summary(roadmap_items)
        }
    
    async def generate_roadmap_summary(self, items: List[Dict[str, Any]]) -> str:
        """Generate roadmap summary"""
        prompt = f"""Create a concise summary of this quarterly roadmap:

Items: {len(items)} recommendations
Top priorities: {', '.join([i.get('title', '')[:50] for i in items[:5]])}

Provide a 2-3 paragraph executive summary.
"""
        
        response = await self.deliberation_system.pm_agent.llm_client.chat_completion([
            {"role": "system", "content": "You create executive summaries for product roadmaps."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        
        return response
    
    async def generate_recommendations(
        self,
        themes: List[Dict[str, Any]],
        competitor_insights: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate recommendations from themes and competitor insights (legacy method)"""
        recommendations = []
        
        for theme in themes[:15]:  # Top 15 themes
            # Create recommendation
            recommendation_data = await self.create_recommendation_from_theme(theme, competitor_insights, db)
            
            # Run persona deliberation
            deliberation = await self.deliberation_system.deliberate(
                recommendation_data,
                {
                    "theme": theme,
                    "competitor_insights": competitor_insights
                }
            )
            
            # Create recommendation record
            recommendation = Recommendation(
                title=recommendation_data.get("title", ""),
                description=recommendation_data.get("description", ""),
                feature=theme.get("name", ""),
                impact_score=recommendation_data.get("impact_score", 0),
                feasibility_score=deliberation["evaluations"]["engineering"].get("feasibility_score", 5.0),
                risk_score=deliberation["evaluations"]["engineering"].get("risk_score", 5.0),
                ux_implications=deliberation["evaluations"]["ux"].get("ux_implications", ""),
                business_impact=deliberation["evaluations"]["pm"].get("business_impact", ""),
                pm_verdict=deliberation["evaluations"]["pm"].get("reasoning", ""),
                ux_verdict=deliberation["evaluations"]["ux"].get("reasoning", ""),
                data_scientist_verdict=deliberation["evaluations"]["data_scientist"].get("reasoning", ""),
                engineering_verdict=deliberation["evaluations"]["engineering"].get("reasoning", ""),
                unified_recommendation=deliberation["unified_recommendation"].get("unified_reasoning", ""),
                customer_quotes=await self.extract_customer_quotes(theme.get("id"), db),
                evidence=deliberation,
                status="pending"
            )
            
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            recommendations.append({
                "id": recommendation.id,
                "title": recommendation.title,
                "impact_score": recommendation.impact_score,
                "unified_recommendation": recommendation.unified_recommendation,
                "deliberation": deliberation
            })
        
        return recommendations
    
    async def generate_one_pager(
        self,
        recommendation_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Generate comprehensive one-pager for a recommendation using OnePagerGenerator"""
        return await self.one_pager_generator.generate_one_pager(recommendation_id, db)
