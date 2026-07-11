import type { ReactNode } from "react";

import Card from "@/components/ui/Card";

interface AuthCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}

export default function AuthCard({ title, subtitle, children, footer }: AuthCardProps) {
  return (
    <Card className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">{title}</h1>
        {subtitle && <p className="mt-1 text-ink-soft">{subtitle}</p>}
      </div>
      {children}
      {footer && <div className="border-t border-surface-border pt-5">{footer}</div>}
    </Card>
  );
}
