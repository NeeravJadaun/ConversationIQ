"use client";

import type { Recommendation } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { updateRecommendation } from "@/lib/api";

export function RecommendationPanel({ recommendations }: { recommendations: Recommendation[] }) {
  return (
    <div className="space-y-3">
      {recommendations.map((rec) => (
        <Card key={rec.id}>
          <div className="mb-2 flex items-center gap-2">
            <Badge>{rec.priority}</Badge>
            <span className="text-sm text-muted">{rec.op_id}</span>
          </div>
          <p className="text-sm text-gray-200">{rec.recommendation_text}</p>
          <select
            className="mt-3 rounded border border-white/10 bg-bg px-2 py-1 text-sm"
            defaultValue={rec.status}
            onChange={(event) => updateRecommendation(rec.id, event.target.value as "open" | "acknowledged" | "resolved")}
          >
            <option value="open">open</option>
            <option value="acknowledged">acknowledged</option>
            <option value="resolved">resolved</option>
          </select>
        </Card>
      ))}
    </div>
  );
}
