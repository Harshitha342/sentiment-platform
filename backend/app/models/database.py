from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Index
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# -----------------------------
# Table 1: social_media_posts
# -----------------------------
class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(String(50), index=True)
    content = Column(Text)
    author = Column(String(255))
    created_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_posts_created_at", "created_at"),
    )


# -----------------------------
# Table 2: sentiment_analysis
# -----------------------------
class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(
        String(255),
        ForeignKey("social_media_posts.post_id"),
        nullable=False
    )
    model_name = Column(String(100))
    sentiment_label = Column(String(20))
    confidence_score = Column(Float)
    emotion = Column(String(50), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)


# -----------------------------
# Table 3: sentiment_alerts
# -----------------------------
class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50))
    threshold_value = Column(Float)
    actual_value = Column(Float)
    window_start = Column(DateTime)
    window_end = Column(DateTime)
    post_count = Column(Integer)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON)
