from typing import Dict, List, Any, Optional
from core.agents.base_agent import BaseAgent
from core.llm_client import groq_client
import httpx
from bs4 import BeautifulSoup
import json
import re

class CompetitorAgent(BaseAgent):
    """Competitor Agent - Discovers and analyzes competitors using Groq LLM"""
    
    def __init__(self):
        super().__init__("Competitor Agent")
        self.groq_client = groq_client
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method - discovers and analyzes competitors"""
        product_info = data.get("product_info", {})
        market_context = data.get("market_context", {})
        
        # Step 1: Discover competitors
        competitors = await self.discover_competitors(product_info, market_context)
        
        # Step 2: Analyze each competitor
        analyzed_competitors = []
        for competitor in competitors:
            analysis = await self.analyze_competitor(competitor, product_info)
            analyzed_competitors.append(analysis)
        
        # Step 3: Extract market gaps and opportunities
        gaps_and_opportunities = await self.identify_gaps_and_opportunities(
            analyzed_competitors,
            product_info
        )
        
        return {
            "competitors": analyzed_competitors,
            "market_gaps": gaps_and_opportunities.get("gaps", []),
            "opportunities": gaps_and_opportunities.get("opportunities", []),
            "competitive_landscape": await self.summarize_competitive_landscape(analyzed_competitors)
        }
    
    async def discover_competitors(
        self,
        product_info: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use LLM to discover competitors in the space"""
        prompt = f"""You are a competitive intelligence expert. Based on the following product information, identify competitors, startups, tools, and enterprises operating in the same space.

Product: {product_info.get('name', 'Unknown')}
Description: {product_info.get('description', '')}
Category: {product_info.get('category', '')}
Market Context: {market_context}

For each competitor you identify, provide:
- name: company/product name
- type: startup, enterprise, tool, platform
- website: if known
- brief_description: what they do

Return a JSON array of competitors. Be thorough and identify at least 5-10 competitors.
"""
        
        response = await self.groq_client.chat_completion([
            {"role": "system", "content": "You are an expert competitive intelligence analyst. Always return valid JSON arrays."},
            {"role": "user", "content": prompt}
        ], temperature=0.7, max_tokens=2000)
        
        try:
            competitors = json.loads(response)
            if not isinstance(competitors, list):
                competitors = [competitors]
            return competitors[:15]  # Limit to 15 competitors
        except:
            # Fallback: return mock competitors
            return [
                {"name": "Competitor A", "type": "startup", "website": None, "brief_description": "Similar product"},
                {"name": "Competitor B", "type": "enterprise", "website": None, "brief_description": "Enterprise solution"}
            ]
    
    async def analyze_competitor(
        self,
        competitor: Dict[str, Any],
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive competitor analysis"""
        name = competitor.get("name", "Unknown")
        website = competitor.get("website")
        
        # Scrape website if available
        scraped_data = {}
        if website:
            scraped_data = await self.scrape_competitor_website(website)
        
        # LLM analysis of competitor
        analysis_prompt = f"""Analyze this competitor in detail:

Name: {name}
Description: {competitor.get('brief_description', '')}
Scraped Data: {json.dumps(scraped_data, indent=2)[:2000]}

Provide a comprehensive analysis as JSON with:
- positioning: how they position themselves
- strengths: list of strengths
- weaknesses: list of weaknesses
- key_features: main features
- target_audience: who they target
- pricing_strategy: if available
- market_position: their position in market
"""
        
        analysis = await self.groq_client.chat_completion([
            {"role": "system", "content": "You are a competitive analyst. Return detailed JSON analysis."},
            {"role": "user", "content": analysis_prompt}
        ], temperature=0.6, max_tokens=1500)
        
        try:
            analysis_data = json.loads(analysis)
        except:
            analysis_data = {
                "positioning": "Unknown",
                "strengths": [],
                "weaknesses": [],
                "key_features": [],
                "target_audience": "Unknown",
                "pricing_strategy": "Unknown",
                "market_position": "Unknown"
            }
        
        # Extract complaints and sentiment
        complaints = await self.extract_competitor_complaints(name, scraped_data)
        
        return {
            **competitor,
            **analysis_data,
            "scraped_data": scraped_data,
            "complaints": complaints,
            "sentiment_score": await self.calculate_competitor_sentiment(scraped_data, complaints)
        }
    
    async def scrape_competitor_website(self, url: str) -> Dict[str, Any]:
        """Scrape competitor website for information"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract key information
                title = soup.find('title')
                title_text = title.text if title else ""
                
                # Find pricing information
                pricing_elements = soup.find_all(text=re.compile(r'\$|price|pricing', re.I))
                
                # Find feature mentions
                feature_keywords = ['feature', 'capability', 'function', 'tool']
                features = []
                for keyword in feature_keywords:
                    elements = soup.find_all(text=re.compile(keyword, re.I))
                    features.extend([e.strip() for e in elements[:5]])
                
                return {
                    "title": title_text,
                    "pricing_mentions": pricing_elements[:5] if pricing_elements else [],
                    "feature_mentions": features[:10],
                    "content_preview": soup.get_text()[:1000]
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def extract_competitor_complaints(
        self,
        competitor_name: str,
        scraped_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract complaints and pain points about competitor"""
        prompt = f"""Based on the following data about {competitor_name}, identify:
- Common complaints from customers
- Pain points mentioned
- Areas where they fall short
- Negative sentiment patterns

Data: {json.dumps(scraped_data, indent=2)[:1500]}

Return JSON array of complaints, each with:
- complaint: the complaint text
- category: category of complaint
- frequency_indicators: how often mentioned
"""
        
        response = await self.groq_client.chat_completion([
            {"role": "system", "content": "Extract competitor complaints and pain points. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        
        try:
            return json.loads(response)
        except:
            return []
    
    async def calculate_competitor_sentiment(
        self,
        scraped_data: Dict[str, Any],
        complaints: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall sentiment score for competitor"""
        # Simple sentiment calculation
        base_sentiment = 0.5
        complaint_penalty = len(complaints) * 0.1
        return max(-1.0, min(1.0, base_sentiment - complaint_penalty))
    
    async def identify_gaps_and_opportunities(
        self,
        competitors: List[Dict[str, Any]],
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify market gaps and opportunities"""
        prompt = f"""Based on competitor analysis, identify:
1. Market gaps where competitors are weak
2. Opportunities where our product can outperform
3. Competitive advantages we can leverage

Competitors analyzed: {len(competitors)}
Our Product: {product_info.get('name', '')} - {product_info.get('description', '')}

Return JSON with:
- gaps: array of market gaps
- opportunities: array of opportunities
- competitive_advantages: our advantages

Each gap/opportunity should have:
- title: brief title
- description: detailed description
- impact: potential impact (high, medium, low)
- feasibility: how feasible to pursue
"""
        
        response = await self.groq_client.chat_completion([
            {"role": "system", "content": "You are a strategic analyst identifying market opportunities. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.7, max_tokens=2000)
        
        try:
            return json.loads(response)
        except:
            return {
                "gaps": [],
                "opportunities": [],
                "competitive_advantages": []
            }
    
    async def summarize_competitive_landscape(
        self,
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize the overall competitive landscape"""
        return {
            "total_competitors": len(competitors),
            "market_leaders": [c["name"] for c in competitors[:3]],
            "emerging_players": [c["name"] for c in competitors[3:6]],
            "key_differentiators": "Analysis in progress"
        }








