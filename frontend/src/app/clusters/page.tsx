"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ClusterList } from "@/components/clusters/ClusterList";
import { getClusters, recomputeClusters } from "@/lib/api";
import type { FailureCluster } from "@/types";

export default function ClustersPage() {
  const [clusters, setClusters] = useState<FailureCluster[]>([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => { getClusters().then(setClusters).catch(() => setClusters([])); }, []);

  async function rerun() {
    setLoading(true);
    try {
      setClusters(await recomputeClusters());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-gray-50">
      <div className="mx-auto max-w-7xl space-y-6">
        <Link href="/" className="text-sm text-accent">Dashboard</Link>
        <header className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Failure Pattern Analysis</h1>
            <p className="mt-1 text-sm text-muted">Conversations are grouped by semantic failure pattern. Each cluster represents an operating procedure gap.</p>
          </div>
          <button className="rounded bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500" onClick={rerun} disabled={loading}>
            {loading ? "Re-running..." : "Re-run Clustering"}
          </button>
        </header>
        <ClusterList clusters={clusters} />
      </div>
    </main>
  );
}
