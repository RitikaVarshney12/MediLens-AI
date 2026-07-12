import type { AxiosProgressEvent } from "axios";

import { apiClient } from "@/services/apiClient";
import type { Report } from "@/types/report";

interface UploadReportResponse {
  report: Report;
  message: string;
}

export async function uploadReport(
  file: File,
  onProgress?: (percent: number) => void
): Promise<Report> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<UploadReportResponse>(
    "/api/reports/upload",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (!onProgress || !event.total) return;
        onProgress(Math.round((event.loaded / event.total) * 100));
      },
    }
  );

  return data.report;
}