import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from app.models.database import Base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}
