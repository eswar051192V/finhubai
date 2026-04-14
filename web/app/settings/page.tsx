import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure the FastAPI process via environment variables (see repo{" "}
          <code className="rounded bg-secondary px-1 py-0.5 text-sm">.env.example</code>).
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>API keys &amp; NSE</CardTitle>
          <CardDescription>Restart the backend after changing .env.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-muted-foreground">
          <ul className="list-inside list-disc space-y-2 leading-relaxed">
            <li>
              <strong className="text-foreground">FINNHUB_API_KEY</strong> — company news for
              sentiment.
            </li>
            <li>
              <strong className="text-foreground">FRED_API_KEY</strong> — macro series (wired for
              future dashboard use).
            </li>
            <li>
              <strong className="text-foreground">NSE_COOKIES</strong> — paste Cookie header from a
              browser session on nseindia.com if option chain / FII-DII return 401/403.
            </li>
            <li>
              <strong className="text-foreground">SENTIMENT_FINBERT_ENABLED</strong> — set{" "}
              <code className="rounded bg-secondary px-1">true</code> only if transformers + torch are
              installed.
            </li>
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Public access</CardTitle>
          <CardDescription>Cloudflare Tunnel + Caddy</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground leading-relaxed">
          Follow <code className="rounded bg-secondary px-1">deploy/cloudflare-tunnel.md</code> to
          expose a single HTTPS hostname: app traffic to Next.js,{" "}
          <code className="rounded bg-secondary px-1">/api</code> to FastAPI.
        </CardContent>
      </Card>
    </div>
  );
}
