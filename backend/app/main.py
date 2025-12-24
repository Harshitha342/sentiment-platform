from fastapi import FastAPI

from app.api.routes import router as api_router
from app.models.database import Base, engine
from app.api.websocket import router as websocket_router

# Create FastAPI app FIRST
app = FastAPI(title="Sentiment Analysis Platform")

# Include API routes
app.include_router(api_router)
app.include_router(websocket_router)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
