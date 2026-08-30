import { useMutation } from "@tanstack/react-query";

import { generateComments } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";
import { useModerationStore } from "@/store/moderation-store";

export const useGenerateComments = () => {
  const setGeneratedComments = useModerationStore(
    (state) => state.setGeneratedComments,
  );
  const clearLatestBatch = useModerationStore(
    (state) => state.clearLatestBatch,
  );

  return useMutation({
    mutationKey: QUERY_KEYS.GENERATE_COMMENTS,
    mutationFn: ({ topic, count }: { topic: string; count: number }) =>
      generateComments(topic, count),
    onSuccess: (data) => {
      setGeneratedComments(data.comments);
      clearLatestBatch();
    },
  });
};
