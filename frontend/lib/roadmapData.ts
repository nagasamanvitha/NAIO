// Realistic Roadmap Generation Data with Persona Debates
import { mockThemes, mockRecommendations, mockCompetitors, mockPersonaDebates } from './mockData'

// Enhanced Persona Debates with Real Reasoning
export const enhancedPersonaDebates = {
  1: {
    feature: "Data Export Functionality",
    theme_id: 1,
    theme_data: mockThemes[0],
    recommendation: mockRecommendations[0],
    competitor_context: mockCompetitors.find(c => c.name === "DataFlow Pro"),
    
    customer_voice: {
      persona: "Enterprise Customer",
      verdict: "CRITICAL - Must have immediately",
      priority: 10,
      reasoning: `Based on 45 customer requests and 3 lost deals totaling $375K ARR, this is a revenue blocker. Customers explicitly state: "Lost deal to DataFlow Pro because they have reliable export" and "Our team of 50+ needs this functionality." The pain level is 8.5/10 with high urgency. This feature is mentioned in 12% of all feedback.`,
      data_points: {
        request_count: 45,
        lost_deals: 3,
        arr_at_risk: 125000,
        pain_level: 8.5,
        urgency_score: 9.0,
        customer_quotes: [
          "Lost deal to DataFlow Pro because they have reliable export",
          "Our team of 50+ needs this functionality",
          "Can we get CSV export? It would save us hours every week"
        ]
      },
      emotional_tone: "Frustrated and urgent - customers are actively switching"
    },
    
    growth_pm: {
      persona: "Growth Product Manager",
      verdict: "HIGH PRIORITY - Revenue impact is clear",
      priority: 9,
      reasoning: `Financial analysis shows: $200K total ARR requesting this feature, $125K ARR at risk, 3 confirmed lost deals. Competitive pressure is HIGH - DataFlow Pro has this feature and is winning deals. Win rate against them is only 35%. Trend velocity is 0.3 (growing). ROI projection: Prevent 3+ lost deals per quarter = $375K+ ARR protected. This is a table-stakes feature for enterprise.`,
      data_points: {
        total_arr_requesting: 200000,
        arr_at_risk: 125000,
        lost_deal_count: 3,
        competitive_pressure: "high",
        win_rate: 0.35,
        trend_velocity: 0.3,
        roi_projection: "$375K+ ARR protected per quarter"
      },
      business_metrics: {
        revenue_impact: "High",
        market_position: "Competitive disadvantage",
        strategic_importance: "Table stakes for enterprise"
      }
    },
    
    ux_designer: {
      persona: "UX Designer",
      verdict: "MEDIUM - Important but not innovative",
      priority: 7,
      reasoning: `From a UX perspective, export is a standard feature users expect - it's not innovative but it's essential. Current workarounds are clunky and create friction. However, this is more of a functional gap than a UX innovation. Customer value score is 8.5/10 which is high, but the UX impact is about removing friction rather than creating delight. Should prioritize but not at the expense of core UX improvements that differentiate us.`,
      data_points: {
        customer_value: 8.5,
        usability_impact: "High - removes friction",
        innovation_level: "Low - standard feature",
        user_satisfaction_impact: "High"
      },
      ux_considerations: {
        design_complexity: "Medium",
        user_education_needed: "Low",
        accessibility: "Standard"
      }
    },
    
    engineering: {
      persona: "Engineering Lead",
      verdict: "FEASIBLE - Medium effort, low risk",
      priority: 8,
      reasoning: `Technical feasibility is 7.5/10. We have existing data infrastructure, so export functionality is straightforward. Risk is low (2.0/10) - this is a well-understood feature. Estimated effort: 6-8 weeks for CSV, Excel, and JSON exports. No major architectural changes needed. Can leverage existing data pipeline.`,
      data_points: {
        feasibility_score: 7.5,
        risk_score: 2.0,
        estimated_effort: "6-8 weeks",
        technical_complexity: "Medium",
        dependencies: "None - can work independently"
      },
      technical_details: {
        architecture_impact: "Low",
        scalability: "High - can handle enterprise volumes",
        maintenance: "Low - standard feature"
      }
    },
    
    data_scientist: {
      persona: "Data Scientist",
      verdict: "DATA SUPPORTS - Strong signal",
      priority: 9,
      reasoning: `Data analysis shows: 45 requests (high frequency), trend velocity of 0.3 (growing), 3 lost deals directly attributed. Customer value score: 8.5/10. Request frequency is 2.3x higher than average theme. Statistical significance: High. The data clearly supports prioritizing this feature.`,
      data_points: {
        request_frequency: 45,
        trend_velocity: 0.3,
        statistical_significance: "High",
        correlation_with_churn: 0.65,
        predictive_value: "High - likely to prevent future churn"
      },
      analytics: {
        confidence_level: "95%",
        sample_size: "45 requests from 12 accounts",
        trend_direction: "Growing"
      }
    },
    
    consensus: {
      final_verdict: "APPROVED - High Priority Q1",
      final_score: 9.2,
      reasoning: `Team consensus reached after debate: This is a revenue blocker with clear financial impact ($375K ARR at risk, 3 lost deals). While UX notes it's not innovative, the functional gap is critical. Engineering confirms feasibility. Data strongly supports. Customer Voice urgency (10/10) combined with Growth PM revenue impact (9/10) outweighs UX concerns. Must prioritize in Q1 to prevent further revenue loss.`,
      debate_summary: "Customer Voice and Growth PM aligned on critical revenue impact. UX raised valid point about innovation, but functional gap is too important. Engineering confirmed feasibility. Data Scientist validated strong signal. Consensus: Approve for Q1.",
      next_steps: [
        "Add to Q1 roadmap",
        "Assign engineering team",
        "Set target ship date: 8 weeks",
        "Notify requesting customers",
        "Track adoption post-launch"
      ]
    }
  },
  
  6: {
    feature: "API Access",
    theme_id: 6,
    theme_data: mockThemes[5],
    recommendation: mockRecommendations[5],
    competitor_context: mockCompetitors.find(c => c.name === "DevTools Platform"),
    
    customer_voice: {
      persona: "Enterprise Developer",
      verdict: "CRITICAL - Blocking growth",
      priority: 10,
      reasoning: `This is blocking enterprise customers from scaling. $120K ARR customer at 60% churn risk explicitly stated: "This is blocking us from scaling" and "We're considering switching to DevTools Platform." Trend velocity is 0.6 (fastest growing). Pain level: 8.0/10. This is a deal-breaker for enterprise.`,
      data_points: {
        request_count: 22,
        churn_risk: 0.6,
        arr_at_risk: 120000,
        pain_level: 8.0,
        urgency_score: 9.5,
        customer_quotes: [
          "This is blocking us from scaling",
          "We're considering switching to DevTools Platform",
          "We need API access to automate our workflows"
        ]
      },
      emotional_tone: "Frustrated - actively evaluating alternatives"
    },
    
    growth_pm: {
      persona: "Growth Product Manager",
      verdict: "HIGH PRIORITY - Strategic positioning",
      priority: 9,
      reasoning: `Strategic analysis: API is table stakes for enterprise. $180K total ARR requesting, $120K at risk. DevTools Platform has this and win rate is only 40%. Trend velocity: 0.6 (fastest growing theme). This is a strategic differentiator - without it, we can't compete for enterprise deals. ROI: Retain $120K ARR customer + enable enterprise sales = $200K+ ARR potential.`,
      data_points: {
        total_arr_requesting: 180000,
        arr_at_risk: 120000,
        competitive_pressure: "high",
        win_rate: 0.40,
        trend_velocity: 0.6,
        roi_projection: "$200K+ ARR potential"
      },
      business_metrics: {
        revenue_impact: "Very High",
        market_position: "Competitive disadvantage",
        strategic_importance: "Table stakes for enterprise"
      }
    },
    
    ux_designer: {
      persona: "UX Designer",
      verdict: "LOW - Developer-facing feature",
      priority: 5,
      reasoning: `This is a developer-facing feature with no direct UX impact for end users. However, enabling integrations improves overall product experience indirectly. The UX impact is about enabling better workflows through integrations, not about the API itself. Should prioritize but understand it's for a technical audience.`,
      data_points: {
        customer_value: 9.5,
        usability_impact: "Indirect - enables integrations",
        innovation_level: "Medium - enables ecosystem",
        user_satisfaction_impact: "Indirect but high"
      },
      ux_considerations: {
        design_complexity: "Low - developer docs",
        user_education_needed: "High - technical documentation",
        accessibility: "Developer-focused"
      }
    },
    
    engineering: {
      persona: "Engineering Lead",
      verdict: "FEASIBLE BUT HIGH EFFORT",
      priority: 7,
      reasoning: `Technical feasibility: 6.5/10. This requires significant infrastructure work - API gateway, authentication, rate limiting, documentation. Risk: 4.0/10 (medium). Estimated effort: 10-12 weeks. Requires new infrastructure but we have the capability. This is a strategic investment.`,
      data_points: {
        feasibility_score: 6.5,
        risk_score: 4.0,
        estimated_effort: "10-12 weeks",
        technical_complexity: "High",
        dependencies: "API infrastructure, documentation team"
      },
      technical_details: {
        architecture_impact: "High - new infrastructure needed",
        scalability: "Critical - must handle enterprise load",
        maintenance: "Medium - ongoing API support needed"
      }
    },
    
    data_scientist: {
      persona: "Data Scientist",
      verdict: "DATA SUPPORTS - Strong signal",
      priority: 9,
      reasoning: `Data shows: 22 requests, fastest growing trend (velocity 0.6), high-value customers (avg $8K ARR per request). Churn risk correlation: 0.60. Predictive value: Very high - this is a churn predictor. The data strongly supports prioritizing this.`,
      data_points: {
        request_frequency: 22,
        trend_velocity: 0.6,
        statistical_significance: "Very High",
        correlation_with_churn: 0.60,
        predictive_value: "Very High - churn predictor"
      },
      analytics: {
        confidence_level: "98%",
        sample_size: "22 requests from 8 enterprise accounts",
        trend_direction: "Fastest growing"
      }
    },
    
    consensus: {
      final_verdict: "APPROVED - Strategic Priority Q1",
      final_score: 9.5,
      reasoning: `Team consensus: High-value customer retention ($120K ARR at 60% churn risk) and strategic positioning outweigh UX concerns and engineering effort. This is table stakes for enterprise. Customer Voice urgency (10/10) and Growth PM strategic importance (9/10) combined with Data Scientist validation (9/10) outweigh Engineering effort concerns. Must prioritize despite high effort - it's a strategic investment.`,
      debate_summary: "Customer Voice and Growth PM aligned on strategic importance. UX noted it's developer-facing (valid). Engineering confirmed feasibility but high effort. Data Scientist validated strong signal. Consensus: Approve for Q1 despite effort - strategic investment.",
      next_steps: [
        "Add to Q1 roadmap (strategic)",
        "Assign senior engineering team",
        "Set target ship date: 12 weeks",
        "Engage with $120K ARR customer during development",
        "Plan API documentation and developer relations"
      ]
    }
  }
}

