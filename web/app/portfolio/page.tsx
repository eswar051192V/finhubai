"use client";

import { useState } from "react";
import { Loader2, PieChart, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiPost } from "@/lib/api";

interface RiskResult {
  annual_return_pct: number;
  annual_volatility_pct: number;
  sharpe_ratio: number;
  stress_scenarios: Record<string, number>;
  symbols: string[];
  weights: number[];
  error?: string;
}

interface RetirementResult {
  years_to_retirement: number;
  projected_corpus: number;
  corpus_needed: number;
  surplus_or_deficit: number;
  on_track: boolean;
  monthly_need_at_retirement: number;
  error?: string;
}

function fmtBig(v: number): string {
  if (v >= 1e7) return `₹${(v / 1e7).toFixed(1)} Cr`;
  if (v >= 1e5) return `₹${(v / 1e5).toFixed(1)} L`;
  return `₹${v.toLocaleString()}`;
}

export default function PortfolioPage() {
  const [tab, setTab] = useState<"risk" | "retire">("risk");
  const [symbolsInput, setSymbolsInput] = useState("RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS");
  const [riskData, setRiskData] = useState<RiskResult | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);

  const [age, setAge] = useState("30");
  const [retireAge, setRetireAge] = useState("60");
  const [corpus, setCorpus] = useState("500000");
  const [sip, setSip] = useState("25000");
  const [retireData, setRetireData] = useState<RetirementResult | null>(null);
  const [retireLoading, setRetireLoading] = useState(false);

  const runRisk = () => {
    setRiskLoading(true);
    const symbols = symbolsInput.split(",").map((s) => s.trim()).filter(Boolean);
    const holdings = symbols.map((s) => ({ symbol: s, weight: 1 / symbols.length }));
    apiPost<RiskResult>("/api/portfolio/risk", { holdings })
      .then(setRiskData)
      .catch(() => {})
      .finally(() => setRiskLoading(false));
  };

  const runRetire = () => {
    setRetireLoading(true);
    apiPost<RetirementResult>("/api/portfolio/retirement", {
      current_age: +age,
      retirement_age: +retireAge,
      current_corpus: +corpus,
      monthly_sip: +sip,
    })
      .then(setRetireData)
      .catch(() => {})
      .finally(() => setRetireLoading(false));
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Portfolio Intelligence</h1>
        <p className="text-muted-foreground">
          Risk analysis, stress testing, and retirement planning.
        </p>
      </div>

      <div className="flex gap-2">
        <Button variant={tab === "risk" ? "default" : "outline"} size="sm" onClick={() => setTab("risk")}>
          <PieChart className="mr-2 h-4 w-4" /> Risk Analysis
        </Button>
        <Button variant={tab === "retire" ? "default" : "outline"} size="sm" onClick={() => setTab("retire")}>
          <TrendingUp className="mr-2 h-4 w-4" /> Retirement Planner
        </Button>
      </div>

      {tab === "risk" && (
        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-3 pt-6">
              <div>
                <Label>Symbols (comma-separated)</Label>
                <Input value={symbolsInput} onChange={(e) => setSymbolsInput(e.target.value)} />
              </div>
              <Button onClick={runRisk} disabled={riskLoading}>
                {riskLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Analyze risk
              </Button>
            </CardContent>
          </Card>

          {riskData && !riskData.error && (
            <div className="grid gap-3 sm:grid-cols-3">
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Annual Return</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold">{riskData.annual_return_pct.toFixed(1)}%</p></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Volatility</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold">{riskData.annual_volatility_pct.toFixed(1)}%</p></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Sharpe Ratio</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold">{riskData.sharpe_ratio.toFixed(2)}</p></CardContent>
              </Card>
              <Card className="sm:col-span-3">
                <CardHeader className="pb-2"><CardTitle className="text-sm">Stress Scenarios</CardTitle></CardHeader>
                <CardContent className="flex flex-wrap gap-4">
                  {Object.entries(riskData.stress_scenarios).map(([k, v]) => (
                    <div key={k} className="text-sm">
                      <span className="text-muted-foreground">{k.replace(/_/g, " ")}:</span>{" "}
                      <span className={v < 0 ? "text-red-400 font-medium" : "text-emerald-400 font-medium"}>{v.toFixed(1)}%</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}
          {riskData?.error && <p className="text-sm text-red-400">{riskData.error}</p>}
        </div>
      )}

      {tab === "retire" && (
        <div className="space-y-4">
          <Card>
            <CardContent className="grid gap-3 pt-6 sm:grid-cols-2">
              <div><Label>Current Age</Label><Input value={age} onChange={(e) => setAge(e.target.value)} type="number" /></div>
              <div><Label>Retirement Age</Label><Input value={retireAge} onChange={(e) => setRetireAge(e.target.value)} type="number" /></div>
              <div><Label>Current Corpus (₹)</Label><Input value={corpus} onChange={(e) => setCorpus(e.target.value)} type="number" /></div>
              <div><Label>Monthly SIP (₹)</Label><Input value={sip} onChange={(e) => setSip(e.target.value)} type="number" /></div>
              <Button onClick={runRetire} disabled={retireLoading} className="sm:col-span-2">
                {retireLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Calculate
              </Button>
            </CardContent>
          </Card>

          {retireData && !retireData.error && (
            <div className="grid gap-3 sm:grid-cols-2">
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Projected Corpus</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold text-emerald-400">{fmtBig(retireData.projected_corpus)}</p></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Corpus Needed</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold">{fmtBig(retireData.corpus_needed)}</p></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Surplus / Deficit</CardTitle></CardHeader>
                <CardContent>
                  <p className={`text-2xl font-bold ${retireData.on_track ? "text-emerald-400" : "text-red-400"}`}>
                    {retireData.surplus_or_deficit > 0 ? "+" : ""}{fmtBig(retireData.surplus_or_deficit)}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Monthly Need at Retirement</CardTitle></CardHeader>
                <CardContent><p className="text-2xl font-bold">{fmtBig(retireData.monthly_need_at_retirement)}</p></CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
