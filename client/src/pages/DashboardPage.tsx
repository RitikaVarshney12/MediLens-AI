import StatCard from "@/components/ui/StatCard";
import UploadDropzone from "@/components/reports/UploadDropzone";
import ReportsList from "@/components/reports/ReportsList";
import { useReports } from "@/hooks/useReports";
import { computeReportStats } from "@/lib/reports/stats";
import { formatDate, formatFileSize } from "@/lib/formatters";

export default function DashboardPage() {
  const { data: reports, isLoading } = useReports();
  const stats = computeReportStats(reports ?? []);

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold text-ink">Welcome to MediLens AI</h1>
        <p className="mt-1 text-ink-soft">Upload a report to get started.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Total reports" value={stats.totalReports} icon="🗂️" />
        <StatCard label="Storage usage" value={formatFileSize(stats.storageUsageBytes)} icon="💾" />
        <StatCard
          label="Latest upload"
          value={stats.latestUploadAt ? formatDate(stats.latestUploadAt) : "—"}
          icon="🕒"
        />
      </div>

      <UploadDropzone />

      <ReportsList reports={reports ?? []} isLoading={isLoading} />
    </div>
  );
}