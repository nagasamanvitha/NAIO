from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
import json

class MockDataGenerator:
    """Generate comprehensive mock data for all sources"""
    
    # App Store Review Data
    APP_STORE_REVIEWS = [
        "Great app! Love the new dashboard feature. Makes my work so much easier.",
        "The app crashes when I try to export data. Very frustrating.",
        "Would love to see dark mode support. The current UI is too bright.",
        "Excellent customer support. They helped me integrate with Salesforce quickly.",
        "The mobile app needs better offline support. Can't work without internet.",
        "Love the analytics features but wish there was a way to export to Excel.",
        "Bug: The search function doesn't work properly. Returns wrong results.",
        "Amazing product! The new AI features are game-changing.",
        "The pricing is too high for small businesses. Need a cheaper tier.",
        "Great app but the onboarding process is confusing. Needs improvement.",
        "The API documentation is outdated. Please update it.",
        "Love the real-time collaboration features. Team productivity increased 50%.",
        "The app is slow when loading large datasets. Performance needs work.",
        "Would be great to have Slack integration. That's a must-have for us.",
        "The mobile app UI is outdated. Needs a modern redesign.",
        "Excellent reporting features. The custom dashboards are perfect.",
        "The app freezes when switching between projects. Very annoying bug.",
        "Love the new notification system. Much better than before.",
        "Need better data visualization options. Current charts are limited.",
        "The app doesn't sync properly between devices. Lost some data.",
        "Great customer service. They fixed my issue within hours.",
        "The search feature is amazing. Finds everything instantly.",
        "The app needs better security features. Concerned about data privacy.",
        "Love the new update! The performance improvements are noticeable.",
        "The mobile app needs push notifications. Missing important updates.",
        "The export feature is broken. Can't download my reports.",
        "Excellent product! Worth every penny.",
        "The app crashes on Android 12. Please fix compatibility issues.",
        "Would love to see more integrations. HubSpot would be great.",
        "The dashboard is cluttered. Needs better organization.",
    ]
    
    COUNTRIES = ["United States", "United Kingdom", "Canada", "Australia", "Germany", "France", "Japan", "India", "Brazil", "Mexico"]
    
    CRM_FEEDBACK = [
        "Customer mentioned they need SSO integration for enterprise deployment.",
        "Prospect asked about API rate limits during sales call.",
        "Customer requested white-labeling options for their brand.",
        "Prospect concerned about data residency requirements.",
        "Customer wants custom reporting dashboards for their team.",
        "Prospect asked about mobile app availability during demo.",
        "Customer requested webhook support for real-time updates.",
        "Prospect needs advanced analytics for their use case.",
        "Customer mentioned slow performance with large datasets.",
        "Prospect asked about integration with their existing tools.",
    ]
    
    SUPPORT_TICKETS = [
        "User reports that the export feature is not working. Error message appears when trying to download CSV.",
        "Customer experiencing slow page load times on the dashboard. Takes 30+ seconds to load.",
        "Feature request: Would love to see a dark mode option in settings.",
        "Bug report: The app crashes when switching between projects on mobile.",
        "Integration request: Need to connect with Zapier for workflow automation.",
        "User confused about how to set up webhooks. Documentation unclear.",
        "Performance issue: The search function is very slow with 10k+ records.",
        "Feature request: Add ability to export reports to PDF format.",
        "Bug: The notification system is not sending emails properly.",
        "User wants to know if there's a way to customize the dashboard layout.",
    ]
    
    SALES_NOTES = [
        "Discovery call: Customer needs real-time collaboration features for their remote team.",
        "Demo feedback: Prospect loved the analytics but wants more customization options.",
        "Objection handling: Pricing concerns addressed. Emphasized ROI and enterprise features.",
        "Follow-up: Customer interested in API access. Scheduled technical deep-dive.",
        "Competitive: Prospect comparing with Competitor A. Our integration ecosystem is key differentiator.",
        "Use case: Customer wants to use for customer feedback analysis. Perfect fit.",
        "Timeline: Customer wants to implement by Q2. Need to highlight fast onboarding.",
        "Decision maker: CTO is the main stakeholder. Technical features are priority.",
        "Budget: Customer has budget approved. Ready to move forward if we meet requirements.",
        "Pain point: Current solution too slow. Our performance is a major selling point.",
    ]
    
    USER_INTERVIEWS = [
        "User mentioned they struggle with the current workflow. They want a more streamlined process.",
        "Interview revealed that users find the navigation confusing. Need better UX design.",
        "User wants more control over notifications. Too many alerts currently.",
        "Interview: Users love the core features but want better mobile experience.",
        "User feedback: The onboarding process is too long. Needs to be simplified.",
        "Interview revealed pain point: Data export is limited. Need more format options.",
        "User wants better search functionality. Current search is not intuitive.",
        "Interview: Users need better collaboration features. Current tools are basic.",
        "User feedback: The dashboard is overwhelming. Need better organization.",
        "Interview revealed: Users want more customization options for their workspace.",
    ]
    
    SOCIAL_MEDIA_POSTS = [
        "Just tried the new feature - amazing! @ProductName",
        "Wish @ProductName had better mobile support. Desktop is great though.",
        "Frustrated with @ProductName today. The app keeps crashing.",
        "Love the new update from @ProductName! The UI improvements are great.",
        "Anyone else having issues with @ProductName sync? Mine isn't working.",
        "Shoutout to @ProductName support team. They fixed my issue super fast!",
        "The new @ProductName dashboard is 🔥. So much better than before.",
        "Really need @ProductName to add Slack integration. That would be perfect.",
        "Just discovered @ProductName. This is exactly what I needed!",
        "The @ProductName mobile app needs work. Desktop version is much better.",
    ]
    
    NPS_COMMENTS = [
        "Love the product! Best tool I've used this year.",
        "Good product but could use some improvements.",
        "It's okay. Does what it needs to do.",
        "Not satisfied. Too many bugs and missing features.",
        "Excellent! Would definitely recommend to others.",
        "Decent product. Gets the job done.",
        "Amazing features! The team loves it.",
        "Needs work. Too many issues to recommend.",
        "Great value for money. Very happy with purchase.",
        "Could be better. Missing some key features I need.",
    ]
    
    @staticmethod
    def generate_app_store_reviews(count: int = 50) -> List[Dict[str, Any]]:
        """Generate App Store review data matching Kaggle dataset structure"""
        reviews = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(count):
            review_text = random.choice(MockDataGenerator.APP_STORE_REVIEWS)
            star_rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[0.1, 0.1, 0.2, 0.3, 0.3]  # More positive reviews
            )[0]
            
            # Determine sentiment based on rating
            issue_flag = "Yes" if star_rating <= 2 else "No"
            
            # Generate date
            days_ago = random.randint(0, 90)
            review_date = (base_date + timedelta(days=days_ago)).strftime("%d.%m.%Y")
            
            reviews.append({
                "source": "app_store",
                "source_id": f"ASR-{10000 + i}",
                "content": review_text,
                "context": {
                    "date": review_date,
                    "platform": random.choice(["iOS", "Android"]),
                    "country": random.choice(MockDataGenerator.COUNTRIES),
                    "star": star_rating,
                    "user_id": f"user_{random.randint(1000, 9999)}",
                    "issue_flag": issue_flag,
                    "likes_count": random.randint(0, 50),
                    "dislike_count": random.randint(0, 10),
                    "label": "positive" if star_rating >= 4 else "negative" if star_rating <= 2 else "neutral"
                }
            })
        
        return reviews
    
    @staticmethod
    def generate_support_tickets(count: int = 30) -> List[Dict[str, Any]]:
        """Generate support tickets (Zendesk/Intercom style)"""
        tickets = []
        
        for i in range(count):
            content = random.choice(MockDataGenerator.SUPPORT_TICKETS)
            priority = random.choice(["low", "medium", "high", "urgent"])
            
            tickets.append({
                "source": random.choice(["zendesk", "intercom"]),
                "source_id": f"{'ZD' if random.random() > 0.5 else 'IC'}-{2000 + i}",
                "content": content,
                "context": {
                    "priority": priority,
                    "status": random.choice(["open", "pending", "resolved", "closed"]),
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    "assignee": f"agent_{random.randint(1, 10)}"
                }
            })
        
        return tickets
    
    @staticmethod
    def generate_sales_notes(count: int = 25) -> List[Dict[str, Any]]:
        """Generate sales notes (Salesforce/Gong style)"""
        notes = []
        
        for i in range(count):
            content = random.choice(MockDataGenerator.SALES_NOTES)
            
            notes.append({
                "source": random.choice(["salesforce", "gong"]),
                "source_id": f"{'SF' if random.random() > 0.5 else 'GONG'}-{3000 + i}",
                "content": content,
                "context": {
                    "account_name": f"Account {chr(65 + (i % 26))}{i // 26 + 1}",
                    "arr": random.randint(10000, 500000),
                    "stage": random.choice(["prospect", "qualified", "demo", "negotiation", "closed-won", "closed-lost"]),
                    "sales_rep": f"rep_{random.randint(1, 15)}",
                    "call_duration": random.randint(15, 60),
                    "sentiment": random.choice(["positive", "neutral", "negative"])
                }
            })
        
        return notes
    
    @staticmethod
    def generate_user_interviews(count: int = 15) -> List[Dict[str, Any]]:
        """Generate user interview data (Dovetail style)"""
        interviews = []
        
        for i in range(count):
            content = random.choice(MockDataGenerator.USER_INTERVIEWS)
            
            interviews.append({
                "source": "dovetail",
                "source_id": f"DT-{4000 + i}",
                "content": content,
                "context": {
                    "interview_date": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
                    "duration": random.randint(30, 90),
                    "interviewer": f"researcher_{random.randint(1, 5)}",
                    "user_persona": random.choice(["power_user", "casual_user", "admin", "end_user"]),
                    "tags": random.sample(["ux", "feature_request", "pain_point", "workflow"], k=random.randint(1, 3))
                }
            })
        
        return interviews
    
    @staticmethod
    def generate_social_media(count: int = 40) -> List[Dict[str, Any]]:
        """Generate social media posts"""
        posts = []
        platforms = ["twitter", "linkedin", "reddit", "facebook"]
        
        for i in range(count):
            content = random.choice(MockDataGenerator.SOCIAL_MEDIA_POSTS)
            platform = random.choice(platforms)
            
            posts.append({
                "source": "social",
                "source_id": f"SOCIAL-{5000 + i}",
                "content": content,
                "context": {
                    "platform": platform,
                    "engagement": random.randint(0, 1000),
                    "retweets": random.randint(0, 100) if platform == "twitter" else 0,
                    "likes": random.randint(0, 500),
                    "sentiment": random.choice(["positive", "neutral", "negative"])
                }
            })
        
        return posts
    
    @staticmethod
    def generate_nps_feedback(count: int = 60) -> List[Dict[str, Any]]:
        """Generate NPS feedback"""
        feedback = []
        
        for i in range(count):
            score = random.randint(0, 10)
            comment = random.choice(MockDataGenerator.NPS_COMMENTS)
            
            # Determine segment based on score
            if score >= 9:
                segment = "promoter"
            elif score >= 7:
                segment = "passive"
            else:
                segment = "detractor"
            
            feedback.append({
                "source": "nps",
                "source_id": f"NPS-{6000 + i}",
                "content": comment,
                "context": {
                    "score": score,
                    "segment": segment,
                    "user_segment": random.choice(["enterprise", "smb", "individual"]),
                    "survey_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                }
            })
        
        return feedback
    
    @staticmethod
    def generate_crm_feedback(count: int = 20) -> List[Dict[str, Any]]:
        """Generate CRM feedback (from sales/account management)"""
        feedback = []
        
        for i in range(count):
            content = random.choice(MockDataGenerator.CRM_FEEDBACK)
            
            feedback.append({
                "source": "crm",
                "source_id": f"CRM-{7000 + i}",
                "content": content,
                "context": {
                    "account_id": f"ACC-{random.randint(100, 999)}",
                    "account_name": f"Company {chr(65 + (i % 26))}",
                    "arr": random.randint(50000, 1000000),
                    "account_manager": f"am_{random.randint(1, 10)}",
                    "churn_risk": random.choice(["low", "medium", "high"]),
                    "last_contact": (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat()
                }
            })
        
        return feedback
    
    @staticmethod
    def generate_in_app_feedback(count: int = 30) -> List[Dict[str, Any]]:
        """Generate in-app feedback"""
        feedback = []
        
        in_app_messages = [
            "The new feature is great! Love it.",
            "This button doesn't work. Please fix.",
            "Would love to see more customization options here.",
            "The loading time is too long. Needs optimization.",
            "Great update! The UI improvements are noticeable.",
            "Bug: The form validation is not working correctly.",
            "Feature request: Add keyboard shortcuts for power users.",
            "The mobile view needs improvement. Hard to use on phone.",
            "Love the new design! Much cleaner interface.",
            "The search results are not accurate. Please improve algorithm.",
        ]
        
        for i in range(count):
            content = random.choice(in_app_messages)
            
            feedback.append({
                "source": "in_app",
                "source_id": f"IAP-{8000 + i}",
                "content": content,
                "context": {
                    "user_id": f"user_{random.randint(10000, 99999)}",
                    "session_id": f"session_{random.randint(1000, 9999)}",
                    "page": random.choice(["/dashboard", "/analytics", "/settings", "/projects"]),
                    "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                    "device": random.choice(["desktop", "mobile", "tablet"])
                }
            })
        
        return feedback
    
    @staticmethod
    def generate_community_forum_posts(count: int = 25) -> List[Dict[str, Any]]:
        """Generate community forum posts"""
        posts = []
        
        forum_topics = [
            "How do I export data to Excel?",
            "The API documentation needs updating.",
            "Feature request: Dark mode please!",
            "Bug report: App crashes on startup.",
            "Great product! Just needs better mobile support.",
            "How to integrate with Zapier?",
            "The search function is not working properly.",
            "Love the new update! Performance is much better.",
            "Need help with webhook setup.",
            "Feature request: Add more chart types.",
        ]
        
        for i in range(count):
            content = random.choice(forum_topics)
            
            posts.append({
                "source": "forum",
                "source_id": f"FORUM-{9000 + i}",
                "content": content,
                "context": {
                    "forum": random.choice(["community", "discord", "reddit"]),
                    "author": f"user_{random.randint(100, 999)}",
                    "replies": random.randint(0, 20),
                    "views": random.randint(10, 500),
                    "upvotes": random.randint(0, 50),
                    "category": random.choice(["feature_request", "bug_report", "question", "discussion"])
                }
            })
        
        return posts
    
    @staticmethod
    def generate_all_mock_data() -> Dict[str, List[Dict[str, Any]]]:
        """Generate all types of mock data"""
        return {
            "app_store_reviews": MockDataGenerator.generate_app_store_reviews(50),
            "support_tickets": MockDataGenerator.generate_support_tickets(30),
            "sales_notes": MockDataGenerator.generate_sales_notes(25),
            "user_interviews": MockDataGenerator.generate_user_interviews(15),
            "social_media": MockDataGenerator.generate_social_media(40),
            "nps_feedback": MockDataGenerator.generate_nps_feedback(60),
            "crm_feedback": MockDataGenerator.generate_crm_feedback(20),
            "in_app_feedback": MockDataGenerator.generate_in_app_feedback(30),
            "forum_posts": MockDataGenerator.generate_community_forum_posts(25),
        }
    
    @staticmethod
    def get_all_feedback_flat() -> List[Dict[str, Any]]:
        """Get all feedback as a flat list for processing"""
        all_data = MockDataGenerator.generate_all_mock_data()
        feedback_list = []
        
        for source_type, items in all_data.items():
            feedback_list.extend(items)
        
        return feedback_list
