"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiPost } from "@/lib/api";

const brokers = ["zerodha", "upstox", "hdfc_sky", "angel_one", "ibkr"] as const;
const segments = [
  "equity_delivery",
  "equity_intraday",
  "futures",
  "options",
] as const;
const sides = ["buy", "sell"] as const;

export default function CostPage() {
  const [broker, setBroker] = useState<string>("zerodha");
  const [segment, setSegment] = useState<string>("equity_delivery");
  const [side, setSide] = useState<string>("buy");
  const [quantity, setQuantity] = useState("100");
  const [price, setPrice] = useState("2500");
  const [premium, setPremium] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        broker,
        segment,
        side,
        quantity: Number(quantity),
        price: Number(price),
      };
      if (segment === "options" && premium.trim()) {
        body.premium = Number(premium);
      }
      const data = await apiPost<Record<string, unknown>>("/api/cost-calculator", body);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">True cost calculator</h1>
        <p className="text-muted-foreground">
          Retail defaults — always reconcile with your contract note.
        </p>
      </div>
      <Card className="border-border/80 bg-card/90">
        <CardHeader>
          <CardTitle>Trade</CardTitle>
          <CardDescription>Broker, segment, side, quantity, and price.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Broker</Label>
                <Select value={broker} onValueChange={(v) => v && setBroker(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {brokers.map((b) => (
                      <SelectItem key={b} value={b}>
                        {b}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Segment</Label>
                <Select value={segment} onValueChange={(v) => v && setSegment(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {segments.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s.replace(/_/g, " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Side</Label>
              <Select value={side} onValueChange={(v) => v && setSide(v)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sides.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="qty">Quantity</Label>
                <Input
                  id="qty"
                  inputMode="decimal"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="price">Price</Label>
                <Input
                  id="price"
                  inputMode="decimal"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                />
              </div>
            </div>
            {segment === "options" && (
              <div className="space-y-2">
                <Label htmlFor="prem">Option premium (per unit)</Label>
                <Input
                  id="prem"
                  inputMode="decimal"
                  placeholder="Optional — defaults to price"
                  value={premium}
                  onChange={(e) => setPremium(e.target.value)}
                />
              </div>
            )}
            {error && (
              <p className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}
            <Button type="submit" disabled={loading} className="w-full sm:w-auto">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Calculate
            </Button>
          </form>
        </CardContent>
      </Card>
      {result && (
        <Card className="border-border/80 bg-card/60">
          <CardHeader>
            <CardTitle className="text-lg">Result</CardTitle>
            <CardDescription>Currency and charge breakdown from the API.</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="max-h-96 overflow-auto rounded-lg bg-secondary/50 p-4 text-xs leading-relaxed text-muted-foreground">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
