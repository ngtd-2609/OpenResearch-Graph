import type { ReactNode } from "react";

type StatusTone = "neutral" | "success" | "warning" | "error";

type StatusBadgeProps = {
  children: ReactNode;
  tone?: StatusTone;
  label?: string;
};

export default function StatusBadge({
  children,
  tone = "neutral",
  label,
}: StatusBadgeProps) {
  return (
    <span
      aria-label={label}
      className={`badge badge--${tone}`}
      data-tone={tone}
      role="status"
    >
      {children}
    </span>
  );
}
