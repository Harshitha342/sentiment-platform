import os
import asyncio
from typing import List, Dict

from transformers import pipeline
from transformers.pipelines.base import PipelineException


class SentimentAnalyzer:
    """
    Unified interface for sentiment and emotion analysis
    using Hugging Face transformer models (local).
    """

    def __init__(self, model_type: str = "local", model_name: str = None):
        """
        Initialize sentiment analyzer

        Args:
            model_type: 'local' or 'external' (external stub for later)
            model_name: optional override for sentiment model
        """
        self.model_type = model_type

        if model_type != "local":
            raise NotImplementedError("External LLM support will be added later")

        # Load model names from env or defaults
        self.sentiment_model_name = (
            model_name
            or os.getenv(
                "HUGGINGFACE_MODEL",
                "distilbert-base-uncased-finetuned-sst-2-english",
            )
        )

        self.emotion_model_name = os.getenv(
            "EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base"
        )

        # Load pipelines (cached automatically by HF)
        self.sentiment_pipeline = pipeline(
            "text-classification",
            model=self.sentiment_model_name,
            return_all_scores=True,
        )

        self.emotion_pipeline = pipeline(
            "text-classification",
            model=self.emotion_model_name,
            return_all_scores=True,
        )

    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of input text
        """
        if text is None or not text.strip():
            raise ValueError("Text cannot be empty")

        if len(text.strip()) < 10:
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.5,
                "model_name": self.sentiment_model_name,
            }

        try:
            results = self.sentiment_pipeline(text)[0]
        except PipelineException:
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "model_name": self.sentiment_model_name,
            }

        # Find strongest label
        best = max(results, key=lambda x: x["score"])
        label = best["label"].lower()

        if label not in {"positive", "negative"}:
            label = "neutral"

        return {
            "sentiment_label": label,
            "confidence_score": round(float(best["score"]), 4),
            "model_name": self.sentiment_model_name,
        }

    async def analyze_emotion(self, text: str) -> Dict:
        """
        Detect primary emotion in text
        """
        if text is None or not text.strip():
            raise ValueError("Text cannot be empty")

        if len(text.strip()) < 10:
            return {
                "emotion": "neutral",
                "confidence_score": 0.5,
                "model_name": self.emotion_model_name,
            }

        results = self.emotion_pipeline(text)[0]
        best = max(results, key=lambda x: x["score"])

        emotion = best["label"].lower()

        allowed_emotions = {
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "neutral",
        }

        if emotion not in allowed_emotions:
            emotion = "neutral"

        return {
            "emotion": emotion,
            "confidence_score": round(float(best["score"]), 4),
            "model_name": self.emotion_model_name,
        }

    async def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """
        Analyze multiple texts efficiently
        """
        if not texts:
            return []

        tasks = []
        for text in texts:
            if not text or not text.strip():
                tasks.append(
                    asyncio.sleep(
                        0,
                        result={
                            "sentiment_label": "neutral",
                            "confidence_score": 0.0,
                            "model_name": self.sentiment_model_name,
                        },
                    )
                )
            else:
                tasks.append(self.analyze_sentiment(text))

        return await asyncio.gather(*tasks)
