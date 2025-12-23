import os
import asyncio
from typing import List

from transformers import pipeline
from transformers.pipelines import Pipeline


class SentimentAnalyzer:
    """
    Unified interface for sentiment analysis using multiple model backends
    """

    _sentiment_pipeline: Pipeline = None
    _emotion_pipeline: Pipeline = None

    def __init__(self, model_type: str = "local", model_name: str = None):
        self.model_type = model_type

        if model_type == "local":
            self.sentiment_model_name = model_name or os.getenv(
                "HUGGINGFACE_MODEL",
                "distilbert-base-uncased-finetuned-sst-2-english"
            )

            self.emotion_model_name = os.getenv(
                "EMOTION_MODEL",
                "j-hartmann/emotion-english-distilroberta-base"
            )

            # Cache models (important for performance)
            if not SentimentAnalyzer._sentiment_pipeline:
                SentimentAnalyzer._sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.sentiment_model_name
                )

            if not SentimentAnalyzer._emotion_pipeline:
                SentimentAnalyzer._emotion_pipeline = pipeline(
                    "text-classification",
                    model=self.emotion_model_name,
                    return_all_scores=True
                )

        elif model_type == "external":
            # Placeholder for Phase 4+
            self.api_key = os.getenv("EXTERNAL_LLM_API_KEY")
            self.external_model = os.getenv("EXTERNAL_LLM_MODEL")
        else:
            raise ValueError("model_type must be 'local' or 'external'")

    async def analyze_sentiment(self, text: str) -> dict:
        if text is None:
            raise ValueError("Text cannot be None")

        if not text.strip():
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "model_name": self.sentiment_model_name
            }

        if self.model_type == "local":
            result = await asyncio.to_thread(
                SentimentAnalyzer._sentiment_pipeline,
                text[:512]
            )

            label = result[0]["label"].lower()
            score = float(result[0]["score"])

            if label not in ["positive", "negative"]:
                label = "neutral"

            return {
                "sentiment_label": label,
                "confidence_score": round(score, 4),
                "model_name": self.sentiment_model_name
            }

        raise NotImplementedError("External sentiment not implemented yet")

    async def analyze_emotion(self, text: str) -> dict:
        if text is None:
            raise ValueError("Text cannot be None")

        if len(text.strip()) < 10:
            return {
                "emotion": "neutral",
                "confidence_score": 0.0,
                "model_name": self.emotion_model_name
            }

        scores = await asyncio.to_thread(
            SentimentAnalyzer._emotion_pipeline,
            text[:512]
        )

        emotions = scores[0]
        top_emotion = max(emotions, key=lambda x: x["score"])

        emotion = top_emotion["label"].lower()
        confidence = float(top_emotion["score"])

        return {
            "emotion": emotion,
            "confidence_score": round(confidence, 4),
            "model_name": self.emotion_model_name
        }

    async def batch_analyze(self, texts: List[str]) -> List[dict]:
        if not texts:
            return []

        tasks = [self.analyze_sentiment(text) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = []
        for result in results:
            if isinstance(result, Exception):
                output.append({
                    "sentiment_label": "neutral",
                    "confidence_score": 0.0,
                    "model_name": self.sentiment_model_name
                })
            else:
                output.append(result)

        return output
