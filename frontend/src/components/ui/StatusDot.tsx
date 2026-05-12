export function StatusDot({ active = false }: { active?: boolean }) {
  return <span className={`inline-block h-2.5 w-2.5 rounded-full ${active ? "animate-pulse bg-accent" : "bg-muted"}`} />;
}
