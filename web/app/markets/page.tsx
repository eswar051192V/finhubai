"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Loader2,
  Search,
  TrendingDown,
  TrendingUp,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { apiGet, apiPost } from "@/lib/api";
import type {
  CategoryInfo,
  CategoryResponse,
  InstrumentQuote,
  SearchResult,
  TagInfo,
  UniverseProgress,
} from "@/lib/types";

const CATEGORY_ICONS: Record<string, string> = {
  india_equity: "IN",
  india_equity_all: "NSE+",
  bse_equity: "BSE",
  india_mf: "MF",
  india_mf_all: "MF+",
  india_bonds: "BD",
  india_index: "IX",
  india_fno: "F&O",
  energy: "OIL",
  commodities: "CMD",
  forex: "FX",
  forex_all: "FX+",
  us_equity: "US",
  us_options: "OPT",
  crypto: "BTC",
  crypto_all: "₿+",
  us_bonds: "UST",
  us_futures: "FUT",
  real_estate: "RE",
  real_estate_all: "REIT",
  metals_all: "AU",
};

const PAGE_SIZE = 50;

// Visual style per tag family so index badges stand out
function tagClass(tag: string): string {
  if (tag.startsWith("NIFTY")) return "bg-blue-500/15 text-blue-300 border-blue-500/30";
  if (tag === "SENSEX" || tag.startsWith("BSE")) return "bg-orange-500/15 text-orange-300 border-orange-500/30";
  if (tag === "FNO") return "bg-purple-500/15 text-purple-300 border-purple-500/30";
  if (tag === "REIT" || tag === "INVIT") return "bg-amber-500/15 text-amber-300 border-amber-500/30";
  if (tag === "ETF") return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
  if (tag === "CRYPTO" || tag === "TOP10") return "bg-yellow-500/15 text-yellow-300 border-yellow-500/30";
  if (tag === "PHYSICAL") return "bg-rose-500/15 text-rose-300 border-rose-500/30";
  if (tag === "FOREX") return "bg-teal-500/15 text-teal-300 border-teal-500/30";
  return "bg-muted/50 text-muted-foreground border-border";
}

