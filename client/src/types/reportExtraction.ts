export type OcrStatus = "processing" | "completed" | "failed";

export interface MedicalParameter {
  parameter: string;
  value: string;
  unit: string | null;
  reference_range: string | null;
}

export interface ReportExtraction {
  id: string;
  report_id: string;
  raw_text: string | null;
  structured_json: MedicalParameter[] | null;
  ocr_status: OcrStatus;
  processing_started_at: string | null;
  completed_at: string | null;
  created_at: string;
}