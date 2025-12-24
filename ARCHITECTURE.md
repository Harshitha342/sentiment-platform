System Architecture – Real-Time Sentiment Analysis Platform
1. Overview

This system is a real-time sentiment analysis platform that ingests social media–like posts, analyzes sentiment and emotion using NLP models, stores results in a database, and serves insights through REST APIs, WebSockets, and a live dashboard.

The architecture is event-driven, containerized, and designed for scalability and real-time updates.

2. System Diagram
┌────────────┐
│  Ingester  │
│ (Generator)│
└─────┬──────┘
      │ Redis Stream
      ▼
┌────────────┐
│   Redis    │
│  Streams   │◄─────────────┐
└─────┬──────┘              │
      │ Consumer Group      │ Pub/Sub
      ▼                     │
┌────────────┐              │
│   Worker   │──────────────┘
│ (Analyzer) │
└─────┬──────┘
      │
      ▼
┌────────────┐
│ PostgreSQL │
│ (Storage)  │
└─────┬──────┘
      │
      ▼
┌────────────┐       WebSocket
│  Backend   │◄─────────────────┐
│ (FastAPI)  │                  │
└─────┬──────┘                  │
      │ REST API                │
      ▼                         │
┌────────────┐                  │
│  Frontend  │──────────────────┘
│ (Dashboard)│
└────────────┘

3. Component Descriptions
3.1 Ingester Service

Simulates incoming social media posts

Publishes posts to Redis Streams

Configurable ingestion rate

Ensures continuous data flow

3.2 Redis

Acts as:

Stream broker for ingestion → processing

Cache for aggregate metrics

Pub/Sub source for WebSocket updates

Enables decoupling between services

3.3 Worker Service

Consumes posts from Redis Stream

Performs:

Sentiment analysis

Emotion detection

Uses HuggingFace transformer models

Stores results in PostgreSQL

3.4 PostgreSQL

Persistent storage for:

Raw posts

Sentiment analysis results

Alerts

Supports aggregation and historical queries

3.5 Backend API (FastAPI)

Exposes REST endpoints:

Health check

Posts retrieval

Sentiment aggregation

Distribution stats

Provides WebSocket endpoint for real-time updates

Handles alert monitoring logic

3.6 Frontend Dashboard

Built with React + Recharts

Displays:

Live sentiment distribution

Time-series sentiment trends

Recent posts feed

Updates via REST + WebSocket

4. Data Flow

Post Generation

Ingester creates synthetic social media posts

Message Streaming

Posts published to Redis Stream

Processing

Worker consumes stream messages

Applies sentiment & emotion models

Persistence

Results saved to PostgreSQL

Serving

Backend API queries DB

Aggregates and caches results in Redis

Real-Time Updates

WebSocket pushes new posts & metrics to frontend

5. Technology Justification
Technology	Reason
FastAPI	Async support, high performance, automatic docs
Redis	Fast streaming, caching, pub/sub
PostgreSQL	Reliable relational storage & aggregation
Docker	Consistent, portable deployment
Transformers	State-of-the-art NLP models
React	Component-based, real-time UI
Recharts	Simple, responsive charting
6. Database Schema
social_media_posts
Column	Type
id	UUID
post_id	VARCHAR
source	VARCHAR
content	TEXT
author	VARCHAR
created_at	TIMESTAMP
sentiment_analysis
Column	Type
id	UUID
post_id	VARCHAR
sentiment_label	VARCHAR
confidence_score	FLOAT
emotion	VARCHAR
model_name	VARCHAR
analyzed_at	TIMESTAMP
sentiment_alerts
Column	Type
id	UUID
alert_type	VARCHAR
actual_ratio	FLOAT
threshold	FLOAT
created_at	TIMESTAMP
7. API Design

REST endpoints follow /api/* convention

JSON responses with clear structure

WebSocket endpoint:

/ws/sentiment

Push-based real-time updates

8. Scalability Considerations

Redis Streams allow horizontal worker scaling

Stateless backend supports multiple replicas

Database can be scaled using read replicas

Caching reduces DB load

9. Security Considerations

Environment variables for secrets

No credentials hardcoded

CORS configuration for frontend

Can add:

Rate limiting

Authentication (JWT)

HTTPS in production