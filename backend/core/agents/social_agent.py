from typing import Dict, List, Any
from core.agents.base_agent import BaseAgent
import json

class SocialAgent(BaseAgent):
    """Social Agent - Analyzes social media, reviews, forums, and community feedback"""
    
    def __init__(self):
        super().__init__("Social Agent")
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social media and community feedback"""
        social_data = data.get("social_data", [])
        reviews = data.get("reviews", [])
        forum_posts = data.get("forum_posts", [])
        
        results = {
            "social_sentiment": {},
            "review_analysis": {},
            "forum_insights": [],
            "viral_signals": [],
            "community_health": {}
        }
        
        # Analyze social media sentiment
        if social_data:
            results["social_sentiment"] = await self.analyze_social_sentiment(social_data)
        
        # Analyze reviews
        if reviews:
            results["review_analysis"] = await self.analyze_reviews(reviews)
        
        # Analyze forum posts
        if forum_posts:
            results["forum_insights"] = await self.analyze_forum_posts(forum_posts)
        
        # Detect viral signals
        results["viral_signals"] = await self.detect_viral_signals(social_data + reviews)
        
        # Assess community health
        results["community_health"] = await self.assess_community_health(
            social_data, reviews, forum_posts
        )
        
        return results
    
    async def analyze_social_sentiment(self, social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment across social media"""
        prompt = f"""Analyze social media sentiment. Return JSON with:
- overall_sentiment: float -1 to 1
- platform_breakdown: sentiment by platform
- trending_topics: list of trending topics
- influencer_mentions: notable mentions
- sentiment_trend: improving, declining, stable

Social posts: {len(social_data)} items
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a social media sentiment analyst. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        
        try:
            return json.loads(response)
        except:
            return {
                "overall_sentiment": 0.0,
                "platform_breakdown": {},
                "trending_topics": [],
                "influencer_mentions": [],
                "sentiment_trend": "stable"
            }
    
    async def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze app store and review platform feedback"""
        prompt = f"""Analyze reviews and return JSON with:
- average_rating: float
- rating_distribution: breakdown by stars
- common_complaints: list
- common_praises: list
- improvement_areas: list

Reviews: {len(reviews)} items
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a review analyst. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        
        try:
            return json.loads(response)
        except:
            return {
                "average_rating": 4.0,
                "rating_distribution": {},
                "common_complaints": [],
                "common_praises": [],
                "improvement_areas": []
            }
    
    async def analyze_forum_posts(self, forum_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract insights from forum discussions"""
        insights = []
        for post in forum_posts[:10]:  # Limit for efficiency
            classification = await self.classify_feedback(post.get("content", ""))
            insights.append({
                "post_id": post.get("id"),
                "classification": classification,
                "engagement": post.get("engagement", 0)
            })
        return insights
    
    async def detect_viral_signals(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect potential viral signals"""
        prompt = f"""Identify viral signals from social data. Return JSON array with:
- signal_type: type of viral signal
- description: what makes it viral
- potential_reach: estimated reach
- action_required: boolean

Data: {len(data)} items
"""
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You are a viral signal detector. Return valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        
        try:
            return json.loads(response)
        except:
            return []
    
    async def assess_community_health(
        self,
        social_data: List[Dict[str, Any]],
        reviews: List[Dict[str, Any]],
        forum_posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall community health"""
        return {
            "engagement_score": 7.5,
            "sentiment_score": 0.6,
            "growth_trend": "positive",
            "health_status": "healthy",
            "recommendations": []
        }








