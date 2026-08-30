"use client";

import { AlertTriangle, Info, Scale } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BiasAuditChart } from "@/components/shared/moderation/bias-audit-chart";
import { LabelBadge, labelText } from "@/components/shared/moderation/label-helpers";

import { useGetBiasAudit } from "@/features/moderation/hooks/use-get-bias-audit";
import { useGetMetrics } from "@/features/moderation/hooks/use-get-metrics";
import { cn } from "@/lib/utils";
import type { ModelMetrics } from "@/types/moderation";

export default function AuditPage() {
  const { data: audit, isLoading: auditLoading } = useGetBiasAudit();
  const { data: metrics, isLoading: metricsLoading } = useGetMetrics();

  const isLoading = auditLoading || metricsLoading;

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!audit || !metrics) {
    return (
      <div className="flex-center min-h-[50vh] gap-3 text-center">
        <AlertTriangle className="size-5 text-destructive" />
        <p>Impossible de charger les données d’audit.</p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-subtitle font-semibold">Audit de biais</h1>
        <p className="text-muted-foreground">
          Transparence sur les performances et les biais potentiels des
          modèles.
        </p>
      </div>

      <section className="rounded-xl border border-background-200 bg-background-100 p-6">
        <div className="flex items-start gap-3">
          <Scale className="mt-1 size-5 shrink-0 text-accent" />
          <div className="space-y-2">
            <h2 className="text-subtitle-2 font-semibold">
              Méthodologie de l’audit
            </h2>
            <p className="text-foreground leading-relaxed">
              {audit.methodology_note}
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-subtitle-2 font-semibold">
          Taux de signalement par groupe
        </h2>
        <BiasAuditChart audit={audit} />
      </section>

      <section className="space-y-4">
        <h2 className="text-subtitle-2 font-semibold">
          Paires d’exemples standard / variante
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {audit.example_pairs.map((pair, index) => (
            <Card key={index}>
              <CardContent className="space-y-4 pt-6">
                <ExampleText label="Version standard" text={pair.standard} />
                <PredictionRow prediction={pair.prediction_standard} />
                <hr className="border-background-200" />
                <ExampleText
                  label="Variante de dialecte"
                  text={pair.dialect_variant}
                />
                <PredictionRow prediction={pair.prediction_variant} />
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-subtitle-2 font-semibold">
          Matrices de confusion
        </h2>
        <div className="grid gap-6 lg:grid-cols-2">
          <ConfusionMatrixCard
            title="Logistic Regression"
            metrics={metrics.logistic_regression}
          />
          <ConfusionMatrixCard
            title="Random Forest"
            metrics={metrics.random_forest}
          />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-subtitle-2 font-semibold">Cas limites</h2>
        <div className="grid gap-4">
          {metrics.edge_cases.map((edgeCase, index) => (
            <Card key={index}>
              <CardContent className="space-y-3 pt-6">
                <div className="flex items-center gap-2">
                  <Info className="size-4 text-muted-foreground" />
                  <span className="font-medium">{edgeCase.case_type}</span>
                </div>
                <p className="text-foreground">{edgeCase.example_text}</p>
                <div className="flex items-center gap-3">
                  <LabelBadge label={edgeCase.prediction.label} />
                  <span className="text-small text-muted-foreground">
                    Confiance : {Math.round(edgeCase.prediction.confidence * 100)} %
                  </span>
                </div>
                <p className="text-small text-muted-foreground">
                  {edgeCase.note}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

function ExampleText({ label, text }: { label: string; text: string }) {
  return (
    <div className="space-y-1">
      <p className="text-small text-muted-foreground">{label}</p>
      <p className="text-foreground">{text}</p>
    </div>
  );
}

function PredictionRow({
  prediction,
}: {
  prediction: { label: "hate_speech" | "offensive" | "neutral"; confidence: number };
}) {
  return (
    <div className="flex items-center gap-3">
      <LabelBadge label={prediction.label} />
      <span className="text-small text-muted-foreground">
        {labelText(prediction.label)} —{" "}
        {Math.round(prediction.confidence * 100)} %
      </span>
    </div>
  );
}

const headers = ["hate_speech", "offensive", "neutral"] as const;

function ConfusionMatrixCard({
  title,
  metrics,
}: {
  title: string;
  metrics: ModelMetrics;
}) {
  const max = Math.max(...metrics.confusion_matrix.flat());

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-small">
            <thead>
              <tr>
                <th className="p-2 text-left font-medium text-muted-foreground">
                  Vrai \ Prédit
                </th>
                {headers.map((h) => (
                  <th
                    key={h}
                    className="p-2 text-center font-medium text-muted-foreground"
                  >
                    {labelText(h)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.confusion_matrix.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="p-2 font-medium text-muted-foreground">
                    {labelText(headers[rowIndex])}
                  </td>
                  {row.map((value, colIndex) => {
                    const ratio = value > 0 ? value / max : 0;
                    return (
                      <td
                        key={colIndex}
                        className={cn(
                          "p-2 text-center rounded-md",
                          ratio > 0.6 && "text-white",
                        )}
                        style={
                          value > 0
                            ? {
                                backgroundColor: `color-mix(in oklch, var(--primary) ${Math.max(
                                  15,
                                  Math.round(ratio * 100),
                                )}%, transparent)`,
                              }
                            : undefined
                        }
                      >
                        {value}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
