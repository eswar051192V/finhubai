"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BookOpen, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { apiGet } from "@/lib/api";

interface WikiEntry {
  slug: string;
  title: string;
  category: string;
  tags: string[];
}

export default function WikiPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [articles, setArticles] = useState<WikiEntry[]>([]);
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState<WikiEntry[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet<string[]>("/api/wiki/categories"),
      apiGet<WikiEntry[]>("/api/wiki/articles"),
    ])
      .then(([cats, arts]) => {
        setCategories(cats);
        setArticles(arts);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (search.trim().length < 2) {
      setSearchResults(null);
      return;
    }
    const t = setTimeout(() => {
      apiGet<WikiEntry[]>(`/api/wiki/search?q=${encodeURIComponent(search)}`)
        .then(setSearchResults)
        .catch(() => {});
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  const grouped: Record<string, WikiEntry[]> = {};
  for (const a of articles) {
    (grouped[a.category] ??= []).push(a);
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <Skeleton className="h-10 w-64" />
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-primary">
            <BookOpen className="h-6 w-6" />
            <h1 className="text-2xl font-semibold tracking-tight">Wiki</h1>
          </div>
          <p className="mt-1 text-muted-foreground">
            Reference guides for every asset class, market concept, and trading term
            covered by FinanceLab.
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search articles..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {searchResults && searchResults.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Search results</CardTitle>
          </CardHeader>
          <CardContent className="max-h-72 divide-y divide-border/50 overflow-auto">
            {searchResults.map((r) => (
              <Link
                key={r.slug}
                href={`/wiki/${r.slug}`}
                className="flex items-center justify-between rounded-md px-3 py-2.5 hover:bg-accent/60"
              >
                <span className="text-sm font-medium">{r.title}</span>
                <Badge variant="outline" className="text-[10px]">
                  {r.category}
                </Badge>
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {searchResults && searchResults.length === 0 && (
        <p className="py-4 text-center text-muted-foreground">No articles match your search.</p>
      )}

      {categories.map((cat) => {
        const catArticles = grouped[cat] || [];
        if (catArticles.length === 0) return null;
        return (
          <Card key={cat} className="border-border/80">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{cat}</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-border/40">
              {catArticles.map((a) => (
                <Link
                  key={a.slug}
                  href={`/wiki/${a.slug}`}
                  className="flex items-center justify-between rounded-md px-2 py-2.5 transition-colors hover:bg-accent/60"
                >
                  <span className="text-sm font-medium text-foreground">
                    {a.title}
                  </span>
                  <div className="hidden gap-1 sm:flex">
                    {a.tags.slice(0, 3).map((t) => (
                      <Badge
                        key={t}
                        variant="outline"
                        className="text-[10px] text-muted-foreground"
                      >
                        {t}
                      </Badge>
                    ))}
                  </div>
                </Link>
              ))}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
