"""
Use static mock competitor data to enrich themes with ARR, lost deals, and competitor info
This provides realistic data even when feedback doesn't have ARR values
"""
from typing import Dict, Any, List

# Static competitor data (from frontend mockData.ts)
MOCK_COMPETITORS = [
    {
        "name": "DataFlow Pro",
        "lost_deals_attributed": 5,
        "total_arr_lost": 375000,
        "mentioned_in_feedback": 12,
        "competitive_pressure": "high",
        "strengths": ["Reliable data export (CSV, Excel, JSON)", "Fast dashboard performance"],
        "weaknesses": ["Poor mobile app experience", "Limited third-party integrations"],
        "feature_comparison": {
            "data_export": {"them": True, "us": False, "gap": "critical"},
            "csv_export": {"them": True, "us": False, "gap": "critical"},
            "export": {"them": True, "us": False, "gap": "critical"},
            "csv": {"them": True, "us": False, "gap": "critical"},
            "excel": {"them": True, "us": False, "gap": "critical"},
            "download": {"them": True, "us": False, "gap": "critical"}
        }
    },
    {
        "name": "MobileFirst Analytics",
        "lost_deals_attributed": 2,
        "total_arr_lost": 58000,
        "mentioned_in_feedback": 8,
        "competitive_pressure": "medium",
        "strengths": ["Superior mobile app (iOS & Android)", "Excellent UX/UI design"],
        "weaknesses": ["Limited enterprise features", "No API access"],
        "feature_comparison": {
            "mobile_app": {"them": True, "us": False, "gap": "critical"},
            "mobile": {"them": True, "us": False, "gap": "critical"},
            "ios": {"them": True, "us": False, "gap": "critical"},
            "android": {"them": True, "us": False, "gap": "critical"},
            "app": {"them": True, "us": False, "gap": "critical"}
        }
    },
    {
        "name": "DevTools Platform",
        "lost_deals_attributed": 3,
        "total_arr_lost": 180000,
        "mentioned_in_feedback": 15,
        "competitive_pressure": "high",
        "strengths": ["Comprehensive API access", "Developer-friendly documentation", "Strong integrations"],
        "weaknesses": ["Poor dashboard performance", "Limited reporting features"],
        "feature_comparison": {
            "api": {"them": True, "us": False, "gap": "critical"},
            "integration": {"them": True, "us": False, "gap": "critical"},
            "webhook": {"them": True, "us": False, "gap": "critical"},
            "zapier": {"them": True, "us": False, "gap": "critical"},
            "developer": {"them": True, "us": False, "gap": "critical"}
        }
    },
    {
        "name": "Analytics Pro Suite",
        "lost_deals_attributed": 2,
        "total_arr_lost": 95000,
        "mentioned_in_feedback": 9,
        "competitive_pressure": "medium",
        "strengths": ["Superior reporting and analytics", "Advanced data visualization"],
        "weaknesses": ["Complex UI", "Expensive pricing"],
        "feature_comparison": {
            "reporting": {"them": True, "us": False, "gap": "critical"},
            "analytics": {"them": True, "us": False, "gap": "critical"},
            "dashboard": {"them": True, "us": False, "gap": "critical"},
            "visualization": {"them": True, "us": False, "gap": "critical"}
        }
    },
    {
        "name": "SpeedDash",
        "lost_deals_attributed": 4,
        "total_arr_lost": 220000,
        "mentioned_in_feedback": 10,
        "competitive_pressure": "high",
        "strengths": ["Lightning-fast performance", "Optimized queries"],
        "weaknesses": ["Limited customization", "Basic reporting"],
        "feature_comparison": {
            "performance": {"them": True, "us": False, "gap": "critical"},
            "speed": {"them": True, "us": False, "gap": "critical"},
            "slow": {"them": False, "us": True, "gap": "advantage"},
            "loading": {"them": True, "us": False, "gap": "critical"},
            "fast": {"them": True, "us": False, "gap": "critical"}
        }
    }
]

