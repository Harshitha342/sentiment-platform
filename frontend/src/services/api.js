const BASE_URL = "http://localhost:8000";

export async function fetchPosts(limit = 10, offset = 0, filters = {}) {
  const params = new URLSearchParams({ limit, offset, ...filters });
  const res = await fetch(`${BASE_URL}/api/posts?${params}`);
  return res.json();
}

export async function fetchDistribution(hours = 24) {
  const res = await fetch(
    `${BASE_URL}/api/sentiment/distribution?hours=${hours}`
  );
  return res.json();
}

export async function fetchAggregateData(period) {
  const res = await fetch(
    `${BASE_URL}/api/sentiment/aggregate?period=${period}`
  );
  return res.json();
}

export function connectWebSocket(onMessage, onOpen, onClose) {
  const ws = new WebSocket("ws://localhost:8000/ws/sentiment");

  ws.onopen = onOpen;
  ws.onmessage = (event) => onMessage(JSON.parse(event.data));
  ws.onerror = console.error;
  ws.onclose = onClose;

  return ws;
}
