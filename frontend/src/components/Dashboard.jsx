import { useEffect, useState } from "react";
import DistributionChart from "./DistributionChart";
import SentimentChart from "./SentimentChart";
import RecentPosts from "./RecentPosts";
import {
  fetchDistribution,
  fetchAggregateData,
  fetchPosts,
  connectWebSocket,
} from "../services/api";

export default function Dashboard() {
  const [distributionData, setDistributionData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [recentPosts, setRecentPosts] = useState([]);
  const [metrics, setMetrics] = useState({
    total: 0,
    positive: 0,
    negative: 0,
    neutral: 0,
  });
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    async function loadInitialData() {
      const dist = await fetchDistribution(24);
      const trend = await fetchAggregateData("hour");
      const posts = await fetchPosts(5, 0);

      setDistributionData(dist.distribution);
      setTrendData(trend.data);
      setRecentPosts(posts.posts);
      setMetrics({
        total: dist.total,
        positive: dist.distribution.positive,
        negative: dist.distribution.negative,
        neutral: dist.distribution.neutral,
      });
      setLastUpdate(new Date());
    }

    loadInitialData();

    const ws = connectWebSocket(
      (msg) => {
        setLastUpdate(new Date());
        if (msg.type === "sentiment_update") {
          setDistributionData(msg.distribution);
        }
        if (msg.type === "new_post") {
          setRecentPosts((prev) => [msg.post, ...prev.slice(0, 4)]);
        }
      },
      () => setConnectionStatus("connected"),
      () => setConnectionStatus("disconnected")
    );

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          Real-Time Sentiment Analysis Dashboard
        </h1>
        <div className="text-sm">
          <span className="mr-4">
            Status:{" "}
            <span
              className={
                connectionStatus === "connected"
                  ? "text-green-400"
                  : "text-red-400"
              }
            >
              ● {connectionStatus}
            </span>
          </span>
          <span>
            Last Update:{" "}
            {lastUpdate ? lastUpdate.toLocaleTimeString() : "--"}
          </span>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <DistributionChart data={distributionData} />
        <RecentPosts posts={recentPosts} />
      </div>

      {/* Trend */}
      <SentimentChart data={trendData} />

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(metrics).map(([key, value]) => (
          <div
            key={key}
            className="bg-gray-800 rounded-lg p-4 text-center"
          >
            <p className="text-sm uppercase text-gray-400">{key}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
