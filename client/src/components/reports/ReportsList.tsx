import { useState } from "react";

import Card from "@/components/ui/Card";
import Skeleton from "@/components/ui/Skeleton";
import ReportStatusBadge from "@/components/reports/ReportStatusBadge";
import ReportDetailModal from "@/components/reports/ReportDetailModal";
import { formatDate, formatFileSize } from "@/lib/formatters";
import type { Report } from "@/types/report";

interface ReportsListProps {
  reports: Report[];
  isLoading: boolean;
}

export default function ReportsList({ reports, isLoading }: ReportsListProps) {
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  // Re-derived from the live (polling) `reports` array on every render, so
  // the open modal reflects status changes (e.g. processing -> completed)
  // instead of showing a stale snapshot from the moment it was opened.
  const selectedReport = reports.find((report) => report.id === selectedReportId) ?? null;

  if (isLoading) {
    return (
      <Card className="flex flex-col gap-3">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
      </Card>
    );
  }

  if (reports.length === 0) {
    return (
      <Card className="flex flex-col items-center gap-2 py-10 text-center">
        <span className="text-3xl" aria-hidden="true">
          🗂️
        </span>
        <h3 className="font-semibold text-ink">No reports yet</h3>
        <p className="max-w-sm text-sm text-ink-soft">
          Upload your first blood report, lab result, or prescription above to see it here.
        </p>
      </Card>
    );
  }

  return (
    <>
      <Card className="overflow-hidden p-0">
        <div className="border-b border-surface-border px-6 py-4">
          <h2 className="font-semibold text-ink">Recent reports</h2>
        </div>
        <ul className="divide-y divide-surface-border">
          {reports.map((report) => (
            <li key={report.id}>
              <button
                type="button"
                onClick={() => setSelectedReportId(report.id)}
                className="flex w-full items-center justify-between gap-4 px-6 py-4 text-left transition-colors hover:bg-surface-subtle"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-ink">{report.file_name}</p>
                  <p className="text-sm text-ink-soft">
                    {formatDate(report.uploaded_at)} · {formatFileSize(report.file_size)}
                  </p>
                </div>
                <ReportStatusBadge status={report.status} />
              </button>
            </li>
          ))}
        </ul>
      </Card>

      {selectedReport && (
        <ReportDetailModal report={selectedReport} onClose={() => setSelectedReportId(null)} />
      )}
    </>
  );
}