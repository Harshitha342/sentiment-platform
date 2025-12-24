from fastapi import APIRouter, status, Query
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import text, select, func, case
from app.models.database import async_session_maker
from app.models.social_media_post import SocialMediaPost
from app.models.sentiment_analysis import SentimentAnalysis

import redis.asyncio as redis
import os

#ONE router only
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
                    SELECT COUNT(*) FROM social_media_posts
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
            )).scalar()
    except Exception:
        db_status = "disconnected"

    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await redis_client.ping()
    except Exception:
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

        if source:
            stmt = stmt.where(SocialMediaPost.source == source)
        if sentiment:
            stmt = stmt.where(SentimentAnalysis.sentiment_label == sentiment)
        if start_date:
            stmt = stmt.where(SocialMediaPost.created_at >= start_date)
        if end_date:
            stmt = stmt.where(SocialMediaPost.created_at <= end_date)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt)

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


# =====================================================
# Sentiment Aggregate Endpoint (PHASE 4.1 — ENDPOINT 3)
# =====================================================
@router.get("/sentiment/aggregate")
async def get_sentiment_aggregate(
    period: str = Query(..., pattern="^(minute|hour|day)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source: Optional[str] = None,
):
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(hours=24)

    bucket = func.date_trunc(period, SocialMediaPost.created_at)

    async with async_session_maker() as session:
        stmt = (
            select(
                bucket.label("timestamp"),
                func.count().label("total"),
                func.sum(case((SentimentAnalysis.sentiment_label == "positive", 1), else_=0)).label("positive"),
                func.sum(case((SentimentAnalysis.sentiment_label == "negative", 1), else_=0)).label("negative"),
                func.sum(case((SentimentAnalysis.sentiment_label == "neutral", 1), else_=0)).label("neutral"),
                func.avg(SentimentAnalysis.confidence_score).label("avg_confidence"),
            )
            .join(SentimentAnalysis, SocialMediaPost.post_id == SentimentAnalysis.post_id)
            .where(
                SocialMediaPost.created_at >= start_date,
                SocialMediaPost.created_at <= end_date
            )
            .group_by("timestamp")
            .order_by("timestamp")
        )

        if source:
            stmt = stmt.where(SocialMediaPost.source == source)

        rows = (await session.execute(stmt)).all()

    data = []
    summary = {
        "total_posts": 0,
        "positive_total": 0,
        "negative_total": 0,
        "neutral_total": 0,
    }

    for r in rows:
        total = r.total or 0
        data.append({
            "timestamp": r.timestamp.isoformat(),
            "positive_count": r.positive,
            "negative_count": r.negative,
            "neutral_count": r.neutral,
            "total_count": total,
            "positive_percentage": round((r.positive / total) * 100, 2) if total else 0,
            "negative_percentage": round((r.negative / total) * 100, 2) if total else 0,
            "neutral_percentage": round((r.neutral / total) * 100, 2) if total else 0,
            "average_confidence": round(r.avg_confidence or 0, 4)
        })

        summary["total_posts"] += total
        summary["positive_total"] += r.positive
        summary["negative_total"] += r.negative
        summary["neutral_total"] += r.neutral

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": data,
        "summary": summary
    }
