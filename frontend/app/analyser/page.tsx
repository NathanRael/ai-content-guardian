"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { TranslationNotice } from "@/components/shared/moderation/translation-notice";
import { RecommendationBanner } from "@/components/shared/moderation/recommendation-banner";
import { ModelComparisonPanel } from "@/components/shared/moderation/model-comparison-panel";
import { ExplanationPanel } from "@/components/shared/moderation/explanation-panel";
import { CollapsibleSection } from "@/components/shared/moderation/collapsible-section";
import { useAnalyzeComment } from "@/features/moderation/hooks/use-analyze-comment";
import { ApiError } from "@/lib/api-client";

export default function AnalyzePage() {
  const [text, setText] = useState("");
  const { mutateAsync, data, isPending, reset } = useAnalyzeComment();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    reset();
    try {
      await mutateAsync(text.trim());
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : "Une erreur est survenue lors de l'analyse.",
      );
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-subtitle font-semibold">Analyser un commentaire</h1>
        <p className="text-muted-foreground">
          Saisissez un texte pour obtenir une analyse des deux modèles.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Collez le commentaire à analyser..."
          rows={5}
          data-cy="analyze-textarea"
        />
        <Button
          type="submit"
          disabled={isPending || !text.trim()}
          data-cy="analyze-submit"
        >
          {isPending ? "Analyse en cours..." : "Analyser"}
        </Button>
      </form>

      {data && (
        <div className="space-y-6">
          <div className="rounded-lg border border-background-200 bg-background-100 p-4">
            <p className="text-small text-muted-foreground mb-1">Texte analysé</p>
            <p className="text-foreground">{data.original_text}</p>
          </div>

          {data.translated_text && (
            <TranslationNotice
              language={data.detected_language}
              translatedText={data.translated_text}
            />
          )}

          <RecommendationBanner
            recommendation={data.recommendation}
            reason={data.recommendation_reason}
          />

          <ModelComparisonPanel result={data} />

          <CollapsibleSection title="Voir le détail">
            <ExplanationPanel
              explanation={data.explanation}
              dialectMarkerScore={data.dialect_marker_score}
            />
          </CollapsibleSection>
        </div>
      )}
    </div>
  );
}
