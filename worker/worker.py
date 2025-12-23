import os
import json
import asyncio
import redis.asyncio as redis
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.services.sentiment_analyzer import SentimentAnalyzer
from app.models.database import Base
from processor import save_post_and_analysis

STREAM = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
GROUP = os.getenv("REDIS_CONSUMER_GROUP", "sentiment_workers")
CONSUMER = os.getenv("HOSTNAME", "worker-1")

DATABASE_URL = os.getenv("DATABASE_URL")


class SentimentWorker:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )

        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)

        self.analyzer = SentimentAnalyzer()

    async def ensure_group(self):
        try:
            await self.redis.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
        except redis.ResponseError:
            pass  # group already exists

    async def process_message(self, message_id, data):
        db = self.Session()
        try:
            sentiment = await self.analyzer.analyze_sentiment(data["content"])
            emotion = await self.analyzer.analyze_emotion(data["content"])

            await save_post_and_analysis(db, data, sentiment, emotion)
            await self.redis.xack(STREAM, GROUP, message_id)
            print(f"Processed {message_id}")

        except Exception as e:
            db.rollback()
            print(f"Error processing {message_id}: {e}")
        finally:
            db.close()

    async def run(self):
        await self.ensure_group()
        print("Worker started")

        while True:
            messages = await self.redis.xreadgroup(
                GROUP,
                CONSUMER,
                streams={STREAM: ">"},
                count=10,
                block=5000,
            )

            for _, entries in messages:
                tasks = [
                    self.process_message(message_id, data)
                    for message_id, data in entries
                ]
                await asyncio.gather(*tasks)


if __name__ == "__main__":
    worker = SentimentWorker()
    asyncio.run(worker.run())
