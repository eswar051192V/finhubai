#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════
#  FinanceLab / FinHubAI — UNIFIED ALL-PHASE LAUNCHER  (Phases 1 → 8)
#
#  Boots every service needed by the full stack in one shot:
#      • Docker (TimescaleDB + Redis)
#      • Ollama local AI server (Phase 3 RAG / NLQ)
#      • FastAPI backend (Phase 1-8 API routes)
#      • APScheduler + Celery-optional worker (scheduled jobs, alerts)
#      • Next.js frontend
#      • Caddy reverse proxy
#      • Telegram alert bot      (if TELEGRAM_BOT_TOKEN set)
#      • Cloudflare Tunnel       (if CLOUDFLARE_TUNNEL_TOKEN set)
#      • Prometheus metrics      (if PROMETHEUS_ENABLED=true)
#
#  Usage:      chmod +x start.sh && ./start.sh
#  Ctrl-C once to stop everything cleanly.
#
#  Port overrides:
#      FINLAB_API_PORT=8001 FINLAB_WEB_PORT=3001 \
#      FINLAB_API_URL=http://127.0.0.1:8001 ./start.sh
# ══════════════════════════════════════════════════════════════════════════
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Load .env so service flags are available
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

API_PORT="${FINLAB_API_PORT:-8000}"
WEB_PORT="${FINLAB_WEB_PORT:-3000}"
SCHED_PORT="${FINLAB_SCHEDULER_PORT:-8010}"
export FINLAB_API_URL="${FINLAB_API_URL:-http://127.0.0.1:${API_PORT}}"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BLUE='\033[0;34m'; MAGENTA='\033[0;35m'; NC='\033[0m'

log()   { printf "${GREEN}[start]${NC} %s\n" "$*"; }
phase() { printf "\n${MAGENTA}━━━ %s ━━━${NC}\n" "$*"; }
warn()  { printf "${YELLOW}[start]${NC} %s\n" "$*"; }
err()   { printf "${RED}[start]${NC} %s\n" "$*"; }

PIDS=()
RUN_DOCKER_DOWN=0

