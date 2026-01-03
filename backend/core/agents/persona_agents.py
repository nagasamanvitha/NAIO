from typing import Dict, List, Any
from core.agents.base_agent import BaseAgent
import json

class PersonaAgent(BaseAgent):
    """Base class for persona agents"""
    
    def __init__(self, name: str, role: str):
        super().__init__(name)
        self.role = role
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Persona agents don't analyze data directly, they evaluate recommendations"""
        # This is a placeholder - persona agents use evaluate() instead
        return {"status": "persona_agent", "role": self.role}
    
    async def evaluate(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a recommendation from this persona's perspective with detailed reasoning"""
        # Extract context details
        theme = context.get('theme', {})
        competitor_insights = context.get('competitor_insights', {})
        mock_competitor_data = context.get('mock_competitor_data', {})
        internal_company_data = context.get('internal_company_data', {})
        theme_name = theme.get('name', recommendation.get('feature', ''))
        theme_impact = theme.get('impact_score', recommendation.get('impact_score', 0))
        feedback_count = theme.get('feedback_count', 0)
        lost_deal_info = theme.get('extra_metadata', {}).get('lost_deal_info', {}) if isinstance(theme.get('extra_metadata'), dict) else {}
        
        # Extract ARR and business metrics
        avg_arr = lost_deal_info.get('estimated_avg_arr', 0) or theme.get('avg_arr', 0)
        total_arr = lost_deal_info.get('total_arr', 0) or theme.get('total_arr', 0)
        lost_deal_count = lost_deal_info.get('lost_deal_count', 0)
        lost_deal_arr = lost_deal_info.get('lost_deal_arr', 0)
        competitor_mentions = lost_deal_info.get('competitor_mentions', [])
        
        prompt = f"""As a {self.role}, you need to evaluate this recommendation and explain your thinking process in DETAIL using ALL available data.

RECOMMENDATION TO EVALUATE:
Title: {recommendation.get('title', '')}
Description: {recommendation.get('description', '')}
Feature: {theme_name}
Impact Score: {theme_impact}/10
Request Frequency: {feedback_count} customer requests

COMPREHENSIVE THEME DATA (USE ALL OF THIS):
- Theme Name: {theme_name}
- Description: {theme.get('description', '')}
- Customer Value Score: {theme.get('customer_value', 0)}/10
- Request Frequency: {feedback_count} customer requests
- Impact Score: {theme_impact}/10
- Trend Velocity: {theme.get('trend_velocity', 0)}
- Strategic Segment Weight: {theme.get('strategic_segment_weight', 0)}

CRITICAL BUSINESS METRICS (PRIORITIZE BASED ON THESE):
- Average Customer ARR: ${avg_arr:,.0f} per customer
- Total ARR at Stake: ${total_arr:,.0f} across all affected customers
- Lost Deals: {lost_deal_count} deals lost to competitors
- Lost ARR: ${lost_deal_arr:,.0f} in revenue at risk
- Competitors Mentioned: {', '.join(competitor_mentions) if competitor_mentions else 'None'}
- Has Lost Deals: {lost_deal_info.get('has_lost_deals', False)}

COMPETITOR INTELLIGENCE (FROM DATABASE):
{json.dumps(competitor_insights, indent=2)[:2000] if competitor_insights else 'No competitor data available'}

MOCK COMPETITOR DATA (STATIC MARKET INTELLIGENCE):
{json.dumps(mock_competitor_data, indent=2)[:1500] if mock_competitor_data else 'No mock competitor data available'}

INTERNAL COMPANY DATA:
{json.dumps(internal_company_data, indent=2)[:1000] if internal_company_data else 'No internal company data available'}

YOUR EVALUATION PROCESS (THINK THROUGH THIS SYSTEMATICALLY):
Think through this like a real {self.role} would, using ALL the data provided:

1. INITIAL REACTION & BUSINESS IMPACT:
   - What is your immediate reaction? Why?
   - Consider: Impact score ({theme_impact}/10), Lost deals ({lost_deal_count}), Lost ARR (${lost_deal_arr:,.0f}), Competitor pressure ({', '.join(competitor_mentions) if competitor_mentions else 'None'})
   - What does the ARR data tell you? (${avg_arr:,.0f} avg ARR, ${total_arr:,.0f} total at stake)

2. COMPETITIVE ANALYSIS:
   - How does the competitor intelligence affect your decision?
   - Are we losing deals? Which competitors? What are they doing better?
   - What are the market gaps? What opportunities exist?
   - Reference specific competitor data from both database and mock data

3. PRIORITIZATION ASSESSMENT:
   - Should this be HIGH, MEDIUM, or LOW priority? WHY?
   - Consider: Lost deals count, ARR at risk, competitor pressure, impact score, customer value
   - What's the urgency? Is this blocking revenue? Is this a competitive threat?
   - How does this compare to other priorities?

4. KEY CONSIDERATIONS FROM YOUR PERSPECTIVE:
   - What matters most from your {self.role} perspective?
   - What are the risks? What could go wrong?
   - What are the opportunities? What could go right?
   - What are the dependencies or constraints?

5. FINAL CONCLUSION WITH DETAILED REASONING:
   - What is your final verdict? (approve, reject, modify, needs_more_info)
   - WHY did you reach this conclusion? Reference specific data points.
   - What's your priority recommendation? (P0/Critical, P1/High, P2/Medium, P3/Low)
   - What's the business case? Reference ARR, lost deals, competitor data.

CRITICAL: Return your evaluation as a VALID JSON object with EXACTLY these fields (all required):

{{
  "verdict": "approve|reject|modify|needs_more_info",
  "priority_level": "P0/Critical|P1/High|P2/Medium|P3/Low",
  "reasoning": "DETAILED reasoning (500+ words) explaining your thought process. Reference: Impact score ({theme_impact}/10), Lost deals ({lost_deal_count}), Lost ARR (${lost_deal_arr:,.0f}), Competitor mentions ({', '.join(competitor_mentions) if competitor_mentions else 'None'}), ARR data (${avg_arr:,.0f} avg, ${total_arr:,.0f} total), and how all this data influences your decision.",
  "initial_thoughts": "Your first reaction and why, considering ALL the data provided (ARR, lost deals, competitors, impact). Be specific and reference numbers.",
  "key_considerations": "What matters most from your {self.role} perspective and why. List 7-10 specific points with data references. Format as a clear, structured text (not a list).",
  "concerns": ["Specific concern 1 with explanation and data reference", "Specific concern 2 with explanation and data reference", "..."],
  "opportunities": ["Potential benefit 1 with business impact", "Potential benefit 2 with business impact", "..."],
  "suggestions": ["Concrete suggestion 1", "Concrete suggestion 2", "..."],
  "feasibility_score": 5.0,
  "risk_score": 5.0,
  "priority_justification": "DETAILED explanation (300+ words) of why this should or shouldn't be prioritized. Reference: lost deals count ({lost_deal_count}), ARR at risk (${lost_deal_arr:,.0f}), competitor pressure ({', '.join(competitor_mentions) if competitor_mentions else 'None'}), impact score ({theme_impact}/10), customer value, and compare to other priorities.",
  "business_impact": "Specific business impact (revenue, retention, market position) with ARR and lost deal references. REQUIRED for PM role.",
  "ux_implications": "Specific UX implications and recommendations. REQUIRED for UX Designer role.",
  "data_insights": "Specific data insights referencing theme metrics. REQUIRED for Data Scientist role.",
  "technical_assessment": "Specific technical assessment with feasibility and risk analysis. REQUIRED for Engineering Lead role.",
  "prioritization_recommendation": "Explicit recommendation on when to build this (Q1, Q2, Q3, Q4, or backlog) with reasoning."
}}

IMPORTANT JSON FORMATTING RULES:
1. All string values must be properly escaped (use \\" for quotes inside strings)
2. Arrays must use square brackets []
3. Numbers must not have quotes
4. Do NOT include markdown code blocks (```json or ```)
5. Do NOT include any text before or after the JSON
6. Start with {{ and end with }}
7. All fields are REQUIRED - provide meaningful content for each
"""
        
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": f"You are an expert {self.role} with deep domain knowledge. Think critically, explain your reasoning clearly, and provide detailed evaluations. CRITICAL: Return ONLY valid JSON. Do not include markdown code blocks, explanations, or any other text. Just the raw JSON object."},
            {"role": "user", "content": prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no explanations. Just the JSON object starting with { and ending with }."}
        ], temperature=0.7, max_tokens=4000)
        
        # Improved JSON parsing - handle markdown code blocks and extract JSON
        def extract_json(text: str) -> dict:
            """Extract JSON from text, handling markdown code blocks"""
            import re
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()
            
            # Try to find JSON object boundaries
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx+1]
            
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                # Try to fix common issues
                # Remove trailing commas
                text = re.sub(r',\s*}', '}', text)
                text = re.sub(r',\s*]', ']', text)
                try:
                    return json.loads(text)
                except:
                    raise e
        
        try:
            evaluation = extract_json(response)
            evaluation["persona"] = self.role
            
            # Ensure all required fields exist with defaults
            if "verdict" not in evaluation:
                evaluation["verdict"] = "needs_more_info"
            if "reasoning" not in evaluation or not evaluation.get("reasoning"):
                evaluation["reasoning"] = evaluation.get("priority_justification", "Evaluation completed but detailed reasoning not provided.")
            if "initial_thoughts" not in evaluation:
                evaluation["initial_thoughts"] = evaluation.get("reasoning", "")[:200] + "..." if evaluation.get("reasoning") else "Initial evaluation in progress."
            if "key_considerations" not in evaluation:
                evaluation["key_considerations"] = evaluation.get("reasoning", "")[:300] + "..." if evaluation.get("reasoning") else "Key considerations being analyzed."
            if "concerns" not in evaluation:
                evaluation["concerns"] = []
            if "opportunities" not in evaluation:
                evaluation["opportunities"] = []
            if "suggestions" not in evaluation:
                evaluation["suggestions"] = []
            if "feasibility_score" not in evaluation:
                evaluation["feasibility_score"] = 5.0
            if "risk_score" not in evaluation:
                evaluation["risk_score"] = 5.0
            if "priority_level" not in evaluation:
                evaluation["priority_level"] = "P2/Medium"
            
            return evaluation
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"❌ ERROR parsing {self.role} evaluation: {error_msg}")
            print(f"❌ Response was: {response[:500]}...")
            print(f"❌ Full traceback:\n{error_trace}")
            
            # Return a more informative fallback
            return {
                "persona": self.role,
                "verdict": "needs_more_info",
                "reasoning": f"Evaluation parsing failed: {error_msg}. Original response: {response[:200]}...",
                "initial_thoughts": "Unable to parse LLM response. Please check logs for details.",
                "key_considerations": "JSON parsing error occurred. LLM response may be malformed.",
                "concerns": ["Unable to complete evaluation due to parsing error"],
                "opportunities": [],
                "suggestions": ["Review LLM response format and retry evaluation"],
                "feasibility_score": 5.0,
                "risk_score": 5.0,
                "priority_level": "P2/Medium",
                "priority_justification": "Unable to determine priority due to parsing error."
            }

