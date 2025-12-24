from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio

router = APIRouter()

@router.websocket("/ws/sentiment")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    #  Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to sentiment stream",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    try:
        # KEEP THE CONNECTION ALIVE
        while True:
            await asyncio.sleep(30)

            # Example metrics update (temporary dummy)
            await websocket.send_json({
                "type": "metrics_update",
                "data": {
                    "last_minute": {
                        "positive": 3,
                        "negative": 1,
                        "neutral": 2,
                        "total": 6
                    },
                    "last_hour": {
                        "positive": 30,
                        "negative": 12,
                        "neutral": 18,
                        "total": 60
                    },
                    "last_24_hours": {
                        "positive": 300,
                        "negative": 120,
                        "neutral": 180,
                        "total": 600
                    }
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
