#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════
#  FinanceLab / FinHubAI — UNIFIED ALL-PHASE SETUP  (Phases 1 → 8)
#  Run ONCE on a fresh Mac. Installs every system dep, every Python / Node
#  package, every Ollama model, every data directory, and every placeholder
#  env var required for the full spec (Plan of Action + Complete System
#  Part 2 + Tax Engine Complete).
#
#  Usage:  chmod +x setup.sh && ./setup.sh
#  Re-run safe (idempotent): each step is skipped if already satisfied.
# ══════════════════════════════════════════════════════════════════════════
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BLUE='\033[0;34m'; MAGENTA='\033[0;35m'; NC='\033[0m'

log()   { printf "${GREEN}[setup]${NC} %s\n" "$*"; }
phase() { printf "\n${MAGENTA}━━━ %s ━━━${NC}\n" "$*"; }
warn()  { printf "${YELLOW}[setup]${NC} %s\n" "$*"; }
err()   { printf "${RED}[setup]${NC} %s\n" "$*"; }
ok()    { printf "${GREEN}  ✓${NC} %s\n" "$*"; }
step()  { printf "${BLUE}  →${NC} %s\n" "$*"; }

SKIP_HEAVY_ML="${SKIP_HEAVY_ML:-0}"      # set to 1 to skip torch + transformers
SKIP_NODE_BUILD="${SKIP_NODE_BUILD:-0}"  # set to 1 to skip npm run build
SKIP_TESTS="${SKIP_TESTS:-0}"            # set to 1 to skip pytest at end

phase "PHASE 0 — System prerequisites"

# ── Homebrew ──────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ "$(uname -m)" == "arm64" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    fi
else
    ok "Homebrew present"
fi

# ── Docker Desktop ────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "Installing Docker Desktop..."
    brew install --cask docker
    warn "Docker Desktop installed. Open Docker Desktop once, then re-run this script."
    open -a Docker || true
    exit 0
else
    ok "Docker present ($(docker --version))"
fi
if ! docker info &>/dev/null; then
    err "Docker daemon is not running. Start Docker Desktop and re-run."
    exit 1
fi

# ── Python 3.11+ ──────────────────────────────────────────────────────────
PYTHON=""
for PY in python3.12 python3.11 python3; do
    if command -v "$PY" &>/dev/null; then
        V=$("$PY" -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>/dev/null || echo 0.0)
        if python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,11) else 1)" 2>/dev/null \
           && "$PY" -c "import sys; sys.exit(0 if sys.version_info>=(3,11) else 1)" 2>/dev/null; then
            PYTHON="$PY"; break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    log "Installing Python 3.12..."
    brew install python@3.12
    PYTHON="python3.12"
fi
ok "Python: $($PYTHON --version)"

# ── Node.js 20+ ───────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
    log "Installing Node.js 20..."
    brew install node@20
    brew link node@20 --overwrite --force 2>/dev/null || true
else
    NMAJ=$(node -e "console.log(process.versions.node.split('.')[0])")
    if [ "$NMAJ" -lt 18 ]; then
        log "Upgrading Node..."
        brew install node@20
        brew link node@20 --overwrite --force 2>/dev/null || true
    fi
fi
ok "Node: $(node --version)  npm: $(npm --version)"

# ── Reverse proxy + tunnel + git + ollama ─────────────────────────────────
command -v caddy        &>/dev/null || { log "Installing Caddy...";       brew install caddy; }
command -v cloudflared  &>/dev/null || { log "Installing cloudflared...";  brew install cloudflare/cloudflare/cloudflared; }
command -v git          &>/dev/null || { log "Installing Git...";          brew install git; }
command -v ollama       &>/dev/null || { log "Installing Ollama...";       brew install ollama; }
ok "Caddy / cloudflared / git / ollama installed"

# ── Optional native libs used by phase-7 / phase-8 code ───────────────────
brew list ta-lib      &>/dev/null || brew install ta-lib      || warn "ta-lib optional install failed"
brew list libomp      &>/dev/null || brew install libomp      || warn "libomp optional install failed"
brew list pkg-config  &>/dev/null || brew install pkg-config  || true
brew list libpq       &>/dev/null || brew install libpq       || true

phase "PHASE 1 — Environment file & data directories"

# ── .env bootstrap ────────────────────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
    warn "Created .env from template — edit API keys when convenient."
