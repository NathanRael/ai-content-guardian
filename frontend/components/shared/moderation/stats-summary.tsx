import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { BatchSummary } from "@/types/moderation";

interface StatsSummaryProps {
  summary: BatchSummary;
}

export function StatsSummary({ summary }: StatsSummaryProps) {
  const data = [
    { name: "Sûr", value: summary.safe, key: "safe" as const },
    { name: "Offensant", value: summary.offensive, key: "offensive" as const },
    {
      name: "Discours haineux",
      value: summary.hate_speech,
      key: "hate_speech" as const,
    },
  ];

  const colors: Record<(typeof data)[number]["key"], string> = {
    safe: "var(--chart-2)",
    offensive: "var(--chart-4)",
    hate_speech: "var(--destructive)",
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Répartition du lot analysé</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, value }) => `${name} : ${value}`}
                >
                  {data.map((entry) => (
                    <Cell key={entry.key} fill={colors[entry.key]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-md)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Synthèse</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <StatRow label="Total analysé" value={summary.total} />
          <StatRow label="Sûr" value={summary.safe} />
          <StatRow label="Offensant" value={summary.offensive} />
          <StatRow label="Discours haineux" value={summary.hate_speech} />

          <div className="flex items-center justify-between border-t border-background-200 pt-4">
            <span className="text-muted-foreground">Niveau de risque</span>
            <RiskBadge level={summary.risk_level} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

function RiskBadge({ level }: { level: BatchSummary["risk_level"] }) {
  const config = {
    low: { text: "Faible", className: "bg-accent/10 text-accent" },
    medium: {
      text: "Moyen",
      className: "bg-secondary/50 text-secondary-foreground",
    },
    high: { text: "Élevé", className: "bg-destructive/10 text-destructive" },
  };

  return (
    <Badge
      variant="outline"
      className={cn("font-medium", config[level].className)}
    >
      {config[level].text}
    </Badge>
  );
}
