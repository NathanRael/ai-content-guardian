export type ModerationLabel = "hate_speech" | "offensive" | "neutral";

export interface ModelPrediction {
  label: ModerationLabel;
  confidence: number;
}

export interface ExplanationWord {
  word: string;
  weight: number;
}

export interface Explanation {
  method: "lime";
  top_words: ExplanationWord[];
}

export interface AnalysisResult {
  original_text: string;
  detected_language: string;
  translated_text: string | null;
  logistic_regression: ModelPrediction;
  random_forest: ModelPrediction;
  models_agree: boolean;
  dialect_marker_score: number;
  recommendation: "auto_flag_possible" | "human_review_required";
  recommendation_reason: string;
  explanation: Explanation;
}

export interface BatchAnalysisResult extends AnalysisResult {
  id: string;
}

export interface BatchSummary {
  total: number;
  safe: number;
  offensive: number;
  hate_speech: number;
  risk_level: "low" | "medium" | "high";
}

export interface BatchAnalysisResponse {
  results: BatchAnalysisResult[];
  summary: BatchSummary;
}

export interface GeneratedComment {
  id: string;
  text: string;
}

export interface GenerateCommentsResponse {
  comments: GeneratedComment[];
}

export interface PerClassMetrics {
  precision: number;
  recall: number;
  f1_score: number;
  support: number;
}

export interface ModelMetrics {
  accuracy: number;
  per_class: Record<ModerationLabel, PerClassMetrics>;
  confusion_matrix: number[][];
}

export interface MetricsResponse {
  logistic_regression: ModelMetrics;
  random_forest: ModelMetrics;
  edge_cases: EdgeCase[];
}

export interface EdgeCase {
  case_type: string;
  example_text: string;
  prediction: {
    logistic_regression: ModelPrediction;
    random_forest: ModelPrediction;
  };
  note: string;
}

export interface ExamplePairPredictions {
  logistic_regression: ModelPrediction;
  random_forest: ModelPrediction;
}

export interface ExamplePair {
  standard: string;
  dialect_variant: string;
  prediction_standard: ExamplePairPredictions;
  prediction_variant: ExamplePairPredictions;
}

export interface BiasAuditResponse {
  methodology_note: string;
  flag_rate_high_dialect_markers: number;
  flag_rate_low_dialect_markers: number;
  gap: number;
  example_pairs: ExamplePair[];
}

export interface TrainingDataSummary {
  source: string;
  size: number;
  class_distribution: Record<string, number>;
}

export interface ModelInfoResponse {
  intended_use: string;
  not_intended_for: string[];
  known_limitations: string[];
  human_role: string;
  training_data_summary: TrainingDataSummary;
}
