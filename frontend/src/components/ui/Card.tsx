export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-lg border border-white/10 bg-surface p-4 shadow-sm ${className}`}>{children}</div>;
}
