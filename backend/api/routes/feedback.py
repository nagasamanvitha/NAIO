from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from core.database import Feedback, Theme, get_db
from core.data_processor import DataProcessor
from core.clustering import FeedbackClustering
from core.impact_scoring import ImpactScorer
from datetime import datetime, timedelta

router = APIRouter()
data_processor = DataProcessor()
clustering = FeedbackClustering()
impact_scorer = ImpactScorer()

# Cache for theme clustering (to avoid expensive operations on every request)
_theme_cluster_cache = {}
_cache_timestamp = {}
CACHE_DURATION = timedelta(seconds=30)  # Cache for 30 seconds

async def _get_theme_data(theme: Theme, db: Session) -> Dict[str, Any]:
    """Helper function to extract theme data with ARR, lost deals, competitors, impact score, and pain score
    
    AGGREGATES DATA FROM ALL FEEDBACK ITEMS in the theme cluster.
    
    Returns comprehensive theme data including:
    - Competitors: Full competitor information (from ALL feedback items)
    - ARR value: Total and average ARR (aggregated from ALL feedback items)
    - Lost deals: Count and ARR value of lost deals (from ALL feedback items)
    - Impact score: Overall impact score
    - Pain score: Average pain level from ALL feedback items
    """
    from core.database import Competitor
    
    # Get ALL feedback items grouped in this theme (all similar requests)
    theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
    
    # AGGREGATE ARR from ALL feedback items in the theme
    total_arr_from_feedback = sum([f.arr for f in theme_feedback if f.arr and f.arr > 0]) if theme_feedback else 0
    arr_count = len([f for f in theme_feedback if f.arr and f.arr > 0])
    avg_arr_from_feedback = total_arr_from_feedback / arr_count if arr_count > 0 else 0
    
    # Calculate pain score from ALL feedback items (average pain_level of all similar requests)
    pain_scores = [f.pain_level for f in theme_feedback if f.pain_level and f.pain_level > 0]
    pain_score = sum(pain_scores) / len(pain_scores) if pain_scores else (theme.customer_value or 0.0)
    
    # Extract lost deal info from extra_metadata (already aggregated from all feedback items during theme creation)
    lost_deal_info = {}
    if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
        lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
    
    # AGGREGATE competitors from ALL feedback items in the theme (not just lost deals)
    all_competitor_mentions = set()
    
    # Get competitor mentions from lost_deal_info (already aggregated)
    if lost_deal_info.get("competitor_mentions"):
        all_competitor_mentions.update(lost_deal_info.get("competitor_mentions", []))
    
    # Also scan ALL feedback items for competitor mentions
    existing_competitors = db.query(Competitor).all()
    competitor_names_lower = {c.name.lower(): c.name for c in existing_competitors}
    
    for feedback in theme_feedback:
        if feedback.content:
            content_lower = feedback.content.lower()
            # Check for competitor mentions in feedback content
            for comp_lower, comp_name in competitor_names_lower.items():
                if comp_lower in content_lower:
                    all_competitor_mentions.add(comp_name)
    
    # Enrich with mock data if needed
    if not lost_deal_info or lost_deal_info.get("estimated_avg_arr", 0) == 0:
        from core.mock_competitor_enrichment import enrich_theme_with_mock_competitor_data
        enriched_data = enrich_theme_with_mock_competitor_data(
            theme.name,
            theme.description or "",
            len(theme_feedback)
        )
        if lost_deal_info and lost_deal_info.get("estimated_avg_arr", 0) > 0:
            lost_deal_info = {**enriched_data, **{k: v for k, v in lost_deal_info.items() if v}}
        else:
            lost_deal_info = enriched_data
        # Add mock competitor mentions to our set
        if enriched_data.get("competitor_mentions"):
            all_competitor_mentions.update(enriched_data.get("competitor_mentions", []))
    
    estimated_avg_arr = lost_deal_info.get("estimated_avg_arr", 0)
    estimated_total_arr = lost_deal_info.get("total_arr", 0)
    
    # Use actual aggregated ARR from ALL feedback items (preferred)
    if avg_arr_from_feedback > 0:
        avg_arr = avg_arr_from_feedback
        total_arr = total_arr_from_feedback
    elif estimated_avg_arr > 0:
        avg_arr = estimated_avg_arr
        total_arr = estimated_total_arr if estimated_total_arr > 0 else (estimated_avg_arr * len(theme_feedback))
    else:
        theme_lower = (theme.name + " " + (theme.description or "")).lower()
        if any(word in theme_lower for word in ["enterprise", "large", "big"]):
            avg_arr = 100000
        elif any(word in theme_lower for word in ["smb", "small", "startup"]):
            avg_arr = 15000
        else:
            avg_arr = 50000
        total_arr = avg_arr * len(theme_feedback) if theme_feedback else avg_arr
    
    # Get competitor information - full competitor objects from ALL mentions
    competitor_mentions = list(all_competitor_mentions)
    competitors = []
    if competitor_mentions:
        competitor_objects = db.query(Competitor).filter(
            Competitor.name.in_(competitor_mentions)
        ).all()
        competitors = [
            {
                "name": c.name,
                "description": c.description,
                "positioning": c.positioning,
                "strengths": c.strengths or [],
                "weaknesses": c.weaknesses or [],
                "opportunities": c.opportunities or [],
                "market_gaps": c.market_gaps or [],
                "customer_reviews_sentiment": c.customer_reviews_sentiment,
                "social_sentiment": c.social_sentiment,
                "website_url": c.website_url,
                "pricing_info": c.pricing_info,
                "funding_info": c.funding_info
            }
            for c in competitor_objects
        ]
        # Also include any mentioned competitors that aren't in the database yet
        mentioned_names = {c.name for c in competitor_objects}
        for comp_name in competitor_mentions:
            if comp_name not in mentioned_names:
                competitors.append({
                    "name": comp_name,
                    "description": None,
                    "positioning": None,
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "market_gaps": [],
                    "customer_reviews_sentiment": None,
                    "social_sentiment": None,
                    "website_url": None,
                    "pricing_info": None,
                    "funding_info": None
                })
    
    # Get actual count of feedback items linked to this theme (more accurate than request_frequency)
    actual_feedback_count = len(theme_feedback)
    
    # Get ALL feedback items for this theme (all individual requests grouped in this cluster)
    feedback_items_data = [
        {
            "id": item.id,
            "content": item.content,
            "source": item.source,
            "source_id": item.source_id,
            "sentiment_score": item.sentiment_score,
            "pain_level": item.pain_level,
            "arr": item.arr,
            "account_id": item.account_id,
            "user_segment": item.user_segment,
            "classification": item.classification,
            "urgency": item.urgency,
            "churn_risk": item.churn_risk,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "extra_metadata": item.extra_metadata or {}
        }
        for item in theme_feedback
    ]
    
    # Return theme data with ALL fields aggregated from ALL feedback items in the theme cluster
    # All metrics (ARR, lost deals, competitors, pain score) are calculated from ALL similar feedback requests grouped together
    return {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        "request_frequency": actual_feedback_count,  # ACTUAL count of ALL similar feedback items grouped in this theme
        "feedback_count": actual_feedback_count,  # Explicit count of feedback items in this theme
        "customer_value": theme.customer_value,  # Keep for backward compatibility
        "pain_score": pain_score,  # Average pain score from ALL feedback items in theme
        "trend_velocity": theme.trend_velocity,
        "impact_score": theme.overall_impact_score or 0.0,  # Calculated from all feedback items
        # ARR values - aggregated from ALL feedback items in the theme
        "total_arr": total_arr,  # Total ARR from ALL feedback items
        "avg_arr": avg_arr,  # Average ARR from ALL feedback items
        "arr_value": total_arr,  # Alias for clarity
        # Lost deals - aggregated from ALL feedback items in the theme
        "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),  # Count from ALL feedback items
        "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),  # ARR value from ALL lost deals
        "lost_deals": {  # Structured lost deals info (aggregated from all feedback items)
            "count": lost_deal_info.get("lost_deal_count", 0),
            "arr_value": lost_deal_info.get("lost_deal_arr", 0),
            "has_lost_deals": lost_deal_info.get("has_lost_deals", False)
        },
        # Competitors - aggregated from ALL feedback items in the theme
        "competitor_mentions": competitor_mentions,  # All competitor names mentioned in ANY feedback item
        "competitors": competitors,  # Full competitor information (from all feedback items)
        "has_lost_deals": lost_deal_info.get("has_lost_deals", False),
        # ALL individual feedback requests grouped in this theme cluster
        "feedback_items": feedback_items_data,  # All feedback items that were clustered together
        # Professional Impact Score Breakdown (Airtable-style formula insights)
        "impact_score_breakdown": theme.extra_metadata.get("impact_score_breakdown", {}) if theme.extra_metadata and isinstance(theme.extra_metadata, dict) else {}
    }

