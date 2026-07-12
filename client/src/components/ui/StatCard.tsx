import type { ReactNode } from "react";

import Card from "@/components/ui/Card";

interface StatCardProps {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
}

export default function StatCard({ label, value, icon }: StatCardProps) {
  return (
    <Card className="flex items-center gap-4">
      {icon && (
        <span
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-600"
          aria-hidden="true"
        >
          {icon}
        </span>
      )}
      <div>
        <p className="text-sm text-ink-soft">{label}</p>
        <p className="text-xl font-bold text-ink">{value}</p>
      </div>
    </Card>
  );
}