"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme, type Theme } from "@/components/providers/ThemeProvider";
import { cn } from "@/lib/utils";

const options: { value: Theme; icon: React.ReactNode; label: string }[] = [
  { value: "light", icon: <Sun size={13} />, label: "Light" },
  { value: "dark", icon: <Moon size={13} />, label: "Dark" },
  { value: "system", icon: <Monitor size={13} />, label: "System" },
];

export function ThemeSwitcher({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme();

  return (
    <div
      className={cn(
        "flex items-center rounded-lg border border-[color:var(--border)] bg-[color:var(--surface-muted)] p-0.5",
        className,
      )}
      role="group"
      aria-label="Theme"
    >
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          title={opt.label}
          aria-pressed={theme === opt.value}
          onClick={() => setTheme(opt.value)}
          className={cn(
            "flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-all",
            theme === opt.value
              ? "bg-[color:var(--surface)] text-[color:var(--text)] shadow-sm"
              : "text-quiet hover:text-[color:var(--text)]",
          )}
        >
          {opt.icon}
          <span className="hidden sm:inline">{opt.label}</span>
        </button>
      ))}
    </div>
  );
}
