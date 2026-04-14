"use client";

import { useState } from "react";
import { Calculator, Loader2, Scale } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiPost } from "@/lib/api";

interface TaxComputeResult {
  treatment: string;
  gross_gain: number;
  tax_amount: number;
  effective_rate: number;
  breakdown: Record<string, number>;
  notes: string[];
}

interface USTaxResult {
  gain_inr: number;
  treatment: string;
  gain_tax_inr: number;
  ftc_inr: number;
  total_tax_inr: number;
  notes: string[];
}

interface CumulativeResult {
  total_gain: number;
  total_tax: number;
  effective_rate: number;
  by_treatment: Record<string, number>;
  advance_tax_schedule: Record<string, number>;
}

function fmtINR(v: number): string {
  return `₹${v.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

const TREATMENTS = [
  { value: "india_stcg_equity", label: "STCG Equity (20%)" },
  { value: "india_ltcg_equity", label: "LTCG Equity (12.5%)" },
  { value: "india_business_fo", label: "F&O Business Income" },
  { value: "india_speculative", label: "Speculative (Intraday)" },
  { value: "india_debt", label: "Debt MF / Bonds" },
  { value: "india_crypto", label: "Crypto (30% flat)" },
];

export default function TaxPage() {
  const [tab, setTab] = useState<"compute" | "us" | "cumulative">("compute");
  const [gain, setGain] = useState("100000");
  const [treatment, setTreatment] = useState("india_stcg_equity");
  const [taxResult, setTaxResult] = useState<TaxComputeResult | null>(null);

  const [usGain, setUsGain] = useState("1000");
  const [usDays, setUsDays] = useState("400");
  const [usDiv, setUsDiv] = useState("200");
  const [usResult, setUsResult] = useState<USTaxResult | null>(null);

  const [cumInput, setCumInput] = useState(
    JSON.stringify([
      { gain: 50000, treatment: "india_stcg_equity" },
      { gain: 200000, treatment: "india_ltcg_equity" },
      { gain: 30000, treatment: "india_business_fo" },
    ], null, 2)
  );
  const [cumResult, setCumResult] = useState<CumulativeResult | null>(null);
  const [loading, setLoading] = useState(false);

  const computeTax = () => {
    setLoading(true);
    apiPost<TaxComputeResult>("/api/tax/compute", { gain: +gain, treatment })
      .then(setTaxResult)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const computeUS = () => {
    setLoading(true);
    apiPost<USTaxResult>("/api/tax/us-india", { gain_usd: +usGain, holding_days: +usDays, dividend_usd: +usDiv })
      .then(setUsResult)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const computeCum = () => {
    setLoading(true);
    try {
      const txns = JSON.parse(cumInput);
      apiPost<CumulativeResult>("/api/tax/cumulative", { transactions: txns })
        .then(setCumResult)
        .catch(() => {})
        .finally(() => setLoading(false));
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <div className="flex items-center gap-2 text-primary">
          <Scale className="h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">Tax Intelligence</h1>
        </div>
        <p className="mt-1 text-muted-foreground">
          India multi-asset tax computation, US cross-border taxation, and cumulative tax bill.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button variant={tab === "compute" ? "default" : "outline"} size="sm" onClick={() => setTab("compute")}>
          <Calculator className="mr-1 h-4 w-4" /> India Tax
        </Button>
        <Button variant={tab === "us" ? "default" : "outline"} size="sm" onClick={() => setTab("us")}>US ↔ India</Button>
        <Button variant={tab === "cumulative" ? "default" : "outline"} size="sm" onClick={() => setTab("cumulative")}>Cumulative Bill</Button>
      </div>

      {tab === "compute" && (
        <Card>
          <CardContent className="space-y-4 pt-6">
            <div className="grid gap-3 sm:grid-cols-2">
              <div><Label>Gain (₹)</Label><Input type="number" value={gain} onChange={(e) => setGain(e.target.value)} /></div>
              <div>
                <Label>Type</Label>
                <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={treatment} onChange={(e) => setTreatment(e.target.value)}>
                  {TREATMENTS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
            </div>
            <Button onClick={computeTax} disabled={loading}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Compute Tax</Button>
            {taxResult && (
              <div className="grid gap-3 sm:grid-cols-3 pt-3">
                <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Tax Amount</CardTitle></CardHeader>
                  <CardContent><p className="text-2xl font-bold text-red-400">{fmtINR(taxResult.tax_amount)}</p></CardContent></Card>
                <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Effective Rate</CardTitle></CardHeader>
                  <CardContent><p className="text-2xl font-bold">{(taxResult.effective_rate * 100).toFixed(1)}%</p></CardContent></Card>
                <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Net Gain</CardTitle></CardHeader>
                  <CardContent><p className="text-2xl font-bold text-emerald-400">{fmtINR(taxResult.gross_gain - taxResult.tax_amount)}</p></CardContent></Card>
                {taxResult.notes.length > 0 && (
                  <div className="sm:col-span-3 text-sm text-muted-foreground">
                    {taxResult.notes.map((n, i) => <p key={i}>→ {n}</p>)}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "us" && (
        <Card>
          <CardContent className="space-y-4 pt-6">
            <div className="grid gap-3 sm:grid-cols-3">
              <div><Label>Capital Gain ($)</Label><Input type="number" value={usGain} onChange={(e) => setUsGain(e.target.value)} /></div>
              <div><Label>Holding Days</Label><Input type="number" value={usDays} onChange={(e) => setUsDays(e.target.value)} /></div>
              <div><Label>Dividends ($)</Label><Input type="number" value={usDiv} onChange={(e) => setUsDiv(e.target.value)} /></div>
            </div>
            <Button onClick={computeUS} disabled={loading}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Compute US Tax</Button>
            {usResult && (
              <div className="space-y-3 pt-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Total India Tax</CardTitle></CardHeader>
                    <CardContent><p className="text-2xl font-bold text-red-400">{fmtINR(usResult.total_tax_inr)}</p></CardContent></Card>
                  <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">FTC Available</CardTitle></CardHeader>
                    <CardContent><p className="text-2xl font-bold text-emerald-400">{fmtINR(usResult.ftc_inr)}</p></CardContent></Card>
                </div>
                <Badge variant="outline">{usResult.treatment}</Badge>
                {usResult.notes.map((n, i) => <p key={i} className="text-sm text-muted-foreground">→ {n}</p>)}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "cumulative" && (
        <Card>
          <CardContent className="space-y-4 pt-6">
            <div><Label>Transactions (JSON array)</Label>
              <textarea className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono" value={cumInput} onChange={(e) => setCumInput(e.target.value)} />
            </div>
            <Button onClick={computeCum} disabled={loading}>{loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Compute Cumulative</Button>
            {cumResult && (
              <div className="space-y-3 pt-3">
                <div className="grid gap-3 sm:grid-cols-3">
                  <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Total Gain</CardTitle></CardHeader>
                    <CardContent><p className="text-xl font-bold">{fmtINR(cumResult.total_gain)}</p></CardContent></Card>
                  <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Total Tax</CardTitle></CardHeader>
                    <CardContent><p className="text-xl font-bold text-red-400">{fmtINR(cumResult.total_tax)}</p></CardContent></Card>
                  <Card><CardHeader className="pb-1"><CardTitle className="text-xs text-muted-foreground">Effective Rate</CardTitle></CardHeader>
                    <CardContent><p className="text-xl font-bold">{(cumResult.effective_rate * 100).toFixed(1)}%</p></CardContent></Card>
                </div>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Advance Tax Schedule</CardTitle></CardHeader>
                  <CardContent className="grid grid-cols-4 gap-2">
                    {Object.entries(cumResult.advance_tax_schedule).map(([k, v]) => (
                      <div key={k} className="text-center">
                        <p className="text-xs text-muted-foreground">{k.replace("_", " ").toUpperCase()}</p>
                        <p className="font-mono font-medium">{fmtINR(v)}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
