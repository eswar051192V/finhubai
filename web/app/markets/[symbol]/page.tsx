"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  TrendingDown,
  TrendingUp,
  BarChart3,
  LineChart as LineIcon,
  CandlestickChart,
  Newspaper,
  Loader2,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiGet } from "@/lib/api";
import type {
  NewsArticle,
  PriceHistory,
  PricePoint,
  TickerDetailResponse,
  TickerPerformance,
} from "@/lib/types";

// ────────────────────────────────────────────────────────────────────
// Helpers
// ────────────────────────────────────────────────────────────────────

function fmt(v: number | null | undefined, d = 2): string {
  if (v == null || Number.isNaN(v)) return "--";
  return v.toLocaleString(undefined, {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });
}

function fmtCompact(v: number | null | undefined): string {
  if (v == null || Number.isNaN(v)) return "--";
  const abs = Math.abs(v);
  if (abs >= 1e12) return (v / 1e12).toFixed(2) + "T";
  if (abs >= 1e9) return (v / 1e9).toFixed(2) + "B";
  if (abs >= 1e6) return (v / 1e6).toFixed(2) + "M";
  if (abs >= 1e3) return (v / 1e3).toFixed(2) + "K";
  return v.toFixed(2);
}

function fmtPct(v: number | null | undefined): string {
  if (v == null || Number.isNaN(v)) return "--";
  const sign = v >= 0 ? "+" : "";
  return `${sign}${v.toFixed(2)}%`;
}

