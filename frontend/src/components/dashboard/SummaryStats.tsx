import type { OperatingProcedure, Recommendation } from "@/types";
import { Card } from "@/components/ui/Card";

export function SummaryStats({ procedures, recommendations }: { procedures: OperatingProcedure[]; recommendations: Recommendation[] }) {
  const avg = procedures.length ? procedures.reduce((sum, op) => sum + op.health_score, 0) / procedures.length : 0;
  const totalConversations = procedures.reduce((sum, op) => sum + op.conversation_count, 0);
  const stats = [
    ["Total OPs Monitored", procedures.length],
    ["Conversations Today", totalConversations],
    ["Avg Health Score", avg.toFixed(1)],
    ["Open Recommendations", recommendations.filter((rec) => rec.status === "open").length],
  ];
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
      {stats.map(([label, value]) => (
        <Card key={label.toString()}>
          <p className="text-3xl font-bold text-accent">{value}</p>
          <p className="mt-1 text-sm text-muted">{label}</p>
        </Card>
      ))}
    </div>
  );
}
