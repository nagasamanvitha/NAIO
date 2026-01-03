from typing import Dict, List, Any, Optional
from core.database import Feedback, Theme, Recommendation, FeatureNotification
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import json

class QuarterlyReportGenerator:
    """Generate comprehensive quarterly product feedback intelligence reports"""
    
    def __init__(self):
        pass
    
    def get_quarter_dates(self, quarter: str, year: int) -> tuple[datetime, datetime]:
        """Get start and end dates for a quarter
        
        Q1 → Jan 1 – Mar 31
        Q2 → Apr 1 – Jun 30
        Q3 → Jul 1 – Sep 30
        Q4 → Oct 1 – Dec 31
        """
        quarter_map = {
            'Q1': (1, 3, 31),   # Jan 1 - Mar 31
            'Q2': (4, 6, 30),   # Apr 1 - Jun 30
            'Q3': (7, 9, 30),   # Jul 1 - Sep 30
            'Q4': (10, 12, 31)  # Oct 1 - Dec 31
        }
        
        if quarter not in quarter_map:
            raise ValueError(f"Invalid quarter: {quarter}. Must be Q1, Q2, Q3, or Q4")
        
        start_month, end_month, end_day = quarter_map[quarter]
        start_date = datetime(year, start_month, 1)
        end_date = datetime(year, end_month, end_day)
        
        return start_date, end_date
    
    def get_previous_quarter(self, quarter: str, year: int) -> tuple[str, int]:
        """Get previous quarter and year"""
        prev_map = {
            'Q1': ('Q4', year - 1),
            'Q2': ('Q1', year),
            'Q3': ('Q2', year),
            'Q4': ('Q3', year)
        }
        return prev_map[quarter]
    
    def get_next_quarter(self, quarter: str, year: int) -> tuple[str, int]:
        """Get next quarter and year"""
        next_map = {
            'Q1': ('Q2', year),
            'Q2': ('Q3', year),
            'Q3': ('Q4', year),
            'Q4': ('Q1', year + 1)
        }
        return next_map[quarter]
    
    async def generate_quarterly_report(
        self,
        quarter: str,
        year: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate comprehensive quarterly report for a specific quarter
        
        QUARTERLY FLOW LOGIC:
        - Q1 (Jan-Mar): Collect feedback → Generate themes → Recommend Q2 roadmap
        - Q2 (Apr-Jun): Build & ship Q1 recommendations → Track adoption → Report Q2 data + shipped features → Recommend Q3 roadmap
        - Q3 (Jul-Sep): Build & ship Q2 recommendations → Track adoption → Report Q3 data + shipped features → Recommend Q4 roadmap
        - Q4 (Oct-Dec): Build & ship Q3 recommendations → Track adoption → Report Q4 data + shipped features → Recommend next year Q1 roadmap
        
        KEY RULE: Insights from Quarter X → Roadmap for Quarter X+1
                  Features shipped in Quarter X → Reported in Quarter X report
        
        Quarter dates:
        - Q1 → Jan 1 – Mar 31
        - Q2 → Apr 1 – Jun 30
        - Q3 → Jul 1 – Sep 30
        - Q4 → Oct 1 – Dec 31
        
        Returns report with:
        - Executive Summary
        - Feedback Summary for the Quarter (data collected THIS quarter)
        - Top Themes of the Quarter (themes from THIS quarter)
        - Top Feature Requests This Quarter (requests from THIS quarter)
        - Feature Recommendations Ranked by Impact (from THIS quarter)
        - Roadmap Recommendation for Next Quarter (Q+1 based on THIS quarter's data)
        - Customer Quote Digest (This Quarter)
        - Deal Impact (This Quarter)
        - Shipped Feature Impact (features shipped THIS quarter, based on previous quarter's recommendations)
        - "New This Quarter" Highlights
        - Success Metrics for the Quarter
        """
        start_date, end_date = self.get_quarter_dates(quarter, year)
        prev_quarter, prev_year = self.get_previous_quarter(quarter, year)
        next_quarter, next_year = self.get_next_quarter(quarter, year)
        
        # Run independent operations in parallel for faster generation
        import asyncio
        
        # Group 1: Independent database queries (can run in parallel)
        feedback_summary, top_themes, top_feature_requests, ranked_recommendations, customer_quotes, deal_impact, shipped_impact, new_highlights, success_metrics = await asyncio.gather(
            self._generate_feedback_summary(start_date, end_date, prev_quarter, prev_year, db),
            self._generate_top_themes(start_date, end_date, db),
            self._generate_top_feature_requests(start_date, end_date, db),
            self._generate_ranked_recommendations(start_date, end_date, db),
            self._generate_customer_quote_digest(start_date, end_date, db),
            self._generate_deal_impact(start_date, end_date, db),
            self._generate_shipped_feature_impact(start_date, end_date, db),
            self._generate_new_highlights(start_date, end_date, prev_quarter, prev_year, db),
            self._generate_success_metrics(start_date, end_date, db)
        )
        
        # Group 2: Roadmap recommendation (depends on top_feature_requests, so run after)
        roadmap_recommendation = await self._generate_roadmap_recommendation(
            start_date, end_date, next_quarter, next_year, db
        )
        
        # Executive Summary
        executive_summary = self._generate_executive_summary(
            feedback_summary,
            top_themes,
            top_feature_requests,
            deal_impact,
            shipped_impact,
            success_metrics
        )
        
        return {
            "quarter": quarter,
            "year": year,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "display": f"{quarter} {year} ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
            },
            "generated_at": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "feedback_summary": feedback_summary,
            "top_themes": top_themes,
            "top_feature_requests": top_feature_requests,
            "ranked_recommendations": ranked_recommendations,
            "roadmap_recommendation": roadmap_recommendation,
            "customer_quotes": customer_quotes,
            "deal_impact": deal_impact,
            "shipped_feature_impact": shipped_impact,
            "new_highlights": new_highlights,
            "success_metrics": success_metrics
        }
    
    async def _generate_feedback_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_quarter: str,
        prev_year: int,
        db: Session
    ) -> Dict[str, Any]:
        """Generate feedback summary for the quarter"""
        # Get feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        # Get previous quarter feedback for comparison
        prev_start, prev_end = self.get_quarter_dates(prev_quarter, prev_year)
        prev_quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= prev_start,
                Feedback.created_at <= prev_end
            )
        ).all()
        
        # Source breakdown
        source_breakdown = {}
        for feedback in quarter_feedback:
            source = feedback.source or "unknown"
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        # Calculate growth
        current_count = len(quarter_feedback)
        prev_count = len(prev_quarter_feedback)
        growth_percentage = ((current_count - prev_count) / prev_count * 100) if prev_count > 0 else 0
        
        # Coverage calculation (sources with data)
        sources_with_data = len([s for s in source_breakdown.keys() if source_breakdown[s] > 0])
        total_sources = 8  # Zendesk, Intercom, Sales, NPS, Reviews, Gong, Dovetail, Forum/Social
        coverage_percentage = (sources_with_data / total_sources * 100)
        
        return {
            "total_feedback_items": current_count,
            "previous_quarter_count": prev_count,
            "growth_percentage": round(growth_percentage, 1),
            "growth_direction": "up" if growth_percentage > 0 else "down" if growth_percentage < 0 else "stable",
            "source_breakdown": source_breakdown,
            "sources_covered": sources_with_data,
            "coverage_percentage": round(coverage_percentage, 1),
            "total_sources": total_sources
        }
    
    async def _generate_top_themes(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate top themes for the quarter - ONLY data from this quarter"""
        # Get feedback ONLY from this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        theme_ids = list(set([f.theme_id for f in quarter_feedback if f.theme_id]))
        
        if not theme_ids:
            return []
        
        # Get themes that have feedback in this quarter
        themes = db.query(Theme).filter(Theme.id.in_(theme_ids)).all()
        
        theme_data = []
        for theme in themes:
            # Get feedback for this theme ONLY in this quarter
            theme_feedback = [f for f in quarter_feedback if f.theme_id == theme.id]
            
            if not theme_feedback:
                continue  # Skip if no feedback in this quarter
            
            # Calculate ARR ONLY from this quarter's feedback
            quarter_arr = sum([f.arr for f in theme_feedback if f.arr and f.arr > 0])
            arr_feedback_count = len([f for f in theme_feedback if f.arr and f.arr > 0])
            avg_arr = quarter_arr / arr_feedback_count if arr_feedback_count > 0 else 0
            
            # Get lost deal info ONLY from this quarter's feedback
            lost_deal_keywords = ["lost deal", "competitor won", "went with", "chose competitor", "switched to", "moved to", "cancelled because", "churned due to", "lost to", "competitor", "switching", "churn", "cancel"]
            quarter_lost_deals = []
            quarter_lost_deal_arr = 0
            quarter_competitor_mentions = set()
            
            for feedback in theme_feedback:
                if not feedback.content:
                    continue
                content_lower = feedback.content.lower()
                if any(keyword in content_lower for keyword in lost_deal_keywords):
                    quarter_lost_deals.append(feedback)
                    if feedback.arr:
                        quarter_lost_deal_arr += feedback.arr
                    # Extract competitor mentions from this quarter's feedback
                    from core.database import Competitor
                    existing_competitors = db.query(Competitor).all()
                    competitor_names_lower = {c.name.lower(): c.name for c in existing_competitors}
                    for comp_lower, comp_name in competitor_names_lower.items():
                        if comp_lower in content_lower:
                            quarter_competitor_mentions.add(comp_name)
            
            # Calculate trend velocity based on this quarter vs previous quarter
            # Determine current quarter
            if start_date.month <= 3:
                current_q = 'Q1'
            elif start_date.month <= 6:
                current_q = 'Q2'
            elif start_date.month <= 9:
                current_q = 'Q3'
            else:
                current_q = 'Q4'
            
            prev_quarter, prev_year = self.get_previous_quarter(current_q, start_date.year)
            prev_start, prev_end = self.get_quarter_dates(prev_quarter, prev_year)
            
            prev_quarter_feedback = db.query(Feedback).filter(
                and_(
                    Feedback.theme_id == theme.id,
                    Feedback.created_at >= prev_start,
                    Feedback.created_at <= prev_end
                )
            ).count()
            current_requests = len(theme_feedback)
            trend_velocity = (current_requests - prev_quarter_feedback) / max(prev_quarter_feedback, 1) if prev_quarter_feedback > 0 else (1.0 if current_requests > 0 else 0.0)
            
            theme_data.append({
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "request_frequency": len(theme_feedback),  # ONLY this quarter
                "impact_score": theme.overall_impact_score or 0,  # Overall impact (can keep this)
                "quarter_arr": round(quarter_arr, 2),  # ONLY this quarter
                "avg_arr": round(avg_arr, 2),  # ONLY this quarter
                "lost_deal_count": len(quarter_lost_deals),  # ONLY this quarter
                "lost_deal_arr": round(quarter_lost_deal_arr, 2),  # ONLY this quarter
                "competitor_mentions": list(quarter_competitor_mentions),  # ONLY this quarter
                "trend_velocity": round(trend_velocity, 2),
                "is_new": theme.created_at >= start_date if theme.created_at else False,
                "quarter_only": True,  # Flag to indicate this is quarter-specific data
                "period_label": f"{'Q1' if start_date.month <= 3 else 'Q2' if start_date.month <= 6 else 'Q3' if start_date.month <= 9 else 'Q4'} {start_date.year}"  # Add period label
            })
        
        # Sort by request frequency in this quarter (not overall impact)
        theme_data.sort(key=lambda x: (x["request_frequency"], x["quarter_arr"]), reverse=True)
        
        return theme_data[:10]  # Top 10 themes for this quarter
    
    async def _generate_top_feature_requests(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate top feature requests for the quarter"""
        # Get recommendations created in this quarter or linked to themes with feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        theme_ids = list(set([f.theme_id for f in quarter_feedback if f.theme_id]))
        
        if not theme_ids:
            return []
        
        # Get recommendations linked to these themes
        recommendations = db.query(Recommendation).filter(
            Recommendation.feature.in_([t.name for t in db.query(Theme).filter(Theme.id.in_(theme_ids)).all()])
        ).all()
        
        feature_requests = []
        for rec in recommendations:
            # Get theme for this recommendation
            theme = db.query(Theme).filter(Theme.name == rec.feature).first()
            if not theme:
                continue
            
            # Get feedback for this theme in this quarter
            theme_feedback = [f for f in quarter_feedback if f.theme_id == theme.id]
            
            # Calculate metrics for this quarter
            quarter_arr = sum([f.arr for f in theme_feedback if f.arr and f.arr > 0])
            avg_arr = quarter_arr / len([f for f in theme_feedback if f.arr and f.arr > 0]) if len([f for f in theme_feedback if f.arr and f.arr > 0]) > 0 else 0
            
            # Get lost deal info
            lost_deal_info = {}
            competitor_mentions = []
            if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
                competitor_mentions = lost_deal_info.get("competitor_mentions", [])
            
            # Get customer quotes
            customer_quotes = []
            if rec.customer_quotes:
                if isinstance(rec.customer_quotes, list):
                    customer_quotes = rec.customer_quotes[:3]  # Top 3 quotes
                else:
                    customer_quotes = [rec.customer_quotes]
            
            feature_requests.append({
                "id": rec.id,
                "title": rec.title,
                "feature": rec.feature,
                "description": rec.description,
                "impact_score": rec.impact_score or 0,
                "request_frequency": len(theme_feedback),
                "quarter_arr": round(quarter_arr, 2),
                "avg_arr": round(avg_arr, 2),
                "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),
                "competitor_mentions": competitor_mentions,
                "pain_score": theme.customer_value or 0,
                "urgency": "high" if lost_deal_info.get("has_lost_deals", False) else "medium",
                "customer_quotes": customer_quotes,
                "status": rec.status
            })
        
        # Sort by impact score
        feature_requests.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return feature_requests[:15]  # Top 15 feature requests
    
    async def _generate_ranked_recommendations(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate ranked feature recommendations based on impact score for this quarter"""
        # Get recommendations linked to themes with feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        theme_ids = list(set([f.theme_id for f in quarter_feedback if f.theme_id]))
        
        if not theme_ids:
            return []
        
        # Get themes with feedback in this quarter
        themes = db.query(Theme).filter(Theme.id.in_(theme_ids)).all()
        theme_names = [t.name for t in themes]
        
        if not theme_names:
            return []
        
        # Get recommendations for themes with feedback in this quarter
        recommendations = db.query(Recommendation).filter(
            Recommendation.feature.in_(theme_names)
        ).all()
        
        ranked_data = []
        for rec in recommendations:
            # Find associated theme by name
            theme = next((t for t in themes if t.name == rec.feature), None)
            if not theme:
                continue
            
            # Get feedback for this theme in this quarter
            theme_feedback = [f for f in quarter_feedback if f.theme_id == theme.id]
            if not theme_feedback:
                continue
            
            # Calculate quarter-specific metrics
            quarter_arr = sum([f.arr for f in theme_feedback if f.arr and f.arr > 0])
            lost_deal_keywords = ["lost deal", "competitor won", "went with", "chose competitor", "switched to", "moved to", "cancelled because", "churned due to", "lost to"]
            lost_deal_count = len([f for f in theme_feedback if any(kw in (f.content or "").lower() for kw in lost_deal_keywords)])
            
            ranked_data.append({
                "id": rec.id,
                "title": rec.title,
                "feature": rec.feature,
                "description": rec.description,
                "impact_score": rec.impact_score or 0,
                "feasibility_score": rec.feasibility_score or 0,
                "risk_score": rec.risk_score or 0,
                "status": rec.status,
                "quarter_arr": round(quarter_arr, 2),
                "request_frequency": len(theme_feedback),
                "lost_deal_count": lost_deal_count,
                "priority": "P0" if rec.impact_score and rec.impact_score >= 8 else "P1" if rec.impact_score and rec.impact_score >= 6 else "P2"
            })
        
        # Sort by impact score descending
        ranked_data.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return ranked_data[:10]  # Top 10 ranked recommendations
    
    async def _generate_roadmap_recommendation(
        self,
        start_date: datetime,
        end_date: datetime,
        next_quarter: str,
        next_year: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate roadmap recommendation for NEXT quarter based on CURRENT quarter's data
        
        Flow: Current Quarter (Q) data → Recommendations for Next Quarter (Q+1)
        Example: Q1 data → Q2 roadmap recommendations
        """
        # Get top feature requests from this quarter
        top_requests = await self._generate_top_feature_requests(start_date, end_date, db)
        
        # Select top features for next quarter roadmap
        recommended_features = []
        for req in top_requests[:8]:  # Top 8 for next quarter
            # Get full recommendation data
            rec = db.query(Recommendation).filter(Recommendation.id == req["id"]).first()
            if not rec:
                continue
            
            # Get theme
            theme = db.query(Theme).filter(Theme.name == rec.feature).first()
            
            # Get customer quotes with data justification
            customer_quotes = []
            if rec.customer_quotes:
                if isinstance(rec.customer_quotes, list):
                    customer_quotes = rec.customer_quotes[:5]
                else:
                    customer_quotes = [rec.customer_quotes]
            
            # Determine which teams benefit
            teams_benefit = []
            if req.get("lost_deal_count", 0) > 0:
                teams_benefit.append("Sales")
            if req.get("request_frequency", 0) > 10:
                teams_benefit.append("Customer Success")
            if rec.feasibility_score and rec.feasibility_score > 7:
                teams_benefit.append("Engineering")
            if not teams_benefit:
                teams_benefit = ["Product", "All Teams"]
            
            # Risk of not doing it
            risk_level = "high"
            risk_reasons = []
            if req.get("lost_deal_count", 0) > 0:
                risk_level = "critical"
                risk_reasons.append(f"{req.get('lost_deal_count', 0)} lost deals (${req.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk)")
            elif req.get("competitor_mentions"):
                risk_level = "high"
                risk_reasons.append(f"Competitive pressure from {', '.join(req.get('competitor_mentions', [])[:2])}")
            elif req.get("request_frequency", 0) > 20:
                risk_level = "high"
                risk_reasons.append(f"High demand ({req.get('request_frequency', 0)} requests)")
            else:
                risk_level = "medium"
                risk_reasons.append("Moderate customer demand")
            
            # Estimated timeline
            if rec.feasibility_score:
                if rec.feasibility_score >= 8:
                    timeline = next_quarter
                    estimated_weeks = "6-8 weeks"
                elif rec.feasibility_score >= 6:
                    timeline = next_quarter
                    estimated_weeks = "8-12 weeks"
                else:
                    timeline = f"{next_quarter} or {self.get_next_quarter(next_quarter, next_year)[0]}"
                    estimated_weeks = "12+ weeks"
            else:
                timeline = next_quarter
                estimated_weeks = "8-10 weeks"
            
            recommended_features.append({
                "id": rec.id,
                "title": rec.title,
                "feature": rec.feature,
                "summary": rec.description[:200] + "..." if len(rec.description) > 200 else rec.description,
                "why_this_matters_now": self._generate_why_this_matters(req, rec),
                "top_customer_quotes": customer_quotes,
                "arr_impact_potential": {
                    "total_arr_requested": req.get("quarter_arr", 0),
                    "avg_customer_arr": req.get("avg_arr", 0),
                    "lost_deal_arr": req.get("lost_deal_arr", 0),
                    "customers_affected": req.get("request_frequency", 0)
                },
                "teams_benefit": teams_benefit,
                "risk_of_not_doing_it": {
                    "level": risk_level,
                    "reasons": risk_reasons,
                    "impact": f"${req.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk" if req.get("lost_deal_arr", 0) > 0 else "Customer satisfaction impact"
                },
                "estimated_timeline": {
                    "quarter": timeline,
                    "weeks": estimated_weeks,
                    "feasibility_score": rec.feasibility_score or 0
                },
                "alternatives_considered": self._generate_alternatives_considered(rec, theme),
                "impact_score": rec.impact_score or 0,
                "priority": "P0" if risk_level == "critical" else "P1" if risk_level == "high" else "P2"
            })
        
        return {
            "next_quarter": next_quarter,
            "next_year": next_year,
            "recommended_features": recommended_features,
            "total_recommended": len(recommended_features),
            "total_arr_at_stake": sum([f["arr_impact_potential"]["lost_deal_arr"] for f in recommended_features]),
            "critical_features": len([f for f in recommended_features if f["risk_of_not_doing_it"]["level"] == "critical"])
        }
    
    def _generate_why_this_matters(self, req: Dict[str, Any], rec: Recommendation) -> str:
        """Generate data-driven justification for why this matters now"""
        reasons = []
        
        if req.get("lost_deal_count", 0) > 0:
            reasons.append(f"🚨 {req.get('lost_deal_count', 0)} lost deals (${req.get('lost_deal_arr', 0)/1000:.0f}K ARR at risk)")
        
        if req.get("request_frequency", 0) > 0:
            reasons.append(f"📊 {req.get('request_frequency', 0)} customer requests this quarter")
        
        if req.get("competitor_mentions"):
            reasons.append(f"⚔️ Competitive pressure from {', '.join(req.get('competitor_mentions', [])[:2])}")
        
        if req.get("avg_arr", 0) > 50000:
            reasons.append(f"💰 High-value customers affected (${req.get('avg_arr', 0)/1000:.0f}K avg ARR)")
        
        if req.get("pain_score", 0) > 7:
            reasons.append(f"😰 High pain score ({req.get('pain_score', 0):.1f}/10)")
        
        if not reasons:
            reasons.append("📈 Growing customer demand")
        
        return " | ".join(reasons)
    
    def _generate_alternatives_considered(self, rec: Recommendation, theme: Optional[Theme]) -> List[str]:
        """Generate alternatives considered"""
        alternatives = []
        
        if rec.evidence and isinstance(rec.evidence, dict):
            evaluations = rec.evidence.get("evaluations", {})
            engineering = evaluations.get("engineering", {})
            
            if engineering.get("alternatives"):
                alternatives.extend(engineering.get("alternatives", []))
        
        if not alternatives:
            alternatives = [
                "Do nothing (not recommended - high risk)",
                "Partial implementation (may not address core need)",
                "Third-party integration (evaluation needed)"
            ]
        
        return alternatives[:3]  # Top 3 alternatives
    
    async def _generate_customer_quote_digest(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Generate customer quote digest for the quarter"""
        # Get feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).order_by(Feedback.created_at.desc()).all()
        
        # Group quotes by theme
        quotes_by_theme = {}
        for feedback in quarter_feedback:
            if not feedback.theme_id or not feedback.content:
                continue
            
            theme = db.query(Theme).filter(Theme.id == feedback.theme_id).first()
            if not theme:
                continue
            
            theme_name = theme.name
            if theme_name not in quotes_by_theme:
                quotes_by_theme[theme_name] = []
            
            quotes_by_theme[theme_name].append({
                "quote": feedback.content[:300] + "..." if len(feedback.content) > 300 else feedback.content,
                "source": feedback.source or "Unknown",
                "arr": feedback.arr or 0,
                "sentiment": feedback.sentiment_score or 0,
                "date": feedback.created_at.isoformat() if feedback.created_at else None
            })
        
        # Get top quotes (by ARR or sentiment)
        all_quotes = []
        for theme_name, quotes in quotes_by_theme.items():
            # Sort by ARR or sentiment
            quotes.sort(key=lambda x: x["arr"] if x["arr"] > 0 else abs(x["sentiment"]), reverse=True)
            all_quotes.extend(quotes[:3])  # Top 3 per theme
        
        # Sort all quotes
        all_quotes.sort(key=lambda x: x["arr"] if x["arr"] > 0 else abs(x["sentiment"]), reverse=True)
        
        return {
            "total_quotes": len(quarter_feedback),
            "quotes_by_theme": quotes_by_theme,
            "top_quotes": all_quotes[:20],  # Top 20 quotes
            "themes_with_quotes": len(quotes_by_theme)
        }
    
    async def _generate_deal_impact(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Generate deal impact for the quarter"""
        # Get feedback in this quarter that indicates lost deals
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        lost_deal_keywords = [
            "lost deal", "competitor won", "went with", "chose competitor",
            "switched to", "moved to", "cancelled because", "churned due to",
            "lost to", "competitor", "switching", "churn", "cancel"
        ]
        
        lost_deals = []
        total_lost_arr = 0
        competitor_mentions = set()
        
        for feedback in quarter_feedback:
            if not feedback.content:
                continue
            
            content_lower = feedback.content.lower()
            if any(keyword in content_lower for keyword in lost_deal_keywords):
                lost_deals.append({
                    "feedback_id": feedback.id,
                    "content": feedback.content[:200],
                    "arr": feedback.arr or 0,
                    "source": feedback.source,
                    "date": feedback.created_at.isoformat() if feedback.created_at else None
                })
                if feedback.arr:
                    total_lost_arr += feedback.arr
        
        # Get themes with lost deals
        themes_with_lost_deals = []
        for feedback in quarter_feedback:
            if feedback.theme_id:
                theme = db.query(Theme).filter(Theme.id == feedback.theme_id).first()
                if theme and theme.extra_metadata:
                    lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
                    if lost_deal_info.get("has_lost_deals", False):
                        themes_with_lost_deals.append({
                            "theme_id": theme.id,
                            "theme_name": theme.name,
                            "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                            "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),
                            "competitor_mentions": lost_deal_info.get("competitor_mentions", [])
                        })
                        competitor_mentions.update(lost_deal_info.get("competitor_mentions", []))
        
        # Remove duplicates
        seen_themes = set()
        unique_themes = []
        for theme in themes_with_lost_deals:
            if theme["theme_id"] not in seen_themes:
                seen_themes.add(theme["theme_id"])
                unique_themes.append(theme)
        
        return {
            "lost_deals_count": len(lost_deals),
            "total_lost_arr": round(total_lost_arr, 2),
            "lost_deals": lost_deals[:10],  # Top 10 lost deals
            "themes_with_lost_deals": unique_themes,
            "competitor_mentions": list(competitor_mentions),
            "churn_risks": len([f for f in quarter_feedback if f.churn_risk and f.churn_risk > 0.7]),
            "enterprise_blockers": len([f for f in quarter_feedback if f.user_segment and "enterprise" in f.user_segment.lower() and f.urgency == "critical"])
        }
    
    async def _generate_shipped_feature_impact(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate shipped feature impact for the CURRENT quarter
        
        Shows features that were shipped DURING this quarter.
        These features were recommended in the PREVIOUS quarter's report.
        
        Example: Q2 report shows features shipped in Q2 (which were recommended in Q1 report)
        """
        # Get recommendations that were shipped in this quarter
        # Use created_at since Recommendation model doesn't have updated_at
        # Check if shipped_at is in extra_metadata, otherwise use created_at
        shipped_recommendations = db.query(Recommendation).filter(
            Recommendation.status == "shipped"
        ).all()
        
        # Filter by quarter - check if shipped_at in extra_metadata or use created_at
        quarter_shipped = []
        for rec in shipped_recommendations:
            shipped_date = None
            if rec.extra_metadata and rec.extra_metadata.get("shipped_at"):
                try:
                    # Parse shipped_at date
                    shipped_at_str = rec.extra_metadata["shipped_at"]
                    # Remove timezone info if present to make it naive
                    if 'Z' in shipped_at_str or '+' in shipped_at_str or shipped_at_str.count('-') > 2:
                        # Has timezone, remove it
                        shipped_at_str = shipped_at_str.split('+')[0].split('Z')[0].split('.')[0]
                    shipped_date = datetime.fromisoformat(shipped_at_str)
                    # Ensure it's naive (no timezone)
                    if shipped_date.tzinfo is not None:
                        shipped_date = shipped_date.replace(tzinfo=None)
                except Exception as e:
                    # If parsing fails, use created_at
                    shipped_date = rec.created_at
            else:
                shipped_date = rec.created_at
            
            # Ensure created_at is also naive for comparison
            if shipped_date and shipped_date.tzinfo is not None:
                shipped_date = shipped_date.replace(tzinfo=None)
            
            # Ensure start_date and end_date are naive
            start_date_naive = start_date.replace(tzinfo=None) if start_date.tzinfo else start_date
            end_date_naive = end_date.replace(tzinfo=None) if end_date.tzinfo else end_date
            
            if shipped_date and start_date_naive <= shipped_date <= end_date_naive:
                quarter_shipped.append(rec)
        
        shipped_recommendations = quarter_shipped
        
        shipped_features = []
        for rec in shipped_recommendations:
            # Get adoption stats
            notifications = db.query(FeatureNotification).filter(
                FeatureNotification.feature_id == rec.id
            ).all()
            
            total_notified = len(notifications)
            adopted = sum(1 for n in notifications if n.adoption_rate and n.adoption_rate > 0.5)
            adoption_rate = (adopted / total_notified * 100) if total_notified > 0 else 0
            
            # Get theme for original request volume
            theme = db.query(Theme).filter(Theme.name == rec.feature).first()
            original_requests = 0
            if theme:
                original_requests = db.query(Feedback).filter(Feedback.theme_id == theme.id).count()
            
            # Get shipped date from extra_metadata or use created_at
            shipped_date = None
            if rec.extra_metadata and rec.extra_metadata.get("shipped_at"):
                shipped_date = rec.extra_metadata["shipped_at"]
            else:
                shipped_date = rec.created_at.isoformat() if rec.created_at else None
            
            shipped_features.append({
                "id": rec.id,
                "title": rec.title,
                "feature": rec.feature,
                "shipped_date": shipped_date,
                "original_request_volume": original_requests,
                "total_notified": total_notified,
                "adopted": adopted,
                "adoption_rate": round(adoption_rate, 1),
                "impact_score": rec.impact_score or 0
            })
        
        return {
            "features_shipped": len(shipped_features),
            "shipped_features": shipped_features,
            "total_adoption_rate": round(
                sum([f["adoption_rate"] for f in shipped_features]) / len(shipped_features) if shipped_features else 0,
                1
            ),
            "total_notified": sum([f["total_notified"] for f in shipped_features]),
            "total_adopted": sum([f["adopted"] for f in shipped_features])
        }
    
    async def _generate_new_highlights(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_quarter: str,
        prev_year: int,
        db: Session
    ) -> Dict[str, Any]:
        """Generate new highlights for the quarter"""
        # Get themes created in this quarter
        quarter_themes = db.query(Theme).filter(
            and_(
                Theme.created_at >= start_date,
                Theme.created_at <= end_date
            )
        ).all()
        
        # Get previous quarter themes for comparison
        prev_start, prev_end = self.get_quarter_dates(prev_quarter, prev_year)
        prev_themes = db.query(Theme).filter(
            and_(
                Theme.created_at >= prev_start,
                Theme.created_at <= prev_end
            )
        ).all()
        
        # Get feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        # New bugs (negative sentiment, bug classification)
        new_bugs = [f for f in quarter_feedback if 
                   (f.sentiment_score and f.sentiment_score < -0.3) or 
                   (f.classification and "bug" in f.classification.lower())]
        
        # New feature themes
        new_feature_themes = [t for t in quarter_themes if t.customer_value and t.customer_value > 7]
        
        # Sudden spikes (themes with high trend velocity)
        sudden_spikes = [t for t in quarter_themes if t.trend_velocity and t.trend_velocity > 0.5]
        
        # Social media negative trend (negative sentiment from social sources)
        social_negative = [f for f in quarter_feedback if 
                          f.source and ("social" in f.source.lower() or "forum" in f.source.lower()) and
                          f.sentiment_score and f.sentiment_score < -0.3]
        
        return {
            "new_themes": len(quarter_themes),
            "new_bugs": {
                "count": len(new_bugs),
                "top_bugs": [{"id": f.id, "content": f.content[:150], "source": f.source} for f in new_bugs[:5]]
            },
            "new_feature_themes": {
                "count": len(new_feature_themes),
                "themes": [{"id": t.id, "name": t.name, "impact_score": t.overall_impact_score or 0} for t in new_feature_themes[:5]]
            },
            "sudden_spikes": {
                "count": len(sudden_spikes),
                "themes": [{"id": t.id, "name": t.name, "trend_velocity": t.trend_velocity or 0} for t in sudden_spikes[:5]]
            },
            "social_negative_trend": {
                "count": len(social_negative),
                "items": [{"id": f.id, "content": f.content[:150], "sentiment": f.sentiment_score} for f in social_negative[:5]]
            },
            "growth_vs_previous": {
                "themes_growth": len(quarter_themes) - len(prev_themes),
                "feedback_growth": len(quarter_feedback) - len(db.query(Feedback).filter(
                    and_(
                        Feedback.created_at >= prev_start,
                        Feedback.created_at <= prev_end
                    )
                ).all())
            }
        }
    
    async def _generate_success_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Generate success metrics for the quarter"""
        # Get feedback in this quarter
        quarter_feedback = db.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).all()
        
        # Get themes created in this quarter
        quarter_themes = db.query(Theme).filter(
            and_(
                Theme.created_at >= start_date,
                Theme.created_at <= end_date
            )
        ).all()
        
        # Get recommendations created in this quarter (customer-driven roadmap items)
        quarter_recommendations = db.query(Recommendation).filter(
            and_(
                Recommendation.created_at >= start_date,
                Recommendation.created_at <= end_date
            )
        ).all()
        
        # Calculate PM time saved
        # Manual processing: ~5 minutes per feedback item (reading, categorizing, tagging)
        # Automated processing: ~0.1 minutes per item (AI does the work)
        total_feedback = len(quarter_feedback)
        manual_time_per_item_minutes = 5.0
        automated_time_per_item_minutes = 0.1
        time_saved_per_item = manual_time_per_item_minutes - automated_time_per_item_minutes
        
        total_manual_time_hours = (total_feedback * manual_time_per_item_minutes) / 60.0
        total_automated_time_hours = (total_feedback * automated_time_per_item_minutes) / 60.0
        pm_time_saved_hours = (total_feedback * time_saved_per_item) / 60.0
        
        # Calculate % roadmap customer-driven
        # Get all recommendations (not just this quarter) to see total roadmap
        all_recommendations = db.query(Recommendation).all()
        total_roadmap_items = len(all_recommendations)
        customer_driven_items = len(quarter_recommendations)  # Recommendations from this quarter's feedback
        
        # Also count recommendations that are based on themes with feedback
        # Filter recommendations where feature name matches any quarter theme name
        quarter_theme_names = [t.name for t in quarter_themes]
        theme_based_recommendations = db.query(Recommendation).filter(
            Recommendation.feature.in_(quarter_theme_names)
        ).all()
        
        # Unique customer-driven recommendations
        customer_driven_set = set([r.id for r in quarter_recommendations] + [r.id for r in theme_based_recommendations])
        customer_driven_count = len(customer_driven_set)
        
        roadmap_customer_driven_percentage = (customer_driven_count / total_roadmap_items * 100) if total_roadmap_items > 0 else 0
        
        # Feedback coverage % (already calculated in feedback_summary, but include here for completeness)
        source_breakdown = {}
        for feedback in quarter_feedback:
            source = feedback.source or "unknown"
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        sources_with_data = len([s for s in source_breakdown.keys() if source_breakdown[s] > 0])
        total_sources = 8  # Zendesk, Intercom, Sales, NPS, Reviews, Gong, Dovetail, Forum/Social
        coverage_percentage = (sources_with_data / total_sources * 100)
        
        # Number of themes discovered
        themes_discovered = len(quarter_themes)
        
        return {
            "feedback_coverage_percentage": round(coverage_percentage, 1),
            "sources_covered": sources_with_data,
            "total_sources": total_sources,
            "pm_time_saved_hours": round(pm_time_saved_hours, 1),
            "pm_time_saved_days": round(pm_time_saved_hours / 8.0, 1),  # Assuming 8-hour workday
            "total_manual_time_hours": round(total_manual_time_hours, 1),
            "total_automated_time_hours": round(total_automated_time_hours, 1),
            "total_feedback_processed": total_feedback,
            "roadmap_customer_driven_percentage": round(roadmap_customer_driven_percentage, 1),
            "customer_driven_roadmap_items": customer_driven_count,
            "total_roadmap_items": total_roadmap_items,
            "themes_discovered": themes_discovered,
            "efficiency_improvement": round((pm_time_saved_hours / total_manual_time_hours * 100) if total_manual_time_hours > 0 else 0, 1)
        }
    
    def _generate_executive_summary(
        self,
        feedback_summary: Dict[str, Any],
        top_themes: List[Dict[str, Any]],
        top_feature_requests: List[Dict[str, Any]],
        deal_impact: Dict[str, Any],
        shipped_impact: Dict[str, Any],
        success_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary"""
        total_arr_at_stake = sum([t.get("lost_deal_arr", 0) for t in top_themes])
        total_lost_deals = sum([t.get("lost_deal_count", 0) for t in top_themes])
        
        return {
            "key_metrics": {
                "total_feedback": feedback_summary.get("total_feedback_items", 0),
                "feedback_growth": feedback_summary.get("growth_percentage", 0),
                "top_themes_count": len(top_themes),
                "top_feature_requests": len(top_feature_requests),
                "total_arr_at_stake": round(total_arr_at_stake, 2),
                "lost_deals": total_lost_deals,
                "features_shipped": shipped_impact.get("features_shipped", 0),
                "average_adoption_rate": shipped_impact.get("total_adoption_rate", 0)
            },
            "key_insights": [
                f"Collected {feedback_summary.get('total_feedback_items', 0)} feedback items ({feedback_summary.get('growth_percentage', 0):.1f}% {'growth' if feedback_summary.get('growth_percentage', 0) > 0 else 'decline'} vs previous quarter)",
                f"Identified {len(top_themes)} top themes with ${total_arr_at_stake/1000:.0f}K ARR at stake",
                f"{total_lost_deals} lost deals attributed to missing features",
                f"Shipped {shipped_impact.get('features_shipped', 0)} features with {shipped_impact.get('total_adoption_rate', 0):.1f}% average adoption rate"
            ],
            "recommendations": [
                "Prioritize features addressing lost deals to protect revenue",
                "Focus on high-impact themes with strong customer demand",
                "Monitor adoption of shipped features to validate product-market fit"
            ],
            "success_metrics": {
                "pm_time_saved_hours": success_metrics.get("pm_time_saved_hours", 0),
                "roadmap_customer_driven_percentage": success_metrics.get("roadmap_customer_driven_percentage", 0),
                "themes_discovered": success_metrics.get("themes_discovered", 0),
                "feedback_coverage_percentage": success_metrics.get("feedback_coverage_percentage", 0)
            }
        }