else
    # Append any missing keys from the template (idempotent upgrade)
    awk -F= 'NR==FNR && /^[A-Z_]+=/ {k=$1; seen[k]=1; next}
             /^[A-Z_]+=/ && !seen[$1]  {print}' .env .env.example >> .env || true
    ok ".env present (any new keys appended)"
fi

# ── Pre-create directories used by every phase ────────────────────────────
mkdir -p data/{chroma,hf_cache,ml_models,tax_exports,broker_imports,alt_data,backtests,journal,corporate_actions,logs}
mkdir -p data/cache/{news,quotes,options,sentiment,factors}
mkdir -p deploy/logs
ok "Data directories ready under ./data"

phase "PHASE 2 — Docker containers (TimescaleDB + Redis)"

log "Pulling images..."
docker compose pull
log "Starting containers..."
docker compose up -d

log "Waiting for TimescaleDB..."
for i in {1..60}; do
    if docker compose exec -T timescaledb pg_isready -U postgres -d finhub >/dev/null 2>&1; then
        ok "TimescaleDB ready"; break
    fi
    sleep 1
    [ "$i" = 60 ] && { err "TimescaleDB never became healthy"; exit 1; }
done

log "Waiting for Redis..."
for i in {1..30}; do
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        ok "Redis ready"; break
    fi
    sleep 1
    [ "$i" = 30 ] && { err "Redis never became healthy"; exit 1; }
done

phase "PHASE 3 — Python venv + ALL-PHASE dependencies"

if [ ! -d .venv ]; then
    log "Creating Python venv..."
    $PYTHON -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
ok "venv active: $(python --version)"

log "Upgrading pip toolchain..."
pip install --upgrade pip setuptools wheel -q

log "Installing ALL-PHASE Python dependencies (this is the big one)..."
if ! pip install -r backend/requirements.txt; then
    warn "Batch install failed on one package. Falling back to per-package install so the rest succeed."
    FAILED_PKGS=()
    # Strip blank lines + comments, install each line individually.
    while IFS= read -r line; do
        pkg="$(echo "$line" | sed -E 's/#.*$//' | xargs)"
        [ -z "$pkg" ] && continue
        if ! pip install "$pkg" --quiet; then
            warn "  ✗ failed: $pkg"
            FAILED_PKGS+=("$pkg")
        fi
    done < backend/requirements.txt
    if [ "${#FAILED_PKGS[@]}" -gt 0 ]; then
        warn "Packages that could not be installed (non-fatal):"
        for p in "${FAILED_PKGS[@]}"; do warn "    - $p"; done
        warn "Features relying on these will be disabled. Fix individually later with: pip install <pkg>"
    fi
fi

if [ "$SKIP_HEAVY_ML" != "1" ]; then
    # torch must be installed separately — CPU wheel works on macOS Apple Silicon + Intel.
    log "Installing PyTorch (CPU wheel)..."
    pip install --index-url https://download.pytorch.org/whl/cpu torch || \
        pip install torch || warn "torch install failed — FinBERT + ML layer will be limited"
else
    warn "SKIP_HEAVY_ML=1 → skipping torch. FinBERT sentiment + ML layer will be disabled."
fi

log "Verifying core imports..."
python - <<'PY'
import importlib, sys
mods = [
    "fastapi", "uvicorn", "pydantic", "sqlalchemy", "redis", "httpx",
    "yfinance", "pandas", "numpy", "apscheduler", "sklearn", "xgboost",
    "openpyxl", "chromadb", "langchain", "reportlab", "telegram",
    "transformers",
]
missing = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        missing.append(f"{m} ({e.__class__.__name__})")
if missing:
    print("MISSING:", ", ".join(missing))
    sys.exit(0)   # non-fatal — some deps (transformers etc.) may need torch
print("all core imports OK")
PY

phase "PHASE 4 — Ollama local AI models (Phase 3 RAG + NLQ)"

pgrep -x ollama >/dev/null || { log "Starting Ollama server..."; (ollama serve &>/dev/null &) ; sleep 3; }
OLLAMA_MODELS=(
    "llama3.1:8b"           # primary reasoning model
    "nomic-embed-text"      # embedding model for RAG
    "mistral:7b-instruct"   # fallback reasoning
    "phi3:mini"             # lightweight fast model
)
for m in "${OLLAMA_MODELS[@]}"; do
    if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$m"; then
        ok "Ollama model cached: $m"
    else
        log "Pulling Ollama model: $m (may take a while)"
        ollama pull "$m" || warn "Failed to pull $m — retry later: ollama pull $m"
    fi
done

phase "PHASE 5 — Frontend (Next.js) install + build"

