"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet } from "@/lib/api";

export default function SentimentPage() {
  const [ticker, setTicker] = useState("RELIANCE.NS");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const path = `/api/sentiment/${encodeURIComponent(ticker.trim())}`;
      const data = await apiGet<Record<string, unknown>>(path);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Sentiment</h1>
        <p className="text-muted-foreground">
          FII/DII-weighted flow proxy, optional Finnhub headlines, FinBERT off by default.
        </p>
      </div>
      <Card className="border-border/80 bg-card/90">
        <CardHeader>
          <CardTitle>Ticker</CardTitle>
          <CardDescription>yfinance-style symbol (e.g. RELIANCE.NS, AAPL).</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1 space-y-2">
            <Label htmlFor="t">Ticker</Label>
            <Input id="t" value={ticker} onChange={(e) => setTicker(e.target.value)} />
          </div>
          <Button type="button" onClick={load} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Load
          </Button>
        </CardContent>
      </Card>
      {error && (
        <p className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      )}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Composite</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[28rem] overflow-auto rounded-lg bg-secondary/50 p-4 text-xs leading-relaxed">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
