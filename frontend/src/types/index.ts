export type ResolutionStatus = "resolved" | "escalated" | "looped" | "failed";

export type OperatingProcedure = {
  id: string;
  name: string;
  description: string;
  health_score: number;
  resolution_rate: number;
  escalation_rate: number;
  loop_rate: number;
  avg_turn_count: number;
  avg_sentiment_score: number;
  conversation_count: number;
  last_computed_at: string;
};

export type Conversation = {
  id: string;
  op_id: string;
  op_name: string;
  turns: { role: "customer" | "agent"; text: string; timestamp: string }[];
  resolution_status: ResolutionStatus;
  turn_count: number;
  customer_sentiment: "positive" | "neutral" | "negative";
  intent_detected: string;
  session_duration_seconds: number;
  created_at: string;
};

export type FailureCluster = {
  id: number;
  op_id: string;
  cluster_label: number;
  size: number;
  centroid_summary: string;
  example_conversation_ids: string[];
  gap_description: string;
  created_at: string;
};

export type Recommendation = {
  id: number;
  op_id: string;
  cluster_id: number | null;
  recommendation_text: string;
  priority: "high" | "medium" | "low";
  status: "open" | "acknowledged" | "resolved";
  created_at: string;
};

export type ProcedureDetail = OperatingProcedure & {
  recent_conversations: Conversation[];
  failure_clusters: FailureCluster[];
  recommendations: Recommendation[];
  breakdown: Record<string, number>;
};
