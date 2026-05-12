"use client";

import { Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function TrendLineChart({ data }: { data: { date: string; health_score: number }[] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 11 }} minTickGap={24} />
          <YAxis domain={[0, 100]} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(255,255,255,.1)" }} />
          <ReferenceLine y={80} stroke="#10B981" strokeDasharray="3 3" />
          <ReferenceLine y={60} stroke="#EF4444" strokeDasharray="3 3" />
          <Line type="monotone" dataKey="health_score" stroke="#3B82F6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
