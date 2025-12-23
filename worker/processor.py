from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import SocialMediaPost, SentimentAnalysis


async def save_post_and_analysis(
    db: Session,
    post_data: dict,
    sentiment_result: dict,
    emotion_result: dict,
):
    """
    Save post + sentiment + emotion to database
    """

    post = (
        db.query(SocialMediaPost)
        .filter(SocialMediaPost.post_id == post_data["post_id"])
        .first()
    )

    if not post:
        post = SocialMediaPost(
            post_id=post_data["post_id"],
            source=post_data["source"],
            content=post_data["content"],
            author=post_data["author"],
            created_at=post_data["created_at"],
            ingested_at=datetime.utcnow(),
        )
        db.add(post)
        db.flush()

    analysis = SentimentAnalysis(
        post_id=post.post_id,
        model_name=sentiment_result["model_name"],
        sentiment_label=sentiment_result["sentiment_label"],
        confidence_score=sentiment_result["confidence_score"],
        emotion=emotion_result["emotion"],
        analyzed_at=datetime.utcnow(),
    )

    db.add(analysis)
    db.commit()

    return post.id, analysis.id
