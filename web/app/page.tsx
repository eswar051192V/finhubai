"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Calculator,
  Coins,
  Database,
  Globe,
  LineChart,
  PieChart,
  Scale,
  Search,
  Sparkles,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { apiGet } from "@/lib/api";
import type { PulseItem } from "@/lib/types";

const PULSE_LABELS: Record<string, { label: string; icon: string }> = {
  nifty50: { label: "NIFTY 50", icon: "IN" },
  sensex: { label: "SENSEX", icon: "IN" },
  sp500: { label: "S&P 500", icon: "US" },
  nasdaq: { label: "NASDAQ", icon: "US" },
  dow: { label: "DOW", icon: "US" },
  gold: { label: "Gold", icon: "AU" },
  silver: { label: "Silver", icon: "AG" },
  wti_crude: { label: "WTI Crude", icon: "OIL" },
  brent_crude: { label: "Brent", icon: "OIL" },
  natural_gas: { label: "Nat Gas", icon: "NG" },
  bitcoin: { label: "Bitcoin", icon: "BTC" },
  ethereum: { label: "Ethereum", icon: "ETH" },
  usdinr: { label: "USD/INR", icon: "FX" },
  eurusd: { label: "EUR/USD", icon: "FX" },
  us_10y: { label: "US 10Y", icon: "BD" },
  vix: { label: "VIX", icon: "VX" },
  dxy: { label: "DXY", icon: "DX" },
};

function fmt(val: number | null | undefined): string {
  if (val == null) return "--";
  return val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

const tiles = [
  { href: "/markets", title: "Markets", desc: "13 categories: India, US, energy, commodities, crypto, forex, bonds, REITs.", icon: Globe },
  { href: "/screener", title: "Screener", desc: "Morning scanner — top gainers, losers, and unusual volume.", icon: Search },
  { href: "/gonogo", title: "GO/NO-GO", desc: "Composite 0-100 signal combining valuation, technicals, and sentiment.", icon: Target },
  { href: "/portfolio", title: "Portfolio", desc: "Risk analysis, stress testing, and retirement planning.", icon: PieChart },
  { href: "/research", title: "Research", desc: "Thesis evaluation, management quality, and earnings intelligence.", icon: BookOpen },
  { href: "/tax", title: "Tax Engine", desc: "India multi-asset tax, US cross-border, cumulative tax bill.", icon: Scale },
  { href: "/cost", title: "True Cost", desc: "Brokerage, STT, charges across major brokers.", icon: Calculator },
  { href: "/options", title: "Option Chain", desc: "Max pain, PCR, OI change from NSE.", icon: LineChart },
  { href: "/sentiment", title: "Sentiment", desc: "FII/DII-weighted flow + news keywords.", icon: Sparkles },
  { href: "/markets/metals", title: "Gold & Silver", desc: "City-wise metal prices across 15 Indian cities.", icon: Coins },
  { href: "/wiki", title: "Wiki", desc: "37 reference articles on every asset class and trading concept.", icon: BookOpen },
  { href: "/data", title: "Data & AI", desc: "Download all market data and ask your local AI assistant.", icon: Database },
  { href: "/settings", title: "Settings", desc: "API keys, environment, and Cloudflare Tunnel setup.", icon: BarChart3 },
];

function PulseCard({ item }: { item: PulseItem }) {
  const meta = PULSE_LABELS[item.id] || { label: item.id, icon: "?" };
  const up = (item.change_pct ?? 0) >= 0;
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/60 bg-card/60 px-3 py-2.5">
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-secondary text-[10px] font-bold text-muted-foreground">
          {meta.icon}
        </span>
        <div>
          <p className="text-xs font-medium leading-tight">{meta.label}</p>
          <p className="font-mono text-sm">{fmt(item.last)}</p>
        </div>
      </div>
      {item.change_pct != null && (
        <span
          className={cn(
            "inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-xs font-medium",
            up ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400",
          )}
        >
          {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
          {up ? "+" : ""}{item.change_pct.toFixed(2)}%
        </span>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [pulse, setPulse] = useState<PulseItem[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<{ pulse: PulseItem[] }>("/api/markets/pulse")
      .then((d) => setPulse(d.pulse))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-10">
      <div className="space-y-3">
        <p className="text-sm font-medium uppercase tracking-widest text-primary">FinanceLab</p>
        <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
          Full-spectrum market intelligence
        </h1>
        <p className="max-w-2xl text-muted-foreground">
          India &amp; US equities, mutual funds, F&amp;O, energy, commodities, crypto,
          forex, bonds, REITs — with GO/NO-GO signals, portfolio risk, tax engine,
          research lab, and 37 wiki reference articles. All live.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link href="/markets" className={cn(buttonVariants({ variant: "default" }), "inline-flex")}>
            Explore markets <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <Link href="/gonogo" className={cn(buttonVariants({ variant: "outline" }), "inline-flex")}>
            GO/NO-GO signal
          </Link>
          <Link href="/screener" className={cn(buttonVariants({ variant: "outline" }), "inline-flex")}>
            Run screener
          </Link>
        </div>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold tracking-tight">Market pulse</h2>
        {loading ? (
          <div className="grid gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 12 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-lg" />
            ))}
          </div>
        ) : pulse && pulse.length > 0 ? (
          <div className="grid gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {pulse.map((p) => <PulseCard key={p.id} item={p} />)}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Unable to load pulse — is the backend running?</p>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {tiles.map(({ href, title, desc, icon: Icon }) => (
          <Link key={href} href={href} className="group block">
            <Card className="h-full border-border/80 bg-card/80 transition-colors hover:border-primary/40">
              <CardHeader>
                <div className="mb-2 flex items-center gap-2 text-primary">
                  <Icon className="h-5 w-5" />
                  <CardTitle className="text-base group-hover:text-primary">{title}</CardTitle>
                </div>
                <CardDescription className="text-sm leading-relaxed">{desc}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