function fmt(val: number | null | undefined, decimals = 2): string {
  if (val == null) return "--";
  return val.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function ChangeBadge({ pct }: { pct?: number | null }) {
  if (pct == null) return <Badge variant="outline">--</Badge>;
  const isUp = pct >= 0;
  return (
    <span
      className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-xs font-medium ${
        isUp
          ? "bg-emerald-500/15 text-emerald-400"
          : "bg-red-500/15 text-red-400"
      }`}
    >
      {isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
      {isUp ? "+" : ""}
      {pct.toFixed(2)}%
    </span>
  );
}

function TagPill({ tag }: { tag: string }) {
  return (
    <span
      className={`inline-flex items-center rounded border px-1.5 py-[1px] text-[10px] font-medium leading-4 ${tagClass(
        tag,
      )}`}
    >
      {tag}
    </span>
  );
}

function InstrumentRow({ inst }: { inst: InstrumentQuote }) {
  const tags = (inst.tags || []).slice(0, 4); // cap so rows stay tidy
  return (
    <Link
      href={`/markets/${encodeURIComponent(inst.symbol)}`}
      className="flex items-center justify-between gap-3 rounded-md px-3 py-2.5 transition-colors hover:bg-accent/60"
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate text-sm font-medium text-foreground">
            {inst.name || inst.symbol}
          </p>
          <span className="text-xs text-muted-foreground">{inst.symbol}</span>
        </div>
        {tags.length > 0 && (
          <div className="mt-1 flex flex-wrap gap-1">
            {tags.map((t) => (
              <TagPill key={t} tag={t} />
            ))}
            {(inst.tags?.length ?? 0) > tags.length && (
              <span className="text-[10px] text-muted-foreground">
                +{(inst.tags?.length ?? 0) - tags.length} more
              </span>
            )}
          </div>
        )}
      </div>
      <div className="flex items-center gap-3 text-right">
        <span className="font-mono text-sm">
          {inst.currency && inst.currency !== "INR" && inst.currency !== "USD"
            ? `${inst.currency} `
            : ""}
          {fmt(inst.last)}
        </span>
        <ChangeBadge pct={inst.change_pct} />
      </div>
    </Link>
  );
}

export default function MarketsPage() {
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  const [activeCat, setActiveCat] = useState<string | null>(null);
  const [catData, setCatData] = useState<CategoryResponse | null>(null);
  const [loadingCat, setLoadingCat] = useState(false);
  const [searchQ, setSearchQ] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [refreshState, setRefreshState] = useState<UniverseProgress | null>(null);
  const [triggeringRefresh, setTriggeringRefresh] = useState(false);

  // Load categories once
  useEffect(() => {
    apiGet<CategoryInfo[]>("/api/markets/categories").then(setCategories).catch(() => {});
    apiGet<TagInfo[]>("/api/markets/tags").then(setTags).catch(() => {});
  }, []);

  // Load category page when cat / tag / page changes
  useEffect(() => {
    if (!activeCat) return;
    setLoadingCat(true);
    setCatData(null);
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String(page * PAGE_SIZE),
    });
    if (activeTag) params.set("tag", activeTag);
    apiGet<CategoryResponse>(`/api/markets/category/${activeCat}?${params}`)
      .then(setCatData)
      .catch(() => {})
      .finally(() => setLoadingCat(false));
  }, [activeCat, activeTag, page]);

  // Default to first category
  useEffect(() => {
    if (!categories.length) return;
    if (!activeCat) setActiveCat(categories[0].id);
  }, [categories, activeCat]);

  // Reset page on cat/tag change
  useEffect(() => {
    setPage(0);
  }, [activeCat, activeTag]);

  // Search with debounce
  useEffect(() => {
    if (searchQ.trim().length < 2) {
      setSearchResults(null);
      return;
    }
    const timeout = setTimeout(() => {
      setSearchLoading(true);
      apiGet<SearchResult[]>(`/api/markets/search?q=${encodeURIComponent(searchQ)}`)
        .then(setSearchResults)
        .catch(() => {})
        .finally(() => setSearchLoading(false));
    }, 350);
    return () => clearTimeout(timeout);
  }, [searchQ]);

  // Poll refresh progress while running
  useEffect(() => {
    if (!refreshState?.running) return;
    const iv = setInterval(() => {
      apiGet<UniverseProgress>("/api/markets/universe/progress")
        .then((p) => {
          setRefreshState(p);
          if (!p.running) {
            // Reload categories + tags
            apiGet<CategoryInfo[]>("/api/markets/categories").then(setCategories);
            apiGet<TagInfo[]>("/api/markets/tags").then(setTags);
          }
        })
        .catch(() => {});
    }, 2000);
    return () => clearInterval(iv);
  }, [refreshState?.running]);

  async function triggerRefresh() {
    setTriggeringRefresh(true);
    try {
      await apiPost("/api/markets/universe/refresh", {});
      setRefreshState({ running: true, step: "starting" });
    } catch {
      // ignore
    } finally {
      setTriggeringRefresh(false);
    }
  }

  // Group categories: curated vs extended
  const { curated, extended } = useMemo(() => {
    const c = categories.filter((x) => x.kind !== "extended");
    const e = categories.filter((x) => x.kind === "extended");
    return { curated: c, extended: e };
  }, [categories]);

  // Tag filter dropdown: limit to top ~40 most populous tags
  const tagOptions = useMemo(() => tags.slice(0, 60), [tags]);

  const totalPages = catData?.total ? Math.ceil((catData.total || 0) / PAGE_SIZE) : 1;
  const showingFrom = page * PAGE_SIZE + 1;
  const showingTo = Math.min(
    (page + 1) * PAGE_SIZE,
    catData?.total || catData?.count || 0,
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Markets</h1>
          <p className="text-muted-foreground">
            Live prices across India (NSE/BSE equity, MFs, F&amp;O, REITs),
            US, energy, commodities, crypto, forex, bonds, metals & real estate
            — with Nifty 50 / Sensex / sectoral index tags.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search symbol or name..."
              className="pl-9"
              value={searchQ}
              onChange={(e) => setSearchQ(e.target.value)}
            />
          </div>
          <Button
            variant="outline"
            size="sm"
            disabled={triggeringRefresh || refreshState?.running}
            onClick={triggerRefresh}
            className="gap-1.5"
            title="Download NSE / BSE / AMFI / F&O / crypto universe"
          >
            {refreshState?.running || triggeringRefresh ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Download className="h-3.5 w-3.5" />
            )}
            {refreshState?.running
              ? refreshState.step
              : triggeringRefresh
              ? "Starting..."
              : "Load full universe"}
          </Button>
        </div>
      </div>

      {refreshState?.running && (
        <Card className="border-blue-500/30 bg-blue-500/5">
          <CardContent className="py-3 text-sm">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
              <span className="font-medium">Downloading universe:</span>
              <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                {refreshState.step}
              </code>
              <span className="ml-auto text-xs text-muted-foreground">
                NSE equity, BSE, AMFI MFs, index constituents, F&amp;O, crypto...
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {refreshState && !refreshState.running && refreshState.counts && (
        <Card className="border-emerald-500/30 bg-emerald-500/5">
          <CardContent className="py-3 text-xs">
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-medium text-emerald-300">Universe loaded:</span>
              {Object.entries(refreshState.counts).map(([k, v]) => (
                <span key={k} className="text-muted-foreground">
                  <code className="text-foreground">{k}</code> = {v}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {searchResults && searchResults.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">
              Search results{searchLoading && " ..."}
            </CardTitle>
          </CardHeader>
          <CardContent className="max-h-72 overflow-auto">
            {searchResults.map((r) => (
              <Link
                key={`${r.category}-${r.symbol}`}
                href={`/markets/${encodeURIComponent(r.symbol)}`}
                className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-accent/60"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium">{r.name}</span>
                    <span className="text-xs text-muted-foreground">{r.symbol}</span>
                  </div>
                  {(r.tags?.length ?? 0) > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {r.tags!.slice(0, 4).map((t) => (
                        <TagPill key={t} tag={t} />
                      ))}
                    </div>
                  )}
                </div>
                <Badge variant="outline" className="ml-2 text-[10px]">
                  {r.category.replace(/_/g, " ")}
                </Badge>
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Category tabs — curated */}
      <div>
        <p className="mb-2 text-xs font-medium uppercase text-muted-foreground">
          Curated
        </p>
        <div className="flex flex-wrap gap-2">
          {curated.map((cat) => (
            <Button
              key={cat.id}
              variant={activeCat === cat.id ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setActiveCat(cat.id);
                setActiveTag(null);
                setSearchQ("");
                setSearchResults(null);
              }}
              className="gap-1.5"
            >
              <span className="font-mono text-[10px] opacity-60">
                {CATEGORY_ICONS[cat.id] || ""}
              </span>
              {cat.label}
              <span className="text-[10px] opacity-50">{cat.count}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Category tabs — extended (downloaded universe) */}
      {extended.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase text-muted-foreground">
            Full Universe
          </p>
          <div className="flex flex-wrap gap-2">
            {extended.map((cat) => (
              <Button
                key={cat.id}
                variant={activeCat === cat.id ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  setActiveCat(cat.id);
                  setActiveTag(null);
                  setSearchQ("");
                  setSearchResults(null);
                }}
                className="gap-1.5 border-blue-500/30"
              >
                <span className="font-mono text-[10px] opacity-60">
                  {CATEGORY_ICONS[cat.id] || "∞"}
                </span>
                {cat.label}
                <span className="text-[10px] opacity-50">{cat.count.toLocaleString()}</span>
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Tag filter */}
      {tagOptions.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase text-muted-foreground">
            Filter by Index / Tag
          </p>
          <div className="flex flex-wrap gap-1.5">
            {activeTag && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setActiveTag(null)}
                className="h-7 gap-1 px-2 text-xs"
              >
                <X className="h-3 w-3" /> Clear
              </Button>
            )}
            {tagOptions.map((t) => (
              <button
                key={t.tag}
                onClick={() => setActiveTag(activeTag === t.tag ? null : t.tag)}
                className={`rounded border px-2 py-0.5 text-[11px] font-medium transition ${
                  activeTag === t.tag
                    ? "border-primary bg-primary/20 text-primary"
                    : tagClass(t.tag) + " hover:opacity-80"
                }`}
                title={`${t.label} — ${t.count} symbols`}
              >
                {t.label}
                <span className="ml-1 opacity-60">{t.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Metal prices shortcut */}
      <div className="flex gap-2">
        <Link href="/markets/metals">
          <Button variant="outline" size="sm">
            Gold &amp; Silver by City (India)
          </Button>
        </Link>
      </div>

      {/* Category instrument list */}
      <Card className="border-border/80">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              {activeCat
                ? activeCat
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (c) => c.toUpperCase())
                : "Select a category"}
              {activeTag && (
                <span className="ml-2 text-xs font-normal text-muted-foreground">
                  · filtered by{" "}
                  <TagPill tag={activeTag} />
                </span>
              )}
            </CardTitle>
            {catData?.total != null && (
              <span className="text-xs text-muted-foreground">
                {showingFrom}–{showingTo} of {catData.total.toLocaleString()}
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loadingCat ? (
            <div className="space-y-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : catData && catData.instruments.length ? (
            <>
              <div className="divide-y divide-border/50">
                {catData.instruments.map((inst) => (
                  <InstrumentRow key={inst.symbol} inst={inst} />
                ))}
              </div>
              {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between border-t pt-3">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 0}
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                  >
                    <ChevronLeft className="mr-1 h-3.5 w-3.5" /> Prev
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    Page {page + 1} / {totalPages.toLocaleString()}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page + 1 >= totalPages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next <ChevronRight className="ml-1 h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
            </>
          ) : (
            <p className="py-8 text-center text-muted-foreground">
              {activeCat
                ? "No instruments in this category for the current filter."
                : "Pick a category to see live quotes."}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
