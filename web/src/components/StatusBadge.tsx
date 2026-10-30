const S = {
  planned: { label: "Planned", cls: "bg-white text-ink" },
  in_progress: { label: "In progress", cls: "bg-butter text-ink" },
  completed: { label: "Completed", cls: "bg-moss text-white" },
} as const;
export default function StatusBadge({ status }: { status: keyof typeof S }) {
  const s = S[status];
  return <span className={`${s.cls} text-xs font-bold px-2.5 py-1 rounded-full border-2 border-ink whitespace-nowrap`}>{s.label}</span>;
}
