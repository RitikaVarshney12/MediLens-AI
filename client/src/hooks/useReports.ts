import { useQuery } from "@tanstack/react-query";

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

export function useReports() {
  return useQuery({
    queryKey: REPORTS_QUERY_KEY,
    queryFn: fetchReports,
  });
}