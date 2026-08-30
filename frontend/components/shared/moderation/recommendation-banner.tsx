import { AlertTriangle, CheckCircle } from "lucide-react";

import { cn } from "@/lib/utils";

interface RecommendationBannerProps {
  recommendation: "auto_flag_possible" | "human_review_required";
  reason: string;
}

export function RecommendationBanner({
  recommendation,
  reason,
}: RecommendationBannerProps) {
  const isHumanReview = recommendation === "human_review_required";

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-lg border p-4",
        isHumanReview
          ? "border-destructive/20 bg-destructive/10 text-destructive"
          : "border-background-200 bg-background-100 text-foreground",
      )}
      data-cy="recommendation-banner"
    >
      {isHumanReview ? (
        <AlertTriangle className="mt-0.5 size-5 shrink-0" />
      ) : (
        <CheckCircle className="mt-0.5 size-5 shrink-0" />
      )}
      <div className="space-y-1">
        <p className="font-semibold">
          {isHumanReview
            ? "Revu humain recommandé"
            : "Signalisation automatique possible"}
        </p>
        <p className="text-small opacity-90">{reason}</p>
      </div>
    </div>
  );
}
