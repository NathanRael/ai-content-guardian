import { CheckIcon, XIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AnalysisResult } from "@/types/moderation";

import { ConfidenceBar } from "./confidence-bar";
import { LabelBadge } from "./label-helpers";

interface ModelComparisonPanelProps {
  result: AnalysisResult;
}

export function ModelComparisonPanel({ result }: ModelComparisonPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparaison des modèles</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-6 sm:grid-cols-2">
          <ModelResult
            name="Logistic Regression"
            prediction={result.logistic_regression}
          />
          <ModelResult
            name="Random Forest"
            prediction={result.random_forest}
          />
        </div>

        <div
          className={cn(
            "flex items-center gap-2 rounded-md border px-3 py-2 text-small",
            result.models_agree
              ? "border-background-200 bg-background-100 text-foreground"
              : "border-destructive/20 bg-destructive/10 text-destructive",
          )}
        >
          {result.models_agree ? (
            <CheckIcon className="size-4" />
          ) : (
            <XIcon className="size-4" />
          )}
          <span className="font-medium">
            {result.models_agree
              ? "Les modèles sont d'accord"
              : "Les modèles ne sont pas d'accord"}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

function ModelResult({
  name,
  prediction,
}: {
  name: string;
  prediction: AnalysisResult["logistic_regression"];
}) {
  return (
    <div className="space-y-3 rounded-lg border border-background-200 p-4">
      <p className="text-small font-medium text-muted-foreground">{name}</p>
      <div className="flex items-center gap-2">
        <LabelBadge label={prediction.label} />
      </div>
      <ConfidenceBar value={prediction.confidence} label={prediction.label} />
    </div>
  );
}
