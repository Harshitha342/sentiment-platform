from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from app.models.database import Base
from datetime import datetime

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, index=True)
    sentiment_label = Column(String)
    confidence_score = Column(Float)
    emotion = Column(String)
    model_name = Column(String)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
