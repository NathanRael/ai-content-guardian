"use client";

import { AlertTriangle, BookOpen, Users } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useGetModelInfo } from "@/features/moderation/hooks/use-get-model-info";

export default function ModelInfoPage() {
  const { data, isLoading } = useGetModelInfo();

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex-center min-h-[50vh] gap-3">
        <AlertTriangle className="size-5 text-destructive" />
        <p>Impossible de charger la fiche modèle.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-subtitle font-semibold">Fiche modèle</h1>
        <p className="text-muted-foreground">
          Informations sur l’usage prévu, les limites et les données
          d’entraînement.
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <BookOpen className="size-5 text-accent" />
          <CardTitle>Usage prévu</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-foreground">{data.intended_use}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <AlertTriangle className="size-5 text-destructive" />
          <CardTitle>Usage non prévu</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-2 pl-5 text-foreground">
            {data.not_intended_for.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Limites connues</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-2 pl-5 text-foreground">
            {data.known_limitations.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Users className="size-5 text-accent" />
          <CardTitle>Rôle humain</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-foreground">{data.human_role}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Résumé des données d’entraînement</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <StatRow label="Source" value={data.training_data_summary.source} />
          <StatRow
            label="Taille"
            value={data.training_data_summary.size.toLocaleString("fr-FR")}
          />
          <div>
            <p className="text-small text-muted-foreground mb-2">
              Répartition des classes
            </p>
            <div className="grid gap-2 sm:grid-cols-3">
              {Object.entries(data.training_data_summary.class_distribution).map(
                ([key, value]) => (
                  <div
                    key={key}
                    className="rounded-lg border border-background-200 p-3"
                  >
                    <p className="text-small text-muted-foreground">{key}</p>
                    <p className="text-lead font-semibold">
                      {value.toLocaleString("fr-FR")}
                    </p>
                  </div>
                ),
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-background-200 pb-3">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
