import type { Report } from "@/types/report";

export interface ReportStats {
  totalReports: number;
  storageUsageBytes: number;
  latestUploadAt: string | null;
}

export function computeReportStats(reports: Report[]): ReportStats {
  return {
    totalReports: reports.length,
    storageUsageBytes: reports.reduce((sum, report) => sum + report.file_size, 0),
    latestUploadAt: reports[0]?.uploaded_at ?? null,
  };
}