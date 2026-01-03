// Static mock data - always available, no API calls needed
// Includes all unique PGC-R OS features

export const mockFeedback = [
  {
    id: 1,
    source: "app_store",
    content: "The app crashes when I try to export data. This is really frustrating! We lost a deal to CompetitorX because they have reliable export.",
    classification: "bug",
    sentiment_score: -0.8,
    pain_level: 8.5,
    urgency: "high",
    user_segment: "enterprise",
    feature: "Data Export",
    reason: "Critical bug preventing data export functionality",
    account_id: "acc_001",
    arr: 50000,
    churn_risk: 0.7,
    theme_id: 1,
    impact_score: 9.2,
    lost_deal_flag: true,
    competitor_mentioned: "CompetitorX",
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    // Product Genome
    genome: {
      category: "bug",
      pain_level: 8.5,
      urgency: "high",
      persona: "enterprise_admin",
      feature: "Data Export",
      customer_arr: 50000,
      lost_deal: true,
      competitor: "CompetitorX"
    }
  },
  {
    id: 2,
    source: "zendesk",
    content: "We need better mobile app support. The current mobile experience is lacking compared to CompetitorY.",
    classification: "feature_request",
    sentiment_score: -0.3,
    pain_level: 6.0,
    urgency: "medium",
    user_segment: "mid_market",
    feature: "Mobile App",
    reason: "Improve mobile user experience",
    account_id: "acc_002",
    arr: 25000,
    churn_risk: 0.4,
    theme_id: 2,
    impact_score: 7.8,
    lost_deal_flag: false,
    competitor_mentioned: "CompetitorY",
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "feature_request",
      pain_level: 6.0,
      urgency: "medium",
      persona: "mobile_user",
      feature: "Mobile App",
      customer_arr: 25000,
      lost_deal: false,
      competitor: "CompetitorY"
    }
  },
  {
    id: 3,
    source: "intercom",
    content: "Can we get CSV export functionality? It would save us hours every week. Our team of 50+ needs this.",
    classification: "feature_request",
    sentiment_score: 0.2,
    pain_level: 7.0,
    urgency: "high",
    user_segment: "enterprise",
    feature: "Data Export",
    reason: "High demand for CSV export feature",
    account_id: "acc_003",
    arr: 75000,
    churn_risk: 0.3,
    theme_id: 1,
    impact_score: 8.5,
    lost_deal_flag: false,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "feature_request",
      pain_level: 7.0,
      urgency: "high",
      persona: "data_analyst",
      feature: "Data Export",
      customer_arr: 75000,
      lost_deal: false
    }
  },
  {
    id: 4,
    source: "salesforce",
    content: "The dashboard is too slow. Takes forever to load analytics. Lost 2 deals this month because of performance issues.",
    classification: "performance",
    sentiment_score: -0.6,
    pain_level: 7.5,
    urgency: "high",
    user_segment: "enterprise",
    feature: "Dashboard Performance",
    reason: "Performance issues affecting user experience",
    account_id: "acc_004",
    arr: 100000,
    churn_risk: 0.5,
    theme_id: 3,
    impact_score: 9.0,
    lost_deal_flag: true,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "performance",
      pain_level: 7.5,
      urgency: "high",
      persona: "power_user",
      feature: "Dashboard Performance",
      customer_arr: 100000,
      lost_deal: true,
      lost_deal_count: 2
    }
  },
  {
    id: 5,
    source: "nps",
    content: "Love the product but wish it integrated with Slack. Would make our workflow so much better.",
    classification: "integration_request",
    sentiment_score: 0.5,
    pain_level: 6.5,
    urgency: "medium",
    user_segment: "mid_market",
    feature: "Slack Integration",
    reason: "Workflow improvement request",
    account_id: "acc_005",
    arr: 30000,
    churn_risk: 0.2,
    theme_id: 4,
    impact_score: 7.2,
    lost_deal_flag: false,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "integration_request",
      pain_level: 6.5,
      urgency: "medium",
      persona: "team_collaborator",
      feature: "Slack Integration",
      customer_arr: 30000,
      lost_deal: false
    }
  },
  {
    id: 6,
    source: "app_store",
    content: "Great app! But the UI could be more intuitive. Some features are hard to find.",
    classification: "usability_issue",
    sentiment_score: 0.3,
    pain_level: 5.5,
    urgency: "medium",
    user_segment: "smb",
    feature: "UI/UX Improvements",
    reason: "Usability improvements needed",
    account_id: "acc_006",
    arr: 5000,
    churn_risk: 0.3,
    theme_id: 5,
    impact_score: 6.8,
    lost_deal_flag: false,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "usability_issue",
      pain_level: 5.5,
      urgency: "medium",
      persona: "casual_user",
      feature: "UI/UX Improvements",
      customer_arr: 5000,
      lost_deal: false
    }
  },
  {
    id: 7,
    source: "forum",
    content: "We need API access to automate our workflows. This is blocking us from scaling. CompetitorZ has this and we're considering switching.",
    classification: "feature_request",
    sentiment_score: -0.2,
    pain_level: 8.0,
    urgency: "high",
    user_segment: "enterprise",
    feature: "API Access",
    reason: "Critical for automation and scaling",
    account_id: "acc_007",
    arr: 120000,
    churn_risk: 0.6,
    theme_id: 6,
    impact_score: 9.5,
    lost_deal_flag: true,
    competitor_mentioned: "CompetitorZ",
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "feature_request",
      pain_level: 8.0,
      urgency: "high",
      persona: "developer",
      feature: "API Access",
      customer_arr: 120000,
      lost_deal: true,
      competitor: "CompetitorZ",
      churn_risk: 0.6
    }
  },
  {
    id: 8,
    source: "social_media",
    content: "The mobile app needs dark mode! My eyes hurt using it at night.",
    classification: "feature_request",
    sentiment_score: 0.1,
    pain_level: 4.0,
    urgency: "low",
    user_segment: "smb",
    feature: "Mobile App",
    reason: "User experience enhancement",
    account_id: "acc_008",
    arr: 8000,
    churn_risk: 0.1,
    theme_id: 2,
    impact_score: 5.5,
    lost_deal_flag: false,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "feature_request",
      pain_level: 4.0,
      urgency: "low",
      persona: "mobile_user",
      feature: "Mobile App",
      customer_arr: 8000,
      lost_deal: false
    }
  },
  {
    id: 9,
    source: "gong",
    content: "Customer mentioned they need better reporting features. Current reports are too basic. They're evaluating CompetitorA for this.",
    classification: "feature_request",
    sentiment_score: -0.1,
    pain_level: 6.5,
    urgency: "medium",
    user_segment: "mid_market",
    feature: "Reporting",
    reason: "Enhanced reporting capabilities needed",
    account_id: "acc_009",
    arr: 35000,
    churn_risk: 0.4,
    theme_id: 7,
    impact_score: 7.0,
    lost_deal_flag: true,
    competitor_mentioned: "CompetitorA",
    created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "feature_request",
      pain_level: 6.5,
      urgency: "medium",
      persona: "analyst",
      feature: "Reporting",
      customer_arr: 35000,
      lost_deal: true,
      competitor: "CompetitorA"
    }
  },
  {
    id: 10,
    source: "dovetail",
    content: "Users struggle with the onboarding process. Too many steps and unclear instructions.",
    classification: "usability_issue",
    sentiment_score: -0.4,
    pain_level: 7.0,
    urgency: "high",
    user_segment: "smb",
    feature: "Onboarding",
    reason: "Improve user onboarding experience",
    account_id: "acc_010",
    arr: 12000,
    churn_risk: 0.5,
    theme_id: 5,
    impact_score: 7.5,
    lost_deal_flag: false,
    competitor_mentioned: null,
    created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    genome: {
      category: "usability_issue",
      pain_level: 7.0,
      urgency: "high",
      persona: "new_user",
      feature: "Onboarding",
      customer_arr: 12000,
      lost_deal: false
    }
  }
]

