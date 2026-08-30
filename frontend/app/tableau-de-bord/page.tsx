"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { CommentCard } from "@/components/shared/moderation/comment-card";
import { StatsSummary } from "@/components/shared/moderation/stats-summary";
import { useLatestBatch } from "@/features/moderation/hooks/use-latest-batch";

export default function DashboardPage() {
  const batch = useLatestBatch();

  if (!batch) {
    return (
      <div className="flex-center min-h-[60vh] gap-6 text-center">
        <div className="space-y-2">
          <h1 className="text-subtitle font-semibold">Aucun lot analysé</h1>
          <p className="text-muted-foreground">
            Lancez une simulation pour générer et analyser un lot de
            commentaires.
          </p>
        </div>
        <Button asChild data-cy="dashboard-simulation-link">
          <Link href="/simulation">Aller à la simulation</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-subtitle font-semibold">Tableau de bord</h1>
          <p className="text-muted-foreground">
            Résultats du dernier lot analysé
          </p>
        </div>
        <Button asChild variant="outline" data-cy="dashboard-new-simulation">
          <Link href="/simulation">Nouvelle simulation</Link>
        </Button>
      </div>

      <StatsSummary summary={batch.summary} />

      <section className="space-y-4">
        <h2 className="text-subtitle-2 font-semibold">
          Commentaires analysés
        </h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 max-h-[80vh] overflow-y-auto pr-2">
          {batch.results.map((comment) => (
            <CommentCard key={comment.id} comment={comment} />
          ))}
        </div>
      </section>
    </div>
  );
}
