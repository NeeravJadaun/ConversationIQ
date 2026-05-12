import Link from "next/link";
import type { OperatingProcedure } from "@/types";
import { scoreTone } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { StatusDot } from "@/components/ui/StatusDot";

export function HealthScoreCard({ op, changed = false }: { op: OperatingProcedure; changed?: boolean }) {
  const tone = scoreTone(op.health_score);
  return (
    <Card className="flex h-full flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">{op.id}</p>
          <h3 className="mt-1 text-base font-semibold text-gray-50">{op.name}</h3>
        </div>
        <StatusDot active={changed} />
      </div>
      <div className={`flex h-20 w-20 items-center justify-center rounded-full border-4 ${tone}`}>
        <span className="text-2xl font-bold">{Math.round(op.health_score)}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="text-muted">Resolution</p>
          <p className="font-semibold">{Math.round(op.resolution_rate * 100)}%</p>
        </div>
        <div>
          <p className="text-muted">Escalation</p>
          <p className="font-semibold">{Math.round(op.escalation_rate * 100)}%</p>
        </div>
      </div>
      <Link className="mt-auto text-sm font-semibold text-accent hover:text-blue-300" href={`/procedures/${op.id}`}>
        View Details →
      </Link>
    </Card>
  );
}
