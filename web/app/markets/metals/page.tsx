"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { apiGet } from "@/lib/api";
import type { MetalPrices } from "@/lib/types";

function fmt(val: number): string {
  return val.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function MetalsPage() {
  const [data, setData] = useState<MetalPrices | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<MetalPrices>("/api/markets/metals/india")
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-8 w-56" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (!data || data.error) {
    return (
      <div className="mx-auto max-w-3xl py-12 text-center text-muted-foreground">
        {data?.error || "Failed to load metal prices."}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/markets" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Gold &amp; Silver by City (India)
          </h1>
          <p className="text-sm text-muted-foreground">
            Futures-based + city premium estimates. Verify with local jewellers.
          </p>
        </div>
      </div>

      {data.reference && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Reference Rates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
              <div>
                <p className="text-muted-foreground">Gold (USD/oz)</p>
                <p className="font-mono">${fmt(data.reference.gold_usd_per_oz)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Silver (USD/oz)</p>
                <p className="font-mono">${fmt(data.reference.silver_usd_per_oz)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">USD/INR</p>
                <p className="font-mono">{data.reference.usdinr.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Gold Base (INR/10g)</p>
                <p className="font-mono">{fmt(data.reference.gold_inr_per_10g_base)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">City Prices</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-muted-foreground">
                <th className="py-2 pr-4">City</th>
                <th className="py-2 pr-4 text-right">Gold 24K / 10g</th>
                <th className="py-2 pr-4 text-right">Gold 22K / 10g</th>
                <th className="py-2 text-right">Silver / kg</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {(data.cities || []).map((c) => (
                <tr key={c.city} className="hover:bg-accent/30">
                  <td className="py-2.5 pr-4 font-medium">{c.city}</td>
                  <td className="py-2.5 pr-4 text-right font-mono">
                    {fmt(c.gold_24k_per_10g)}
                  </td>
                  <td className="py-2.5 pr-4 text-right font-mono">
                    {fmt(c.gold_22k_per_10g)}
                  </td>
                  <td className="py-2.5 text-right font-mono">
                    {fmt(c.silver_per_kg)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
