import { cn } from "@/lib/utils";

type StatusDotVariant = "agent" | "approval" | "task";

const AGENT_STATUS_DOT_CLASS_BY_STATUS: Record<string, string> = {
  online: "bg-emerald-500",
  busy: "bg-[color:var(--accent)]",
  provisioning: "bg-[color:var(--accent)]",
  updating: "bg-[color:var(--accent)]",
  deleting: "bg-[color:var(--danger)]",
  offline: "bg-slate-500",
};

const APPROVAL_STATUS_DOT_CLASS_BY_STATUS: Record<string, string> = {
  approved: "bg-[color:var(--success)]",
  rejected: "bg-[color:var(--danger)]",
  pending: "bg-[color:var(--warning)]",
};

const TASK_STATUS_DOT_CLASS_BY_STATUS: Record<string, string> = {
  inbox: "bg-[color:var(--surface-strong)]",
  in_progress: "bg-[color:var(--status-inprogress-bg)]",
  review: "bg-[color:var(--info)]",
  done: "bg-[color:var(--success)]",
};

const STATUS_DOT_CLASS_BY_VARIANT: Record<
  StatusDotVariant,
  Record<string, string>
> = {
  agent: AGENT_STATUS_DOT_CLASS_BY_STATUS,
  approval: APPROVAL_STATUS_DOT_CLASS_BY_STATUS,
  task: TASK_STATUS_DOT_CLASS_BY_STATUS,
};

const DEFAULT_STATUS_DOT_CLASS: Record<StatusDotVariant, string> = {
  agent: "bg-[color:var(--surface-strong)]",
  approval: "bg-[color:var(--warning)]",
  task: "bg-[color:var(--surface-strong)]",
};

export const statusDotClass = (
  status: string | null | undefined,
  variant: StatusDotVariant = "agent",
) => {
  const normalized = (status ?? "").trim().toLowerCase();
  if (!normalized) {
    return DEFAULT_STATUS_DOT_CLASS[variant];
  }
  return (
    STATUS_DOT_CLASS_BY_VARIANT[variant][normalized] ??
    DEFAULT_STATUS_DOT_CLASS[variant]
  );
};

type StatusDotProps = {
  status?: string | null;
  variant?: StatusDotVariant;
  className?: string;
};

export function StatusDot({
  status,
  variant = "agent",
  className,
}: StatusDotProps) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "inline-block h-2.5 w-2.5 rounded-full",
        statusDotClass(status, variant),
        className,
      )}
    />
  );
}
