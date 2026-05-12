import type { FailureCluster } from "@/types";
import { Card } from "@/components/ui/Card";

export function ClusterDetail({ cluster, onGenerate }: { cluster: FailureCluster; onGenerate?: () => void }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold">Cluster {cluster.id}</h3>
          <p className="text-sm text-muted">{cluster.size} conversations</p>
        </div>
        {onGenerate ? (
          <button className="rounded border border-accent px-3 py-2 text-sm text-accent hover:bg-accent hover:text-white" onClick={onGenerate}>
            Generate Fix Recommendation →
          </button>
        ) : null}
      </div>
      <p className="mt-3 text-sm text-gray-300">{cluster.gap_description}</p>
      <blockquote className="mt-3 border-l-2 border-white/20 pl-3 text-sm text-muted">{cluster.centroid_summary}</blockquote>
    </Card>
  );
}
