import time
import random
import asyncio
import os
from datetime import datetime
import redis.asyncio as redis


class DataIngester:
    def __init__(self, redis_client, stream_name: str, posts_per_minute: int = 60):
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.posts_per_minute = posts_per_minute

        # Templates
        self.positive_templates = [
            "I absolutely love {}!",
            "{} is amazing!",
            "{} exceeded my expectations!"
        ]
        self.negative_templates = [
            "Very disappointed with {}",
            "Terrible experience with {}",
            "I hate {}"
        ]
        self.neutral_templates = [
            "Just tried {}",
            "Using {} for the first time",
            "Received {} today"
        ]

        self.products = ["iPhone 16", "ChatGPT", "Netflix", "Amazon Prime"]

    def generate_post(self) -> dict:
        post_id = f"post_{int(time.time() * 1000)}"

        template = random.choice(
            self.positive_templates +
            self.negative_templates +
            self.neutral_templates
        )
        content = template.format(random.choice(self.products))

        return {
            "post_id": post_id,
            "source": random.choice(["reddit", "twitter", "linkedin"]),
            "content": content,
            "author": f"user_{random.randint(1000, 9999)}",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    async def publish_post(self, post_data: dict) -> bool:
        try:
            await self.redis_client.xadd(
                self.stream_name,
                {
                    "post_id": post_data["post_id"],
                    "source": post_data["source"],
                    "content": post_data["content"],
                    "author": post_data["author"],
                    "created_at": post_data["created_at"]
                }
            )
            print(f"Published post {post_data['post_id']}")
            return True
        except Exception as e:
            print(f"Failed to publish post: {e}")
            return False

    async def start(self, duration_seconds: int = None):
        interval = 60 / self.posts_per_minute
        start_time = time.time()

        try:
            while True:
                post = self.generate_post()
                await self.publish_post(post)

                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("Ingester stopped gracefully")


async def main():
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    ingester = DataIngester(
        redis_client=redis_client,
        stream_name=os.getenv("REDIS_STREAM_NAME", "social_posts_stream"),
        posts_per_minute=60
    )

    await ingester.start()


if __name__ == "__main__":
    asyncio.run(main())
