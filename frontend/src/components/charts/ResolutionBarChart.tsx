"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function ResolutionBarChart({ data }: { data: any[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data.slice(-4)}>
          <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
          <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(255,255,255,.1)" }} />
          <Bar dataKey="resolved" stackId="a" fill="#10B981" />
          <Bar dataKey="escalated" stackId="a" fill="#F59E0B" />
          <Bar dataKey="looped" stackId="a" fill="#F97316" />
          <Bar dataKey="failed" stackId="a" fill="#EF4444" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
