import logging
logging.basicConfig(level=logging.INFO)
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, text
from app.models.database import async_session_maker
from app.models.sentiment_analysis import SentimentAnalysis
from app.models.social_media_post import SocialMediaPost


class AlertService:
    def __init__(self):
        self.negative_ratio_threshold = float(
            os.getenv("ALERT_NEGATIVE_RATIO_THRESHOLD", 2.0)
        )
        self.window_minutes = int(
            os.getenv("ALERT_WINDOW_MINUTES", 5)
        )
        self.min_posts = int(
            os.getenv("ALERT_MIN_POSTS", 10)
        )

    async def check_thresholds(self) -> Optional[dict]:
        window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)

        async with async_session_maker() as session:
            stmt = (
                select(
                    SentimentAnalysis.sentiment_label,
                    func.count().label("count")
                )
                .join(
                    SocialMediaPost,
                    SocialMediaPost.post_id == SentimentAnalysis.post_id
                )
                .where(SentimentAnalysis.analyzed_at >= window_start)
                .group_by(SentimentAnalysis.sentiment_label)
            )

            result = await session.execute(stmt)
            rows = result.all()

        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for label, count in rows:
            counts[label] = count

        total = sum(counts.values())

        if total < self.min_posts or counts["positive"] == 0:
            return None

        ratio = counts["negative"] / counts["positive"]

        if ratio <= self.negative_ratio_threshold:
            return None

        return {
            "alert_triggered": True,
            "alert_type": "high_negative_ratio",
            "threshold": self.negative_ratio_threshold,
            "actual_ratio": round(ratio, 2),
            "window_minutes": self.window_minutes,
            "metrics": {
                **counts,
                "total_count": total
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def save_alert(self, alert_data: dict) -> int:
        async with async_session_maker() as session:
            result = await session.execute(
                text("""
                    INSERT INTO sentiment_alerts (alert_type, payload, created_at)
                    VALUES (:type, :payload, NOW())
                    RETURNING id
                """),
                {
                    "type": alert_data["alert_type"],
                    "payload": alert_data,
                }
            )
            await session.commit()
            return result.scalar()

async def run_monitoring_loop(self, check_interval_seconds: int = 60):
    while True:
        logging.info("AlertService running check...")
        alert = await self.check_thresholds()
        if alert:
            logging.warning(f"ALERT: {alert}")
            await self.save_alert(alert)
        await asyncio.sleep(check_interval_seconds)