// Roadmap Generation Process
export const generateRoadmap = () => {
  // Step 1: Gather all themes sorted by impact
  const themes = [...mockThemes].sort((a, b) => b.overall_impact_score - a.overall_impact_score)
  
  // Step 2: Select top themes (top 10)
  const topThemes = themes.slice(0, 10)
  
  // Step 3: Get competitor insights
  const competitorInsights = {
    total_competitors: mockCompetitors.length,
    total_arr_at_risk: mockCompetitors.reduce((sum, c) => sum + c.total_arr_lost, 0),
    total_lost_deals: mockCompetitors.reduce((sum, c) => sum + c.lost_deals_attributed, 0),
    high_pressure_competitors: mockCompetitors.filter(c => c.competitive_pressure === 'high'),
    feature_gaps: mockCompetitors.flatMap(c => 
      Object.entries(c.feature_comparison)
        .filter(([_, data]: [string, any]) => data.them && !data.us)
        .map(([feature]) => ({ competitor: c.name, feature, gap: 'critical' }))
    )
  }
  
  // Step 4: Create recommendations from themes
  const recommendations = topThemes.map(theme => {
    const rec = mockRecommendations.find(r => r.feature === theme.name)
    return {
      ...rec,
      theme,
      competitor_context: mockCompetitors.find(c => 
        theme.competitors_mentioned?.includes(c.name) || 
        rec?.competitors_mentioned?.includes(c.name)
      )
    }
  }).filter(Boolean)
  
  // Step 5: Run persona debates
  const debatedRecommendations = recommendations.map(rec => {
    const debate = enhancedPersonaDebates[rec.id as keyof typeof enhancedPersonaDebates]
    if (debate) {
      return {
        ...rec,
        persona_debate: debate,
        final_score: debate.consensus.final_score,
        final_verdict: debate.consensus.final_verdict
      }
    }
    // Generate debate if not exists
    return {
      ...rec,
      final_score: rec.impact_score,
      final_verdict: rec.impact_score > 8 ? "APPROVED" : "PENDING"
    }
  })
  
  // Step 6: Sort by final score
  debatedRecommendations.sort((a, b) => (b.final_score || 0) - (a.final_score || 0))
  
  // Step 7: Final team debate on top candidates
  const topCandidates = debatedRecommendations.slice(0, 5)
  
  const finalDebate = {
    participants: ["Customer Voice", "Growth PM", "UX Designer", "Engineering Lead", "Data Scientist"],
    discussion: [
      {
        speaker: "Growth PM",
        statement: `Based on our analysis, we have $720K ARR at risk across 13 lost deals. The top 5 features address $580K of that risk. We need to prioritize revenue protection.`
      },
      {
        speaker: "Customer Voice",
        statement: `I agree. Customers are actively switching - we're losing deals to DataFlow Pro, DevTools Platform, and Analytics Pro. These features are deal-breakers.`
      },
      {
        speaker: "Engineering Lead",
        statement: `I understand the urgency, but we have capacity constraints. API Access is 10-12 weeks. Data Export is 6-8 weeks. We can't do everything in Q1.`
      },
      {
        speaker: "Data Scientist",
        statement: `The data is clear: Data Export and API Access have the highest correlation with churn (0.65 and 0.60). These should be top priority.`
      },
      {
        speaker: "UX Designer",
        statement: `I support Data Export - it removes friction. API Access is important but developer-facing. Let's prioritize user-facing features first.`
      },
      {
        speaker: "Growth PM",
        statement: `We need both. Data Export for immediate revenue protection, API Access for strategic positioning. Let's commit to both in Q1.`
      }
    ],
    consensus: {
      selected_features: topCandidates.map(c => ({
        id: c.id,
        title: c.title,
        impact_score: c.final_score,
        quarter: "Q1",
        reasoning: c.persona_debate?.consensus.reasoning || "High impact based on data"
      })),
      debate_summary: "Team reached consensus: Prioritize Data Export (immediate revenue protection) and API Access (strategic positioning) in Q1. These address $300K+ ARR at risk and 4 lost deals.",
      consensus_reasoning: "Combined analysis of customer feedback, competitive pressure, revenue impact, and technical feasibility led to prioritizing features that address both immediate revenue protection and strategic market positioning."
    }
  }
  
  // Step 8: Generate final roadmap
  const roadmap = {
    quarter: "Q1 2024",
    year: 2024,
    generated_at: new Date().toISOString(),
    total_themes_considered: themes.length,
    top_candidates_evaluated: topCandidates.length,
    final_selected: topCandidates.length,
    items: topCandidates.map((item, index) => ({
      id: item.id,
      title: item.title,
      priority: index + 1,
      impact_score: item.final_score,
      quarter: "Q1",
      estimated_ship_date: item.persona_debate?.engineering.data_points.estimated_effort || "8-10 weeks",
      persona_debate: item.persona_debate,
      reasoning: item.persona_debate?.consensus.reasoning
    })),
    competitor_context: competitorInsights,
    final_debate: finalDebate,
    metadata: {
      total_arr_at_risk: competitorInsights.total_arr_at_risk,
      total_lost_deals: competitorInsights.total_lost_deals,
      win_rate_improvement_target: "Increase from 54% to 65%",
      revenue_protection_target: "$580K ARR"
    }
  }
  
  return roadmap
}

export const mockRoadmap = generateRoadmap()








