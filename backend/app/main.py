from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.websocket import router as ws_router

app = FastAPI(title="Sentiment Analysis Platform")

# 🔥 ABSOLUTE CORS OVERRIDE (TEMPORARY, FOR DEBUGGING)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)
