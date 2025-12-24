const API_BASE = "http://localhost:8000/api";

/* =========================
   POSTS
========================= */
export async function fetchPosts(limit = 5, offset = 0, filters = {}) {
  const params = new URLSearchParams({
    limit,
    offset,
    ...filters,
  });

  const res = await fetch(`${API_BASE}/posts?${params}`);
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

/* =========================
   DISTRIBUTION
========================= */
export async function fetchDistribution(hours = 24, source = null) {
  const params = new URLSearchParams({ hours });
  if (source) params.append("source", source);

  const res = await fetch(`${API_BASE}/sentiment/distribution?${params}`);
  if (!res.ok) throw new Error("Failed to fetch distribution");
  return res.json();
}

/* =========================
   AGGREGATE (TREND)
========================= */
export async function fetchAggregate(period = "hour", startDate, endDate) {
  const params = new URLSearchParams({ period });

  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);

  const res = await fetch(`${API_BASE}/sentiment/aggregate?${params}`);
  if (!res.ok) throw new Error("Failed to fetch aggregate");
  return res.json();
}

/* =========================
   WEBSOCKET
========================= */
export function connectWebSocket(onMessage, onError, onClose) {
  const ws = new WebSocket("ws://localhost:8000/ws/sentiment");

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = onError;
  ws.onclose = onClose;

  return ws;
}
