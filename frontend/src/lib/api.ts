import type { FailureCluster, OperatingProcedure, ProcedureDetail, Recommendation, TrendPoint } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const getProcedures = () => api<OperatingProcedure[]>("/api/procedures");
export const getProcedure = (id: string) => api<ProcedureDetail>(`/api/procedures/${id}`);
export const getTrend = (id: string) => api<TrendPoint[]>(`/api/procedures/${id}/trend`);
export const getClusters = () => api<FailureCluster[]>("/api/clusters");
export const recomputeClusters = () => api<FailureCluster[]>("/api/clusters/recompute", { method: "POST" });
export const getRecommendations = () => api<Recommendation[]>("/api/recommendations");
export const generateRecommendation = (op_id: string, cluster_id?: number) =>
  api<Recommendation>("/api/recommendations/generate", { method: "POST", body: JSON.stringify({ op_id, cluster_id }) });
export const updateRecommendation = (id: number, status: "open" | "acknowledged" | "resolved") =>
  api<Recommendation>(`/api/recommendations/${id}`, { method: "PATCH", body: JSON.stringify({ status }) });
