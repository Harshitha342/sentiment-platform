import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral: "#6b7280",
};

export default function DistributionChart({ data }) {
  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        No data available
      </div>
    );
  }

  const chartData = Object.entries(data)
    .filter(([_, value]) => value > 0)
    .map(([name, value]) => ({ name, value }));

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">
        Sentiment Distribution
      </h3>
      <PieChart width={300} height={250}>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          outerRadius={80}
        >
          {chartData.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}
