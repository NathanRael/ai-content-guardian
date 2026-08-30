import { cn } from "@/lib/utils";
import type { ModerationLabel } from "@/types/moderation";

interface ConfidenceBarProps {
  value: number;
  label?: ModerationLabel;
  className?: string;
}

export function ConfidenceBar({ value, label, className }: ConfidenceBarProps) {
  const percentage = Math.round(value * 100);

  const fillClass =
    label === "hate_speech"
      ? "bg-destructive"
      : label === "offensive"
        ? "bg-secondary-foreground"
        : "bg-accent";

  return (
    <div className={cn("w-full", className)}>
      <div className="flex justify-between text-small mb-1">
        <span className="text-muted-foreground">Confiance</span>
        <span className="font-medium">{percentage} %</span>
      </div>
      <div className="h-2 w-full rounded-full bg-background-200 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", fillClass)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