function Delta({ pct, size = "sm" }: { pct?: number | null; size?: "sm" | "lg" }) {
  if (pct == null) return <span className="text-muted-foreground">--</span>;
  const up = pct >= 0;
  const cls = up ? "text-emerald-400" : "text-red-400";
  const bg = up ? "bg-emerald-500/10" : "bg-red-500/10";
  const text = size === "lg" ? "text-lg" : "text-xs";
  return (
    <span className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 font-medium ${bg} ${cls} ${text}`}>
      {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
      {fmtPct(pct)}
    </span>
  );
}

function Stat({
  label,
  value,
  mono = true,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-border/40 py-1.5 last:border-b-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`text-right text-sm ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────
// Pure SVG Candlestick / Line / Area chart + volume + hover crosshair
// ────────────────────────────────────────────────────────────────────

interface ChartProps {
  points: PricePoint[];
  kind: "candle" | "line" | "area";
  height?: number;
}

function PriceChart({ points, kind, height = 360 }: ChartProps) {
  const [hover, setHover] = useState<{ i: number } | null>(null);

  if (!points || points.length === 0) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground"
      >
        No price data
      </div>
    );
  }

  const W = 1000;
  const H = height;
  const volH = 60;
  const pad = { top: 12, right: 48, bottom: 24 + volH, left: 12 };
  const priceH = H - pad.top - pad.bottom;
  const innerW = W - pad.left - pad.right;

  const highs = points.map((p) => p.high ?? p.close);
  const lows = points.map((p) => p.low ?? p.close);
  const minPrice = Math.min(...lows);
  const maxPrice = Math.max(...highs);
  const priceRange = maxPrice - minPrice || 1;
  const maxVol = Math.max(...points.map((p) => p.volume || 0)) || 1;

  const n = points.length;
  const candleW = Math.max(1, (innerW / n) * 0.7);
  const step = innerW / n;

  const yPrice = (v: number) =>
    pad.top + priceH - ((v - minPrice) / priceRange) * priceH;

  const linePath = points
    .map((p, i) => {
      const x = pad.left + i * step + step / 2;
      const y = yPrice(p.close);
      return `${i === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");

  const areaPath =
    linePath +
    ` L ${(pad.left + (n - 1) * step + step / 2).toFixed(2)} ${pad.top + priceH} L ${(pad.left + step / 2).toFixed(2)} ${pad.top + priceH} Z`;

  const gridYs = [0, 0.25, 0.5, 0.75, 1].map((t) => ({
    y: pad.top + t * priceH,
    label: maxPrice - t * priceRange,
  }));

  const change = points[n - 1].close - points[0].close;
  const up = change >= 0;
  const bullish = "#10b981";
  const bearish = "#ef4444";
  const lineColor = up ? bullish : bearish;
  const hovered = hover != null ? points[hover.i] : null;

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        height={H}
        className="overflow-visible"
        onMouseLeave={() => setHover(null)}
        onMouseMove={(e) => {
          const rect = (e.currentTarget as SVGSVGElement).getBoundingClientRect();
          const relX = ((e.clientX - rect.left) / rect.width) * W;
          const idx = Math.max(0, Math.min(n - 1, Math.floor((relX - pad.left) / step)));
          setHover({ i: idx });
        }}
      >
        {gridYs.map((g, i) => (
          <g key={i}>
            <line
              x1={pad.left}
              x2={W - pad.right}
              y1={g.y}
              y2={g.y}
              stroke="currentColor"
              strokeOpacity={0.08}
              strokeDasharray="2 3"
            />
            <text x={W - pad.right + 6} y={g.y + 3} fontSize="10" fill="currentColor" opacity={0.6}>
              {fmt(g.label)}
            </text>
          </g>
        ))}

        {kind !== "candle" && (
          <>
            {kind === "area" && <path d={areaPath} fill={lineColor} fillOpacity={0.12} />}
            <path d={linePath} fill="none" stroke={lineColor} strokeWidth={1.5} />
          </>
        )}

        {kind === "candle" &&
          points.map((p, i) => {
            const cx = pad.left + i * step + step / 2;
            const open = p.open ?? p.close;
            const close = p.close;
            const isUp = close >= open;
            const color = isUp ? bullish : bearish;
            const yO = yPrice(open);
            const yC = yPrice(close);
            return (
              <g key={i}>
                <line
                  x1={cx}
                  x2={cx}
                  y1={yPrice(p.high ?? close)}
                  y2={yPrice(p.low ?? close)}
                  stroke={color}
                  strokeWidth={1}
                />
                <rect
                  x={cx - candleW / 2}
                  y={Math.min(yO, yC)}
                  width={candleW}
                  height={Math.max(1, Math.abs(yC - yO))}
                  fill={color}
                  opacity={0.9}
                />
              </g>
            );
          })}

        {points.map((p, i) => {
          const x = pad.left + i * step + step / 2 - candleW / 2;
          const h = ((p.volume || 0) / maxVol) * volH;
          const open = p.open ?? p.close;
          const isUp = (p.close ?? 0) >= open;
          const y = H - pad.bottom + volH - h;
          return (
            <rect
              key={`v${i}`}
              x={x}
              y={y}
              width={candleW}
              height={h}
              fill={isUp ? bullish : bearish}
              opacity={0.35}
            />
          );
        })}
        <line
          x1={pad.left}
          x2={W - pad.right}
          y1={H - pad.bottom}
          y2={H - pad.bottom}
          stroke="currentColor"
          strokeOpacity={0.15}
        />

        {hover && (
          <>
            <line
              x1={pad.left + hover.i * step + step / 2}
              x2={pad.left + hover.i * step + step / 2}
              y1={pad.top}
              y2={H - pad.bottom + volH}
              stroke="currentColor"
              strokeOpacity={0.35}
              strokeDasharray="2 3"
            />
            {hovered && (
              <circle
                cx={pad.left + hover.i * step + step / 2}
                cy={yPrice(hovered.close)}
                r={3}
                fill={lineColor}
              />
            )}
          </>
        )}
      </svg>

      {hovered && (
        <div className="pointer-events-none absolute left-2 top-2 rounded border border-border/60 bg-background/90 px-2 py-1 text-[11px] font-mono backdrop-blur">
          <div className="text-muted-foreground">{hovered.date}</div>
          <div>
            O <span className="text-foreground">{fmt(hovered.open)}</span>{" "}
            H <span className="text-foreground">{fmt(hovered.high)}</span>{" "}
            L <span className="text-foreground">{fmt(hovered.low)}</span>{" "}
            C <span className="text-foreground">{fmt(hovered.close)}</span>
          </div>
          <div className="text-muted-foreground">Vol {fmtCompact(hovered.volume)}</div>
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────
// Page
// ────────────────────────────────────────────────────────────────────

const PERIOD_OPTIONS: { label: string; period: string; interval: string }[] = [
  { label: "1D", period: "1d", interval: "5m" },
  { label: "5D", period: "5d", interval: "30m" },
  { label: "1M", period: "1mo", interval: "1d" },
  { label: "6M", period: "6mo", interval: "1d" },
  { label: "1Y", period: "1y", interval: "1d" },
  { label: "5Y", period: "5y", interval: "1wk" },
  { label: "Max", period: "max", interval: "1mo" },
];

export default function TickerDetailPage() {
  const params = useParams<{ symbol: string | string[] }>();
  const router = useRouter();
  const rawSymbol = Array.isArray(params.symbol) ? params.symbol[0] : params.symbol;
  const symbol = decodeURIComponent(rawSymbol || "");

  const [data, setData] = useState<TickerDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [chartPeriod, setChartPeriod] = useState("1y");
  const [chartInterval, setChartInterval] = useState("1d");
  const [chartHist, setChartHist] = useState<PriceHistory | null>(null);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartKind, setChartKind] = useState<"candle" | "line" | "area">("candle");

  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    setErr(null);
    apiGet<TickerDetailResponse>(`/api/markets/ticker/${encodeURIComponent(symbol)}`)
      .then((d) => {
        setData(d);
        setChartHist(d.history);
      })
      .catch((e) => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [symbol]);

  useEffect(() => {
    if (!symbol) return;
    setChartLoading(true);
    apiGet<PriceHistory>(
      `/api/markets/history/${encodeURIComponent(symbol)}?period=${chartPeriod}&interval=${chartInterval}`,
    )
      .then(setChartHist)
      .catch((e) => setErr(String(e)))
      .finally(() => setChartLoading(false));
  }, [symbol, chartPeriod, chartInterval]);

  const quote = data?.quote;
  const perf = data?.performance;
  const news = data?.news?.articles || [];
  const hist = chartHist?.points || [];

  const currencyLabel = useMemo(() => {
    const c = quote?.currency;
    if (!c) return "";
    return c === "USD" ? "$" : c === "INR" ? "₹" : `${c} `;
  }, [quote?.currency]);

  if (loading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-12 w-80" />
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-[360px] w-full" />
      </div>
    );
  }

  if (err || !quote) {
    return (
      <div className="p-6">
        <Link
          href="/markets"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Markets
        </Link>
        <Card className="mt-4">
          <CardContent className="p-6 text-sm text-red-400">
            Couldn&apos;t load {symbol}. {err || quote?.error || "Unknown error"}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4 md:p-6">
      {/* Breadcrumb */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => router.back()}
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Markets
        </button>
        <div className="flex items-center gap-2">
          <Link href={`/gonogo?symbol=${encodeURIComponent(symbol)}`}>
            <Button variant="outline" size="sm">GO/NO-GO</Button>
          </Link>
          <Link href={`/sentiment?symbol=${encodeURIComponent(symbol)}`}>
            <Button variant="outline" size="sm">Sentiment</Button>
          </Link>
          <Link href={`/options?symbol=${encodeURIComponent(symbol)}`}>
            <Button variant="outline" size="sm">Options</Button>
          </Link>
        </div>
      </div>

      {/* Header */}
      <Card>
        <CardContent className="flex flex-col gap-4 p-6 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-2xl font-semibold tracking-tight">
                {quote.long_name || quote.name || symbol}
              </h1>
              <Badge variant="outline" className="font-mono">{symbol}</Badge>
              {quote.exchange && <Badge variant="secondary">{quote.exchange}</Badge>}
              {quote.sector && <Badge variant="outline">{quote.sector}</Badge>}
            </div>
            <div className="mt-3 flex items-baseline gap-3">
              <span className="font-mono text-4xl font-semibold">
                {currencyLabel}
                {fmt(quote.last)}
              </span>
              <Delta pct={quote.change_pct} size="lg" />
              {quote.prev_close != null && quote.last != null && (
                <span className="font-mono text-sm text-muted-foreground">
                  {quote.last - quote.prev_close >= 0 ? "+" : ""}
                  {fmt(quote.last - quote.prev_close)}
                </span>
              )}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              {quote.industry || ""} {quote.country ? `· ${quote.country}` : ""}
              {quote.website && (
                <>
                  {" · "}
                  <a
                    href={quote.website}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-0.5 text-foreground/80 hover:text-foreground"
                  >
                    Website <ExternalLink className="h-3 w-3" />
                  </a>
                </>
              )}
            </div>
          </div>

          <div className="grid flex-shrink-0 grid-cols-2 gap-x-6 gap-y-1 text-sm">
            <Stat label="Open" value={fmt(quote.open)} />
            <Stat label="Prev Close" value={fmt(quote.prev_close)} />
            <Stat label="Day Low" value={fmt(quote.day_low)} />
            <Stat label="Day High" value={fmt(quote.day_high)} />
            <Stat label="52W Low" value={fmt(quote["52w_low"])} />
            <Stat label="52W High" value={fmt(quote["52w_high"])} />
            <Stat label="Volume" value={fmtCompact(quote.volume)} />
            <Stat label="Avg Vol" value={fmtCompact(quote.avg_volume)} />
          </div>
        </CardContent>
      </Card>

      {/* Chart + Performance */}
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <CardTitle className="text-base">Price chart</CardTitle>
            <div className="flex flex-wrap gap-2">
              <div className="flex rounded-md border bg-muted/20 p-0.5">
                {PERIOD_OPTIONS.map((o) => (
                  <button
                    key={o.label}
                    onClick={() => {
                      setChartPeriod(o.period);
                      setChartInterval(o.interval);
                    }}
                    className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
                      chartPeriod === o.period
                        ? "bg-background text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {o.label}
                  </button>
                ))}
              </div>
              <div className="flex rounded-md border bg-muted/20 p-0.5">
                <button
                  onClick={() => setChartKind("candle")}
                  className={`inline-flex items-center gap-1 rounded px-2 py-1 text-xs ${
                    chartKind === "candle" ? "bg-background shadow-sm" : "text-muted-foreground"
                  }`}
                  title="Candlestick"
                >
                  <CandlestickChart className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => setChartKind("line")}
                  className={`inline-flex items-center gap-1 rounded px-2 py-1 text-xs ${
                    chartKind === "line" ? "bg-background shadow-sm" : "text-muted-foreground"
                  }`}
                  title="Line"
                >
                  <LineIcon className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => setChartKind("area")}
                  className={`inline-flex items-center gap-1 rounded px-2 py-1 text-xs ${
                    chartKind === "area" ? "bg-background shadow-sm" : "text-muted-foreground"
                  }`}
                  title="Area"
                >
                  <BarChart3 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {chartLoading ? (
              <div className="flex h-[360px] items-center justify-center text-muted-foreground">
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> loading…
              </div>
            ) : (
              <PriceChart points={hist} kind={chartKind} height={360} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {(
              [
                ["1 Day", "1d"],
                ["5 Day", "5d"],
                ["1 Month", "1m"],
                ["3 Month", "3m"],
                ["6 Month", "6m"],
                ["YTD", "ytd"],
                ["1 Year", "1y"],
                ["5 Year", "5y"],
              ] as const
            ).map(([label, key]) => (
              <Stat
                key={key}
                label={label}
                value={
                  <Delta
                    pct={(perf as TickerPerformance | undefined)?.[key] as number | null | undefined}
                  />
                }
                mono={false}
              />
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="news">News ({news.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Description</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-relaxed text-muted-foreground">
              {quote.description || "No description available for this instrument."}
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Valuation</CardTitle>
              </CardHeader>
              <CardContent>
                <Stat label="Market Cap" value={fmtCompact(quote.market_cap)} />
                <Stat label="P/E (TTM)" value={fmt(quote.pe_ratio)} />
                <Stat label="Forward P/E" value={fmt(quote.forward_pe)} />
                <Stat label="P/B" value={fmt(quote.pb_ratio)} />
                <Stat label="PEG" value={fmt(quote.peg_ratio)} />
                <Stat label="EPS (TTM)" value={fmt(quote.eps)} />
                <Stat label="Book Value" value={fmt(quote.book_value)} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Dividends & Risk</CardTitle>
              </CardHeader>
              <CardContent>
                <Stat
                  label="Dividend Yield"
                  value={quote.dividend_yield != null ? `${(quote.dividend_yield * 100).toFixed(2)}%` : "--"}
                />
                <Stat label="Dividend Rate" value={fmt(quote.dividend_rate)} />
                <Stat
                  label="Payout Ratio"
                  value={quote.payout_ratio != null ? `${(quote.payout_ratio * 100).toFixed(2)}%` : "--"}
                />
                <Stat label="Beta" value={fmt(quote.beta)} />
                <Stat label="50D Avg" value={fmt(quote["50d_avg"])} />
                <Stat label="200D Avg" value={fmt(quote["200d_avg"])} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Analyst</CardTitle>
              </CardHeader>
              <CardContent>
                <Stat
                  label="Recommendation"
                  value={quote.recommendation?.toUpperCase() || "--"}
                  mono={false}
                />
                <Stat label="Target Price" value={fmt(quote.target_mean_price)} />
                <Stat label="Analysts" value={fmtCompact(quote.analyst_count)} />
                <Stat label="Sector" value={quote.sector || "--"} mono={false} />
                <Stat label="Industry" value={quote.industry || "--"} mono={false} />
                <Stat label="Employees" value={fmtCompact(quote.employees)} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="financials">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Profitability</CardTitle>
              </CardHeader>
              <CardContent>
                <Stat
                  label="Gross Margin"
                  value={quote.gross_margin != null ? `${(quote.gross_margin * 100).toFixed(2)}%` : "--"}
                />
                <Stat
                  label="Operating Margin"
                  value={quote.operating_margin != null ? `${(quote.operating_margin * 100).toFixed(2)}%` : "--"}
                />
                <Stat
                  label="Profit Margin"
                  value={quote.profit_margin != null ? `${(quote.profit_margin * 100).toFixed(2)}%` : "--"}
                />
                <Stat
                  label="ROE"
                  value={quote.return_on_equity != null ? `${(quote.return_on_equity * 100).toFixed(2)}%` : "--"}
                />
                <Stat
                  label="Revenue Growth"
                  value={quote.revenue_growth != null ? `${(quote.revenue_growth * 100).toFixed(2)}%` : "--"}
                />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Balance Sheet</CardTitle>
              </CardHeader>
              <CardContent>
                <Stat label="Total Revenue" value={fmtCompact(quote.total_revenue)} />
                <Stat label="EBITDA" value={fmtCompact(quote.ebitda)} />
                <Stat label="Debt / Equity" value={fmt(quote.debt_to_equity)} />
                <Stat label="Market Cap" value={fmtCompact(quote.market_cap)} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <HistoryTable points={hist} />
        </TabsContent>

        <TabsContent value="news">
          <NewsList articles={news} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────
// History table (paginated)
// ────────────────────────────────────────────────────────────────────

function HistoryTable({ points }: { points: PricePoint[] }) {
  const [page, setPage] = useState(0);
  const pageSize = 30;
  const pages = Math.max(1, Math.ceil(points.length / pageSize));
  const rows = [...points].reverse().slice(page * pageSize, (page + 1) * pageSize);

  if (!points.length) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground">
          No historical data for this range.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">OHLCV ({points.length} rows)</CardTitle>
        <div className="flex items-center gap-2 text-sm">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
          >
            ‹
          </Button>
          <span className="text-xs text-muted-foreground">
            {page + 1} / {pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= pages - 1}
            onClick={() => setPage((p) => Math.min(pages - 1, p + 1))}
          >
            ›
          </Button>
        </div>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-xs uppercase tracking-wide text-muted-foreground">
              <th className="py-2 text-left">Date</th>
              <th className="py-2 text-right">Open</th>
              <th className="py-2 text-right">High</th>
              <th className="py-2 text-right">Low</th>
              <th className="py-2 text-right">Close</th>
              <th className="py-2 text-right">Change</th>
              <th className="py-2 text-right">Volume</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const prev = rows[i + 1];
              const pct =
                prev && prev.close
                  ? ((r.close - prev.close) / prev.close) * 100
                  : null;
              return (
                <tr key={r.date} className="border-b border-border/30 hover:bg-accent/30">
                  <td className="py-1.5 font-mono text-xs">{r.date}</td>
                  <td className="py-1.5 text-right font-mono">{fmt(r.open)}</td>
                  <td className="py-1.5 text-right font-mono">{fmt(r.high)}</td>
                  <td className="py-1.5 text-right font-mono">{fmt(r.low)}</td>
                  <td className="py-1.5 text-right font-mono">{fmt(r.close)}</td>
                  <td className="py-1.5 text-right">
                    <Delta pct={pct} />
                  </td>
                  <td className="py-1.5 text-right font-mono text-xs">
                    {fmtCompact(r.volume)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

// ────────────────────────────────────────────────────────────────────
// News list
// ────────────────────────────────────────────────────────────────────

function NewsList({ articles }: { articles: NewsArticle[] }) {
  if (!articles.length) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground">
          No news articles found for this ticker.
        </CardContent>
      </Card>
    );
  }
  return (
    <div className="space-y-2">
      {articles.map((a, i) => (
        <Card key={i}>
          <CardContent className="p-4">
            <a href={a.url} target="_blank" rel="noreferrer" className="group block">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium group-hover:text-primary">{a.title}</p>
                  {a.summary && (
                    <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{a.summary}</p>
                  )}
                  <div className="mt-1.5 flex items-center gap-2 text-[11px] text-muted-foreground">
                    <Newspaper className="h-3 w-3" />
                    <span>{a.source}</span>
                    {a.date && <span>· {a.date}</span>}
                    {a.sentiment != null && (
                      <Badge
                        variant="outline"
                        className={
                          a.sentiment > 0
                            ? "border-emerald-500/40 text-emerald-400"
                            : a.sentiment < 0
                              ? "border-red-500/40 text-red-400"
                              : ""
                        }
                      >
                        {a.sentiment > 0 ? "+" : ""}
                        {a.sentiment.toFixed(2)}
                      </Badge>
                    )}
                  </div>
                </div>
                <ExternalLink className="mt-1 h-4 w-4 flex-shrink-0 text-muted-foreground" />
              </div>
            </a>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