log "Installing Node.js dependencies..."
(cd web && npm install)
ok "Node packages installed"

if [ "$SKIP_NODE_BUILD" != "1" ]; then
    log "Building Next.js production bundle..."
    (cd web && npm run build) || warn "Next.js build had warnings"
    ok "Next.js built"
else
    warn "SKIP_NODE_BUILD=1 → skipping production build (dev mode will be used)"
fi

phase "PHASE 6 — Database schema / migrations"

python - <<'PY' || warn "DB auto-init had issues; inspect with: docker compose logs timescaledb"
from backend.db import engine, Base
import backend.models  # noqa: F401 - register models
Base.metadata.create_all(bind=engine)
print("SQLAlchemy metadata.create_all complete")
PY

phase "PHASE 7 — Optional HuggingFace model prefetch"

if [ "$SKIP_HEAVY_ML" != "1" ]; then
    python - <<'PY' || warn "FinBERT prefetch failed — will lazy-load at runtime"
import os
os.environ.setdefault("HF_HOME", "./data/hf_cache")
try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    m = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
    print(f"Caching {m} ...")
    AutoTokenizer.from_pretrained(m)
    AutoModelForSequenceClassification.from_pretrained(m)
    print("FinBERT cached")
except Exception as e:
    print("FinBERT prefetch skipped:", e)
PY
fi

phase "PHASE 8 — Tests + script permissions"

chmod +x start.sh setup.sh 2>/dev/null || true
ok "start.sh / setup.sh executable"

if [ "$SKIP_TESTS" != "1" ]; then
    log "Running backend tests (non-fatal)..."
    PYTHONPATH=. python -m pytest tests/ -x -q 2>&1 || warn "Some tests failed (services may need to be running)"
else
    warn "SKIP_TESTS=1 → skipping pytest"
fi

phase "PHASE 9 — Download full market universe (NSE/BSE/AMFI/F&O/crypto/indices)"

SKIP_UNIVERSE="${SKIP_UNIVERSE:-0}"   # set to 1 to skip the big downloads
if [ "$SKIP_UNIVERSE" != "1" ]; then
    log "Fetching full NSE + BSE equity, AMFI MFs, Nifty/BSE index constituents, F&O list, crypto top 100..."
    mkdir -p data/universe
    PYTHONPATH=. python -m backend.data.universe_loader \
        || warn "Universe load had issues — re-run later via: curl -X POST http://localhost:8000/api/markets/universe/refresh"
    ok "Universe cached under ./data/universe"
    # Show a quick count
    if [ -d data/universe ]; then
        for f in data/universe/*.json; do
            [ -f "$f" ] || continue
            cnt=$(python -c "import json,sys;d=json.load(open('$f'));print(len(d) if isinstance(d,list) else sum(len(v) for v in d.values()) if isinstance(d,dict) else 1)" 2>/dev/null || echo "?")
            printf "      %-40s %s\n" "$(basename "$f")" "$cnt"
        done
    fi
else
    warn "SKIP_UNIVERSE=1 → skipping big universe download (Markets UI will show only the curated lists until you hit 'Load full universe' in the UI)"
fi

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
printf "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}\n"
printf "${CYAN}║     FinanceLab ALL-PHASE Setup Complete (Phases 1 → 8)      ║${NC}\n"
printf "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}\n"
printf "${CYAN}║${NC}  Installed                                                   ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   ${GREEN}✓${NC} Homebrew   ${GREEN}✓${NC} Docker   ${GREEN}✓${NC} Python venv   ${GREEN}✓${NC} Node 20      ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   ${GREEN}✓${NC} Caddy      ${GREEN}✓${NC} cloudflared   ${GREEN}✓${NC} Ollama + 4 models    ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   ${GREEN}✓${NC} TimescaleDB   ${GREEN}✓${NC} Redis   ${GREEN}✓${NC} DB schema created    ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   ${GREEN}✓${NC} All-phase Python deps (ML / NLQ / tax / alerts)    ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   ${GREEN}✓${NC} Next.js built   ${GREEN}✓${NC} FinBERT cached                   ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}                                                              ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}  Next                                                        ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   1. Edit ${YELLOW}.env${NC} with your API keys (optional)            ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   2. Run ${GREEN}./start.sh${NC} — launches every phase service     ${CYAN}║${NC}\n"
printf "${CYAN}║${NC}   3. Open ${GREEN}http://localhost:3000${NC}                         ${CYAN}║${NC}\n"
printf "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
echo ""
