import { useMutation } from "@tanstack/react-query";

import { analyzeComments } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";
import { useModerationStore } from "@/store/moderation-store";
import type { GeneratedComment } from "@/types/moderation";

export const useAnalyzeComments = () => {
  const setLatestBatch = useModerationStore((state) => state.setLatestBatch);
  const clearGeneratedComments = useModerationStore(
    (state) => state.clearGeneratedComments,
  );

  return useMutation({
    mutationKey: QUERY_KEYS.ANALYZE_COMMENTS,
    mutationFn: ({
      comments,
      model,
      translate,
    }: {
      comments: GeneratedComment[];
      model?: "logistic_regression" | "random_forest" | "both";
      translate?: boolean;
    }) => analyzeComments(comments, { model, translate }),
    onSuccess: (data) => {
      setLatestBatch(data);
      clearGeneratedComments();
    },
  });
};
