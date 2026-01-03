from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from core.config import settings

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content = Column(Text)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    extra_metadata = Column(JSON)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)  # zendesk, intercom, salesforce, gong, dovetail, nps, app_store, forum, social
    source_id = Column(String)
    content = Column(Text, nullable=False)
    classification = Column(String)  # bug, feature_request, usability_issue, integration_request
    sentiment_score = Column(Float)
    pain_level = Column(Float)
    urgency = Column(String)  # low, medium, high, critical
    user_segment = Column(String)
    feature = Column(String)
    reason = Column(Text)
    account_id = Column(String)
    arr = Column(Float)
    churn_risk = Column(Float)
    theme_id = Column(Integer, ForeignKey("themes.id"))
    impact_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON)
    
    theme = relationship("Theme", back_populates="feedback_items")

class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    trend_velocity = Column(Float)
    request_frequency = Column(Integer)
    customer_value = Column(Float)
    strategic_segment_weight = Column(Float)
    competitive_pressure = Column(Float)
    recency_score = Column(Float)
    overall_impact_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_metadata = Column(JSON)  # Store lost_deal_info, time_series_data, etc.
    
    feedback_items = relationship("Feedback", back_populates="theme")

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    positioning = Column(Text)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    website_url = Column(String)
    pricing_info = Column(JSON)
    funding_info = Column(JSON)
    customer_reviews_sentiment = Column(Float)
    social_sentiment = Column(Float)
    product_updates = Column(JSON)
    complaints = Column(JSON)
    market_gaps = Column(JSON)
    opportunities = Column(JSON)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_metadata = Column(JSON)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    feature = Column(String)
    impact_score = Column(Float)
    feasibility_score = Column(Float)
    risk_score = Column(Float)
    ux_implications = Column(Text)
    business_impact = Column(Text)
    pm_verdict = Column(Text)
    ux_verdict = Column(Text)
    data_scientist_verdict = Column(Text)
    engineering_verdict = Column(Text)
    unified_recommendation = Column(Text)
    customer_quotes = Column(JSON)
    evidence = Column(JSON)
    status = Column(String, default="pending")  # pending, approved, rejected, in_progress, shipped
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON)

class Roadmap(Base):
    __tablename__ = "roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    quarter = Column(String)  # Q1 2024, Q2 2024, etc.
    year = Column(Integer)
    items = Column(JSON)  # List of recommendation IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON)

class FeatureNotification(Base):
    __tablename__ = "feature_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("recommendations.id"))
    customer_id = Column(String)
    notified_at = Column(DateTime, default=datetime.utcnow)
    adoption_tracked = Column(Boolean, default=False)
    adoption_rate = Column(Float)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and ensure schema is up to date"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations to ensure columns exist (for existing databases)
    try:
        import sqlite3
        from core.config import settings
        
        database_url = settings.database_url
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                from pathlib import Path
                db_path = Path(__file__).parent.parent / db_path[2:]
            else:
                from pathlib import Path
                db_path = Path(db_path)
            
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check and add extra_metadata to themes if missing
                cursor.execute("PRAGMA table_info(themes)")
                columns = [column[1] for column in cursor.fetchall()]
                if "extra_metadata" not in columns:
                    cursor.execute("ALTER TABLE themes ADD COLUMN extra_metadata TEXT")
                    conn.commit()
                
                conn.close()
    except Exception:
        # Migration failed, but that's okay - tables will be created with correct schema
        pass

def get_db():
    """Database dependency with error handling"""
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"❌ Database session error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Re-raise to let the route handler catch it
        raise
    finally:
        if db:
            try:
                db.close()
            except:
                pass