export const mockThemes = [
  {
    id: 1,
    name: "Data Export Functionality",
    description: "High demand for data export features including CSV, Excel, and API access",
    request_frequency: 45,
    customer_value: 8.5,
    trend_velocity: 0.3,
    overall_impact_score: 9.2,
    impact_score: 9.2,
    arr_at_risk: 125000,
    total_arr_requesting: 200000,
    lost_deal_count: 3,
    competitors_mentioned: ["CompetitorX"],
    trend_data: [
      { month: "Jan", count: 5 },
      { month: "Feb", count: 8 },
      { month: "Mar", count: 12 },
      { month: "Apr", count: 15 },
      { month: "May", count: 18 },
      { month: "Jun", count: 20 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    name: "Mobile App Improvements",
    description: "Requests for better mobile app experience, dark mode, and iOS/Android enhancements",
    request_frequency: 38,
    customer_value: 7.5,
    trend_velocity: 0.5,
    overall_impact_score: 8.0,
    impact_score: 8.0,
    arr_at_risk: 33000,
    total_arr_requesting: 58000,
    lost_deal_count: 0,
    competitors_mentioned: ["CompetitorY"],
    trend_data: [
      { month: "Jan", count: 3 },
      { month: "Feb", count: 5 },
      { month: "Mar", count: 8 },
      { month: "Apr", count: 12 },
      { month: "May", count: 15 },
      { month: "Jun", count: 20 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    name: "Performance Optimization",
    description: "Dashboard and analytics performance issues affecting user experience",
    request_frequency: 32,
    customer_value: 9.0,
    trend_velocity: 0.2,
    overall_impact_score: 9.0,
    impact_score: 9.0,
    arr_at_risk: 100000,
    total_arr_requesting: 150000,
    lost_deal_count: 2,
    competitors_mentioned: [],
    trend_data: [
      { month: "Jan", count: 4 },
      { month: "Feb", count: 6 },
      { month: "Mar", count: 8 },
      { month: "Apr", count: 10 },
      { month: "May", count: 12 },
      { month: "Jun", count: 14 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 4,
    name: "Integration Requests",
    description: "Demand for integrations with Slack, Zapier, and other workflow tools",
    request_frequency: 28,
    customer_value: 7.0,
    trend_velocity: 0.4,
    overall_impact_score: 7.5,
    impact_score: 7.5,
    arr_at_risk: 30000,
    total_arr_requesting: 50000,
    lost_deal_count: 0,
    competitors_mentioned: [],
    trend_data: [
      { month: "Jan", count: 2 },
      { month: "Feb", count: 4 },
      { month: "Mar", count: 6 },
      { month: "Apr", count: 8 },
      { month: "May", count: 10 },
      { month: "Jun", count: 12 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 5,
    name: "UI/UX Improvements",
    description: "Usability issues and requests for more intuitive interface design",
    request_frequency: 25,
    customer_value: 6.5,
    trend_velocity: 0.1,
    overall_impact_score: 6.8,
    impact_score: 6.8,
    arr_at_risk: 17000,
    total_arr_requesting: 25000,
    lost_deal_count: 0,
    competitors_mentioned: [],
    trend_data: [
      { month: "Jan", count: 3 },
      { month: "Feb", count: 4 },
      { month: "Mar", count: 5 },
      { month: "Apr", count: 6 },
      { month: "May", count: 7 },
      { month: "Jun", count: 8 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 6,
    name: "API Access",
    description: "Critical need for API access to enable automation and workflow integration",
    request_frequency: 22,
    customer_value: 9.5,
    trend_velocity: 0.6,
    overall_impact_score: 9.5,
    impact_score: 9.5,
    arr_at_risk: 120000,
    total_arr_requesting: 180000,
    lost_deal_count: 1,
    competitors_mentioned: ["CompetitorZ"],
    trend_data: [
      { month: "Jan", count: 1 },
      { month: "Feb", count: 2 },
      { month: "Mar", count: 4 },
      { month: "Apr", count: 6 },
      { month: "May", count: 8 },
      { month: "Jun", count: 12 }
    ],
    created_at: new Date().toISOString()
  },
  {
    id: 7,
    name: "Enhanced Reporting",
    description: "Requests for more advanced reporting and analytics capabilities",
    request_frequency: 20,
    customer_value: 7.2,
    trend_velocity: 0.3,
    overall_impact_score: 7.0,
    impact_score: 7.0,
    arr_at_risk: 35000,
    total_arr_requesting: 55000,
    lost_deal_count: 1,
    competitors_mentioned: ["CompetitorA"],
    trend_data: [
      { month: "Jan", count: 2 },
      { month: "Feb", count: 3 },
      { month: "Mar", count: 4 },
      { month: "Apr", count: 5 },
      { month: "May", count: 6 },
      { month: "Jun", count: 7 }
    ],
    created_at: new Date().toISOString()
  }
]

// Multi-Persona Debate Data
export const mockPersonaDebates = {
  1: {
    feature: "Data Export Functionality",
    customer_voice: {
      verdict: "CRITICAL - Must have",
      reasoning: "We're losing deals because competitors have this. 3 lost deals this quarter. $125K ARR at risk. Customers explicitly mention switching due to lack of export.",
      priority: 10,
      quotes: [
        "Lost a deal to CompetitorX because they have reliable export",
        "Our team of 50+ needs this functionality"
      ]
    },
    growth_pm: {
      verdict: "HIGH PRIORITY - Revenue impact",
      reasoning: "Lost deal count: 3. ARR at risk: $125K. Total ARR requesting: $200K. This is a revenue blocker. Competitive pressure is high - CompetitorX has this feature.",
      priority: 9,
      metrics: {
        arr_at_risk: 125000,
        lost_deals: 3,
        competitive_pressure: "high"
      }
    },
    ux_designer: {
      verdict: "MEDIUM - UX improvement needed",
      reasoning: "Export is a standard feature users expect. Current workarounds are clunky. However, this is more of a functional gap than a UX innovation. Should prioritize but not at expense of core UX improvements.",
      priority: 7,
      ux_impact: "High usability improvement, but not innovative"
    },
    consensus: {
      final_verdict: "APPROVED - High Priority",
      reasoning: "Team consensus: Critical revenue blocker. Lost deals and high ARR at risk outweigh UX concerns. Must prioritize immediately.",
      final_score: 9.2
    }
  },
  6: {
    feature: "API Access",
    customer_voice: {
      verdict: "CRITICAL - Blocking growth",
      reasoning: "This is blocking us from scaling. CompetitorZ has this and we're considering switching. $120K ARR customer at 60% churn risk.",
      priority: 10,
      quotes: [
        "This is blocking us from scaling",
        "We're considering switching to CompetitorZ"
      ]
    },
    growth_pm: {
      verdict: "HIGH PRIORITY - Strategic feature",
      reasoning: "High-value customer ($120K ARR) at risk. API access is table stakes for enterprise. Trend velocity: 0.6 (growing fast). This is a strategic differentiator.",
      priority: 9,
      metrics: {
        arr_at_risk: 120000,
        churn_risk: 0.6,
        trend_velocity: 0.6
      }
    },
    ux_designer: {
      verdict: "LOW - Not a UX feature",
      reasoning: "This is a developer-facing feature. No direct UX impact. However, enabling integrations improves overall product experience indirectly.",
      priority: 5,
      ux_impact: "Indirect - enables better integrations"
    },
    consensus: {
      final_verdict: "APPROVED - Strategic Priority",
      reasoning: "Team consensus: High-value customer retention and strategic positioning outweigh UX concerns. API is table stakes for enterprise.",
      final_score: 9.5
    }
  }
}

export const mockRecommendations = [
  {
    id: 1,
    title: "Enhance Data Export Functionality",
    description: "Add comprehensive data export features including CSV, Excel, and API access to address high customer demand",
    feature: "Data Export",
    impact_score: 9.2,
    feasibility_score: 7.5,
    risk_score: 2.0,
    status: "pending",
    business_impact: "High customer demand for data portability. Requested by 45 customers. $200K ARR requesting. 3 lost deals.",
    pm_verdict: "High priority feature with impact score of 9.2. High customer demand for data portability. Requested by 45 customers.",
    ux_verdict: "Improves user experience for 45 users. Customer value score: 8.5/10.",
    engineering_verdict: "Feasibility: 7.5/10. Risk: 2.0/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 45.",
    unified_recommendation: "Team consensus: Approve. High customer demand for data portability. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Data Export Functionality related features.",
    // Unique features
    arr_at_risk: 125000,
    total_arr_requesting: 200000,
    lost_deal_count: 3,
    competitors_mentioned: ["CompetitorX"],
    persona_debate: mockPersonaDebates[1],
    adoption_tracking: null, // Will be populated when feature ships
    one_pager: {
      customer_quotes: [
        "Lost a deal to CompetitorX because they have reliable export",
        "Our team of 50+ needs this functionality",
        "Can we get CSV export functionality? It would save us hours every week"
      ],
      arr_impact: 200000,
      competitive_angle: "CompetitorX has this feature and is winning deals",
      implementation_estimate: "6-8 weeks",
      roi_projection: "Prevent 3+ lost deals per quarter = $375K+ ARR protected"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    title: "Enhance Mobile App Improvements",
    description: "Improve mobile app experience with dark mode, better navigation, and iOS/Android enhancements",
    feature: "Mobile App",
    impact_score: 8.0,
    feasibility_score: 6.0,
    risk_score: 4.0,
    status: "pending",
    business_impact: "Expands market reach and user accessibility. Requested by 38 customers.",
    pm_verdict: "High priority feature with impact score of 8.0. Expands market reach and user accessibility. Requested by 38 customers.",
    ux_verdict: "Improves user experience for 38 users. Customer value score: 7.5/10.",
    engineering_verdict: "Feasibility: 6.0/10. Risk: 4.0/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 38.",
    unified_recommendation: "Team consensus: Approve. Expands market reach and user accessibility. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Mobile App Improvements related features.",
    arr_at_risk: 33000,
    total_arr_requesting: 58000,
    lost_deal_count: 0,
    competitors_mentioned: ["CompetitorY"],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "We need better mobile app support",
        "The mobile app needs dark mode!"
      ],
      arr_impact: 58000,
      competitive_angle: "CompetitorY has superior mobile experience",
      implementation_estimate: "8-10 weeks",
      roi_projection: "Expand mobile user base by 30% = $17K+ new ARR"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    title: "Optimize Performance",
    description: "Address dashboard and analytics performance issues to improve user experience",
    feature: "Dashboard Performance",
    impact_score: 9.0,
    feasibility_score: 8.5,
    risk_score: 2.0,
    status: "pending",
    business_impact: "Improves user experience and reduces churn. Requested by 32 customers. 2 lost deals due to performance.",
    pm_verdict: "High priority feature with impact score of 9.0. Improves user experience and reduces churn. Requested by 32 customers.",
    ux_verdict: "Improves user experience for 32 users. Customer value score: 9.0/10.",
    engineering_verdict: "Feasibility: 8.5/10. Risk: 2.0/10. Estimated effort: Low.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 32.",
    unified_recommendation: "Team consensus: Approve. Improves user experience and reduces churn. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Performance Optimization related features.",
    arr_at_risk: 100000,
    total_arr_requesting: 150000,
    lost_deal_count: 2,
    competitors_mentioned: [],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "The dashboard is too slow. Takes forever to load analytics",
        "Lost 2 deals this month because of performance issues"
      ],
      arr_impact: 150000,
      competitive_angle: "Performance is table stakes - all competitors have fast dashboards",
      implementation_estimate: "4-6 weeks",
      roi_projection: "Prevent 2+ lost deals per quarter = $200K+ ARR protected"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 4,
    title: "Add Integration Requests",
    description: "Build integrations with Slack, Zapier, and other workflow tools to increase product stickiness",
    feature: "Slack Integration",
    impact_score: 7.5,
    feasibility_score: 7.5,
    risk_score: 3.5,
    status: "pending",
    business_impact: "Increases product stickiness and workflow efficiency. Requested by 28 customers.",
    pm_verdict: "High priority feature with impact score of 7.5. Increases product stickiness and workflow efficiency. Requested by 28 customers.",
    ux_verdict: "Improves user experience for 28 users. Customer value score: 7.0/10.",
    engineering_verdict: "Feasibility: 7.5/10. Risk: 3.5/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 28.",
    unified_recommendation: "Team consensus: Approve. Increases product stickiness and workflow efficiency. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Integration Requests related features.",
    arr_at_risk: 30000,
    total_arr_requesting: 50000,
    lost_deal_count: 0,
    competitors_mentioned: [],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "Love the product but wish it integrated with Slack",
        "Would make our workflow so much better"
      ],
      arr_impact: 50000,
      competitive_angle: "Integrations increase product stickiness",
      implementation_estimate: "6-8 weeks",
      roi_projection: "Increase retention by 5% = $2.5K+ ARR protected"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 5,
    title: "Improve UI/UX",
    description: "Address usability issues and create more intuitive interface design",
    feature: "UI/UX Improvements",
    impact_score: 6.8,
    feasibility_score: 7.0,
    risk_score: 3.0,
    status: "pending",
    business_impact: "Enhances user satisfaction and adoption. Requested by 25 customers.",
    pm_verdict: "High priority feature with impact score of 6.8. Enhances user satisfaction and adoption. Requested by 25 customers.",
    ux_verdict: "Improves user experience for 25 users. Customer value score: 6.5/10.",
    engineering_verdict: "Feasibility: 7.0/10. Risk: 3.0/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 25.",
    unified_recommendation: "Team consensus: Approve. Enhances user satisfaction and adoption. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for UI/UX Improvements related features.",
    arr_at_risk: 17000,
    total_arr_requesting: 25000,
    lost_deal_count: 0,
    competitors_mentioned: [],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "Great app! But the UI could be more intuitive",
        "Some features are hard to find"
      ],
      arr_impact: 25000,
      competitive_angle: "Better UX = higher satisfaction = lower churn",
      implementation_estimate: "8-10 weeks",
      roi_projection: "Reduce churn by 2% = $500+ ARR protected"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 6,
    title: "Enable API Access",
    description: "Provide API access to enable automation and workflow integration for enterprise customers",
    feature: "API Access",
    impact_score: 9.5,
    feasibility_score: 6.5,
    risk_score: 4.0,
    status: "pending",
    business_impact: "Critical for automation and scaling. Requested by 22 customers. $120K ARR customer at risk.",
    pm_verdict: "High priority feature with impact score of 9.5. Critical for automation and scaling. Requested by 22 customers.",
    ux_verdict: "Improves user experience for 22 users. Customer value score: 9.5/10.",
    engineering_verdict: "Feasibility: 6.5/10. Risk: 4.0/10. Estimated effort: High.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 22.",
    unified_recommendation: "Team consensus: Approve. Critical for automation and scaling. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for API Access related features.",
    arr_at_risk: 120000,
    total_arr_requesting: 180000,
    lost_deal_count: 1,
    competitors_mentioned: ["CompetitorZ"],
    persona_debate: mockPersonaDebates[6],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "We need API access to automate our workflows",
        "This is blocking us from scaling",
        "CompetitorZ has this and we're considering switching"
      ],
      arr_impact: 180000,
      competitive_angle: "CompetitorZ has API access - we're losing deals",
      implementation_estimate: "10-12 weeks",
      roi_projection: "Retain $120K ARR customer + enable enterprise sales = $200K+ ARR potential"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 7,
    title: "Enhance Reporting",
    description: "Add more advanced reporting and analytics capabilities",
    feature: "Reporting",
    impact_score: 7.0,
    feasibility_score: 7.0,
    risk_score: 3.0,
    status: "pending",
    business_impact: "Addresses customer needs and competitive gaps. Requested by 20 customers.",
    pm_verdict: "High priority feature with impact score of 7.0. Addresses customer needs and competitive gaps. Requested by 20 customers.",
    ux_verdict: "Improves user experience for 20 users. Customer value score: 7.2/10.",
    engineering_verdict: "Feasibility: 7.0/10. Risk: 3.0/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 20.",
    unified_recommendation: "Team consensus: Approve. Addresses customer needs and competitive gaps. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Enhanced Reporting related features.",
    arr_at_risk: 35000,
    total_arr_requesting: 55000,
    lost_deal_count: 1,
    competitors_mentioned: ["CompetitorA"],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "Customer mentioned they need better reporting features",
        "Current reports are too basic",
        "They're evaluating CompetitorA for this"
      ],
      arr_impact: 55000,
      competitive_angle: "CompetitorA has superior reporting - we're losing deals",
      implementation_estimate: "8-10 weeks",
      roi_projection: "Prevent 1+ lost deal per quarter = $35K+ ARR protected"
    },
    created_at: new Date().toISOString()
  },
  {
    id: 8,
    title: "Improve Onboarding Experience",
    description: "Streamline the onboarding process with clearer instructions and fewer steps",
    feature: "Onboarding",
    impact_score: 7.5,
    feasibility_score: 7.0,
    risk_score: 3.0,
    status: "pending",
    business_impact: "Improves user onboarding experience and reduces time to value. Requested by 15 customers.",
    pm_verdict: "High priority feature with impact score of 7.5. Improves user onboarding experience and reduces time to value. Requested by 15 customers.",
    ux_verdict: "Improves user experience for 15 users. Customer value score: 7.0/10.",
    engineering_verdict: "Feasibility: 7.0/10. Risk: 3.0/10. Estimated effort: Medium.",
    data_scientist_verdict: "Track adoption rate, user engagement, and customer satisfaction metrics. Request frequency: 15.",
    unified_recommendation: "Team consensus: Approve. Improves user onboarding experience and reduces time to value. Recommended for roadmap.",
    ux_implications: "Improves usability and user satisfaction for Onboarding related features.",
    arr_at_risk: 12000,
    total_arr_requesting: 20000,
    lost_deal_count: 0,
    competitors_mentioned: [],
    adoption_tracking: null,
    one_pager: {
      customer_quotes: [
        "Users struggle with the onboarding process",
        "Too many steps and unclear instructions"
      ],
      arr_impact: 20000,
      competitive_angle: "Better onboarding = faster time to value = higher satisfaction",
      implementation_estimate: "6-8 weeks",
      roi_projection: "Reduce onboarding time by 50% = higher activation rate = $5K+ ARR potential"
    },
    created_at: new Date().toISOString()
  }
]

// Mock Notifications Data - For Feature Shipping Workflow
export const mockNotifications = [
  {
    id: 1,
    feature_id: 1,
    feature_name: "Data Export",
    shipped_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    requested_by: [
      { customer_id: "acc_001", customer_name: "Enterprise Corp", arr: 50000 },
      { customer_id: "acc_003", customer_name: "Data Analytics Inc", arr: 75000 }
    ],
    adoption_rate: 0.75,
    request_volume: 2,
    email_templates_generated: 2,
    status: "notified"
  },
  {
    id: 2,
    feature_id: 2,
    feature_name: "Mobile App",
    shipped_date: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    requested_by: [
      { customer_id: "acc_002", customer_name: "MidMarket Solutions", arr: 25000 },
      { customer_id: "acc_008", customer_name: "Mobile First Co", arr: 8000 }
    ],
    adoption_rate: 0.60,
    request_volume: 2,
    email_templates_generated: 2,
    status: "notified"
  }
]

// Competitor Intelligence - Realistic Mock Data
export const mockCompetitors = [
  {
    id: 1,
    name: "DataFlow Pro",
    company_type: "Enterprise SaaS",
    founded: 2018,
    funding: "$45M Series B",
    employees: "150-200",
    website: "dataflowpro.com",
    strengths: [
      "Reliable data export (CSV, Excel, JSON)",
      "Fast dashboard performance (<2s load)",
      "Enterprise-grade security (SOC 2)",
      "Strong API documentation",
      "24/7 enterprise support"
    ],
    weaknesses: [
      "Poor mobile app experience",
      "Limited third-party integrations",
      "Complex pricing structure",
      "Steep learning curve for new users",
      "No free tier available"
    ],
    opportunities: "They lack Slack integration - we can differentiate with workflow tools",
    market_gaps: "Mobile experience is weak, especially for field teams",
    threats: "They're aggressively targeting enterprise accounts with 30% discounts",
    mentioned_in_feedback: 12,
    lost_deals_attributed: 5,
    total_arr_lost: 375000,
    competitive_pressure: "high",
    win_rate_against: 0.35,
    last_mentioned: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    customer_quotes: [
      "Lost deal to DataFlow Pro because they have reliable export functionality",
      "DataFlow Pro's dashboard is much faster - we're considering switching",
      "Their enterprise support is better, but mobile app is terrible"
    ],
    feature_comparison: {
      data_export: { them: true, us: false, gap: "critical" },
      mobile_app: { them: false, us: true, gap: "advantage" },
      api_access: { them: true, us: false, gap: "critical" },
      slack_integration: { them: false, us: true, gap: "advantage" },
      performance: { them: true, us: false, gap: "critical" }
    },
    pricing: {
      starter: "$99/month",
      professional: "$299/month",
      enterprise: "Custom (starts at $999/month)"
    },
    market_position: "Enterprise-focused, high price point",
    recent_news: [
      "Raised $25M Series B in Q2 2024",
      "Launched new API v2 in March 2024",
      "Won 3 enterprise deals in our target market last quarter"
    ]
  },
  {
    id: 2,
    name: "MobileFirst Analytics",
    company_type: "Mobile-First SaaS",
    founded: 2020,
    funding: "$18M Series A",
    employees: "50-75",
    website: "mobilefirst.io",
    strengths: [
      "Superior mobile app (iOS & Android)",
      "Excellent UX/UI design",
      "Dark mode support",
      "Offline functionality",
      "Fast onboarding (<5 minutes)"
    ],
    weaknesses: [
      "Limited enterprise features",
      "No API access",
      "Basic reporting capabilities",
      "Small team = slower feature development",
      "No enterprise support tier"
    ],
    opportunities: "They lack enterprise features - we can win enterprise deals with our platform",
    market_gaps: "Enterprise functionality, API access, advanced reporting",
    threats: "They're winning SMB deals with better mobile experience",
    mentioned_in_feedback: 8,
    lost_deals_attributed: 2,
    total_arr_lost: 58000,
    competitive_pressure: "medium",
    win_rate_against: 0.65,
    last_mentioned: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    customer_quotes: [
      "MobileFirst has a much better mobile app experience",
      "Their UI is more intuitive, but lacks enterprise features we need",
      "We chose MobileFirst for the mobile experience, but missing API is a problem"
    ],
    feature_comparison: {
      data_export: { them: true, us: false, gap: "neutral" },
      mobile_app: { them: true, us: false, gap: "critical" },
      api_access: { them: false, us: true, gap: "advantage" },
      slack_integration: { them: false, us: true, gap: "advantage" },
      performance: { them: true, us: false, gap: "neutral" }
    },
    pricing: {
      starter: "$49/month",
      professional: "$149/month",
      enterprise: "$499/month"
    },
    market_position: "SMB-focused, mobile-first approach",
    recent_news: [
      "Launched dark mode in Q1 2024",
      "Won 'Best Mobile App' award at SaaS Summit 2024",
      "Growing 40% QoQ in SMB segment"
    ]
  },
  {
    id: 3,
    name: "DevTools Platform",
    company_type: "Developer-Focused SaaS",
    founded: 2017,
    funding: "$62M Series C",
    employees: "200-300",
    website: "devtoolsplatform.com",
    strengths: [
      "Comprehensive API access",
      "Developer-friendly documentation",
      "Strong integrations (Zapier, GitHub, Jira)",
      "CLI tools available",
      "Active developer community"
    ],
    weaknesses: [
      "Poor dashboard performance (5-10s load)",
      "Limited reporting features",
      "Complex setup process",
      "Weak mobile experience",
      "Technical support only (no business support)"
    ],
    opportunities: "They have performance issues - we can highlight our speed and user-friendly approach",
    market_gaps: "Performance, reporting, mobile experience, business user support",
    threats: "They're winning developer-focused deals with superior API",
    mentioned_in_feedback: 15,
    lost_deals_attributed: 3,
    total_arr_lost: 180000,
    competitive_pressure: "high",
    win_rate_against: 0.40,
    last_mentioned: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    customer_quotes: [
      "DevTools Platform has better API access - we need that for automation",
      "Their dashboard is slow but API is excellent",
      "We're considering switching to DevTools Platform for API access, but performance is a concern"
    ],
    feature_comparison: {
      data_export: { them: true, us: false, gap: "neutral" },
      mobile_app: { them: false, us: true, gap: "advantage" },
      api_access: { them: true, us: false, gap: "critical" },
      slack_integration: { them: true, us: true, gap: "neutral" },
      performance: { them: false, us: true, gap: "advantage" }
    },
    pricing: {
      starter: "$79/month",
      professional: "$199/month",
      enterprise: "Custom (starts at $799/month)"
    },
    market_position: "Developer-focused, technical audience",
    recent_news: [
      "Launched API v3 with webhooks in Q2 2024",
      "Partnership with GitHub announced",
      "Growing developer community (50K+ developers)"
    ]
  },
  {
    id: 4,
    name: "Analytics Pro Suite",
    company_type: "Enterprise Analytics Platform",
    founded: 2015,
    funding: "$120M Series D",
    employees: "400-500",
    website: "analyticspro.com",
    strengths: [
      "Superior reporting and analytics",
      "Advanced data visualization",
      "Custom dashboard builder",
      "White-label options",
      "Enterprise-grade compliance (GDPR, HIPAA)"
    ],
    weaknesses: [
      "Complex UI with steep learning curve",
      "Expensive pricing",
      "Slow onboarding process",
      "Requires dedicated training",
      "Limited mobile capabilities"
    ],
    opportunities: "Their UI is complex - we can win with simplicity and better UX",
    market_gaps: "User experience, simplicity, mobile, pricing accessibility",
    threats: "They're winning enterprise deals with superior reporting features",
    mentioned_in_feedback: 9,
    lost_deals_attributed: 2,
    total_arr_lost: 95000,
    competitive_pressure: "medium",
    win_rate_against: 0.55,
    last_mentioned: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    customer_quotes: [
      "Analytics Pro has better reporting, but UI is too complex",
      "We're evaluating Analytics Pro for reporting features",
      "Their reporting is superior but we need something simpler"
    ],
    feature_comparison: {
      data_export: { them: true, us: false, gap: "neutral" },
      mobile_app: { them: false, us: true, gap: "advantage" },
      api_access: { them: true, us: false, gap: "neutral" },
      slack_integration: { them: false, us: true, gap: "advantage" },
      performance: { them: true, us: false, gap: "neutral" }
    },
    pricing: {
      starter: "$199/month",
      professional: "$499/month",
      enterprise: "Custom (starts at $2,999/month)"
    },
    market_position: "Enterprise analytics, high-end market",
    recent_news: [
      "Launched AI-powered insights in Q1 2024",
      "Won 5 enterprise deals >$100K ARR last quarter",
      "Expanding into healthcare vertical"
    ]
  },
  {
    id: 5,
    name: "QuickStart Analytics",
    company_type: "SMB-Focused SaaS",
    founded: 2021,
    funding: "$8M Seed",
    employees: "20-30",
    website: "quickstartanalytics.com",
    strengths: [
      "Simple, intuitive UI",
      "Fast setup (<10 minutes)",
      "Affordable pricing",
      "Good customer support",
      "Free tier available"
    ],
    weaknesses: [
      "Limited features",
      "No enterprise capabilities",
      "Basic integrations",
      "Small team = slower development",
      "No API access"
    ],
    opportunities: "They're focused on SMB - we can win with enterprise features",
    market_gaps: "Enterprise features, API, advanced capabilities",
    threats: "They're winning price-sensitive SMB deals",
    mentioned_in_feedback: 5,
    lost_deals_attributed: 1,
    total_arr_lost: 12000,
    competitive_pressure: "low",
    win_rate_against: 0.75,
    last_mentioned: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    customer_quotes: [
      "QuickStart is simpler and cheaper, but lacks features we need",
      "We chose QuickStart for price, but may outgrow it"
    ],
    feature_comparison: {
      data_export: { them: false, us: false, gap: "neutral" },
      mobile_app: { them: true, us: false, gap: "neutral" },
      api_access: { them: false, us: true, gap: "advantage" },
      slack_integration: { them: false, us: true, gap: "advantage" },
      performance: { them: true, us: false, gap: "neutral" }
    },
    pricing: {
      starter: "Free",
      professional: "$29/month",
      enterprise: "$99/month"
    },
    market_position: "SMB-focused, price-sensitive market",
    recent_news: [
      "Launched free tier in Q1 2024",
      "Growing 60% QoQ in SMB segment",
      "Raised $8M seed round"
    ]
  }
]

// Feature Adoption Tracking (for shipped features)
export const mockAdoptionTracking = [
  {
    feature_id: 101,
    feature_name: "Dark Mode",
    requests_before_ship: 250,
    adoption_rate: 0.85,
    adoption_count: 212,
    satisfaction_score: 8.5,
    churn_prevented: 2,
    arr_protected: 15000,
    shipped_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    feature_id: 102,
    feature_name: "Bulk Actions",
    requests_before_ship: 180,
    adoption_rate: 0.72,
    adoption_count: 130,
    satisfaction_score: 7.8,
    churn_prevented: 1,
    arr_protected: 8000,
    shipped_date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString()
  }
]

// Customer Notifications (for shipped features) - Legacy format
export const mockCustomerNotifications = [
  {
    id: 1,
    feature_name: "Dark Mode",
    customers_notified: 250,
    customers_requested: 250,
    notification_sent: true,
    notification_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    adoption_rate: 0.85,
    customer_quotes: [
      "Thank you for listening! Dark mode is exactly what I needed.",
      "So glad you shipped this - my eyes thank you!"
    ]
  },
  {
    id: 2,
    feature_name: "Bulk Actions",
    customers_notified: 180,
    customers_requested: 180,
    notification_sent: true,
    notification_date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    adoption_rate: 0.72,
    customer_quotes: [
      "This saves me hours every week. Thank you!",
      "Finally! This was my #1 request."
    ]
  }
]

export const mockOverview = {
  feedback: {
    total: 865,
    by_classification: {
      bug: 145,
      feature_request: 320,
      usability_issue: 180,
      integration_request: 95,
      performance: 125
    }
  },
  themes: {
    total: 113,
    top_themes: mockThemes.slice(0, 5)
  },
  recommendations: {
    total: 24,
    by_status: {
      pending: 18,
      approved: 4,
      rejected: 2
    }
  },
  competitors: {
    total: 12
  },
  // Unique metrics
  total_arr_at_risk: 425000,
  total_lost_deals: 7,
  total_arr_requesting: 718000,
  competitive_pressure_score: 8.5
}

export const mockInsights = {
  high_impact_themes: mockThemes.slice(0, 10),
  pending_recommendations: mockRecommendations.filter(r => r.status === 'pending'),
  recent_competitors: mockCompetitors,
  lost_deals_summary: {
    total: 7,
    by_competitor: {
      "CompetitorX": 3,
      "CompetitorZ": 1,
      "CompetitorA": 1,
      "Other": 2
    },
    total_arr_lost: 425000
  },
  trending_themes: mockThemes.filter(t => t.trend_velocity > 0.3),
  declining_themes: mockThemes.filter(t => t.trend_velocity < 0.2)
}