@router.post("/process")
async def process_feedback(
    feedback_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Process a batch of feedback"""
    try:
        results = await data_processor.process_feedback_batch(feedback_data, db)
        return {"status": "success", **results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_feedback(
    limit: int = 500,  # Increased to show all feedback
    offset: int = 0,
    source: str = None,
    classification: str = None,
    start_date: str = None,  # ISO format: 2024-01-01
    end_date: str = None,  # ISO format: 2024-12-31
    quarter: str = None,  # Q1, Q2, Q3, Q4
    year: int = None,  # 2024
    db: Session = Depends(get_db)
):
    """List feedback with filters including date range and quarter"""
    from datetime import datetime, timedelta
    from sqlalchemy import and_
    
    # Allow up to 1000 items (enough for all feedback)
    actual_limit = min(limit, 1000)
    
    # Build query with filters
    query = db.query(Feedback)
    
    if source:
        query = query.filter(Feedback.source == source)
    if classification:
        query = query.filter(Feedback.classification == classification)
    
    # Date range filtering
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Feedback.created_at >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            # Add one day to include the entire end date
            end_dt = end_dt + timedelta(days=1)
            query = query.filter(Feedback.created_at < end_dt)
        except:
            pass
    
    # Quarter filtering
    if quarter and year:
        quarter_map = {
            'Q1': (1, 3),
            'Q2': (4, 6),
            'Q3': (7, 9),
            'Q4': (10, 12)
        }
        if quarter in quarter_map:
            start_month, end_month = quarter_map[quarter]
            start_dt = datetime(year, start_month, 1)
            if end_month == 12:
                end_dt = datetime(year + 1, 1, 1)
            else:
                end_dt = datetime(year, end_month + 1, 1)
            query = query.filter(
                and_(
                    Feedback.created_at >= start_dt,
                    Feedback.created_at < end_dt
                )
            )
    
    # Order by created_at desc to show newest first
    feedback_items = query.order_by(Feedback.created_at.desc()).offset(offset).limit(actual_limit).all()
    
    # Get total count for pagination (only if not too large)
    total_count = query.count() if actual_limit < 500 else len(feedback_items)
    
    return {
        "feedback": [
            {
                "id": item.id,
                "source": item.source,
                "content": item.content,
                "classification": item.classification,
                "sentiment_score": item.sentiment_score,
                "pain_level": item.pain_level,
                "urgency": item.urgency,
                "feature": item.feature,
                "user_segment": item.user_segment,
                "theme_id": item.theme_id,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in feedback_items
        ],
        "total": total_count,
        "limit": actual_limit,
        "offset": offset
    }

@router.get("/themes")
async def list_themes(
    limit: int = 100,  # Increased to show all themes (data persists)
    cluster: bool = False,  # Disable clustering by default for performance (can be enabled if needed)
    quarter: str = None,  # Q1, Q2, Q3, Q4
    year: int = None,  # 2024, 2025, etc.
    db: Session = Depends(get_db)
):
    """List all themes with FULL data (ARR, lost deals, competitor info)
    
    If cluster=True, returns themes grouped into major clusters with merged stats.
    If cluster=False, returns individual themes (FASTER - recommended for frequent polling).
    """
    # Allow up to 200 themes (data persists, so show all)
    actual_limit = min(limit, 200)
    
    # Get theme count for cache key
    total_themes_count = db.query(Theme).count()
    
    # Order by impact_score desc, but handle NULL values properly
    # Use distinct() to ensure no duplicate themes
    from sqlalchemy import desc, func, distinct, and_
    from datetime import datetime
    
    query = db.query(Theme)
    
    # Filter by quarter/year if provided
    # Themes should be filtered by the quarter of their feedback, not just created_at
    if quarter and year:
        quarter_map = {
            'Q1': (1, 3),
            'Q2': (4, 6),
            'Q3': (7, 9),
            'Q4': (10, 12)
        }
        if quarter in quarter_map:
            start_month, end_month = quarter_map[quarter]
            start_dt = datetime(year, start_month, 1)
            if end_month == 12:
                end_dt = datetime(year + 1, 1, 1)
            else:
                end_dt = datetime(year, end_month + 1, 1)
            
            # Filter themes by the quarter of their feedback (more accurate than created_at)
            from core.database import Feedback
            quarter_feedback = db.query(Feedback).filter(
                and_(
                    Feedback.created_at >= start_dt,
                    Feedback.created_at < end_dt
                )
            ).all()
            quarter_theme_ids = list(set([f.theme_id for f in quarter_feedback if f.theme_id]))
            
            if quarter_theme_ids:
                query = query.filter(Theme.id.in_(quarter_theme_ids))
            else:
                # Fallback to created_at if no feedback found
                query = query.filter(
                    and_(
                        Theme.created_at >= start_dt,
                        Theme.created_at < end_dt
                    )
                )
    
    themes = query.order_by(
        desc(func.coalesce(Theme.overall_impact_score, 0)),
        desc(Theme.created_at)
    ).limit(actual_limit).all()
    
    # Deduplicate by theme ID (in case database has duplicates)
    seen_ids = set()
    unique_themes = []
    for theme in themes:
        if theme.id not in seen_ids:
            seen_ids.add(theme.id)
            unique_themes.append(theme)
    themes = unique_themes
    
    # If still no themes, just get all themes
    if len(themes) == 0 and total_themes_count > 0:
        all_themes = db.query(Theme).order_by(desc(Theme.created_at)).all()
        # Deduplicate again
        seen_ids = set()
        unique_themes = []
        for theme in all_themes:
            if theme.id not in seen_ids:
                seen_ids.add(theme.id)
                unique_themes.append(theme)
        themes = unique_themes
    
    # Create cache key based on theme IDs (changes when themes are added/removed)
    theme_ids = tuple(sorted([t.id for t in themes]))
    cache_key = f"themes_{len(themes)}_{hash(theme_ids)}"
    
    # Check cache first (only for clustering, which is expensive)
    if cluster and len(themes) > 1:
        if cache_key in _theme_cluster_cache:
            cache_time = _cache_timestamp.get(cache_key)
            if cache_time and datetime.now() - cache_time < CACHE_DURATION:
                print(f"⚡ [THEMES API] Using cached clusters (cache valid for {CACHE_DURATION.total_seconds()}s)")
                return _theme_cluster_cache[cache_key]
    
    # If clustering is enabled, group themes visually under cluster headers (but keep themes separate)
    if cluster and len(themes) > 1:
        print(f"🔵 [THEMES API] Grouping {len(themes)} themes into visual clusters...")
        theme_clusters = await clustering.cluster_themes(themes, db)
        
        # Return themes grouped by clusters, but each theme keeps its individual stats
        # Structure: clusters array with cluster headers and individual themes inside
        clusters_data = []
        all_themes_flat = []  # Also return flat list for backward compatibility
        seen_theme_ids = set()  # Track theme IDs to prevent duplicates
        
        for cluster_info in theme_clusters:
            # Get detailed data for each theme in cluster (keep individual stats)
            cluster_themes_data = []
            for theme in cluster_info["themes"]:
                # Skip if we've already seen this theme ID (prevent duplicates)
                if theme.id is None or theme.id in seen_theme_ids:
                    print(f"  ⚠️ Skipping duplicate theme ID: {theme.id} ({theme.name})")
                    continue
                seen_theme_ids.add(theme.id)
                
                theme_data = await _get_theme_data(theme, db)
                theme_data["created_at"] = theme.created_at.isoformat() if theme.created_at else None
                theme_data["extra_metadata"] = theme.extra_metadata or {}
                theme_data["is_cluster"] = False  # Individual theme, not a cluster
                cluster_themes_data.append(theme_data)
                all_themes_flat.append(theme_data)
            
            # Only create cluster header if there are 2+ themes
            if len(cluster_themes_data) >= 2:
                # Get combined stats from cluster_info
                combined_stats = cluster_info.get("combined_stats", {})
                clusters_data.append({
                    "cluster_name": cluster_info["cluster_name"],
                    "cluster_description": cluster_info["cluster_description"],
                    "is_cluster_header": True,
                    "themes_count": len(cluster_themes_data),
                    "themes": cluster_themes_data,  # Individual themes with their own stats
                    "combined_stats": combined_stats  # Aggregated stats for the cluster
                })
            else:
                # Single theme - add directly to flat list without cluster header
                pass
        
        # Final deduplication of all_themes_flat by theme ID
        final_themes = []
        final_seen_ids = set()
        for theme_data in all_themes_flat:
            theme_id = theme_data.get("id")
            if theme_id and theme_id not in final_seen_ids:
                final_seen_ids.add(theme_id)
                final_themes.append(theme_data)
        
        result = {
            "themes": final_themes,  # Deduplicated flat list of all individual themes
            "clusters": clusters_data,  # Cluster headers with grouped themes
            "clustered": True,
            "total_clusters": len(clusters_data)
        }
        # Cache the result
        _theme_cluster_cache[cache_key] = result
        _cache_timestamp[cache_key] = datetime.now()
        return result
    
    # Return individual themes (no clustering)
    themes_data = []
    seen_theme_ids = set()  # Track theme IDs to prevent duplicates
    
    for theme in themes:
        # Skip if we've already seen this theme ID
        if theme.id in seen_theme_ids:
            continue
        seen_theme_ids.add(theme.id)
        
        theme_data = await _get_theme_data(theme, db)
        theme_data["created_at"] = theme.created_at.isoformat() if theme.created_at else None
        theme_data["extra_metadata"] = theme.extra_metadata or {}
        theme_data["is_cluster"] = False
        themes_data.append(theme_data)
    
    return {
        "themes": themes_data,
        "clustered": False
    }

@router.get("/themes/{theme_id}")
async def get_theme(theme_id: int, db: Session = Depends(get_db)):
    """Get a specific theme with FULL data (ARR, lost deals, competitor info, impact score, pain score, feedback)"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    # Use the helper function to get all theme data (competitors, ARR, lost deals, impact score, pain score)
    theme_data = await _get_theme_data(theme, db)
    
    # Get all feedback for this theme (no limit - show ALL items in the cluster)
    feedback_items = db.query(Feedback).filter(
        Feedback.theme_id == theme_id
    ).order_by(Feedback.created_at.desc()).all()  # Order by newest first
    
    feedback_count = theme.request_frequency or len(feedback_items)
    
    # Add additional fields specific to individual theme endpoint
    # Note: feedback_items are already included in theme_data from _get_theme_data
    theme_data.update({
        "feedback_count": feedback_count,
        "created_at": theme.created_at.isoformat() if theme.created_at else None,
        "updated_at": theme.updated_at.isoformat() if theme.updated_at else None,
        # Alias for backward compatibility (feedback_items is the main field)
        "feedback": theme_data.get("feedback_items", []),
        # Full metadata
        "extra_metadata": theme.extra_metadata or {}
    })
    
    return theme_data

