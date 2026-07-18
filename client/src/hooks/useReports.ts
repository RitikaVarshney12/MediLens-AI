import { useQuery, type Query } from "@tanstack/react-query";

import { supabase } from "@/lib/supabase";
import type { Report } from "@/types/report";

async function fetchReports(): Promise<Report[]> {
  const { data, error } = await supabase
    .from("reports")
    .select("*")
    .order("uploaded_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data as Report[];
}

export const REPORTS_QUERY_KEY = ["reports"] as const;

function hasPendingReports(reports: Report[] | undefined): boolean {
  return (reports ?? []).some((report) => report.status === "uploaded" || report.status === "processing");
}

export function useReports() {
  return useQuery({
    queryKey: REPORTS_QUERY_KEY,
    queryFn: fetchReports,
    refetchInterval: (query: Query<Report[]>) => (hasPendingReports(query.state.data) ? 3000 : false),
  });
}