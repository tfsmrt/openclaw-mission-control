import { type ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface DependencyBannerDependency {
  id: string;
  title: string;
  statusLabel: string;
  isBlocking?: boolean;
  isDone?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

interface DependencyBannerProps {
  variant?: DependencyBannerVariant;
  dependencies?: DependencyBannerDependency[];
  children?: ReactNode;
  className?: string;
  emptyMessage?: string;
}

type DependencyBannerVariant = "blocked" | "resolved";

const toneClassByVariant: Record<DependencyBannerVariant, string> = {
  blocked: "border-[color:var(--danger-border)] bg-[color:var(--danger-soft)] text-danger",
  resolved: "border-[color:var(--info-border)] bg-[color:var(--info-soft)] text-info",
};

export function DependencyBanner({
  variant = "blocked",
  dependencies = [],
  children,
  className,
  emptyMessage = "No dependencies.",
}: DependencyBannerProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {dependencies.length > 0 ? (
        dependencies.map((dependency) => {
          const isBlocking = dependency.isBlocking === true;
          const isDone = dependency.isDone === true;
          return (
            <button
              key={dependency.id}
              type="button"
              onClick={dependency.onClick}
              disabled={dependency.disabled}
              className={cn(
                "w-full rounded-lg border px-3 py-2 text-left transition",
                isBlocking
                  ? "border-[color:var(--danger-border)] bg-[color:var(--danger-soft)] hover:bg-[color:var(--danger-soft)]"
                  : isDone
                    ? "border-emerald-200 bg-[color:var(--success-soft)] hover:bg-[color:var(--success-soft)]"
                    : "border-[color:var(--border)] bg-[color:var(--surface)] hover:bg-[color:var(--surface-muted)]",
                dependency.disabled && "cursor-not-allowed opacity-60",
              )}
            >
              <div className="flex items-center justify-between gap-3">
                <p className="truncate text-sm font-medium text-strong">
                  {dependency.title}
                </p>
                <span
                  className={cn(
                    "text-[10px] font-semibold uppercase tracking-wide",
                    isBlocking
                      ? "text-danger"
                      : isDone
                        ? "text-success"
                        : "text-quiet",
                  )}
                >
                  {dependency.statusLabel}
                </span>
              </div>
            </button>
          );
        })
      ) : (
        <p className="text-sm text-quiet">{emptyMessage}</p>
      )}
      {children ? (
        <div
          className={cn(
            "rounded-lg border p-3 text-xs",
            toneClassByVariant[variant],
          )}
        >
          {children}
        </div>
      ) : null}
    </div>
  );
}
