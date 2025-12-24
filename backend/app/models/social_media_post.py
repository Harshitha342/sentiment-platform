from sqlalchemy import Column, Integer, String, DateTime, Text
from app.models.database import Base
from datetime import datetime

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, index=True)
    content = Column(Text, nullable=False)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
