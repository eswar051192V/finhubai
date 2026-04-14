"use client";

import { useState } from "react";
import { Loader2, Target } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet } from "@/lib/api";

interface GoNoGoResult {
  symbol: string;
  composite_score: number;
  signal: string;
  last_price: number | null;
  breakdown: Record<string, { score: number; reasons: string[] }>;
  error?: string;
}

function signalColor(s: string): string {
  if (s.includes("STRONG GO")) return "bg-emerald-500/20 text-emerald-400";
  if (s === "GO") return "bg-emerald-500/15 text-emerald-300";
  if (s === "BORDERLINE") return "bg-yellow-500/15 text-yellow-400";
  if (s === "NO-GO") return "bg-red-500/15 text-red-300";
  return "bg-red-500/20 text-red-400";
}

export default function GoNoGoPage() {
  const [symbol, setSymbol] = useState("");
  const [data, setData] = useState<GoNoGoResult | null>(null);
  const [loading, setLoading] = useState(false);

  const run = () => {
    if (!symbol.trim()) return;
    setLoading(true);
    setData(null);
    apiGet<GoNoGoResult>(`/api/gonogo/${encodeURIComponent(symbol.trim())}`)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <div className="flex items-center gap-2 text-primary">
          <Target className="h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">GO / NO-GO Signal</h1>
        </div>
        <p className="mt-1 text-muted-foreground">
          Composite 0-100 score combining valuation, technicals, fundamentals,
          sentiment, option chain, and macro signals.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-end">
          <div className="flex-1 space-y-1.5">
            <Label htmlFor="sym">Symbol</Label>
            <Input
              id="sym"
              placeholder="e.g. RELIANCE.NS, AAPL, TCS.NS"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && run()}
            />
          </div>
          <Button onClick={run} disabled={loading || !symbol.trim()}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Analyze
          </Button>
        </CardContent>
      </Card>

      {data && !data.error && (
        <div className="space-y-4">
          <Card>
            <CardContent className="flex items-center justify-between pt-6">
              <div>
                <p className="text-sm text-muted-foreground">{data.symbol}</p>
                <p className="text-4xl font-bold tabular-nums">{data.composite_score}</p>
              </div>
              <Badge className={`text-lg px-4 py-2 ${signalColor(data.signal)}`}>
                {data.signal}
              </Badge>
            </CardContent>
          </Card>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(data.breakdown).map(([key, val]) => (
              <Card key={key}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm capitalize">{key.replace("_", " ")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-semibold tabular-nums">{val.score.toFixed(0)}</p>
                  {val.reasons.length > 0 && (
                    <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {val.reasons.map((r, i) => <li key={i}>• {r}</li>)}
                    </ul>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {data?.error && (
        <p className="text-sm text-red-400">Error: {data.error}</p>
      )}
    </div>
  );
}
