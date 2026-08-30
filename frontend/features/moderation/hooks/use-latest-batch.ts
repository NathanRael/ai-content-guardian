import { useModerationStore } from "@/store/moderation-store";

export const useLatestBatch = () => {
  return useModerationStore((state) => state.latestBatch);
};
