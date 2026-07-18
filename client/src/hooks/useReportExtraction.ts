import { useQuery, type Query } from "@tanstack/react-query";

import { supabase } from "@/lib/supabase";
import type { ReportExtraction } from "@/types/reportExtraction";

async function fetchExtraction(reportId: string): Promise<ReportExtraction | null> {
  const { data, error } = await supabase
    .from("report_extractions")
    .select("*")
    .eq("report_id", reportId)
    .maybeSingle();

  if (error) throw new Error(error.message);
  return data as ReportExtraction | null;
}

export function useReportExtraction(reportId: string | null) {
  return useQuery({
    queryKey: ["report-extraction", reportId],
    queryFn: () => fetchExtraction(reportId as string),
    enabled: !!reportId,
    refetchInterval: (query: Query<ReportExtraction | null>) =>
      query.state.data?.ocr_status === "processing" || query.state.data === undefined
        ? 2000
        : false,
  });
}