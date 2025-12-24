from fastapi import APIRouter, status, Query
from datetime import datetime
from typing import Optional

from sqlalchemy import text, select, func
from app.models.database import async_session_maker
from app.models.social_media_post import SocialMediaPost
from app.models.sentiment_analysis import SentimentAnalysis

import redis.asyncio as redis
import os

# ✅ ONE router, ONE prefix
router = APIRouter(prefix="/api", tags=["api"])

# =====================================================
# Health Check Endpoint
# =====================================================
@router.get("/health", status_code=200)
async def health_check():
    timestamp = datetime.utcnow().isoformat() + "Z"

    db_status = "connected"
    redis_status = "connected"

    total_posts = 0
    total_analyses = 0
    recent_posts_1h = 0

    # ---- Database check ----
    try:
        async with async_session_maker() as session:
            total_posts = (await session.execute(
                text("SELECT COUNT(*) FROM social_media_posts")
            )).scalar()

            total_analyses = (await session.execute(
                text("SELECT COUNT(*) FROM sentiment_analysis")
            )).scalar()

            recent_posts_1h = (await session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM social_media_posts
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
            )).scalar()
    except Exception as e:
        print("DB health error:", e)
        db_status = "disconnected"

    # ---- Redis check ----
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await redis_client.ping()
    except Exception as e:
        print("Redis health error:", e)
        redis_status = "disconnected"

    status_value = "healthy"
    http_status = status.HTTP_200_OK

    if db_status == "disconnected" or redis_status == "disconnected":
        status_value = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": status_value,
        "timestamp": timestamp,
        "services": {
            "database": db_status,
            "redis": redis_status
        },
        "stats": {
            "total_posts": total_posts,
            "total_analyses": total_analyses,
            "recent_posts_1h": recent_posts_1h
        }
    }

# =====================================================
# Get Posts Endpoint
# =====================================================
@router.get("/posts")
async def get_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    async with async_session_maker() as session:
        stmt = (
            select(SocialMediaPost, SentimentAnalysis)
            .join(
                SentimentAnalysis,
                SocialMediaPost.post_id == SentimentAnalysis.post_id
            )
        )

        # ---- filters ----
        if source:
            stmt = stmt.where(SocialMediaPost.source == source)

        if sentiment:
            stmt = stmt.where(SentimentAnalysis.sentiment_label == sentiment)

        if start_date:
            stmt = stmt.where(SocialMediaPost.created_at >= start_date)

        if end_date:
            stmt = stmt.where(SocialMediaPost.created_at <= end_date)

        # ---- total count ----
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt)

        # ---- pagination ----
        stmt = (
            stmt
            .order_by(SocialMediaPost.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)

        posts = []
        for post, analysis in result.all():
            posts.append({
                "post_id": post.post_id,
                "source": post.source,
                "content": post.content,
                "author": post.author,
                "created_at": post.created_at.isoformat(),
                "sentiment": {
                    "label": analysis.sentiment_label,
                    "confidence": analysis.confidence_score,
                    "emotion": analysis.emotion,
                    "model_name": analysis.model_name,
                }
            })

        return {
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset,
            "filters": {
                "source": source,
                "sentiment": sentiment,
                "start_date": start_date,
                "end_date": end_date,
            }
        }
