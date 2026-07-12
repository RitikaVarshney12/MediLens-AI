import type { ReportStatus } from "@/types/report";

const STATUS_STYLES: Record<ReportStatus, string> = {
  uploaded: "bg-primary-50 text-primary-600",
  processing: "bg-amber-50 text-amber-700",
  completed: "bg-emerald-50 text-emerald-700",
  failed: "bg-red-50 text-red-700",
};

const STATUS_LABELS: Record<ReportStatus, string> = {
  uploaded: "Uploaded",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
};

export default function ReportStatusBadge({ status }: { status: ReportStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}