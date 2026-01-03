from typing import Dict, List, Any
from core.database import Recommendation, FeatureNotification, Feedback, get_db
from sqlalchemy.orm import Session
from datetime import datetime

class FeedbackLoop:
    """Manage feedback loop - notify customers when features ship"""
    
    def generate_email_template(
        self,
        recommendation: Recommendation,
        customer_id: str,
        customer_feedback: List[Feedback]
    ) -> Dict[str, Any]:
        """Generate email notification template for a customer"""
        
        # Extract customer quotes from their feedback
        customer_quotes = [
            f.f.content[:200] + "..." if len(f.f.content) > 200 else f.f.content
            for f in customer_feedback[:3]  # Top 3 quotes
        ]
        
        # Generate personalized email
        email_subject = f"🎉 {recommendation.title} is now available!"
        
        email_body = f"""
Hi there!

Great news! We've shipped a feature you requested: **{recommendation.title}**

{recommendation.description or "This feature addresses feedback you provided and is now live in the product."}

**What you asked for:**
"""
        
        for i, quote in enumerate(customer_quotes, 1):
            email_body += f"\n{i}. \"{quote}\"\n"
        
        email_body += f"""

**What's new:**
{recommendation.description or "The feature is now available for you to use."}

**Try it now:**
[Link to feature/documentation]

We'd love to hear your feedback on this update. Your input helps us build better products!

Best regards,
The Product Team

---
This is an automated notification. You're receiving this because you requested this feature.
"""
        
        return {
            "to": customer_id,  # In production, this would be the customer's email
            "subject": email_subject,
            "body": email_body,
            "html_body": self._generate_html_email(email_subject, email_body, recommendation, customer_quotes)
        }
    
    def _generate_html_email(
        self,
        subject: str,
        body: str,
        recommendation: Recommendation,
        quotes: List[str]
    ) -> str:
        """Generate HTML version of email"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .feature-box {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea; border-radius: 5px; }}
        .quote {{ background: #f0f0f0; padding: 15px; margin: 10px 0; border-left: 3px solid #667eea; font-style: italic; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Feature Shipped!</h1>
            <p>{subject.replace('🎉 ', '')}</p>
        </div>
        <div class="content">
            <div class="feature-box">
                <h2>{recommendation.title}</h2>
                <p>{recommendation.description or "This feature addresses feedback you provided and is now live."}</p>
            </div>
            
            <h3>What you asked for:</h3>
"""
        for quote in quotes:
            html += f'<div class="quote">"{quote}"</div>\n'
        
        html += f"""
            <div style="text-align: center;">
                <a href="#" class="button">Try It Now →</a>
            </div>
            
            <div class="footer">
                <p>This is an automated notification. You're receiving this because you requested this feature.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def notify_customers_on_ship(
        self,
        recommendation_id: int,
        db: Session,
        generate_emails: bool = True
    ) -> Dict[str, Any]:
        """Notify customers who requested a feature when it ships"""
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            return {"notified": 0, "message": "Recommendation not found"}
        
        if recommendation.status != "shipped":
            return {"notified": 0, "message": "Recommendation not shipped. Please mark as shipped first."}
        
        # Find feedback items related to this feature
        feedback_items = db.query(Feedback).filter(
            Feedback.feature == recommendation.feature
        ).all()
        
        # Get unique customer IDs with their feedback
        customer_feedback_map: Dict[str, List[Feedback]] = {}
        for item in feedback_items:
            if item.account_id:
                if item.account_id not in customer_feedback_map:
                    customer_feedback_map[item.account_id] = []
                customer_feedback_map[item.account_id].append(item)
        
        customer_ids = list(customer_feedback_map.keys())
        
        # Generate email templates
        email_templates = []
        if generate_emails:
            for customer_id, customer_feedback in customer_feedback_map.items():
                email_template = self.generate_email_template(
                    recommendation,
                    customer_id,
                    customer_feedback
                )
                email_templates.append(email_template)
        
        # Create notifications
        notifications = []
        for customer_id in customer_ids:
            # Check if notification already exists
            existing = db.query(FeatureNotification).filter(
                FeatureNotification.feature_id == recommendation_id,
                FeatureNotification.customer_id == customer_id
            ).first()
            
            if not existing:
                notification = FeatureNotification(
                    feature_id=recommendation_id,
                    customer_id=customer_id,
                    notified_at=datetime.utcnow(),
                    adoption_tracked=False
                )
                db.add(notification)
                notifications.append(notification)
        
        db.commit()
        
        return {
            "notified": len(notifications),
            "total_customers": len(customer_ids),
            "customer_ids": customer_ids,
            "feature": recommendation.title,
            "email_templates": email_templates if generate_emails else [],
            "message": f"Generated {len(email_templates)} email templates for {len(customer_ids)} customers"
        }
    
    def track_adoption(
        self,
        recommendation_id: int,
        customer_id: str,
        adopted: bool,
        db: Session
    ) -> Dict[str, Any]:
        """Track feature adoption for a customer"""
        notification = db.query(FeatureNotification).filter(
            FeatureNotification.feature_id == recommendation_id,
            FeatureNotification.customer_id == customer_id
        ).first()
        
        if notification:
            notification.adoption_tracked = True
            notification.adoption_rate = 1.0 if adopted else 0.0
            db.commit()
        
        return {"status": "tracked", "adopted": adopted}
    
    def get_adoption_stats(
        self,
        recommendation_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get comprehensive adoption statistics comparing request volume vs adoption
        
        Tracks:
        - Original request volume (how many customers requested this feature)
        - Adoption rate (how many actually use it after shipping)
        - Gap analysis (requested vs adopted)
        - Segment breakdown
        - ARR impact analysis
        """
        from core.database import Theme
        
        # Get recommendation
        recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not recommendation:
            return {"error": "Recommendation not found"}
        
        # Get theme to find original request volume
        theme = db.query(Theme).filter(Theme.name == recommendation.feature).first()
        
        # Get original feedback/requests for this feature
        original_requests = []
        if theme:
            original_requests = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        # Get adoption tracking data
        notifications = db.query(FeatureNotification).filter(
            FeatureNotification.feature_id == recommendation_id,
            FeatureNotification.adoption_tracked == True
        ).all()
        
        # Calculate original request metrics
        original_request_count = len(original_requests)
        original_request_arr = sum([f.arr for f in original_requests if f.arr and f.arr > 0])
        original_request_customers = len(set([f.account_id for f in original_requests if f.account_id]))
        
        # Calculate adoption metrics
        total_notified = len(notifications)
        adopted_count = sum(1 for n in notifications if n.adoption_rate and n.adoption_rate > 0.5)
        adoption_rate = (adopted_count / total_notified * 100) if total_notified > 0 else 0.0
        
        # Calculate adoption by segment
        adoption_by_segment = {}
        request_by_segment = {}
        
        for feedback in original_requests:
            segment = feedback.user_segment or "unknown"
            request_by_segment[segment] = request_by_segment.get(segment, 0) + 1
        
        for notification in notifications:
            # Try to find customer segment from original requests
            customer_segment = "unknown"
            for feedback in original_requests:
                if feedback.account_id == notification.customer_id:
                    customer_segment = feedback.user_segment or "unknown"
                    break
            
            if customer_segment not in adoption_by_segment:
                adoption_by_segment[customer_segment] = {"requested": 0, "adopted": 0, "notified": 0}
            
            adoption_by_segment[customer_segment]["notified"] += 1
            if notification.adoption_rate and notification.adoption_rate > 0.5:
                adoption_by_segment[customer_segment]["adopted"] += 1
        
        # Set requested counts
        for segment, count in request_by_segment.items():
            if segment not in adoption_by_segment:
                adoption_by_segment[segment] = {"requested": 0, "adopted": 0, "notified": 0}
            adoption_by_segment[segment]["requested"] = count
        
        # Calculate gap analysis
        gap = original_request_count - adopted_count
        gap_percentage = (gap / original_request_count * 100) if original_request_count > 0 else 0.0
        
        # Calculate ARR impact
        adopted_arr = 0.0
        for notification in notifications:
            if notification.adoption_rate and notification.adoption_rate > 0.5:
                # Find customer ARR from original requests
                for feedback in original_requests:
                    if feedback.account_id == notification.customer_id and feedback.arr:
                        adopted_arr += feedback.arr
                        break
        
        # Adoption insights
        insights = []
        if adoption_rate < 30:
            insights.append("⚠️ Low adoption rate - feature may not meet customer expectations")
        elif adoption_rate < 60:
            insights.append("📊 Moderate adoption - consider improving onboarding or feature discoverability")
        else:
            insights.append("✅ Strong adoption - feature is meeting customer needs")
        
        if gap > original_request_count * 0.5:
            insights.append(f"⚠️ Large gap: {gap} customers requested but haven't adopted ({gap_percentage:.0f}%)")
        
        # Calculate time-based metrics if available
        shipped_at = None
        if recommendation.extra_metadata and recommendation.extra_metadata.get("shipped_at"):
            from datetime import datetime
            shipped_at = recommendation.extra_metadata["shipped_at"]
        
        return {
            # Original request metrics
            "original_request_volume": {
                "total_requests": original_request_count,
                "unique_customers": original_request_customers,
                "total_arr_requested": round(original_request_arr, 2),
                "avg_arr_per_customer": round(original_request_arr / original_request_customers, 2) if original_request_customers > 0 else 0
            },
            
            # Adoption metrics
            "adoption_metrics": {
                "total_notified": total_notified,
                "adopted_count": adopted_count,
                "adoption_rate": round(adoption_rate, 2),  # Percentage
                "adopted_arr": round(adopted_arr, 2),
                "adoption_arr_percentage": round((adopted_arr / original_request_arr * 100) if original_request_arr > 0 else 0, 2)
            },
            
            # Gap analysis
            "demand_vs_adoption": {
                "requested": original_request_count,
                "adopted": adopted_count,
                "gap": gap,
                "gap_percentage": round(gap_percentage, 2),
                "adoption_rate": round(adoption_rate, 2)
            },
            
            # Segment breakdown
            "segment_breakdown": {
                segment: {
                    "requested": data["requested"],
                    "notified": data["notified"],
                    "adopted": data["adopted"],
                    "adoption_rate": round((data["adopted"] / data["notified"] * 100) if data["notified"] > 0 else 0, 2)
                }
                for segment, data in adoption_by_segment.items()
            },
            
            # Insights and recommendations
            "insights": insights,
            
            # Metadata
            "feature_name": recommendation.feature,
            "feature_title": recommendation.title,
            "shipped_at": shipped_at,
            "status": recommendation.status
        }

