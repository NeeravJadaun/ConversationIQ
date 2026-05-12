import type { FailureCluster } from "@/types";
import { Card } from "@/components/ui/Card";

export function ClusterList({ clusters }: { clusters: FailureCluster[] }) {
  return (
    <div className="space-y-4">
      {clusters.map((cluster) => (
        <Card key={cluster.id}>
          <div className="flex items-center justify-between gap-4">
            <h3 className="font-semibold">{cluster.op_id} failure cluster</h3>
            <span className="text-sm text-muted">{cluster.size} conversations</span>
          </div>
          <p className="mt-3 text-sm text-gray-300">{cluster.gap_description}</p>
        </Card>
      ))}
    </div>
  );
}
