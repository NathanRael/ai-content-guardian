import { useMutation } from "@tanstack/react-query";

import { analyzeComments } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";
import { useModerationStore } from "@/store/moderation-store";
import type { AnalysisModel, GeneratedComment } from "@/types/moderation";


export const useAnalyzeComments = () => {
  const setLatestBatch = useModerationStore((state) => state.setLatestBatch);

  return useMutation({
    mutationKey: QUERY_KEYS.ANALYZE_COMMENTS,
    mutationFn: ({
      comments,
      model,
      translate,
    }: {
      comments: GeneratedComment[];
      model?: AnalysisModel;
      translate?: boolean;
    }) => analyzeComments(comments, { model, translate }),
    onSuccess: (data, variables) => {
      setLatestBatch(data, variables.model ?? "both");
    },
  });
};
