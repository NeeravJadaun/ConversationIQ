import { statusClass } from "@/lib/utils";

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  const cls = tone === "neutral" ? "bg-white/5 text-gray-200 border-white/10" : statusClass(tone);
  return <span className={`inline-flex rounded border px-2 py-1 text-xs font-medium ${cls}`}>{children}</span>;
}
