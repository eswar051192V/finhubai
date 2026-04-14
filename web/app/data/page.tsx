"use client";

import { useEffect, useState } from "react";
import {
  Bot,
  CheckCircle2,
  Cloud,
  Database,
  Download,
  Loader2,
  Send,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiGet, apiPost } from "@/lib/api";

interface ApiStatus {
  fred: boolean;
  alpha_vantage: boolean;
  twelve_data: boolean;
  polygon: boolean;
  tiingo: boolean;
  finnhub: boolean;
  marketaux: boolean;
  newsapi: boolean;
  upstox: boolean;
  ollama: boolean;
}

interface TaskInfo {
  status: string;
  detail: string;
  timestamp: string;
}

interface Progress {
  running: boolean;
  started_at: string | null;
  tasks: Record<string, TaskInfo>;
  completed: number;
  total: number;
  errors: string[];
  finished_at?: string;
}

interface AiStatus {
  available: boolean;
  models?: string[];
  error?: string;
}

interface AiResponse {
  model: string;
  response?: string;
  error?: string;
}

function StatusDot({ ok }: { ok: boolean }) {
  return ok ? (
    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
  ) : (
    <XCircle className="h-4 w-4 text-muted-foreground/50" />
  );
}

export default function DataPage() {
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [aiStatus, setAiStatus] = useState<AiStatus | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState<AiResponse | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [pullingModel, setPullingModel] = useState(false);

  useEffect(() => {
    apiGet<ApiStatus>("/api/data/api-status").then(setApiStatus).catch(() => {});
    apiGet<AiStatus>("/api/ai/status").then(setAiStatus).catch(() => {});
  }, []);

  useEffect(() => {
    if (!downloading) return;
    const interval = setInterval(() => {
      apiGet<Progress>("/api/data/progress")
        .then((p) => {
          setProgress(p);
          if (!p.running && p.finished_at) {
            setDownloading(false);
          }
        })
        .catch(() => {});
    }, 2000);
    return () => clearInterval(interval);
  }, [downloading]);

  const startDownload = () => {
    setDownloading(true);
    setProgress(null);
    apiPost<{ status: string }>("/api/data/download", {})
      .then(() => {})
      .catch(() => setDownloading(false));
  };

  const pullModel = (model: string) => {
    setPullingModel(true);
    apiPost<{ status: string }>("/api/ai/pull", { model })
      .then(() => {
        apiGet<AiStatus>("/api/ai/status").then(setAiStatus).catch(() => {});
      })
      .catch(() => {})
      .finally(() => setPullingModel(false));
  };

  const sendChat = () => {
    if (!aiPrompt.trim()) return;
    setAiLoading(true);
    setAiResponse(null);
    apiPost<AiResponse>("/api/ai/chat", { prompt: aiPrompt })
      .then(setAiResponse)
      .catch(() => {})
      .finally(() => setAiLoading(false));
  };

  const configuredCount = apiStatus
    ? Object.values(apiStatus).filter(Boolean).length
    : 0;

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-primary">
          <Database className="h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">
            Data & AI Center
          </h1>
        </div>
        <p className="mt-1 text-muted-foreground">
          Download all market data, company fundamentals, and manage your local
          AI assistant.
        </p>
      </div>

      {/* API Status */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Cloud className="h-4 w-4" />
            API Sources ({configuredCount}/10 connected)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {apiStatus ? (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
              {Object.entries(apiStatus).map(([key, ok]) => (
                <div
                  key={key}
                  className="flex items-center gap-2 rounded-md border border-border/60 px-3 py-2"
                >
                  <StatusDot ok={ok} />
                  <span className="text-sm capitalize">
                    {key.replace(/_/g, " ")}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading...</p>
          )}
        </CardContent>
      </Card>

      {/* Download Data */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              <Download className="h-4 w-4" />
              Download All Market Data
            </CardTitle>
            <Button onClick={startDownload} disabled={downloading}>
              {downloading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              {downloading ? "Downloading..." : "Download Everything"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-sm text-muted-foreground">
            Downloads: NIFTY 50 (1Y), S&P 500 Top 50 (1Y), Crypto Top 11,
            Commodities & Forex, FRED Macro (15 indicators), News from all
            sources, Polygon reference data, Twelve Data instruments, Alpha
            Vantage fundamentals.
          </p>

          {progress && (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="h-2 flex-1 rounded-full bg-secondary">
                  <div
                    className="h-2 rounded-full bg-primary transition-all"
                    style={{
                      width: `${
                        progress.total > 0
                          ? (progress.completed / progress.total) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
                <span className="text-sm font-mono text-muted-foreground">
                  {progress.completed}/{progress.total}
                </span>
              </div>

              <div className="max-h-64 space-y-1 overflow-auto">
                {Object.entries(progress.tasks).map(([name, info]) => (
                  <div
                    key={name}
                    className="flex items-center justify-between rounded px-2 py-1.5 text-sm"
                  >
                    <div className="flex items-center gap-2">
                      {info.status === "done" ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      ) : (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                      )}
                      <span>{name}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {info.detail}
                    </span>
                  </div>
                ))}
              </div>

              {progress.errors.length > 0 && (
                <div className="rounded-md bg-red-500/10 p-3">
                  <p className="text-sm font-medium text-red-400">
                    {progress.errors.length} errors
                  </p>
                  <ul className="mt-1 max-h-32 overflow-auto text-xs text-red-300">
                    {progress.errors.slice(0, 20).map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}

              {!progress.running && progress.finished_at && (
                <Badge
                  variant="outline"
                  className="bg-emerald-500/10 text-emerald-400"
                >
                  Download complete
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Ollama AI */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-4 w-4" />
            Local AI Assistant (Ollama)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <StatusDot ok={aiStatus?.available ?? false} />
            <span className="text-sm">
              {aiStatus?.available
                ? `Ollama running — models: ${aiStatus.models?.join(", ") || "none"}`
                : "Ollama not running — start with: ollama serve"}
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => pullModel("llama3.1:8b")}
              disabled={pullingModel}
            >
              {pullingModel && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
              Pull llama3.1:8b
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => pullModel("nomic-embed-text")}
              disabled={pullingModel}
            >
              {pullingModel && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
              Pull nomic-embed-text
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                apiGet<AiStatus>("/api/ai/status")
                  .then(setAiStatus)
                  .catch(() => {})
              }
            >
              Refresh status
            </Button>
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Ask anything about markets, stocks, tax..."
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
              className="flex-1"
            />
            <Button onClick={sendChat} disabled={aiLoading || !aiPrompt.trim()}>
              {aiLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {aiResponse && (
            <div className="rounded-md border border-border/60 bg-card/80 p-4">
              {aiResponse.error ? (
                <p className="text-sm text-red-400">{aiResponse.error}</p>
              ) : (
                <div className="space-y-2">
                  <Badge variant="outline" className="text-[10px]">
                    {aiResponse.model}
                  </Badge>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
                    {aiResponse.response}
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
