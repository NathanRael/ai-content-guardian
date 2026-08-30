import {
  type AnalysisResult,
  type BatchAnalysisResponse,
  type BiasAuditResponse,
  type GenerateCommentsResponse,
  type GeneratedComment,
  type MetricsResponse,
  type ModelInfoResponse,
} from "@/types/moderation";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const getBaseUrl = () => {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    throw new ApiError(
      "L'URL de l'API n'est pas configurée (NEXT_PUBLIC_API_URL).",
    );
  }
  return url.replace(/\/$/, "");
};

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${getBaseUrl()}${path}`;

  try {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      ...options,
    });

    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as {
        detail?: string;
        message?: string;
      };
      throw new ApiError(
        body.detail ||
          body.message ||
          `Le service a renvoyé une erreur ${response.status}.`,
        response.status,
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      "Impossible de contacter le service d'analyse. Vérifiez votre connexion.",
    );
  }
}

export const analyzeComment = (text: string) =>
  request<AnalysisResult>("/analyze-comment", {
    method: "POST",
    body: JSON.stringify({ text }),
  });

export const generateComments = (topic: string, count: number) =>
  request<GenerateCommentsResponse>("/generate-comments", {
    method: "POST",
    body: JSON.stringify({ topic, count }),
  });

export const analyzeComments = (comments: GeneratedComment[]) =>
  request<BatchAnalysisResponse>("/analyze-comments", {
    method: "POST",
    body: JSON.stringify({ comments }),
  });

export const getMetrics = () => request<MetricsResponse>("/metrics");

export const getBiasAudit = () => request<BiasAuditResponse>("/bias-audit");

export const getModelInfo = () => request<ModelInfoResponse>("/model-info");
