"use client";

import { useState } from "react";
import { BookOpen, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiPost, apiGet } from "@/lib/api";

interface ThesisResult {
  symbol: string;
  thesis_score: number;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  scenarios: Record<string, { description: string; target: number | null; probability: string }>;
  error?: string;
}

interface MgmtResult {
  symbol: string;
  name: string | null;
  score: number;
  grade: string;
  positives: string[];
  flags: string[];
  error?: string;
}

interface EarningsResult {
  symbol: string;
  name: string | null;
  upcoming_earnings: string[] | null;
  strategy_hints: string[];
  recommendation: string;
  error?: string;
}

export default function ResearchPage() {
  const [tab, setTab] = useState<"thesis" | "mgmt" | "earnings">("thesis");
  const [symbol, setSymbol] = useState("");
  const [thesis, setThesis] = useState("");
  const [thesisData, setThesisData] = useState<ThesisResult | null>(null);
  const [mgmtData, setMgmtData] = useState<MgmtResult | null>(null);
  const [earningsData, setEarningsData] = useState<EarningsResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runThesis = () => {
    setLoading(true);
    apiPost<ThesisResult>("/api/research/thesis", { symbol, thesis, thesis_type: "bullish" })
      .then(setThesisData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const runMgmt = () => {
    setLoading(true);
    apiGet<MgmtResult>(`/api/management/${encodeURIComponent(symbol)}`)
      .then(setMgmtData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const runEarnings = () => {
    setLoading(true);
    apiGet<EarningsResult>(`/api/earnings/${encodeURIComponent(symbol)}`)
      .then(setEarningsData)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const gradeColor = (g: string) => {
    if (g === "A") return "bg-emerald-500/20 text-emerald-400";
    if (g === "B") return "bg-blue-500/20 text-blue-400";
    if (g === "C") return "bg-yellow-500/20 text-yellow-400";
    return "bg-red-500/20 text-red-400";
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <div className="flex items-center gap-2 text-primary">
          <BookOpen className="h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">Research Lab</h1>
        </div>
        <p className="mt-1 text-muted-foreground">Thesis evaluation, management quality, and earnings intelligence.</p>
      </div>

      <Card>
        <CardContent className="space-y-3 pt-6">
          <div><Label>Symbol</Label><Input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="e.g. RELIANCE.NS" /></div>
          <div className="flex flex-wrap gap-2">
            <Button variant={tab === "thesis" ? "default" : "outline"} size="sm" onClick={() => setTab("thesis")}>Thesis Check</Button>
            <Button variant={tab === "mgmt" ? "default" : "outline"} size="sm" onClick={() => setTab("mgmt")}>Management Quality</Button>
            <Button variant={tab === "earnings" ? "default" : "outline"} size="sm" onClick={() => setTab("earnings")}>Earnings Intel</Button>
          </div>
        </CardContent>
      </Card>

      {tab === "thesis" && (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <div><Label>Your Thesis</Label><Input value={thesis} onChange={(e) => setThesis(e.target.value)} placeholder="e.g. Jio and retail will drive 20% CAGR" /></div>
            <Button onClick={runThesis} disabled={loading || !symbol}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Evaluate
            </Button>
            {thesisData && !thesisData.error && (
              <div className="space-y-3 pt-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold">{thesisData.thesis_score}</span>
                  <span className="text-muted-foreground">/ 100 thesis strength</span>
                </div>
                {thesisData.supporting_evidence.length > 0 && (
                  <div><p className="text-sm font-medium text-emerald-400">Supporting</p><ul className="mt-1 space-y-1 text-sm text-muted-foreground">{thesisData.supporting_evidence.map((e, i) => <li key={i}>✓ {e}</li>)}</ul></div>
                )}
                {thesisData.contradicting_evidence.length > 0 && (
                  <div><p className="text-sm font-medium text-red-400">Contradicting</p><ul className="mt-1 space-y-1 text-sm text-muted-foreground">{thesisData.contradicting_evidence.map((e, i) => <li key={i}>✗ {e}</li>)}</ul></div>
                )}
                <div className="grid gap-2 sm:grid-cols-3">
                  {Object.entries(thesisData.scenarios).map(([k, v]) => (
                    <Card key={k}><CardHeader className="pb-1"><CardTitle className="text-xs capitalize">{k} ({v.probability})</CardTitle></CardHeader>
                      <CardContent><p className="font-mono">{v.target != null ? `₹${v.target.toLocaleString()}` : "--"}</p><p className="text-xs text-muted-foreground">{v.description}</p></CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "mgmt" && (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <Button onClick={runMgmt} disabled={loading || !symbol}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Assess Management</Button>
            {mgmtData && !mgmtData.error && (
              <div className="space-y-3 pt-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold">{mgmtData.score.toFixed(0)}</span>
                  <Badge className={gradeColor(mgmtData.grade)}>Grade {mgmtData.grade}</Badge>
                </div>
                {mgmtData.positives.length > 0 && <ul className="text-sm text-muted-foreground">{mgmtData.positives.map((p, i) => <li key={i}>✓ {p}</li>)}</ul>}
                {mgmtData.flags.length > 0 && <ul className="text-sm text-red-300">{mgmtData.flags.map((f, i) => <li key={i}>⚠ {f}</li>)}</ul>}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "earnings" && (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <Button onClick={runEarnings} disabled={loading || !symbol}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Get Earnings Intel</Button>
            {earningsData && !earningsData.error && (
              <div className="space-y-3 pt-3">
                {earningsData.upcoming_earnings && (
                  <div><p className="text-sm font-medium">Upcoming Earnings</p>
                    <div className="flex gap-2 mt-1">{earningsData.upcoming_earnings.map((d) => <Badge key={d} variant="outline">{d}</Badge>)}</div>
                  </div>
                )}
                <div><p className="text-sm font-medium">Analyst Rating</p><Badge variant="outline" className="mt-1">{earningsData.recommendation}</Badge></div>
                {earningsData.strategy_hints.length > 0 && (
                  <div><p className="text-sm font-medium">Strategy Hints</p>
                    <ul className="mt-1 space-y-1 text-sm text-muted-foreground">{earningsData.strategy_hints.map((h, i) => <li key={i}>→ {h}</li>)}</ul>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