def enrich_theme_with_mock_competitor_data(theme_name: str, theme_description: str, feedback_count: int) -> Dict[str, Any]:
    """
    Enrich theme with ARR, lost deals, and competitor info using mock competitor data
    Matches themes with competitors based on keywords
    """
    theme_lower = (theme_name + " " + (theme_description or "")).lower()
    
    # Match theme with competitors based on keywords
    matched_competitors = []
    total_lost_deals = 0
    total_lost_arr = 0.0
    
    for competitor in MOCK_COMPETITORS:
        # Check if theme matches competitor's feature gaps
        feature_comparison = competitor.get("feature_comparison", {})
        is_match = False
        match_strength = 0
        
        for feature_key, feature_data in feature_comparison.items():
            if feature_data.get("gap") == "critical":
                # Check if theme contains this feature keyword (word boundary aware)
                # Use both exact substring match and word boundary match
                if feature_key in theme_lower or f" {feature_key} " in theme_lower or theme_lower.startswith(feature_key + " ") or theme_lower.endswith(" " + feature_key):
                    is_match = True
                    match_strength += 1
        
        # Also check competitor name mentions
        competitor_name_lower = competitor["name"].lower()
        if competitor_name_lower in theme_lower:
            is_match = True
            match_strength += 2
        
        if is_match:
            matched_competitors.append(competitor["name"])
            # Estimate lost deals based on match strength and competitor's data
            # Stronger match = more lost deals
            base_lost_deals = max(1, competitor["lost_deals_attributed"] // 4)
            estimated_lost_deals = base_lost_deals * min(match_strength, 3)  # Scale by match strength
            avg_deal_arr = competitor["total_arr_lost"] / competitor["lost_deals_attributed"] if competitor["lost_deals_attributed"] > 0 else 75000
            estimated_lost_arr = estimated_lost_deals * avg_deal_arr
            total_lost_deals += estimated_lost_deals
            total_lost_arr += estimated_lost_arr
    
    # Estimate ARR based on theme content and feedback volume
    # ALWAYS return a non-zero ARR estimate
    estimated_avg_arr = 50000  # Default mid-market
    
    # Check for enterprise keywords
    if any(word in theme_lower for word in ["enterprise", "large", "big", "corporate", "critical", "urgent", "blocking", "essential", "monthly reporting", "reporting"]):
        estimated_avg_arr = 100000  # Enterprise (higher value for critical features)
    elif any(word in theme_lower for word in ["smb", "small", "startup", "individual"]):
        estimated_avg_arr = 15000  # SMB
    elif any(word in theme_lower for word in ["crash", "error", "bug", "broken", "failure"]):
        estimated_avg_arr = 75000  # High-value for bugs (affects all customers)
    
    # If we have lost deals, use that to estimate ARR (more accurate)
    if total_lost_deals > 0 and total_lost_arr > 0:
        estimated_avg_arr = max(estimated_avg_arr, total_lost_arr / total_lost_deals)
    
    # Ensure we always have a minimum ARR (never return 0)
    if estimated_avg_arr == 0:
        estimated_avg_arr = 50000  # Fallback to mid-market default
    
    # Calculate total ARR (average * feedback count, minimum 1 customer)
    customer_count = max(feedback_count, 1)  # At least 1 customer
    total_arr = estimated_avg_arr * customer_count
    
    return {
        "lost_deal_count": total_lost_deals,
        "lost_deal_arr": total_lost_arr,
        "competitor_mentions": matched_competitors,
        "has_lost_deals": total_lost_deals > 0 or len(matched_competitors) > 0,
        "estimated_avg_arr": estimated_avg_arr,
        "total_arr": total_arr,
        "business_impact": f"This theme affects {feedback_count} customers with estimated ${estimated_avg_arr:,.0f} average ARR. " +
                          (f"{total_lost_deals} deals lost to {', '.join(matched_competitors)}" if matched_competitors else "No competitor pressure detected.")
    }

