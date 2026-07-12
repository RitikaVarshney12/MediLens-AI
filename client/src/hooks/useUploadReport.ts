import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { REPORTS_QUERY_KEY } from "@/hooks/useReports";
import { uploadReport } from "@/services/reportsApi";
import type { Report } from "@/types/report";

export function useUploadReport() {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState(0);

  const mutation = useMutation<Report, Error, File>({
    mutationFn: (file) => uploadReport(file, setProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTS_QUERY_KEY });
    },
    onSettled: () => {
      setProgress(0);
    },
  });

  return {
    uploadReport: mutation.mutateAsync,
    isUploading: mutation.isPending,
    progress,
  };
}