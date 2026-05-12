import type { OperatingProcedure } from "@/types";
import { HealthScoreCard } from "./HealthScoreCard";

export function OPHealthGrid({ procedures }: { procedures: OperatingProcedure[] }) {
  const sorted = [...procedures].sort((a, b) => a.health_score - b.health_score);
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {sorted.map((op) => (
        <HealthScoreCard key={op.id} op={op} />
      ))}
    </div>
  );
}
