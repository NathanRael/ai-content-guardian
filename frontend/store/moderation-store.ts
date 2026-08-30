import { create } from "zustand";
import { persist } from "zustand/middleware";

import type {
  BatchAnalysisResponse,
  GeneratedComment,
} from "@/types/moderation";

interface ModerationState {
  latestBatch: BatchAnalysisResponse | null;
  generatedComments: GeneratedComment[] | null;
  setLatestBatch: (batch: BatchAnalysisResponse | null) => void;
  setGeneratedComments: (comments: GeneratedComment[] | null) => void;
  clearLatestBatch: () => void;
  clearGeneratedComments: () => void;
  clearAll: () => void;
}

export const useModerationStore = create<ModerationState>()(
  persist(
    (set) => ({
      latestBatch: null,
      generatedComments: null,
      setLatestBatch: (batch) => set({ latestBatch: batch }),
      setGeneratedComments: (comments) => set({ generatedComments: comments }),
      clearLatestBatch: () => set({ latestBatch: null }),
      clearGeneratedComments: () => set({ generatedComments: null }),
      clearAll: () => set({ latestBatch: null, generatedComments: null }),
    }),
    {
      name: "ai-content-guardian-moderation",
    },
  ),
);
