import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

import type { AnalysisResult } from "@/types/moderation";

interface ExplanationPanelProps {
  explanation: AnalysisResult["explanation"];
  dialectMarkerScore: number;
}

export function ExplanationPanel({
  explanation,
  dialectMarkerScore,
}: ExplanationPanelProps) {
  const data = explanation.top_words
    .slice(0, 10)
    .map((item) => ({ ...item, word: item.word }));

  const dialectPercentage = Math.round(dialectMarkerScore * 100);

  return (
    <div className="space-y-8">
      <section>
        <h3 className="mb-3 text-small font-semibold uppercase tracking-wide text-muted-foreground">
          Mots influents (LIME)
        </h3>
        <div style={{ height: Math.max(200, data.length * 40) }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 8, right: 24, left: 24, bottom: 8 }}
            >
              <XAxis type="number" hide />
              <YAxis
                dataKey="word"
                type="category"
                width={100}
                tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                axisLine={false}
                tickLine={false}
              />
              <Bar dataKey="weight" radius={[4, 4, 4, 4]}>
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      entry.weight >= 0
                        ? "var(--chart-1)"
                        : "var(--muted-foreground)"
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-3 text-small text-muted-foreground">
          Les mots à droite poussent vers la classe prédite. Les mots à gauche
          l’éloignent.
        </p>
      </section>

      <hr className="border-background-200" />

      <section>
        <h3 className="mb-3 text-small font-semibold uppercase tracking-wide text-muted-foreground">
          Marqueurs de dialecte
        </h3>
        <div className="flex items-center justify-between text-small">
          <span className="text-muted-foreground">Score AAE</span>
          <span className="font-medium">{dialectPercentage} %</span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-background-200">
          <div
            className="h-full rounded-full bg-accent transition-all"
            style={{ width: `${dialectPercentage}%` }}
          />
        </div>
        <p className="mt-3 text-small text-muted-foreground">
          Un score élevé indique la présence de marqueurs linguistiques AAE.
          Ces marqueurs ne sont jamais utilisés comme features d’entraînement,
          mais ils peuvent influencer indirectement la prédiction.
        </p>
      </section>
    </div>
  );
}
