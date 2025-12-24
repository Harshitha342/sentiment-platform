from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Sentiment Analysis Platform",
    version="1.0.0"
)

#  THIS LINE IS CRITICAL
app.include_router(api_router)
