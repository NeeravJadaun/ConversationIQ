export function scoreTone(score: number) {
  if (score >= 80) return "text-healthy border-healthy";
  if (score >= 60) return "text-warning border-warning";
  return "text-critical border-critical";
}

export function statusClass(status: string) {
  if (status === "resolved") return "bg-healthy/15 text-healthy border-healthy/30";
  if (status === "escalated") return "bg-warning/15 text-warning border-warning/30";
  if (status === "looped") return "bg-orange-500/15 text-orange-300 border-orange-400/30";
  return "bg-critical/15 text-critical border-critical/30";
}