cleanup() {
    echo ""
    log "Shutting down all services..."
    for pid in "${PIDS[@]:-}"; do
        [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null && kill "$pid" 2>/dev/null || true
    done
    [ "$RUN_DOCKER_DOWN" = 1 ] && docker compose down 2>/dev/null || true
    log "All services stopped."
}
trap cleanup EXIT INT TERM

port_in_use()      { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
require_port_free() {
    if port_in_use "$1"; then
        err "$2 port $1 is already in use."
        err "Inspect: lsof -nP -iTCP:$1 -sTCP:LISTEN"
        err "Or override: FINLAB_API_PORT=8001 FINLAB_WEB_PORT=3001 ./start.sh"
        exit 1
    fi
}

run_bg() {
    # run_bg <label> <logfile> <cmd...>
    local label="$1"; local logfile="$2"; shift 2
    mkdir -p deploy/logs
    ("$@" >"deploy/logs/${logfile}" 2>&1) &
    PIDS+=($!)
    log "started $label (pid $!, log: deploy/logs/${logfile})"
}

phase "PHASE 0 — Preflight"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then cp .env.example .env; warn "Created .env from template."
    else err "No .env found. Run ./setup.sh first."; exit 1; fi
fi
if ! command -v docker &>/dev/null;  then err "docker missing — run ./setup.sh"; exit 1; fi
if ! docker info &>/dev/null;        then err "Docker daemon not running";       exit 1; fi
if [ ! -d .venv ];                   then err ".venv missing — run ./setup.sh";  exit 1; fi

phase "PHASE 1 — Docker (TimescaleDB + Redis)"

docker compose up -d
log "Waiting for TimescaleDB..."
for i in {1..60}; do
    docker compose exec -T timescaledb pg_isready -U postgres -d finhub >/dev/null 2>&1 && { log "TimescaleDB ready"; break; }
    sleep 1; [ "$i" = 60 ] && { err "TimescaleDB unhealthy"; exit 1; }
done
log "Waiting for Redis..."
for i in {1..30}; do
    docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG && { log "Redis ready"; break; }
    sleep 1; [ "$i" = 30 ] && { err "Redis unhealthy"; exit 1; }
done

phase "PHASE 2 — Python venv + dependency sync"

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r backend/requirements.txt 2>&1 | tail -5 || warn "pip install had warnings"
log "venv active: $(python --version)"

phase "PHASE 3 — Ollama (AI / RAG / NLQ)"

if command -v ollama &>/dev/null; then
    if curl -sf "${OLLAMA_HOST:-http://localhost:11434}/api/tags" >/dev/null 2>&1; then
        log "Ollama already running"
    else
        run_bg "ollama"  "ollama.log"  ollama serve
        sleep 3
    fi
else
    warn "ollama not installed — AI features disabled (brew install ollama)"
fi

phase "PHASE 4 — Next.js build check"

if [ ! -d web/node_modules ]; then
    log "Installing web dependencies..."
    (cd web && npm install --silent)
fi
if [ ! -d web/.next ]; then
    log "First-time Next.js build..."
    (cd web && npm run build) || warn "Next build had warnings"
fi

require_port_free "$API_PORT" "API (FastAPI)"
require_port_free "$WEB_PORT" "Web (Next.js)"

phase "PHASE 5 — FastAPI backend (Phase 1-8 API routes)"

run_bg "fastapi" "api.log" \
    uvicorn backend.main:app --host 0.0.0.0 --port "$API_PORT" --reload
sleep 3
for i in {1..20}; do
    curl -sf "http://127.0.0.1:${API_PORT}/api/health" >/dev/null && { log "FastAPI healthy"; break; }
    sleep 1; [ "$i" = 20 ] && { err "FastAPI not responding on $API_PORT"; exit 1; }
done

phase "PHASE 6 — Scheduled jobs (APScheduler / pipeline)"

# Launch the scheduler either as a separate process (if a dedicated runner
# exists) or rely on the one started inside FastAPI. We try the dedicated
# module first so heavy jobs don't block API requests.
if python -c "import backend.data.pipeline" 2>/dev/null; then
    run_bg "scheduler" "scheduler.log" \
        python -c "import time, logging; logging.basicConfig(level=logging.INFO); \
from backend.data.pipeline import pre_market_refresh; \
from apscheduler.schedulers.blocking import BlockingScheduler; \
from zoneinfo import ZoneInfo; \
s=BlockingScheduler(timezone=ZoneInfo('Asia/Kolkata')); \
s.add_job(pre_market_refresh,'cron',hour=8,minute=45); \
s.start()"
else
    warn "backend.data.pipeline not importable — relying on in-process scheduler"
fi

phase "PHASE 7 — Next.js frontend"

run_bg "nextjs" "web.log" \
    bash -c "cd web && FINLAB_API_URL='$FINLAB_API_URL' npm run start -- -p $WEB_PORT"
sleep 4
for i in {1..20}; do
    curl -sf -o /dev/null "http://127.0.0.1:${WEB_PORT}/" && { log "Next.js serving"; break; }
    sleep 1; [ "$i" = 20 ] && { warn "Next.js not yet responding — check deploy/logs/web.log"; break; }
done

phase "PHASE 8 — Caddy / Cloudflare Tunnel / Alerts / Metrics"

# ── Caddy ────────────────────────────────────────────────────────────────
if command -v caddy &>/dev/null; then
    if port_in_use 8443; then warn "Port 8443 busy — skipping Caddy"
    else
        run_bg "caddy" "caddy.log" caddy run --config deploy/Caddyfile
    fi
else
    warn "caddy not installed — skipping reverse proxy"
fi

# ── Cloudflare Tunnel ────────────────────────────────────────────────────
if [ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ] && command -v cloudflared &>/dev/null; then
    run_bg "cloudflared" "cloudflared.log" \
        cloudflared tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN"
else
    [ -z "${CLOUDFLARE_TUNNEL_TOKEN:-}" ] && warn "CLOUDFLARE_TUNNEL_TOKEN unset — tunnel disabled"
fi

# ── Telegram alert bot ───────────────────────────────────────────────────
if [ "${TELEGRAM_ENABLED:-false}" = "true" ] && [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
    if python -c "import backend.engines.alerts_telegram" 2>/dev/null; then
        run_bg "telegram-bot" "telegram.log" \
            python -m backend.engines.alerts_telegram
    else
        warn "TELEGRAM_ENABLED=true but backend.engines.alerts_telegram not implemented yet"
    fi
else
    warn "Telegram alerts disabled (set TELEGRAM_ENABLED=true + TELEGRAM_BOT_TOKEN)"
fi

# ── Prometheus metrics exporter ──────────────────────────────────────────
if [ "${PROMETHEUS_ENABLED:-false}" = "true" ]; then
    PORT="${PROMETHEUS_PORT:-9090}"
    if port_in_use "$PORT"; then warn "Prometheus port $PORT busy"
    else
        run_bg "prometheus" "prom.log" \
            python -c "from prometheus_client import start_http_server; import time; start_http_server($PORT); print('prom on $PORT');
while True: time.sleep(60)"
    fi
fi

RUN_DOCKER_DOWN=1

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
printf "${CYAN}┌────────────────────────────────────────────────────────────┐${NC}\n"
printf "${CYAN}│  FinanceLab ALL PHASES RUNNING                             │${NC}\n"
printf "${CYAN}├────────────────────────────────────────────────────────────┤${NC}\n"
printf "  Frontend     → ${GREEN}http://localhost:${WEB_PORT}${NC}\n"
printf "  API          → ${GREEN}http://localhost:${API_PORT}/api/health${NC}\n"
printf "  API docs     → ${GREEN}http://localhost:${API_PORT}/docs${NC}\n"
printf "  Markets      → ${GREEN}http://localhost:${WEB_PORT}/markets${NC}\n"
printf "  Data & AI    → ${GREEN}http://localhost:${WEB_PORT}/data${NC}\n"
printf "  Tax          → ${GREEN}http://localhost:${WEB_PORT}/tax${NC}\n"
printf "  Portfolio    → ${GREEN}http://localhost:${WEB_PORT}/portfolio${NC}\n"
printf "  Research     → ${GREEN}http://localhost:${WEB_PORT}/research${NC}\n"
printf "  Wiki         → ${GREEN}http://localhost:${WEB_PORT}/wiki${NC}\n"
command -v caddy &>/dev/null && port_in_use 8443 && printf "  Caddy HTTPS  → ${GREEN}https://localhost:8443${NC}\n"
command -v ollama &>/dev/null && printf "  Ollama       → ${GREEN}http://localhost:11434${NC}\n"
[ "${PROMETHEUS_ENABLED:-false}" = "true" ] && printf "  Prometheus   → ${GREEN}http://localhost:${PROMETHEUS_PORT:-9090}${NC}\n"
[ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ] && printf "  CF Tunnel    → ${GREEN}active (see cloudflared.log)${NC}\n"
printf "${CYAN}├────────────────────────────────────────────────────────────┤${NC}\n"
printf "  Logs         → ${YELLOW}deploy/logs/*.log${NC}\n"
printf "  Stop         → ${YELLOW}Ctrl-C${NC} (cleans up Docker + all bg procs)\n"
printf "${CYAN}└────────────────────────────────────────────────────────────┘${NC}\n"
echo ""

# Keep foreground alive until any child exits or Ctrl-C
wait
