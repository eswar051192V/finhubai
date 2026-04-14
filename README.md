# FinanceLab (FinHubAI)

Local-first trading intelligence stack: **FastAPI** backend, **Next.js14** web app, **TimescaleDB** + **Redis** via Docker, and **Caddy** + **Cloudflare Tunnel** for a single public URL.

## Prerequisites

- Docker Desktop (or Docker Engine) on your Mac Mini
- Python 3.11+
- Node.js 20+ and npm
- [Caddy](https://caddyserver.com/docs/install) (optional, for same-origin `/api` + tunnel target)

## Quick start (development)

1. Copy environment template and adjust keys as needed:

   ```bash
   cp .env.example .env
   ```

2. Start databases:

   ```bash
   docker compose up -d
   ```

3. Backend (from repo root):

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd ..
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. Web app:

   ```bash
   cd web
   npm install
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000). API requests to `/api/*` are rewritten to the FastAPI server.

## Production-like local (Caddy + tunnel target)

See [deploy/Caddyfile](deploy/Caddyfile) and [deploy/cloudflare-tunnel.md](deploy/cloudflare-tunnel.md).

## API overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness |
| GET | `/api/health/deps` | DB + Redis checks |
| POST | `/api/cost-calculator` | True cost by broker / segment |
| POST | `/api/tax/when-to-sell` | India STCG/LTCG hold analysis |
| GET | `/api/option-chain/{symbol}` | Max pain, PCR, OI heuristics |
| GET | `/api/sentiment/{ticker}` | Weighted sentiment + FII/DII |
| GET | `/api/market/fii-dii` | Latest FII/DII cash figures |

## Tests

From the repository root (after installing backend dependencies into `backend/.venv`):

```bash
export PYTHONPATH=/path/to/FinHubAI
/path/to/FinHubAI/backend/.venv/bin/pytest tests -v
```

## Specs

- [FINANCELAB_PLAN_OF_ACTION.md](FINANCELAB_PLAN_OF_ACTION.md)
- [FINANCELAB_TAX_ENGINE_COMPLETE.md](FINANCELAB_TAX_ENGINE_COMPLETE.md)
- [FINANCELAB_COMPLETE_SYSTEM_PART2.md](FINANCELAB_COMPLETE_SYSTEM_PART2.md)
