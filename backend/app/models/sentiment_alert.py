from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base

class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"

    id = Column(Integer, primary_key=True)
    alert_type = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    actual_ratio = Column(Float, nullable=False)
    window_minutes = Column(Integer, nullable=False)
    metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
