"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { LiveMessage } from "@/types";

type NewConversationMessage = Extract<LiveMessage, { type: "new_conversation" }>;

export function LiveFeed() {
  const { connected, messages } = useWebSocket();
  const rows = messages.filter((message): message is NewConversationMessage => message.type === "new_conversation");
  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Live Conversation Feed</h2>
        <span className="text-sm text-muted">{connected ? "Simulating live data..." : "Disconnected"}</span>
      </div>
      <div className="space-y-2">
        {rows.length === 0 ? <p className="text-sm text-muted">No live conversations yet.</p> : null}
        {rows.map((row, index) => (
          <div key={`${row.timestamp}-${index}`} className="grid grid-cols-5 gap-3 rounded border border-white/5 bg-white/[0.02] p-3 text-sm">
            <span>{row.op_name || row.op_id}</span>
            <span className="col-span-2 truncate text-gray-300">{row.intent_detected}</span>
            <Badge tone={row.resolution_status}>{row.resolution_status}</Badge>
            <span className="text-right text-muted">{new Date(row.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
