"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CommentCard } from "@/components/shared/moderation/comment-card";
import { CollapsibleSection } from "@/components/shared/moderation/collapsible-section";
import { useGenerateComments } from "@/features/moderation/hooks/use-generate-comments";
import { useAnalyzeComments } from "@/features/moderation/hooks/use-analyze-comments";
import { useModerationStore } from "@/store/moderation-store";
import { ApiError } from "@/lib/api-client";

const countOptions = [10, 20, 30, 40, 50];
const modelOptions: {
  value: "both" | "logistic_regression" | "random_forest";
  label: string;
}[] = [
    { value: "both", label: "Les deux modèles" },
    { value: "logistic_regression", label: "Logistic Regression" },
    { value: "random_forest", label: "Random Forest" },
  ];

export default function SimulationPage() {
  const [topic, setTopic] = useState("");
  const [count, setCount] = useState(20);
  const [model, setModel] = useState<"both" | "logistic_regression" | "random_forest">("both");

  const generatedComments = useModerationStore(
    (state) => state.generatedComments,
  );
  const latestBatch = useModerationStore((state) => state.latestBatch);

  const { mutateAsync: generate, isPending: isGenerating } =
    useGenerateComments();
  const { mutateAsync: analyze, isPending: isAnalyzing } =
    useAnalyzeComments();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    try {
      await generate({ topic: topic.trim(), count });
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : "Erreur lors de la génération des commentaires.",
      );
    }
  };

  const handleAnalyze = async () => {
    if (!generatedComments || generatedComments.length === 0) return;
    try {
      await analyze({ comments: generatedComments, model, translate: false });
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : "Erreur lors de l’analyse du lot.",
      );
    }
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div>
        <h1 className="text-subtitle font-semibold">Simulation</h1>
        <p className="text-muted-foreground">
          Générez un lot de commentaires sur un sujet, puis analysez-le.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="topic">Sujet</Label>
          <Input
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Exemple : politique, sport, jeux vidéo"
            data-cy="simulation-topic"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="count">Nombre de commentaires</Label>
          <Select
            value={String(count)}
            onValueChange={(value) => setCount(Number(value))}
          >
            <SelectTrigger
              id="count"
              className="w-32"
              data-cy="simulation-count"
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {countOptions.map((option) => (
                <SelectItem key={option} value={String(option)}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button
          type="submit"
          disabled={isGenerating || !topic.trim()}
          data-cy="simulation-generate"
        >
          {isGenerating ? "Génération..." : "Générer les commentaires"}
        </Button>
      </form>

      {generatedComments && generatedComments.length > 0 && (
        <div className="space-y-4">
          <CollapsibleSection
            title={`${generatedComments.length} commentaire${generatedComments.length > 1 ? "s" : ""
              } généré${generatedComments.length > 1 ? "s" : ""}`}
          >
            <ul className="space-y-2">
              {generatedComments.map((comment) => (
                <li
                  key={comment.id}
                  className="rounded-md bg-background-100 p-3 text-small text-foreground"
                >
                  {comment.text}
                </li>
              ))}
            </ul>
          </CollapsibleSection>

          <div className="flex flex-wrap items-end gap-4">
            <div className="space-y-2">
              <Label htmlFor="model">Modèle à utiliser</Label>
              <Select
                value={model}
                onValueChange={(value) =>
                  setModel(value as "both" | "logistic_regression" | "random_forest")
                }
              >
                <SelectTrigger
                  id="model"
                  className="w-56"
                  data-cy="simulation-model"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {modelOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              data-cy="simulation-analyze"
            >
              {isAnalyzing
                ? "Analyse en cours..."
                : latestBatch
                  ? "Réanalyser les commentaires"
                  : "Analyser les commentaires"}
            </Button>
          </div>
        </div>
      )}

      {isAnalyzing && (
        <p className="text-muted-foreground">Analyse du lot en cours...</p>
      )}

      {latestBatch && (
        <div className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-subtitle-2 font-semibold">
              Résultats de l’analyse
            </h2>
            <Button
              asChild
              variant="outline"
              data-cy="simulation-dashboard-link"
            >
              <Link href="/tableau-de-bord">Voir le tableau de bord</Link>
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {latestBatch.response.results.map((comment) => (
              <CommentCard
                key={comment.id}
                comment={comment}
                model={latestBatch.model}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
