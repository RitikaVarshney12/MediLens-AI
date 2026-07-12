export type ReportStatus = "uploaded" | "processing" | "completed" | "failed";

export interface Report {
  id: string;
  user_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  status: ReportStatus;
  uploaded_at: string;
}