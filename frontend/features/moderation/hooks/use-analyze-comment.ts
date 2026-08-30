import { useMutation } from "@tanstack/react-query";

import { analyzeComment } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";

export const useAnalyzeComment = () => {
  return useMutation({
    mutationKey: QUERY_KEYS.ANALYZE_COMMENT,
    mutationFn: analyzeComment,
  });
};
