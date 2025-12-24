from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_posts_endpoint():
    r = client.get("/api/posts?limit=1")
    assert r.status_code == 200
    assert "posts" in r.json()
