from typing import Dict, List, Any
from core.database import Theme, Feedback
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from datetime import datetime, timedelta

class ImpactScorer:
    """Calculate impact scores for themes and recommendations with ARR weighting and lost deal tracking"""
    
    def calculate_customer_arr_weight(self, theme: Theme, db: Session) -> float:
        """Calculate ARR weight for a theme based on customer value (Enterprise > Mid-market > SMB)"""
        # Get all feedback for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        if not feedback_items:
            return 0.0
        
        total_arr = 0.0
        arr_count = 0
        
        for feedback in feedback_items:
            if feedback.arr and feedback.arr > 0:
                total_arr += feedback.arr
                arr_count += 1
        
        if arr_count == 0:
            # Try to get estimated ARR from theme metadata (set by LLM)
            if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
                estimated_arr = lost_deal_info.get("estimated_avg_arr", 0)
                if estimated_arr > 0:
                    avg_arr = estimated_arr
                else:
                    return 0.0
            else:
                return 0.0
        else:
            avg_arr = total_arr / arr_count
        
        # Weight by customer segment:
        # Enterprise ($100k+ ARR): 1.0x multiplier
        # Mid-market ($10k-$100k ARR): 0.7x multiplier
        # SMB (<$10k ARR): 0.4x multiplier
        if avg_arr >= 100000:
            segment_weight = 1.0  # Enterprise
        elif avg_arr >= 10000:
            segment_weight = 0.7  # Mid-market
        else:
            segment_weight = 0.4  # SMB
        
        # Normalize ARR to 0-10 scale (log scale for better distribution)
        import math
        arr_score = min(10.0, math.log10(max(1, avg_arr / 1000)) * 2)  # $1k = 0, $100k = 10
        
        return arr_score * segment_weight
    
    async def detect_lost_deals_with_llm(self, theme: Theme, db: Session) -> Dict[str, Any]:
        """Use LLM + Mock Competitor Data to detect lost deals, ARR, and competitors from theme content
        AGGREGATES ALL DATA from ALL feedback items in the theme cluster"""
        from core.llm_client import openrouter_client
        from core.mock_competitor_enrichment import enrich_theme_with_mock_competitor_data
        import json
        import re
        
        # Get ALL feedback for this theme (all items in the cluster)
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        feedback_count = len(feedback_items)
        
        # FIRST: Aggregate ACTUAL data from ALL feedback items in the cluster
        # This ensures we capture ALL ARR, lost deals, and competitors from similar requests
        total_arr_from_feedback = sum([f.arr for f in feedback_items if f.arr and f.arr > 0]) if feedback_items else 0
        arr_count = len([f for f in feedback_items if f.arr and f.arr > 0])
        avg_arr_from_feedback = total_arr_from_feedback / arr_count if arr_count > 0 else 0
        
        # Aggregate lost deals from ALL feedback items using pattern matching
        lost_deal_keywords = [
            "lost deal", "competitor won", "went with", "chose competitor",
            "switched to", "moved to", "cancelled because", "churned due to",
            "lost to", "competitor", "switching", "churn", "cancel"
        ]
        
        # Get existing competitors from database
        from core.database import Competitor
        existing_competitors = db.query(Competitor).all()
        competitor_names = [c.name for c in existing_competitors]
        competitor_names_lower = [c.name.lower() for c in existing_competitors]
        
        # Count lost deals and aggregate ARR from ALL feedback items
        actual_lost_deal_count = 0
        actual_lost_deal_arr = 0.0
        actual_competitor_mentions = set()
        
        for feedback in feedback_items:
            content_lower = (feedback.content or "").lower()
            
            # Check if this feedback indicates a lost deal
            if any(keyword in content_lower for keyword in lost_deal_keywords):
                actual_lost_deal_count += 1
                if feedback.arr and feedback.arr > 0:
                    actual_lost_deal_arr += feedback.arr
                
                # Extract competitor mentions from this feedback
                for comp_name in competitor_names_lower:
                    if comp_name in content_lower:
                        actual_competitor_mentions.add(comp_name)
        
        # Use mock competitor data to get baseline estimates for LLM enhancement
        mock_data = enrich_theme_with_mock_competitor_data(
            theme.name, 
            theme.description or "", 
            feedback_count
        )
        
        # Try LLM extraction (but use mock data as fallback)
        try:
            # Build context from theme and feedback
            theme_content = f"{theme.name}. {theme.description or ''}"
            feedback_texts = [f.content for f in feedback_items[:10] if f.content]
            
            # LLM prompt with mock competitor context
            prompt = f"""Analyze this customer feedback theme and extract business intelligence:

THEME: {theme.name}
DESCRIPTION: {theme.description or 'No description'}
FEEDBACK SAMPLES: {chr(10).join(feedback_texts[:5])}

KNOWN COMPETITORS: DataFlow Pro, MobileFirst Analytics, IntegrateHub, SpeedDash
MOCK DATA ESTIMATES: {json.dumps(mock_data, indent=2)[:500]}

Extract and return JSON with:
1. lost_deal_count: number of lost deals (use mock estimate if reasonable: {mock_data.get('lost_deal_count', 0)})
2. lost_deal_arr: estimated ARR lost (use mock estimate if reasonable: ${mock_data.get('lost_deal_arr', 0):,.0f})
3. competitor_mentions: list of competitor names (prefer: {', '.join(mock_data.get('competitor_mentions', []))})
4. estimated_avg_arr: estimated average customer ARR (use mock estimate if reasonable: ${mock_data.get('estimated_avg_arr', 0):,.0f})
5. business_impact: brief description

Rules:
- Use mock data estimates as baseline, refine based on actual feedback content
- Match competitor names with: DataFlow Pro, MobileFirst Analytics, IntegrateHub, SpeedDash
- If theme is about "export", "csv", "data export" → likely DataFlow Pro
- If theme is about "mobile", "app" → likely MobileFirst Analytics
- If theme is about "api", "integration" → likely IntegrateHub
- If theme is about "performance", "speed" → likely SpeedDash

Return ONLY valid JSON, no other text.
"""
            
            response = await openrouter_client.chat_completion([
                {"role": "system", "content": "You extract business intelligence from customer feedback. Use provided mock data as baseline. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=500)
            
            # Parse LLM response
            llm_data = json.loads(response.strip())
            
            # PRIORITY: Use ACTUAL aggregated data from ALL feedback items first
            # Then enhance with LLM/mock data if needed
            
            # Lost deals: Use actual count from feedback, enhance with LLM if higher
            llm_lost_deal_count = llm_data.get("lost_deal_count", 0) or mock_data.get("lost_deal_count", 0)
            lost_deal_count = max(actual_lost_deal_count, llm_lost_deal_count)  # Take the higher value
            
            # Lost deal ARR: Use actual ARR from lost deal feedback, enhance with LLM if higher
            llm_lost_deal_arr = llm_data.get("lost_deal_arr", 0) or mock_data.get("lost_deal_arr", 0)
            lost_deal_arr = max(actual_lost_deal_arr, llm_lost_deal_arr)  # Take the higher value
            
            # Competitors: Combine actual mentions from ALL feedback with LLM/mock data
            llm_competitor_mentions = llm_data.get("competitor_mentions", []) or mock_data.get("competitor_mentions", [])
            # Convert actual competitor mentions back to proper names
            actual_competitor_names = []
            for comp_lower in actual_competitor_mentions:
                for comp in existing_competitors:
                    if comp.name.lower() == comp_lower:
                        actual_competitor_names.append(comp.name)
                        break
            # Combine all competitor mentions (from actual feedback + LLM/mock)
            all_competitor_mentions = list(set(actual_competitor_names + llm_competitor_mentions))
            
            # ARR: Prefer actual aggregated ARR from ALL feedback items
            estimated_avg_arr = llm_data.get("estimated_avg_arr", 0) or mock_data.get("estimated_avg_arr", 0)
            if avg_arr_from_feedback > 0:
                avg_arr = avg_arr_from_feedback
            else:
                avg_arr = estimated_avg_arr
            
            # If we have lost deals but no ARR, estimate from avg_arr
            if lost_deal_count > 0 and lost_deal_arr == 0 and avg_arr > 0:
                lost_deal_arr = lost_deal_count * avg_arr
            
            return {
                "lost_deal_count": lost_deal_count,
                "lost_deal_arr": lost_deal_arr,
                "competitor_mentions": all_competitor_mentions,
                "has_lost_deals": lost_deal_count > 0 or len(all_competitor_mentions) > 0,
                "estimated_avg_arr": avg_arr,
                "total_arr": total_arr_from_feedback if total_arr_from_feedback > 0 else (avg_arr * feedback_count if feedback_count > 0 else avg_arr),
                "business_impact": llm_data.get("business_impact", "") or mock_data.get("business_impact", "")
            }
        except Exception as e:
            # Fallback: Use ACTUAL aggregated data from ALL feedback items + mock data
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"LLM extraction failed, using actual feedback data + mock: {e}")
            
            # Use actual aggregated data from ALL feedback items
            lost_deal_count = max(actual_lost_deal_count, mock_data.get("lost_deal_count", 0))
            lost_deal_arr = max(actual_lost_deal_arr, mock_data.get("lost_deal_arr", 0))
            
            # Combine actual competitor mentions with mock data
            actual_competitor_names = []
            for comp_lower in actual_competitor_mentions:
                for comp in existing_competitors:
                    if comp.name.lower() == comp_lower:
                        actual_competitor_names.append(comp.name)
                        break
            all_competitor_mentions = list(set(actual_competitor_names + mock_data.get("competitor_mentions", [])))
            
            # Use actual ARR from feedback if available
            if avg_arr_from_feedback > 0:
                avg_arr = avg_arr_from_feedback
            else:
                avg_arr = mock_data.get("estimated_avg_arr", 0)
            
            # If we have lost deals but no ARR, estimate from avg_arr
            if lost_deal_count > 0 and lost_deal_arr == 0 and avg_arr > 0:
                lost_deal_arr = lost_deal_count * avg_arr
            
            return {
                "lost_deal_count": lost_deal_count,
                "lost_deal_arr": lost_deal_arr,
                "competitor_mentions": all_competitor_mentions,
                "has_lost_deals": lost_deal_count > 0 or len(all_competitor_mentions) > 0,
                "estimated_avg_arr": avg_arr,
                "total_arr": total_arr_from_feedback if total_arr_from_feedback > 0 else (avg_arr * feedback_count if feedback_count > 0 else avg_arr),
                "business_impact": mock_data.get("business_impact", "")
            }
    
    def detect_lost_deals(self, theme: Theme, db: Session) -> Dict[str, Any]:
        """Detect lost deals and competitive pressure from feedback - PATTERN-BASED FALLBACK"""
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        lost_deal_count = 0
        lost_deal_arr = 0.0
        competitor_mentions = []
        
        # Enhanced lost deal keywords
        lost_deal_keywords = [
            "lost deal", "competitor won", "went with", "chose competitor",
            "switched to", "moved to", "cancelled because", "churned due to",
            "lost to", "competitor", "switching", "churn", "cancel"
        ]
        
        # Get existing competitors
        from core.database import Competitor
        existing_competitors = db.query(Competitor).all()
        competitor_names = [c.name.lower() for c in existing_competitors]
        
        import re
        for feedback in feedback_items:
            content_lower = (feedback.content or "").lower()
            
            if any(keyword in content_lower for keyword in lost_deal_keywords):
                lost_deal_count += 1
                if feedback.arr:
                    lost_deal_arr += feedback.arr
                
                # Check for existing competitor names
                for comp_name in competitor_names:
                    if comp_name in content_lower:
                        # Find the actual competitor object to get proper name
                        for comp in existing_competitors:
                            if comp.name.lower() == comp_name:
                                competitor_mentions.append(comp.name)
                                break
        
        # Estimate ARR if not available
        avg_arr = 0
        if feedback_items:
            arr_values = [f.arr for f in feedback_items if f.arr]
            if arr_values:
                avg_arr = sum(arr_values) / len(arr_values)
            else:
                # Estimate based on theme content
                theme_lower = (theme.name + " " + (theme.description or "")).lower()
                if any(word in theme_lower for word in ["enterprise", "large", "big"]):
                    avg_arr = 100000  # Enterprise estimate
                elif any(word in theme_lower for word in ["smb", "small", "startup"]):
                    avg_arr = 15000  # SMB estimate
                else:
                    avg_arr = 50000  # Mid-market estimate
        
        return {
            "lost_deal_count": lost_deal_count,
            "lost_deal_arr": lost_deal_arr or (lost_deal_count * avg_arr),
            "competitor_mentions": list(set(competitor_mentions)),
            "has_lost_deals": lost_deal_count > 0 or len(competitor_mentions) > 0,
            "estimated_avg_arr": avg_arr
        }
    
    def calculate_theme_impact_score(self, theme: Theme, db: Session) -> float:
        """
        Professional Impact Scoring Formula (Airtable-style)
        
        Formula: 
        Impact Score = (
            Customer Value (ARR-weighted) × 0.30 +
            Request Frequency (normalized) × 0.25 +
            Segment Strategic Importance × 0.20 +
            Competitive Pressure (lost deals) × 0.25
        )
        
        Each component is normalized to 0-10 scale for consistent weighting.
        """
        import math
        
        # ============================================
        # 1. CUSTOMER VALUE (ARR-weighted) - 30%
        # ============================================
        # Get all feedback for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        # Calculate total ARR from all requesters
        total_arr = sum([f.arr for f in feedback_items if f.arr and f.arr > 0]) if feedback_items else 0
        arr_count = len([f for f in feedback_items if f.arr and f.arr > 0]) if feedback_items else 0
        avg_arr = total_arr / arr_count if arr_count > 0 else 0
        
        # Get ARR weight (Enterprise > Mid-market > SMB)
        arr_weight_norm = self.calculate_customer_arr_weight(theme, db)
        
        # Customer value score: combination of pain level and ARR weight
        customer_value_base = min(10.0, theme.customer_value or 0)
        customer_value_score = (customer_value_base * 0.6) + (arr_weight_norm * 0.4)  # 60% pain, 40% ARR
        
        # ============================================
        # 2. REQUEST FREQUENCY - 25%
        # ============================================
        request_freq = theme.request_frequency or len(feedback_items) if feedback_items else 0
        
        # Logarithmic scaling for better distribution
        # Formula: log10(freq + 1) * 3.33 (so 1 request = 1.0, 10 requests = 3.3, 100 requests = 6.6, 1000 = 10.0)
        if request_freq > 0:
            request_freq_norm = min(10.0, math.log10(request_freq + 1) * 3.33)
        else:
            request_freq_norm = 0.0
        
        # ============================================
        # 3. SEGMENT STRATEGIC IMPORTANCE - 20%
        # ============================================
        # Calculate based on customer segments and strategic weight
        strategic_weight_base = theme.strategic_segment_weight or 0.5
        
        # Segment distribution analysis
        segment_distribution = {}
        segment_arr = {}
        for feedback in feedback_items:
            segment = feedback.user_segment or "unknown"
            segment_distribution[segment] = segment_distribution.get(segment, 0) + 1
            if feedback.arr and feedback.arr > 0:
                segment_arr[segment] = segment_arr.get(segment, 0) + feedback.arr
        
        # Weight by strategic segments (Enterprise > Mid-market > SMB)
        strategic_score = 0.0
        if segment_distribution:
            total_feedback = sum(segment_distribution.values())
            for segment, count in segment_distribution.items():
                segment_weight = 1.0  # Default
                if "enterprise" in segment.lower() or "large" in segment.lower():
                    segment_weight = 1.0
                elif "mid" in segment.lower() or "medium" in segment.lower():
                    segment_weight = 0.7
                elif "smb" in segment.lower() or "small" in segment.lower() or "startup" in segment.lower():
                    segment_weight = 0.4
                
                strategic_score += (count / total_feedback) * segment_weight * 10.0
        
        # Combine with base strategic weight
        strategic_weight_norm = (strategic_score * 0.7) + (strategic_weight_base * 10.0 * 0.3)
        strategic_weight_norm = min(10.0, strategic_weight_norm)
        
        # ============================================
        # 4. COMPETITIVE PRESSURE (Lost Deals) - 25%
        # ============================================
        lost_deal_info = self.detect_lost_deals(theme, db)
        
        # Calculate competitive pressure score
        competitive_score = 0.0
        
        # Lost deal count component (0-5 points)
        lost_deal_count = lost_deal_info.get("lost_deal_count", 0)
        if lost_deal_count > 0:
            competitive_score += min(5.0, lost_deal_count * 1.5)  # +1.5 per lost deal, max 5
        
        # Lost ARR component (0-3 points)
        lost_deal_arr = lost_deal_info.get("lost_deal_arr", 0)
        if lost_deal_arr > 0:
            competitive_score += min(3.0, math.log10(max(1, lost_deal_arr / 1000)) * 1.5)  # Log scale
        
        # Competitor mentions component (0-2 points)
        competitor_mentions = lost_deal_info.get("competitor_mentions", [])
        if competitor_mentions:
            competitive_score += min(2.0, len(competitor_mentions) * 0.5)  # +0.5 per competitor
        
        competitive_pressure_norm = min(10.0, competitive_score)
        
        # ============================================
        # FINAL IMPACT SCORE CALCULATION
        # ============================================
        weights = {
            "customer_value": 0.30,      # 30% - ARR-weighted customer value
            "request_frequency": 0.25,   # 25% - How many times mentioned
            "strategic_importance": 0.20, # 20% - Segment strategic importance
            "competitive_pressure": 0.25  # 25% - Lost deals and competitive pressure
        }
        
        impact_score = (
            customer_value_score * weights["customer_value"] +
            request_freq_norm * weights["request_frequency"] +
            strategic_weight_norm * weights["strategic_importance"] +
            competitive_pressure_norm * weights["competitive_pressure"]
        )
        
        # Store detailed breakdown in theme metadata for insights
        if not hasattr(theme, 'extra_metadata') or theme.extra_metadata is None:
            theme.extra_metadata = {}
        theme.extra_metadata["lost_deal_info"] = lost_deal_info
        theme.extra_metadata["impact_score_breakdown"] = {
            "customer_value": {
                "score": round(customer_value_score, 2),
                "weight": weights["customer_value"],
                "weighted_score": round(customer_value_score * weights["customer_value"], 2),
                "details": {
                    "base_pain_score": round(customer_value_base, 2),
                    "arr_weight": round(arr_weight_norm, 2),
                    "avg_arr": round(avg_arr, 2),
                    "total_arr": round(total_arr, 2),
                    "arr_customers": arr_count
                }
            },
            "request_frequency": {
                "score": round(request_freq_norm, 2),
                "weight": weights["request_frequency"],
                "weighted_score": round(request_freq_norm * weights["request_frequency"], 2),
                "details": {
                    "raw_count": request_freq,
                    "normalized": round(request_freq_norm, 2)
                }
            },
            "strategic_importance": {
                "score": round(strategic_weight_norm, 2),
                "weight": weights["strategic_importance"],
                "weighted_score": round(strategic_weight_norm * weights["strategic_importance"], 2),
                "details": {
                    "base_weight": round(strategic_weight_base, 2),
                    "segment_distribution": segment_distribution,
                    "segment_arr": {k: round(v, 2) for k, v in segment_arr.items()}
                }
            },
            "competitive_pressure": {
                "score": round(competitive_pressure_norm, 2),
                "weight": weights["competitive_pressure"],
                "weighted_score": round(competitive_pressure_norm * weights["competitive_pressure"], 2),
                "details": {
                    "lost_deal_count": lost_deal_count,
                    "lost_deal_arr": round(lost_deal_arr, 2),
                    "competitor_mentions": competitor_mentions,
                    "has_lost_deals": lost_deal_info.get("has_lost_deals", False)
                }
            },
            "formula": "Impact = (Customer Value × 0.30) + (Request Frequency × 0.25) + (Strategic Importance × 0.20) + (Competitive Pressure × 0.25)"
        }
        
        return round(min(10.0, impact_score), 2)
    
    def calculate_recommendation_impact_score(
        self,
        recommendation: Dict[str, Any],
        theme: Theme = None
    ) -> float:
        """Calculate impact score for a recommendation"""
        base_score = recommendation.get("impact_score", 0)
        
        # Boost if linked to high-impact theme
        if theme:
            theme_impact = self.calculate_theme_impact_score(theme)
            base_score = (base_score + theme_impact) / 2
        
        # Factor in account metrics if available
        account_metrics = recommendation.get("account_metrics", {})
        arr = account_metrics.get("arr", 0)
        churn_risk = account_metrics.get("churn_risk", 0.5)
        
        # Higher ARR = higher impact
        arr_boost = min(2.0, arr / 100000)  # Cap at +2 points for $100k+ ARR
        
        # Higher churn risk = higher urgency = higher impact
        churn_boost = churn_risk * 1.5  # Up to +1.5 points
        
        final_score = base_score + arr_boost + churn_boost
        return min(10.0, max(0.0, final_score))
    
    async def update_theme_impact_scores(self, db: Session):
        """Update impact scores AND lost_deal_info aggregation for all themes with ARR weighting and lost deal tracking
        This ensures existing themes get the improved aggregation logic that groups ALL similar requests"""
        themes = db.query(Theme).all()
        updated_count = 0
        
        for theme in themes:
            # Get all feedback items linked to this theme (all similar requests in the cluster)
            feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
            
            if not feedback_items:
                continue
            
            # Recalculate lost_deal_info with improved aggregation (aggregates ALL feedback in theme)
            try:
                lost_deal_info = await self.detect_lost_deals_with_llm(theme, db)
                
                # Update theme metadata with recalculated lost_deal_info
                if not hasattr(theme, 'extra_metadata') or theme.extra_metadata is None:
                    theme.extra_metadata = {}
                theme.extra_metadata["lost_deal_info"] = lost_deal_info
                
                # Recalculate impact score with updated lost_deal_info
                theme.overall_impact_score = self.calculate_theme_impact_score(theme, db)
                updated_count += 1
            except Exception as e:
                print(f"  ⚠️ Error updating theme '{theme.name}': {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        db.commit()
        if updated_count > 0:
            print(f"  ✅ Updated {updated_count} themes with improved aggregation (ARR, lost deals, competitors from ALL feedback items)")
    
    async def get_data_justification_for_theme(self, theme_id: int, db: Session) -> Dict[str, Any]:
        """Get comprehensive data justification for a theme including strategic rationale, customer demand, and prioritization"""
        from core.llm_client import openrouter_client
        from core.database import Theme
        
        theme = db.query(Theme).filter(Theme.id == theme_id).first()
        if not theme:
            return {}
        
        # Get all feedback for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme_id).all()
        total_requests = len(feedback_items)
        total_arr = sum([f.arr for f in feedback_items if f.arr and f.arr > 0])
        arr_count = len([f for f in feedback_items if f.arr and f.arr > 0])
        avg_arr = total_arr / arr_count if arr_count > 0 else 0
        
        # Get lost deal info
        lost_deal_info = {}
        if theme.extra_metadata and theme.extra_metadata.get("lost_deal_info"):
            lost_deal_info = theme.extra_metadata["lost_deal_info"]
        
        lost_deal_count = lost_deal_info.get("lost_deal_count", 0)
        lost_deal_arr = lost_deal_info.get("lost_deal_arr", 0)
        competitor_mentions = lost_deal_info.get("competitor_mentions", [])
        
        # Get customer quotes
        customer_quotes = []
        for feedback in feedback_items[:10]:  # Top 10 quotes
            if feedback.content:
                customer_quotes.append({
                    "quote": feedback.content[:200],
                    "source": feedback.source,
                    "arr": feedback.arr or 0
                })
        
        # Generate strategic rationale using LLM
        strategic_rationale_prompt = f"""Based on this theme data, provide a detailed strategic rationale (400+ words):

Theme: {theme.name}
Description: {theme.description}
Impact Score: {theme.overall_impact_score}/10
Customer Value: {theme.customer_value}/10
Request Frequency: {total_requests} customer requests
Average ARR: ${avg_arr:,.0f}
Total ARR: ${total_arr:,.0f}
Lost Deals: {lost_deal_count}
Lost ARR: ${lost_deal_arr:,.0f}
Competitors Mentioned: {', '.join(competitor_mentions) if competitor_mentions else 'None'}

Provide a comprehensive strategic rationale explaining:
1. Why this theme is strategically important
2. How it addresses customer needs and competitive gaps
3. The business impact (revenue, retention, market position)
4. Why this should be prioritized
"""
        
        try:
            strategic_rationale = await openrouter_client.chat_completion([
                {"role": "system", "content": "You are a strategic product advisor. Provide detailed strategic rationale for product decisions."},
                {"role": "user", "content": strategic_rationale_prompt}
            ], temperature=0.7, max_tokens=2000)
        except:
            strategic_rationale = f"This theme addresses customer needs with {total_requests} requests, ${total_arr:,.0f} in ARR at stake, and {lost_deal_count} lost deals. Impact score of {theme.overall_impact_score}/10 indicates high strategic importance."
        
        # Generate customer demand evidence
        customer_demand_prompt = f"""Based on this data, provide customer demand evidence (300+ words):

Request Frequency: {total_requests} customer requests
Customer Value Score: {theme.customer_value}/10
Pain Level: Average from feedback
ARR Impact: ${avg_arr:,.0f} avg, ${total_arr:,.0f} total
Lost Deals: {lost_deal_count} deals lost
Competitor Mentions: {', '.join(competitor_mentions) if competitor_mentions else 'None'}

Provide specific evidence of customer demand including:
1. Request volume and frequency
2. Customer value and pain scores
3. ARR impact and lost deals
4. Competitive pressure
"""
        
        try:
            customer_demand = await openrouter_client.chat_completion([
                {"role": "system", "content": "You analyze customer demand data. Provide evidence-based assessment."},
                {"role": "user", "content": customer_demand_prompt}
            ], temperature=0.7, max_tokens=1500)
        except:
            customer_demand = f"Strong customer demand evidenced by {total_requests} requests, {theme.customer_value}/10 customer value score, and ${total_arr:,.0f} in ARR at stake. {lost_deal_count} lost deals indicate competitive pressure."
        
        # Generate prioritization recommendation
        prioritization_prompt = f"""Based on this data, provide prioritization recommendation (300+ words):

Impact Score: {theme.overall_impact_score}/10
Lost Deals: {lost_deal_count}
Lost ARR: ${lost_deal_arr:,.0f}
Competitor Pressure: {', '.join(competitor_mentions) if competitor_mentions else 'None'}
Request Frequency: {total_requests}
Customer Value: {theme.customer_value}/10

Recommend when to build this (Q1, Q2, Q3, Q4, or backlog) with detailed reasoning based on:
1. Lost deals urgency
2. ARR at risk
3. Competitive pressure
4. Impact score
5. Resource constraints
"""
        
        try:
            prioritization_recommendation = await openrouter_client.chat_completion([
                {"role": "system", "content": "You prioritize product features. Provide detailed prioritization recommendations."},
                {"role": "user", "content": prioritization_prompt}
            ], temperature=0.7, max_tokens=1500)
        except:
            prioritization_recommendation = f"Recommend prioritizing in next quarter due to {lost_deal_count} lost deals, ${lost_deal_arr:,.0f} in lost ARR, and impact score of {theme.overall_impact_score}/10."
        
        # Generate implementation guidance
        implementation_prompt = f"""Based on this theme, provide implementation guidance (300+ words):

Theme: {theme.name}
Feasibility: Based on impact score {theme.overall_impact_score}/10
Technical Complexity: Moderate (estimate based on feature type)
Business Priority: {'High' if lost_deal_count > 0 or theme.overall_impact_score > 7 else 'Medium' if theme.overall_impact_score > 5 else 'Low'}

Provide implementation guidance including:
1. Recommended approach and architecture
2. Estimated timeline and effort
3. Technical considerations
4. Dependencies and risks
5. Phased rollout strategy if applicable
"""
        
        try:
            implementation_guidance = await openrouter_client.chat_completion([
                {"role": "system", "content": "You provide technical implementation guidance. Be specific and actionable."},
                {"role": "user", "content": implementation_prompt}
            ], temperature=0.7, max_tokens=1500)
        except:
            implementation_guidance = f"Recommended implementation approach: Start with MVP to address core customer needs. Estimated timeline: 6-8 weeks for initial version. Consider phased rollout to validate with high-value customers first."
        
        return {
            "request_volume": total_requests,
            "total_arr_requested": round(total_arr, 2),
            "avg_customer_arr": round(avg_arr, 2),
            "lost_deal_count": lost_deal_count,
            "lost_deal_arr": round(lost_deal_arr, 2),
            "competitor_mentions": competitor_mentions,
            "customer_quotes_count": len(customer_quotes),
            "top_customer_quotes": customer_quotes[:5],
            "impact_score_breakdown": theme.extra_metadata.get("impact_score_breakdown", {}) if theme.extra_metadata else {},
            "strategic_rationale": strategic_rationale,
            "customer_demand": customer_demand,
            "prioritization_recommendation": prioritization_recommendation,
            "implementation_guidance": implementation_guidance,
            "feedback_cluster_summary": f"Cluster of {total_requests} similar customer requests related to {theme.name}. Includes feedback from {len(set([f.source for f in feedback_items if f.source]))} different sources."
        }


