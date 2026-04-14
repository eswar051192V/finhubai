"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2, Search, TrendingDown, TrendingUp, Volume2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiGet } from "@/lib/api";

interface ScanResult {
  symbol: string;
  name: string;
  last: number | null;
  change_pct: number | null;
  volume_ratio: number | null;
  pe: number | null;
  market_cap: number | null;
}

interface ScanResponse {
  scanned: number;
  top_gainers: ScanResult[];
  top_losers: ScanResult[];
  unusual_volume: ScanResult[];
}

function fmt(v: number | null): string {
  if (v == null) return "--";
  return v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function Row({ r }: { r: ScanResult }) {
  const up = (r.change_pct ?? 0) >= 0;
  return (
    <Link
      href={`/markets/${encodeURIComponent(r.symbol)}`}
      className="flex items-center justify-between rounded-md px-3 py-2.5 hover:bg-accent/60"
    >
      <div className="min-w-0">
        <p className="text-sm font-medium">{r.name}</p>
        <p className="text-xs text-muted-foreground">{r.symbol}</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="font-mono text-sm">{fmt(r.last)}</span>
        {r.change_pct != null && (
          <span className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-xs font-medium ${up ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400"}`}>
            {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {up ? "+" : ""}{r.change_pct.toFixed(2)}%
          </span>
        )}
        {r.volume_ratio != null && r.volume_ratio > 1.5 && (
          <Badge variant="outline" className="text-[10px]">
            <Volume2 className="mr-0.5 h-3 w-3" /> {r.volume_ratio}x vol
          </Badge>
        )}
      </div>
    </Link>
  );
}

export default function ScreenerPage() {
  const [data, setData] = useState<ScanResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const runScan = () => {
    setLoading(true);
    apiGet<ScanResponse>("/api/screener?top_n=10")
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Morning Scanner</h1>
          <p className="text-muted-foreground">
            Scan NIFTY 50 for top movers, losers, and unusual volume.
          </p>
        </div>
        <Button onClick={runScan} disabled={loading}>
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
          {loading ? "Scanning..." : "Run scan"}
        </Button>
      </div>

      {data && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-emerald-400">Top Gainers</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-border/40">
              {data.top_gainers.map((r) => <Row key={r.symbol} r={r} />)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-red-400">Top Losers</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-border/40">
              {data.top_losers.map((r) => <Row key={r.symbol} r={r} />)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-blue-400">Unusual Volume</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-border/40">
              {data.unusual_volume.length > 0 ? (
                data.unusual_volume.map((r) => <Row key={r.symbol} r={r} />)
              ) : (
                <p className="py-6 text-center text-sm text-muted-foreground">No unusual volume detected</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {data && (
        <p className="text-sm text-muted-foreground">
          Scanned {data.scanned} stocks from NIFTY universe.
        </p>
      )}
    </div>
  );
}