class PMAgent(PersonaAgent):
    """Product Manager persona agent"""
    
    def __init__(self):
        super().__init__("PM Agent", "Product Manager")
    
    async def evaluate(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """PM evaluation focusing on business impact and strategy"""
        evaluation = await super().evaluate(recommendation, context)
        evaluation["business_impact"] = await self.assess_business_impact(recommendation, context)
        return evaluation
    
    async def assess_business_impact(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Assess business impact"""
        prompt = f"""As a Product Manager, assess the business impact of this feature:

{recommendation.get('title', '')}
{recommendation.get('description', '')}

Consider: revenue impact, customer retention, competitive advantage, strategic alignment.

Provide a brief business impact assessment.
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a Product Manager focused on business outcomes."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        return response

class UXAgent(PersonaAgent):
    """UX Designer persona agent"""
    
    def __init__(self):
        super().__init__("UX Agent", "UX Designer")
    
    async def evaluate(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """UX evaluation focusing on user experience implications"""
        evaluation = await super().evaluate(recommendation, context)
        evaluation["ux_implications"] = await self.assess_ux_implications(recommendation, context)
        return evaluation
    
    async def assess_ux_implications(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Assess UX implications"""
        prompt = f"""As a UX Designer, assess the UX implications of this feature:

{recommendation.get('title', '')}
{recommendation.get('description', '')}

Consider: user flow, usability, accessibility, design complexity, user satisfaction.

Provide UX implications and recommendations.
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a UX Designer focused on user experience."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        return response

class DataScientistAgent(PersonaAgent):
    """Data Scientist persona agent"""
    
    def __init__(self):
        super().__init__("Data Scientist Agent", "Data Scientist")
    
    async def evaluate(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Data Scientist evaluation focusing on data and metrics"""
        evaluation = await super().evaluate(recommendation, context)
        evaluation["data_insights"] = await self.assess_data_implications(recommendation, context)
        return evaluation
    
    async def assess_data_implications(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Assess data and metrics implications"""
        prompt = f"""As a Data Scientist, assess the data implications of this feature:

{recommendation.get('title', '')}
{recommendation.get('description', '')}

Consider: metrics to track, data requirements, A/B testing needs, success criteria.

Provide data science recommendations.
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a Data Scientist focused on metrics and data-driven decisions."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        return response

class EngineeringAgent(PersonaAgent):
    """Engineering persona agent"""
    
    def __init__(self):
        super().__init__("Engineering Agent", "Software Engineer")
    
    async def evaluate(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Engineering evaluation focusing on technical feasibility"""
        evaluation = await super().evaluate(recommendation, context)
        evaluation["technical_assessment"] = await self.assess_technical_feasibility(recommendation, context)
        return evaluation
    
    async def assess_technical_feasibility(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Assess technical feasibility"""
        prompt = f"""As a Software Engineer, assess the technical feasibility of this feature:

{recommendation.get('title', '')}
{recommendation.get('description', '')}

Consider: implementation complexity, technical risks, dependencies, timeline estimates.

Provide technical assessment and recommendations.
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a Software Engineer focused on technical implementation."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        return response

class PersonaDeliberationSystem:
    """System for persona agents to deliberate and converge on recommendations"""
    
    def __init__(self):
        self.pm_agent = PMAgent()
        self.ux_agent = UXAgent()
        self.data_scientist_agent = DataScientistAgent()
        self.engineering_agent = EngineeringAgent()
    
    async def deliberate(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run deliberation process with all persona agents - PARALLEL PROCESSING"""
        import asyncio
        
        # PARALLEL PROCESSING: Run all persona evaluations simultaneously
        pm_task = self.pm_agent.evaluate(recommendation, context)
        ux_task = self.ux_agent.evaluate(recommendation, context)
        ds_task = self.data_scientist_agent.evaluate(recommendation, context)
        eng_task = self.engineering_agent.evaluate(recommendation, context)
        
        # Wait for all evaluations to complete in parallel
        pm_eval, ux_eval, ds_eval, eng_eval = await asyncio.gather(
            pm_task, ux_task, ds_task, eng_task
        )
        
        evaluations = {
            "pm": pm_eval,
            "ux": ux_eval,
            "data_scientist": ds_eval,
            "engineering": eng_eval
        }
        
        # Converge on unified recommendation with full context
        unified = await self.converge_recommendation(recommendation, evaluations, context)
        
        return {
            "evaluations": evaluations,
            "unified_recommendation": unified,
            "consensus_score": self.calculate_consensus(evaluations)
        }
    
    async def converge_recommendation(
        self,
        recommendation: Dict[str, Any],
        evaluations: Dict[str, Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Converge on a unified recommendation through team debate with real conversation"""
        context = context or {}
        theme = context.get('theme', {})
        competitor_insights = context.get('competitor_insights', {})
        mock_competitor_data = context.get('mock_competitor_data', {})
        internal_company_data = context.get('internal_company_data', {})
        lost_deal_info = theme.get('extra_metadata', {}).get('lost_deal_info', {}) if isinstance(theme.get('extra_metadata'), dict) else {}
        
        # Extract all business metrics
        avg_arr = lost_deal_info.get('estimated_avg_arr', 0) or theme.get('avg_arr', 0)
        total_arr = lost_deal_info.get('total_arr', 0) or theme.get('total_arr', 0)
        lost_deal_count = lost_deal_info.get('lost_deal_count', 0)
        lost_deal_arr = lost_deal_info.get('lost_deal_arr', 0)
        competitor_mentions = lost_deal_info.get('competitor_mentions', [])
        
        prompt = f"""As a team of experts (PM, UX Designer, Data Scientist, Engineering Lead), you need to have a REAL DEBATE and converge on a unified recommendation with EXPLICIT PRIORITIZATION.

ORIGINAL RECOMMENDATION:
Title: {recommendation.get('title', '')}
Description: {recommendation.get('description', '')}
Feature: {theme.get('name', recommendation.get('feature', ''))}
Impact Score: {theme.get('impact_score', recommendation.get('impact_score', 0))}/10
Request Frequency: {theme.get('feedback_count', 0)} customer requests
Customer Value: {theme.get('customer_value', 0)}/10

CRITICAL BUSINESS DATA (USE ALL OF THIS IN YOUR DEBATE):
- Average Customer ARR: ${avg_arr:,.0f} per customer
- Total ARR at Stake: ${total_arr:,.0f} across all affected customers
- Lost Deals: {lost_deal_count} deals lost to competitors
- Lost ARR: ${lost_deal_arr:,.0f} in revenue at risk
- Competitors Mentioned: {', '.join(competitor_mentions) if competitor_mentions else 'None'}
- Has Lost Deals: {lost_deal_info.get('has_lost_deals', False)}
- Impact Score: {theme.get('impact_score', recommendation.get('impact_score', 0))}/10
- Customer Value: {theme.get('customer_value', 0)}/10
- Request Frequency: {theme.get('feedback_count', 0)} customer requests

COMPETITOR INTELLIGENCE (FROM DATABASE):
{json.dumps(competitor_insights, indent=2)[:2500] if competitor_insights else 'No competitor data available'}

MOCK COMPETITOR DATA (STATIC MARKET INTELLIGENCE):
{json.dumps(mock_competitor_data, indent=2)[:1500] if mock_competitor_data else 'No mock competitor data available'}

INTERNAL COMPANY DATA:
{json.dumps(internal_company_data, indent=2)[:1000] if internal_company_data else 'No internal company data available'}

INDIVIDUAL EVALUATIONS (Each person has already thought through this):

PM (Product Manager):
- Verdict: {evaluations['pm'].get('verdict', '')}
- Initial Thoughts: {evaluations['pm'].get('initial_thoughts', evaluations['pm'].get('reasoning', ''))[:400]}
- Key Considerations: {evaluations['pm'].get('key_considerations', '')[:300]}
- Reasoning: {evaluations['pm'].get('reasoning', '')[:500]}
- Business Impact: {evaluations['pm'].get('business_impact', '')[:300]}
- Priority Justification: {evaluations['pm'].get('priority_justification', '')[:300]}
- Concerns: {', '.join(evaluations['pm'].get('concerns', [])[:5])}

UX Designer:
- Verdict: {evaluations['ux'].get('verdict', '')}
- Initial Thoughts: {evaluations['ux'].get('initial_thoughts', evaluations['ux'].get('reasoning', ''))[:400]}
- Key Considerations: {evaluations['ux'].get('key_considerations', '')[:300]}
- Reasoning: {evaluations['ux'].get('reasoning', '')[:500]}
- UX Implications: {evaluations['ux'].get('ux_implications', '')[:300]}
- Priority Justification: {evaluations['ux'].get('priority_justification', '')[:300]}
- Concerns: {', '.join(evaluations['ux'].get('concerns', [])[:5])}

Data Scientist:
- Verdict: {evaluations['data_scientist'].get('verdict', '')}
- Initial Thoughts: {evaluations['data_scientist'].get('initial_thoughts', evaluations['data_scientist'].get('reasoning', ''))[:400]}
- Key Considerations: {evaluations['data_scientist'].get('key_considerations', '')[:300]}
- Reasoning: {evaluations['data_scientist'].get('reasoning', '')[:500]}
- Data Insights: {evaluations['data_scientist'].get('data_insights', '')[:300]}
- Priority Justification: {evaluations['data_scientist'].get('priority_justification', '')[:300]}
- Concerns: {', '.join(evaluations['data_scientist'].get('concerns', [])[:5])}

Engineering Lead:
- Verdict: {evaluations['engineering'].get('verdict', '')}
- Initial Thoughts: {evaluations['engineering'].get('initial_thoughts', evaluations['engineering'].get('reasoning', ''))[:400]}
- Key Considerations: {evaluations['engineering'].get('key_considerations', '')[:300]}
- Reasoning: {evaluations['engineering'].get('reasoning', '')[:500]}
- Technical Assessment: {evaluations['engineering'].get('technical_assessment', '')[:300]}
- Feasibility: {evaluations['engineering'].get('feasibility_score', 5)}/10
- Risk: {evaluations['engineering'].get('risk_score', 5)}/10
- Priority Justification: {evaluations['engineering'].get('priority_justification', '')[:300]}
- Concerns: {', '.join(evaluations['engineering'].get('concerns', [])[:5])}

TEAM DEBATE PROCESS:
Now, simulate a REAL team meeting where team members DEBATE each other with DETAILED reasoning:

1. PM presents: "From a business perspective, here's why this matters..." 
   - Reference lost deals: "{lost_deal_info.get('lost_deal_count', 0)} lost deals"
   - Reference competitor threat: "{', '.join(lost_deal_info.get('competitor_mentions', [])) if lost_deal_info.get('competitor_mentions') else 'None'}"
   - Reference impact score: "Impact score of {theme.get('impact_score', 0)}/10"
   - Reference customer value: "{theme.get('customer_value', 0)}/10 customer value"
   - Reference request frequency: "{theme.get('feedback_count', 0)} customer requests"

2. UX responds: "I understand the business case, but from a UX perspective..."
   - Challenge or agree with PM's points
   - Discuss user impact and experience
   - Reference customer value score

3. Data Scientist adds: "The data shows..."
   - Reference request frequency: "{theme.get('feedback_count', 0)} requests"
   - Reference impact score and trends
   - Provide data-driven insights

4. Engineering weighs in: "Technically, this is feasible/risky because..."
   - Discuss implementation challenges
   - Reference feasibility and risk scores
   - Address technical concerns

5. Team debates: Members challenge each other, ask questions, discuss trade-offs
   - "But what about the competitor threat? We're losing deals to {', '.join(lost_deal_info.get('competitor_mentions', [])) if lost_deal_info.get('competitor_mentions') else 'competitors'}!"
   - "Yes, but the UX impact is..."
   - "The data suggests with {theme.get('feedback_count', 0)} requests..."
   - "Engineering-wise, we could..."
   - Reference competitor intelligence: "{json.dumps(competitor_insights, indent=2)[:1000] if competitor_insights else 'No competitor data'}"

6. Find common ground: Address disagreements, weigh all factors (lost deals, competitor data, impact scores, customer value)

7. Reach consensus: Unified decision with clear justification referencing ALL factors discussed

IMPORTANT: The debate MUST reference:
- Lost deals and competitor threats (specific numbers and competitor names)
- Impact scores (specific numbers)
- Customer value scores
- Request frequency (specific numbers)
- Competitor intelligence data
- Technical feasibility and risks

Provide the team's debate and final consensus as JSON with:
- final_verdict: approve, reject, modify, needs_more_info
- unified_reasoning: DETAILED explanation (5-7 paragraphs) of how the team converged, referencing competitor data, lost deals, impact scores, customer value, request frequency, and all factors discussed
- team_discussion: A REAL conversation transcript (15-20 exchanges) showing actual quotes from each person debating, challenging, and discussing. Format like:
  "PM: 'We're losing {lost_deal_info.get('lost_deal_count', 0)} deals to {', '.join(lost_deal_info.get('competitor_mentions', [])) if lost_deal_info.get('competitor_mentions') else 'competitors'} because we don't have this feature. The impact score of {theme.get('impact_score', 0)}/10 and ${lost_deal_info.get('lost_deal_arr', 0):,.0f} in lost ARR tells me this is critical.'
  UX: 'I agree it's important, but we need to ensure the UX doesn't suffer. The {theme.get('customer_value', 0)}/10 customer value score suggests users really want this, so we should prioritize it.'
  Data Scientist: 'The data supports this - {theme.get('feedback_count', 0)} requests is significant. Plus, looking at the competitor intelligence, {json.dumps(competitor_insights.get('opportunities', [])[:2], indent=2)[:200] if competitor_insights.get('opportunities') else 'we need to stay competitive'}.'
  Engineering: 'From a technical standpoint, this is feasible. Risk is moderate, but the business case is strong given the lost deals.'
  PM: 'So we're aligned? Let's prioritize this given the competitive pressure and {lost_deal_info.get('lost_deal_count', 0)} lost deals.'
  Team: [Consensus reached - approve with high priority]"
- key_debate_points: 7-10 main points of discussion (e.g., "Competitor threat: {lost_deal_info.get('lost_deal_count', 0)} lost deals vs. UX concerns", "Impact score {theme.get('impact_score', 0)}/10 vs. implementation effort", "Customer value {theme.get('customer_value', 0)}/10 vs. technical risk") and how they were resolved
- modified_recommendation: if modifications needed, what they are and why
- action_items: 5-7 next steps agreed upon by the team (be specific and actionable, e.g., "Create detailed product requirements document", "Assess technical feasibility with engineering team", "Validate with top 3 customers by ARR", "Design UX mockups for key user flows", "Estimate development timeline and resource requirements", "Prioritize in next sprint planning", "Track customer feedback post-launch")
- implementation_guidance: Detailed guidance on how to build this feature (300+ words) including recommended approach, technical considerations, timeline estimates, phased rollout strategy
- confidence: 0-10 confidence in the final recommendation (with detailed explanation of why, referencing all factors)
- trade_offs: 5-7 specific trade-offs discussed (e.g., "Speed vs. quality", "Business impact vs. technical risk", "Lost deals vs. UX concerns") and how they were weighed
- final_priority: why this recommendation should be prioritized (or not) based on the team's discussion, referencing ALL factors (competitor data, lost deals, impact score, customer value, request frequency, etc.)
"""
        
        response = await self.pm_agent.llm_client.chat_completion([
            {"role": "system", "content": "You facilitate team debates and convergence on product decisions. Multiple experts discuss, debate, and reach consensus. Create a REAL conversation where team members challenge each other, reference specific data (competitor info, lost deals, impact scores, customer value), and reach a unified decision. CRITICAL: Return ONLY valid JSON. Do not include markdown code blocks, explanations, or any other text. Just the raw JSON object."},
            {"role": "user", "content": prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no explanations. Just the JSON object starting with { and ending with }."}
        ], temperature=0.8, max_tokens=4000)  # Increased tokens for more detailed debate
        
        # Improved JSON parsing - handle markdown code blocks and extract JSON
        def extract_json(text: str) -> dict:
            """Extract JSON from text, handling markdown code blocks"""
            import re
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()
            
            # Try to find JSON object boundaries
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx+1]
            
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                # Try to fix common issues
                # Remove trailing commas
                text = re.sub(r',\s*}', '}', text)
                text = re.sub(r',\s*]', ']', text)
                try:
                    return json.loads(text)
                except:
                    raise e
        
        try:
            result = extract_json(response)
            
            # Ensure all required fields exist with meaningful defaults
            if "final_verdict" not in result:
                result["final_verdict"] = "needs_more_info"
            if "unified_reasoning" not in result or not result.get("unified_reasoning"):
                result["unified_reasoning"] = result.get("final_priority", "Team reached consensus through deliberation.")
            if "team_discussion" not in result:
                result["team_discussion"] = result.get("team_discussion_transcript", "Team discussed the recommendation and reached consensus through detailed debate.")
            if "team_discussion_transcript" not in result:
                result["team_discussion_transcript"] = result.get("team_discussion", result.get("team_discussion", "Team discussed the recommendation and reached consensus."))
            if "trade_offs" not in result:
                result["trade_offs"] = result.get("trade_offs", []) if isinstance(result.get("trade_offs"), list) else []
            if "key_debate_points" not in result:
                result["key_debate_points"] = result.get("key_debate_points", "Team discussed impact, feasibility, and business value") if isinstance(result.get("key_debate_points"), str) else "Team discussed impact, feasibility, and business value"
            if "final_priority" not in result:
                result["final_priority"] = result.get("unified_reasoning", "Priority determined by team consensus")
            if "action_items" not in result:
                result["action_items"] = result.get("action_items", []) if isinstance(result.get("action_items"), list) else []
            if "implementation_guidance" not in result:
                result["implementation_guidance"] = result.get("implementation_guidance", result.get("recommended_approach", "Implementation approach to be determined by engineering team based on technical assessment."))
            if "recommended_approach" not in result:
                result["recommended_approach"] = result.get("implementation_guidance", result.get("recommended_approach", "Recommended approach to be determined."))
            if "confidence" not in result:
                result["confidence"] = result.get("confidence", 7.0) if isinstance(result.get("confidence"), (int, float)) else 7.0
            if "modified_recommendation" not in result:
                result["modified_recommendation"] = result.get("modified_recommendation", None)
            
            return result
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"❌ ERROR parsing team deliberation response: {error_msg}")
            print(f"❌ Response was: {response[:500]}...")
            print(f"❌ Full traceback:\n{error_trace}")
            
            return {
                "final_verdict": "needs_more_info",
                "unified_reasoning": f"Team deliberation parsing failed: {error_msg}. Please review the recommendation with the team.",
                "team_discussion": "Team reviewed the recommendation but encountered an error during deliberation parsing. Original response: " + response[:200] + "...",
                "team_discussion_transcript": "Team reviewed the recommendation but encountered an error during deliberation parsing.",
                "modified_recommendation": None,
                "action_items": ["Review deliberation parsing and retry team discussion"],
                "confidence": 5.0,
                "trade_offs": ["Unable to parse trade-offs due to parsing error"],
                "key_debate_points": "Unable to parse debate points. JSON parsing error occurred.",
                "final_priority": "Cannot determine priority due to parsing error"
            }
    
    def calculate_consensus(self, evaluations: Dict[str, Dict[str, Any]]) -> float:
        """Calculate consensus score (0-10)"""
        verdicts = [e.get("verdict", "") for e in evaluations.values()]
        if len(set(verdicts)) == 1:
            return 10.0
        elif len(set(verdicts)) == 2:
            return 7.0
        elif len(set(verdicts)) == 3:
            return 5.0
        else:
            return 3.0

