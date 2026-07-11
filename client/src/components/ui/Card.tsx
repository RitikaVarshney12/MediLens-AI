import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-2xl border border-surface-border bg-surface p-6 shadow-card ${className}`}
    >
      {children}
    </div>
  );
}
