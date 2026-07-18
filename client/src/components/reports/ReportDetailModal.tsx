import { useEffect } from "react";

import Skeleton from "@/components/ui/Skeleton";
import ReportStatusBadge from "@/components/reports/ReportStatusBadge";
import { useReportExtraction } from "@/hooks/useReportExtraction";
import { formatDate, formatFileSize } from "@/lib/formatters";
import type { Report } from "@/types/report";

interface ReportDetailModalProps {
  report: Report;
  onClose: () => void;
}

export default function ReportDetailModal({ report, onClose }: ReportDetailModalProps) {
  const { data: extraction, isLoading } = useReportExtraction(report.id);

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  const isProcessing = report.status === "uploaded" || report.status === "processing";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 px-4 py-8"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="report-detail-title"
        onClick={(event) => event.stopPropagation()}
        className="flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl bg-surface shadow-card-hover"
      >
        <div className="flex items-start justify-between gap-4 border-b border-surface-border px-6 py-4">
          <div className="min-w-0">
            <h2 id="report-detail-title" className="truncate font-semibold text-ink">
              {report.file_name}
            </h2>
            <p className="text-sm text-ink-soft">
              {formatDate(report.uploaded_at)} · {formatFileSize(report.file_size)}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-lg px-2 py-1 text-ink-soft hover:bg-surface-subtle hover:text-ink"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          <div className="mb-5 flex items-center gap-3">
            <ReportStatusBadge status={report.status} />
            {report.status === "completed" && (
              <span className="text-sm font-medium text-emerald-600">Ready for AI analysis</span>
            )}
          </div>

          {isProcessing && (
            <div className="flex flex-col gap-3" aria-live="polite">
              <p className="text-sm text-ink-soft">
                We're reading this report and pulling out the key values. This usually takes a
                minute, and this page will update automatically.
              </p>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          )}

          {report.status === "failed" && (
            <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
              We couldn't process this file. It may be corrupted, unreadable, or too complex to
              scan. Try re-uploading it, or use a clearer scan if it's a photo.
            </p>
          )}

          {report.status === "completed" && (
            <div className="flex flex-col gap-6">
              <div>
                <h3 className="mb-2 font-semibold text-ink">Detected parameters</h3>
                {isLoading ? (
                  <div className="flex flex-col gap-2">
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                  </div>
                ) : extraction?.structured_json && extraction.structured_json.length > 0 ? (
                  <div className="overflow-hidden rounded-xl border border-surface-border">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-surface-subtle text-ink-soft">
                        <tr>
                          <th className="px-4 py-2 font-medium">Parameter</th>
                          <th className="px-4 py-2 font-medium">Value</th>
                          <th className="px-4 py-2 font-medium">Unit</th>
                          <th className="px-4 py-2 font-medium">Reference range</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-surface-border">
                        {extraction.structured_json.map((param, index) => (
                          <tr key={`${param.parameter}-${index}`}>
                            <td className="px-4 py-2 font-medium text-ink">{param.parameter}</td>
                            <td className="px-4 py-2 text-ink">{param.value}</td>
                            <td className="px-4 py-2 text-ink-soft">{param.unit ?? "—"}</td>
                            <td className="px-4 py-2 text-ink-soft">
                              {param.reference_range ?? "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-sm text-ink-soft">
                    No specific lab parameters were detected in this report.
                  </p>
                )}
              </div>

              <div>
                <h3 className="mb-2 font-semibold text-ink">Extracted text</h3>
                {isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : (
                  <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-xl bg-surface-subtle p-4 text-sm text-ink-soft">
                    {extraction?.raw_text || "No text was extracted from this report."}
                  </pre>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}