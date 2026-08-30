import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ModerationLabel } from "@/types/moderation";

export function labelText(label: ModerationLabel) {
  const map: Record<ModerationLabel, string> = {
    hate_speech: "Discours haineux",
    offensive: "Offensant",
    neutral: "Sûr",
  };
  return map[label];
}

export function labelClasses(label: ModerationLabel) {
  return {
    hate_speech: "bg-destructive/10 text-destructive border-destructive/20",
    offensive: "bg-secondary/50 text-secondary-foreground border-secondary",
    neutral: "bg-background-100 text-foreground border-background-200",
  }[label];
}

export function LabelBadge({
  label,
  className,
}: {
  label: ModerationLabel;
  className?: string;
}) {
  return (
    <Badge
      variant="outline"
      className={cn(labelClasses(label), "font-medium", className)}
    >
      {labelText(label)}
    </Badge>
  );
}

export function recommendationText(
  recommendation: "auto_flag_possible" | "human_review_required",
) {
  return recommendation === "human_review_required"
    ? "Revu humain recommandé"
    : "Signalisation automatique possible";
}

export function recommendationClasses(
  recommendation: "auto_flag_possible" | "human_review_required",
) {
  return recommendation === "human_review_required"
    ? "bg-destructive/10 text-destructive border-destructive/20"
    : "bg-background-100 text-foreground border-background-200";
}
