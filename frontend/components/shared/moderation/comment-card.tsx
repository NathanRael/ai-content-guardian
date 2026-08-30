"use client";

import { useState } from "react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { BatchAnalysisResult } from "@/types/moderation";

import { ConfidenceBar } from "./confidence-bar";
import { LabelBadge } from "./label-helpers";
import { ModelComparisonPanel } from "./model-comparison-panel";
import { RecommendationBanner } from "./recommendation-banner";
import { TranslationNotice } from "./translation-notice";
import { ExplanationPanel } from "./explanation-panel";
import { CollapsibleSection } from "./collapsible-section";

interface CommentCardProps {
  comment: BatchAnalysisResult;
}

export function CommentCard({ comment }: CommentCardProps) {
  const [open, setOpen] = useState(false);
  const hasTranslation = comment.translated_text !== null;

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-4">
          <p className="line-clamp-2 text-foreground">{comment.original_text}</p>
          <LabelBadge label={comment.logistic_regression.label} />
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <ConfidenceBar
          value={comment.logistic_regression.confidence}
          label={comment.logistic_regression.label}
        />
      </CardContent>
      <CardFooter className="pt-0">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="ml-auto"
              data-cy="comment-card-detail"
            >
              Voir le détail
            </Button>
          </DialogTrigger>
          <DialogContent className="max-h-[90vh] max-w-4xl overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Détail de l’analyse</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              <div className="rounded-lg border border-background-200 bg-background-100 p-4">
                <p className="text-small text-muted-foreground mb-1">Texte analysé</p>
                <p className="text-foreground">{comment.original_text}</p>
              </div>

              {hasTranslation && comment.translated_text && (
                <TranslationNotice
                  language={comment.detected_language}
                  translatedText={comment.translated_text}
                />
              )}

              <RecommendationBanner
                recommendation={comment.recommendation}
                reason={comment.recommendation_reason}
              />

              <ModelComparisonPanel result={comment} />

              <CollapsibleSection title="Voir le détail">
                <ExplanationPanel
                  explanation={comment.explanation}
                  dialectMarkerScore={comment.dialect_marker_score}
                />
              </CollapsibleSection>
            </div>
          </DialogContent>
        </Dialog>
      </CardFooter>
    </Card>
  );
}
