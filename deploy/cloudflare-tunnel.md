# Cloudflare Tunnel (cloudflared) on macOS

Expose FinanceLab on your Mac Mini to the internet through Cloudflare, with **one hostname** for both the Next.js app and `/api` (via Caddy).

## Prerequisites

- A domain on Cloudflare (DNS managed by Cloudflare).
- Home router allows **outbound** HTTPS; no inbound port forwarding required for Tunnel.
- Caddy installed (`brew install caddy`) and this repo’s [Caddyfile](Caddyfile) tuned to your local ports.

## 1. Install cloudflared

```bash
brew install cloudflare/cloudflare/cloudflared
cloudflared --version
```

## 2. Authenticate

```bash
cloudflared tunnel login
```

Pick your zone in the browser flow.

## 3. Create a named tunnel

```bash
cloudflared tunnel create financelab
```

Note the tunnel **UUID** from `~/.cloudflared/<UUID>.json`.

## 4. Ingress config

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR_TUNNEL_UUID>
credentials-file: /Users/<you>/.cloudflared/<YOUR_TUNNEL_UUID>.json

ingress:
  - hostname: lab.example.com
    service: https://127.0.0.1:8443
    originRequest:
      noTLSVerify: true
  - service: http_status:404
```

- Replace `lab.example.com` with your real subdomain.
- Caddy listens on **8443** in the sample [Caddyfile](Caddyfile); match `service` to whatever you configure.
- `noTLSVerify: true` is only needed if Caddy uses a self-signed certificate locally. If you point the tunnel at `http://127.0.0.1:8080` with plain HTTP in Caddy, omit `originRequest`.

## 5. DNS route

```bash
cloudflared tunnel route dns financelab lab.example.com
```

Or add a **CNAME** in the Cloudflare dashboard: `lab` → `<tunnel-id>.cfargotunnel.com`.

## 6. Run the stack locally

1. `docker compose up -d` (TimescaleDB + Redis).
2. FastAPI: `cd` to repo root, activate venv, `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
3. Next.js production build: `cd web && npm run build && npm run start` (port 3000).
4. Caddy: `caddy run --config deploy/Caddyfile` (from repo root).

## 7. Run cloudflared as a user LaunchAgent

Create `~/Library/LaunchAgents/com.cloudflare.financelab.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.cloudflare.financelab</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/cloudflared</string>
    <string>tunnel</string>
    <string>--config</string>
    <string>/Users/YOU/.cloudflared/config.yml</string>
    <string>run</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.cloudflare.financelab.plist
```

Use `which cloudflared` to fix the binary path if not Homebrew on Apple Silicon.

## Optional: Cloudflare Zero Trust (Access)

In the Cloudflare dashboard, add an **Access application** for `lab.example.com` (e.g. one-time PIN or Google SSO) so the site is not fully public.

## Troubleshooting

- **502 / error1033**: tunnel cannot reach local service — confirm Caddy/Next/uvicorn are listening on the ports in `config.yml`.
- **NSE 401 in app**: set `NSE_COOKIES` in `.env` and restart FastAPI.
