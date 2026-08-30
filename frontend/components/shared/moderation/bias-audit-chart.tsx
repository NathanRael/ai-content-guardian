import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { BiasAuditResponse } from "@/types/moderation";

interface BiasAuditChartProps {
  audit: BiasAuditResponse;
}

export function BiasAuditChart({ audit }: BiasAuditChartProps) {
  const data = [
    {
      name: "Taux de signalement",
      high: audit.flag_rate_high_dialect_markers * 100,
      low: audit.flag_rate_low_dialect_markers * 100,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparaison des taux de signalement</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="name" hide />
              <YAxis
                tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                axisLine={false}
                tickLine={false}
                unit=" %"
              />
              <Tooltip
                formatter={(value) => [`${Number(value).toFixed(1)} %`, ""]}
                contentStyle={{
                  background: "var(--popover)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-md)",
                }}
              />
              <Legend
                verticalAlign="top"
                align="center"
                wrapperStyle={{ paddingBottom: 16 }}
              />
              <Bar
                dataKey="high"
                name="Marqueurs AAE élevés"
                fill="var(--chart-1)"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="low"
                name="Marqueurs AAE faibles"
                fill="var(--chart-3)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-background-200 bg-background-100 p-4">
          <p className="text-small text-muted-foreground">Écart entre les deux groupes</p>
          <p className="text-subtitle-2 font-semibold text-foreground">
            {(audit.gap * 100).toFixed(1)} points
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
