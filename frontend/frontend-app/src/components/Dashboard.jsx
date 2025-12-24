import { useEffect, useState } from "react";
import DistributionChart from "./DistributionChart";
import SentimentTrendChart from "./SentimentTrendChart";

const API_BASE = "http://localhost:8000/api";

export default function Dashboard() {
  const [distribution, setDistribution] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [recentPosts, setRecentPosts] = useState([]);
  const [metrics, setMetrics] = useState({
    total: 0,
    positive: 0,
    negative: 0,
    neutral: 0,
  });
  const [status, setStatus] = useState("connecting");
  const [lastUpdate, setLastUpdate] = useState("--");

  useEffect(() => {
    async function load() {
      try {
        // Health
        await fetch(`${API_BASE}/health`);

        // Distribution
        const distRes = await fetch(`${API_BASE}/sentiment/distribution`);
        const distJson = await distRes.json();

        console.log("distribution raw:", distJson);

        const dist = distJson.distribution || {
          positive: 0,
          negative: 0,
          neutral: 0,
        };

        setDistribution(dist);
        setMetrics({
          total: distJson.total || 0,
          positive: dist.positive,
          negative: dist.negative,
          neutral: dist.neutral,
        });

        // Trend
        const trendRes = await fetch(
          "http://localhost:8000/api/sentiment/aggregate?period=hour"
        );
        const trendJson = await trendRes.json();

        console.log("trend raw:", trendJson);
        if (Array.isArray(trendJson.data)) {
          setTrendData(trendJson.data);
        } else {
          setTrendData([]);
        }

        setTrendData(trendJson.data || []);

        // Posts
        const postsRes = await fetch(`${API_BASE}/posts?limit=5`);
        const postsJson = await postsRes.json();

        setRecentPosts(postsJson.posts || []);

        setStatus("connected");
        setLastUpdate(new Date().toLocaleTimeString());
      } catch (err) {
        console.error("API error:", err);
        setStatus("disconnected");
      }
    }

    load();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-2">
        Real-Time Sentiment Analysis Dashboard
      </h1>

      <div className="flex gap-6 text-sm text-gray-300 mb-6">
        <span>
          Status:{" "}
          <span
            className={
              status === "connected"
                ? "text-green-400"
                : "text-red-400"
            }
          >
            ● {status}
          </span>
        </span>
        <span>Last Update: {lastUpdate}</span>
      </div>

      {/* Distribution + Posts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {distribution ? (
          <DistributionChart data={distribution} />
        ) : (
          <div className="bg-gray-800 p-4 rounded-lg">
            Loading distribution…
          </div>
        )}

        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">Recent Posts</h2>
          {recentPosts.length === 0 ? (
            <p className="text-gray-400">No posts available</p>
          ) : (
            recentPosts.map((p) => (
              <div key={p.post_id} className="border-b border-gray-700 py-2">
                <p className="text-sm">{p.content}</p>
                <p className="text-xs text-gray-400">
                  {p.source} • {p.sentiment.label}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Trend */}
      {trendData.length > 0 ? (
        <SentimentTrendChart data={trendData} />
      ) : (
        <div className="bg-gray-800 p-4 rounded-lg mb-6">
          Loading trend…
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        {[
          ["Total", metrics.total],
          ["Positive", metrics.positive],
          ["Negative", metrics.negative],
          ["Neutral", metrics.neutral],
        ].map(([label, value]) => (
          <div
            key={label}
            className="bg-gray-800 p-4 rounded-lg text-center"
          >
            <p className="text-gray-400">{label}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
