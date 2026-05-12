"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { TrendLineChart } from "@/components/charts/TrendLineChart";
import { ResolutionBarChart } from "@/components/charts/ResolutionBarChart";
import { ClusterDetail } from "@/components/clusters/ClusterDetail";
import { RecommendationPanel } from "@/components/recommendations/RecommendationPanel";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { generateRecommendation, getProcedure, getTrend } from "@/lib/api";
import { scoreTone } from "@/lib/utils";
import type { ProcedureDetail } from "@/types";

export default function ProcedureDetailPage({ params }: { params: { id: string } }) {
  const [detail, setDetail] = useState<ProcedureDetail | null>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    getProcedure(params.id).then(setDetail);
    getTrend(params.id).then(setTrend);
  }, [params.id]);

  if (!detail) return <main className="min-h-screen bg-bg p-6 text-gray-50">Loading...</main>;
  const conversations = detail.recent_conversations.filter((row) => filter === "all" || row.resolution_status === filter);

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-gray-50">
      <div className="mx-auto max-w-7xl space-y-6">
        <Link href="/" className="text-sm text-accent">Dashboard &gt; {detail.id}: {detail.name}</Link>
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">{detail.name}</h1>
            <p className="text-muted">{detail.id} · last updated {new Date(detail.last_computed_at).toLocaleString()}</p>
          </div>
          <div className={`flex h-24 w-24 items-center justify-center rounded-full border-4 ${scoreTone(detail.health_score)}`}>
            <span className="text-3xl font-bold">{Math.round(detail.health_score)}</span>
          </div>
        </header>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            ["Resolution Rate", `${Math.round(detail.resolution_rate * 100)}%`],
            ["Escalation Rate", `${Math.round(detail.escalation_rate * 100)}%`],
            ["Loop Rate", `${Math.round(detail.loop_rate * 100)}%`],
            ["Avg Turns", detail.avg_turn_count.toFixed(1)],
          ].map(([label, value]) => (
            <Card key={label}><p className="text-2xl font-bold text-accent">{value}</p><p className="text-sm text-muted">{label}</p></Card>
          ))}
        </div>
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card><h2 className="mb-3 text-lg font-semibold">Health Score Trend</h2><TrendLineChart data={trend} /></Card>
          <Card><h2 className="mb-3 text-lg font-semibold">Resolution Breakdown</h2><ResolutionBarChart data={trend} /></Card>
        </section>
        <section>
          <h2 className="mb-3 text-xl font-semibold">Failure Clusters for this OP</h2>
          <div className="space-y-3">
            {detail.failure_clusters.map((cluster) => (
              <ClusterDetail key={cluster.id} cluster={cluster} onGenerate={() => generateRecommendation(detail.id, cluster.id).then(() => getProcedure(detail.id).then(setDetail))} />
            ))}
          </div>
        </section>
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Conversations</h2>
            <select className="rounded border border-white/10 bg-surface px-2 py-1 text-sm" value={filter} onChange={(event) => setFilter(event.target.value)}>
              {["all", "resolved", "failed", "escalated", "looped"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
          <Card>
            <div className="space-y-2">
              {conversations.map((row) => (
                <div key={row.id} className="rounded border border-white/5 p-3">
                  <button className="grid w-full grid-cols-6 gap-3 text-left text-sm" onClick={() => setExpanded(expanded === row.id ? null : row.id)}>
                    <span className="col-span-2">{new Date(row.created_at).toLocaleString()}</span>
                    <span className="col-span-2 truncate">{row.intent_detected}</span>
                    <Badge tone={row.resolution_status}>{row.resolution_status}</Badge>
                    <span className="text-right text-muted">{row.turn_count} turns</span>
                  </button>
                  {expanded === row.id ? (
                    <div className="mt-3 space-y-2 border-t border-white/10 pt-3 text-sm">
                      {row.turns.map((turn, index) => <p key={index}><span className="font-semibold text-accent">{turn.role}:</span> {turn.text}</p>)}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </Card>
        </section>
        <section>
          <h2 className="mb-3 text-xl font-semibold">Recommendations</h2>
          <RecommendationPanel recommendations={detail.recommendations} />
        </section>
      </div>
    </main>
  );
}
