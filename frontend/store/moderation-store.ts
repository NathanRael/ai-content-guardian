import { create } from "zustand";
import { persist } from "zustand/middleware";

import type {
  AnalysisModel,
  BatchAnalysisResponse,
  GeneratedComment,
} from "@/types/moderation";

export interface LatestBatch {
  response: BatchAnalysisResponse;
  model: AnalysisModel;
}

interface ModerationState {
  latestBatch: LatestBatch | null;
  generatedComments: GeneratedComment[] | null;
  setLatestBatch: (
    batch: BatchAnalysisResponse | null,
    model?: AnalysisModel,
  ) => void;
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
      setLatestBatch: (batch, model = "both") =>
        set({ latestBatch: batch ? { response: batch, model } : null }),
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
