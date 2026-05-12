"use client";

import { useEffect, useState } from "react";
import { OPHealthGrid } from "@/components/dashboard/OPHealthGrid";
import { SummaryStats } from "@/components/dashboard/SummaryStats";
import { LiveFeed } from "@/components/dashboard/LiveFeed";
import { ClusterList } from "@/components/clusters/ClusterList";
import { RecommendationPanel } from "@/components/recommendations/RecommendationPanel";
import { getClusters, getProcedures, getRecommendations } from "@/lib/api";
import type { FailureCluster, OperatingProcedure, Recommendation } from "@/types";

export default function DashboardPage() {
  const [procedures, setProcedures] = useState<OperatingProcedure[]>([]);
  const [clusters, setClusters] = useState<FailureCluster[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    getProcedures().then(setProcedures).catch(() => setProcedures([]));
    getClusters().then(setClusters).catch(() => setClusters([]));
    getRecommendations().then(setRecommendations).catch(() => setRecommendations([]));
  }, []);

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-gray-50">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">ConversationIQ</h1>
            <p className="mt-1 text-sm text-muted">Real-time OP health monitoring for banking AI agents</p>
          </div>
          <a href="/clusters" className="rounded border border-white/10 px-3 py-2 text-sm text-gray-200 hover:border-accent hover:text-accent">
            Failure Clusters
          </a>
        </header>
        <SummaryStats procedures={procedures} recommendations={recommendations} />
        <section>
          <h2 className="mb-3 text-xl font-semibold">Operating Procedure Health</h2>
          <OPHealthGrid procedures={procedures} />
        </section>
        <LiveFeed />
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div>
            <h2 className="mb-3 text-xl font-semibold">Failure Clusters</h2>
            <ClusterList clusters={clusters.slice(0, 3)} />
          </div>
          <div>
            <h2 className="mb-3 text-xl font-semibold">Top Recommendations</h2>
            <RecommendationPanel recommendations={recommendations.slice(0, 3)} />
          </div>
        </section>
      </div>
    </main>
  );
}
