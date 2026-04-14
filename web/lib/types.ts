export interface CategoryInfo {
  id: string;
  label: string;
  count: number;
  kind?: "curated" | "extended";
}

export interface InstrumentQuote {
  symbol: string;
  name?: string;
  sub_category?: string;
  tags?: string[];
  last?: number | null;
  currency?: string | null;
  prev_close?: number | null;
  change_pct?: number | null;
  error?: string | null;
}

export interface CategoryResponse {
  category: string;
  count: number;
  total?: number;
  offset?: number;
  limit?: number | null;
  tag_filter?: string | null;
  instruments: InstrumentQuote[];
}

export interface TagInfo {
  tag: string;
  label: string;
  count: number;
}

export interface UniverseProgress {
  running: boolean;
  step: string;
  counts?: Record<string, number>;
  error?: string;
}

export interface PulseItem {
  id: string;
  symbol: string;
  last?: number | null;
  change_pct?: number | null;
  currency?: string | null;
}

export interface SearchResult {
  symbol: string;
  name: string;
  category: string;
  sub_category?: string;
  tags?: string[];
}

export interface InstrumentDetail {
  symbol: string;
  last?: number | null;
  currency?: string | null;
  name?: string | null;
  long_name?: string | null;
  exchange?: string | null;
  market_cap?: number | null;
  pe_ratio?: number | null;
  forward_pe?: number | null;
  pb_ratio?: number | null;
  peg_ratio?: number | null;
  eps?: number | null;
  forward_eps?: number | null;
  book_value?: number | null;
  dividend_yield?: number | null;
  dividend_rate?: number | null;
  payout_ratio?: number | null;
  beta?: number | null;
  "52w_high"?: number | null;
  "52w_low"?: number | null;
  "50d_avg"?: number | null;
  "200d_avg"?: number | null;
  volume?: number | null;
  avg_volume?: number | null;
  open?: number | null;
  prev_close?: number | null;
  day_low?: number | null;
  day_high?: number | null;
  change_pct?: number | null;
  sector?: string | null;
  industry?: string | null;
  country?: string | null;
  website?: string | null;
  employees?: number | null;
  description?: string | null;
  earnings_date?: unknown;
  recommendation?: string | null;
  target_mean_price?: number | null;
  analyst_count?: number | null;
  profit_margin?: number | null;
  revenue_growth?: number | null;
  gross_margin?: number | null;
  operating_margin?: number | null;
  return_on_equity?: number | null;
  debt_to_equity?: number | null;
  total_revenue?: number | null;
  ebitda?: number | null;
  error?: string | null;
}

export interface TickerPerformance {
  "1d"?: number | null;
  "5d"?: number | null;
  "1m"?: number | null;
  "3m"?: number | null;
  "6m"?: number | null;
  ytd?: number | null;
  "1y"?: number | null;
  "5y"?: number | null;
  error?: string;
}

export interface TickerDetailResponse {
  quote: InstrumentDetail;
  performance: TickerPerformance;
  history: PriceHistory;
  news: SymbolNews;
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceHistory {
  symbol: string;
  period: string;
  interval: string;
  points: PricePoint[];
  error?: string;
}

export interface NewsArticle {
  title: string;
  url: string;
  source: string;
  date: string;
  summary: string;
  sentiment?: number | null;
}

export interface SymbolNews {
  symbol: string;
  articles: NewsArticle[];
}

export interface AiAnalysis {
  model: string;
  response?: string;
  error?: string;
}

export interface MetalCity {
  city: string;
  gold_24k_per_10g: number;
  gold_22k_per_10g: number;
  silver_per_kg: number;
  premium_inr: number;
}

export interface MetalPrices {
  reference?: {
    gold_usd_per_oz: number;
    silver_usd_per_oz: number;
    usdinr: number;
    gold_inr_per_10g_base: number;
  };
  cities?: MetalCity[];
  error?: string;
}
