# Real-Time Sentiment Analysis Platform

A full-stack, real-time sentiment analysis platform that ingests social media–style posts, performs sentiment and emotion analysis using NLP models, and displays live analytics on a web dashboard. The system supports real-time updates, historical trend analysis, and alerting based on sentiment patterns.

---

## Features

- Real-time sentiment and emotion analysis
- Live dashboard with charts and metrics
- Redis Streams–based ingestion pipeline
- WebSocket updates for instant UI refresh
- REST API for analytics and post retrieval
- Dockerized microservice architecture

---

## Architecture Overview

The system is composed of multiple containerized services for ingestion, processing, storage, API serving, and visualization.

📄 See detailed architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Prerequisites

- Docker **20.10+**
- Docker Compose **2.0+**
- Minimum **4 GB RAM**
- Free ports: **3000**, **8000**
- API keys:
  - Hugging Face (models)
  - Groq (LLM provider)

---

## Quick Start

```bash
# Clone repository
git clone <repo-url>
cd sentiment-platform

# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env

# Start all services
docker-compose up -d

# Wait for services to be healthy (30–60 seconds)
docker-compose ps

# Access dashboard
# Open http://localhost:3000 in browser

# Stop services
docker-compose down

Configuration

Environment variables (defined in .env):

DATABASE_URL – PostgreSQL connection string

REDIS_HOST, REDIS_PORT – Redis configuration

HUGGINGFACE_MODEL – Sentiment model

EMOTION_MODEL – Emotion classifier

EXTERNAL_LLM_API_KEY – Groq API key

ALERT_NEGATIVE_RATIO_THRESHOLD – Alert trigger ratio

API Documentation

Available endpoints:

GET /api/health

GET /api/posts

GET /api/sentiment/distribution

GET /api/sentiment/aggregate

WS /ws/sentiment

Interactive docs available at:
http://localhost:8000/docs

Testing Instructions:
cd backend
pytest --cov=app --cov-report=term
Troubleshooting

CORS errors: Ensure backend CORS middleware allows localhost:3000

No data: Ensure ingester and worker services are running

Ports in use: Stop conflicting services using ports 3000 or 8000

Project Structure
sentiment-platform/
├── backend/
│   ├── app/
│   ├── tests/
├── frontend/
│   ├── src/
├── docker-compose.yml
├── README.md
├── ARCHITECTURE.md

License

MIT License

---

# 📄 FILE 2 — `ARCHITECTURE.md` (COPY–PASTE)

```md
# System Architecture

## System Diagram

[Browser]
   ↓ WebSocket / HTTP
[Frontend Dashboard]
   ↓ REST / WS
[Backend API]
   ↓ Async SQLAlchemy
[PostgreSQL Database]

[Ingester] → [Redis Streams] → [Worker] → [PostgreSQL]

---

## Component Descriptions

### Frontend Dashboard
- React + Vite
- Displays charts, metrics, and live feed
- Connects via REST and WebSocket

### Backend API
- FastAPI application
- Serves analytics endpoints
- Manages WebSocket connections

### Ingester
- Simulates incoming social posts
- Publishes messages to Redis Streams

### Worker
- Consumes Redis Stream messages
- Performs sentiment and emotion analysis
- Writes results to PostgreSQL

### Redis
- Message streaming (Redis Streams)
- Real-time buffering

### PostgreSQL
- Persistent storage
- Stores posts and sentiment results

---

## Data Flow

1. Ingester publishes posts to Redis Stream
2. Worker consumes messages
3. NLP models analyze sentiment and emotion
4. Results stored in PostgreSQL
5. Backend API queries database
6. Frontend displays data via REST/WebSocket

---

## Technology Justification

- **FastAPI**: Async performance, WebSocket support
- **Redis Streams**: Reliable event ingestion
- **PostgreSQL**: Relational consistency
- **Transformers**: State-of-the-art NLP
- **Docker**: Environment consistency

---

## Database Schema

### social_media_posts
- id
- post_id
- content
- source
- author
- created_at

### sentiment_analysis
- id
- post_id (FK)
- sentiment_label
- confidence_score
- emotion
- analyzed_at

---

## API Design

- RESTful endpoints
- JSON responses
- Pagination and filters supported

---

## Scalability Considerations

- Multiple workers can consume Redis Streams
- API horizontally scalable
- Database read replicas possible

---

## Security Considerations

- API keys stored in environment variables
- Rate limiting can be added
- Authentication extensible via JWT

## Demo Note
This project is designed for local Docker-based execution.  
A live video demo could not be recorded at submission time due to a temporary screen recording issue.  
The system is fully functional and can be demonstrated live if required.
