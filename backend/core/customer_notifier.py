from typing import Dict, List, Any
from core.database import Feedback, Recommendation, Theme
from sqlalchemy.orm import Session
from datetime import datetime

class CustomerNotifier:
    """Notify customers when features they requested are shipped"""
    
    def get_customers_to_notify(self, recommendation: Recommendation, db: Session) -> List[Dict[str, Any]]:
        """Get list of customers who requested this feature"""
        # Get theme for this recommendation
        theme = db.query(Theme).filter(Theme.name == recommendation.feature).first()
        
        if not theme:
            return []
        
        # Get all feedback for this theme
        feedback_items = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        customers = []
        seen_accounts = set()
        
        for feedback in feedback_items:
            # Skip if no account identifier
            if not feedback.account_id and not feedback.source_id:
                continue
            
            account_id = feedback.account_id or feedback.source_id
            
            # Avoid duplicates
            if account_id in seen_accounts:
                continue
            seen_accounts.add(account_id)
            
            customers.append({
                "account_id": account_id,
                "source": feedback.source,
                "arr": feedback.arr,
                "user_segment": feedback.user_segment,
                "feedback_content": feedback.content[:200],  # Preview
                "feedback_date": feedback.created_at.isoformat() if feedback.created_at else None
            })
        
        return customers
    
    def generate_notification_email(self, recommendation: Recommendation, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email notification for a customer"""
        subject = f"🎉 We shipped: {recommendation.title}"
        
        body = f"""Hi there,

Great news! We've shipped a feature you requested:

**{recommendation.title}**

{recommendation.description}

We heard your feedback and made it happen. Thank you for helping us build a better product!

Best regards,
The Product Team
"""
        
        return {
            "to": customer.get("account_id"),  # In production, would map to email
            "subject": subject,
            "body": body,
            "customer": customer,
            "recommendation": {
                "title": recommendation.title,
                "description": recommendation.description,
                "feature": recommendation.feature
            }
        }
    
    def notify_customers(self, recommendation: Recommendation, db: Session) -> Dict[str, Any]:
        """Notify all customers who requested this feature"""
        customers = self.get_customers_to_notify(recommendation, db)
        
        notifications = []
        for customer in customers:
            notification = self.generate_notification_email(recommendation, customer)
            notifications.append(notification)
        
        return {
            "recommendation_id": recommendation.id,
            "feature": recommendation.feature,
            "customers_notified": len(notifications),
            "notifications": notifications
        }







