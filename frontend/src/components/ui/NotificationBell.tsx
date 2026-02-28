"use client";

import { useEffect, useRef, useState } from "react";
import { Bell, CheckCheck, MessageSquare, GitPullRequestArrow, AtSign } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  useNotifications,
  type AppNotification,
} from "@/hooks/useNotifications";
import { useRouter } from "next/navigation";

function NotifIcon({ type }: { type: AppNotification["type"] }) {
  if (type === "comment_added")
    return <MessageSquare className="h-3.5 w-3.5 text-info" />;
  if (type === "mention")
    return <AtSign className="h-3.5 w-3.5 text-[color:var(--status-inprogress-text)]" />;
  return <GitPullRequestArrow className="h-3.5 w-3.5 text-success" />;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function NotificationBell() {
  const { notifications, unreadCount, markAllRead, markOneRead, requestPermission } =
    useNotifications();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Request browser notification permission on first unread
  useEffect(() => {
    if (unreadCount > 0) requestPermission();
  }, [unreadCount, requestPermission]);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleNotifClick = async (n: AppNotification) => {
    if (!n.read) await markOneRead(n.id);
    if (n.board_id && n.task_id) {
      router.push(`/boards/${n.board_id}?task=${n.task_id}`);
    } else if (n.board_id) {
      router.push(`/boards/${n.board_id}`);
    }
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "relative flex h-9 w-9 items-center justify-center rounded-lg border transition",
          "border-[color:var(--border)] text-quiet hover:border-[color:var(--border-strong)] hover:bg-[color:var(--surface-muted)] hover:text-muted",
          "dark:border-slate-700",
          open && "border-[color:var(--border-strong)] bg-[color:var(--surface-muted)]",
        )}
        aria-label="Notifications"
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[color:var(--danger)] text-[10px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          className={cn(
            "absolute right-0 top-11 z-50 w-80 overflow-hidden rounded-xl border shadow-lg",
            "border-[color:var(--border)] bg-[color:var(--surface)]",
            "dark:border-slate-700",
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[color:var(--border)] px-4 py-3">
            <span className="text-sm font-semibold text-strong">
              Notifications
            </span>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                className="flex items-center gap-1 text-xs text-quiet hover:text-muted"
              >
                <CheckCheck className="h-3.5 w-3.5" />
                Mark all read
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-sm text-quiet">
                No notifications yet
              </div>
            ) : (
              notifications.map((n) => (
                <button
                  key={n.id}
                  type="button"
                  onClick={() => handleNotifClick(n)}
                  className={cn(
                    "flex w-full items-start gap-3 border-b px-4 py-3 text-left transition last:border-b-0",
                    "border-[color:var(--border)] hover:bg-[color:var(--surface-muted)]",
                    !n.read && "bg-[color:var(--info-soft)]",
                  )}
                >
                  <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-[color:var(--surface-strong)]">
                    <NotifIcon type={n.type} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p
                      className={cn(
                        "truncate text-sm",
                        n.read
                          ? "font-normal text-muted"
                          : "font-medium text-strong",
                      )}
                    >
                      {n.title}
                    </p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-quiet">
                      {n.body}
                    </p>
                    <p className="mt-1 text-[10px] text-quiet">
                      {timeAgo(n.created_at)}
                    </p>
                  </div>
                  {!n.read && (
                    <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-[color:var(--info)]" />
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
