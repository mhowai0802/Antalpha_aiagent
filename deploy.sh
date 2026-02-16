#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# Deploy script for Crypto Trading AI Agent
# Frontend → Vercel  |  Backend → Render
# ─────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Helpers ──────────────────────────────────
info()  { printf "\033[1;34m▸ %s\033[0m\n" "$*"; }
ok()    { printf "\033[1;32m✔ %s\033[0m\n" "$*"; }
warn()  { printf "\033[1;33m⚠ %s\033[0m\n" "$*"; }
err()   { printf "\033[1;31m✖ %s\033[0m\n" "$*"; exit 1; }

# ── Pre-flight checks ───────────────────────
check_tool() {
  if ! command -v "$1" &>/dev/null; then
    err "$1 is not installed. $2"
  fi
}

# ═════════════════════════════════════════════
# 1. DEPLOY BACKEND TO RENDER
# ═════════════════════════════════════════════
deploy_backend() {
  info "Deploying backend to Render..."

  check_tool "render" "Install with: brew install render"

  # Login if needed
  info "Checking Render authentication..."
  if ! render whoami &>/dev/null 2>&1; then
    info "Please log in to Render:"
    render login
  fi
  ok "Authenticated with Render"

  # Validate the render.yaml
  info "Validating render.yaml..."
  render blueprints validate "$REPO_ROOT/render.yaml"
  ok "render.yaml is valid"

  # Check if service already exists
  info "Looking for existing crypto-agent-backend service..."
  SERVICE_ID=$(render services list --output json 2>/dev/null \
    | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    if s.get('service',{}).get('name') == 'crypto-agent-backend':
        print(s['service']['id'])
        break
" 2>/dev/null || true)

  if [ -n "$SERVICE_ID" ]; then
    ok "Found existing service: $SERVICE_ID"
    info "Triggering new deploy..."
    render deploys create "$SERVICE_ID" --wait
    ok "Backend deployed!"

    BACKEND_URL=$(render services show "$SERVICE_ID" --output json 2>/dev/null \
      | python3 -c "import sys,json; d=json.load(sys.stdin); print('https://'+d.get('service',{}).get('serviceDetails',{}).get('url',''))" 2>/dev/null || true)
    if [ -n "$BACKEND_URL" ] && [ "$BACKEND_URL" != "https://" ]; then
      ok "Backend URL: $BACKEND_URL"
    fi
  else
    warn "No existing 'crypto-agent-backend' service found on Render."
    echo ""
    echo "  First-time setup requires the Render Dashboard (one-time only):"
    echo ""
    echo "  1. Go to https://dashboard.render.com"
    echo "  2. Click 'New → Blueprint'"
    echo "  3. Connect this GitHub repo"
    echo "  4. Render will detect render.yaml and create the service"
    echo "  5. Set secret env vars: HKBU_API_KEY, MONGODB_URI, FRONTEND_URL"
    echo "  6. Click 'Deploy Blueprint'"
    echo ""
    echo "  After initial setup, re-run this script to deploy via CLI."
    echo ""
    read -rp "Press Enter after completing dashboard setup (or Ctrl+C to skip)..."
  fi
}

# ═════════════════════════════════════════════
# 2. DEPLOY FRONTEND TO VERCEL
# ═════════════════════════════════════════════
deploy_frontend() {
  info "Deploying frontend to Vercel..."

  check_tool "vercel" "Install with: npm install -g vercel"

  cd "$REPO_ROOT/frontend"

  # Login if needed
  info "Checking Vercel authentication..."
  if ! vercel whoami &>/dev/null 2>&1; then
    info "Please log in to Vercel:"
    vercel login
  fi
  ok "Authenticated with Vercel"

  # Prompt for backend URL if VITE_API_URL not set
  if [ -z "${VITE_API_URL:-}" ]; then
    echo ""
    read -rp "Enter your Render backend URL (e.g. https://crypto-agent-backend.onrender.com): " VITE_API_URL
    if [ -z "$VITE_API_URL" ]; then
      err "Backend URL is required for the frontend to work."
    fi
  fi

  # Set env var on Vercel
  info "Setting VITE_API_URL=$VITE_API_URL on Vercel..."
  echo "$VITE_API_URL" | vercel env add VITE_API_URL production --force 2>/dev/null || true

  # Deploy to production
  info "Building and deploying to production..."
  FRONTEND_URL=$(vercel deploy --prod --yes 2>&1 | tail -1)
  ok "Frontend deployed!"
  ok "Frontend URL: $FRONTEND_URL"

  echo ""
  echo "  ╔══════════════════════════════════════════════════╗"
  echo "  ║  IMPORTANT: Set FRONTEND_URL on Render          ║"
  echo "  ║                                                  ║"
  echo "  ║  Go to your Render service → Environment        ║"
  echo "  ║  Set FRONTEND_URL = $FRONTEND_URL"
  echo "  ║  Then redeploy the backend for CORS to work.    ║"
  echo "  ╚══════════════════════════════════════════════════╝"
  echo ""
}

# ═════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════
echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Crypto Agent - Deploy to Production    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

case "${1:-all}" in
  backend)
    deploy_backend
    ;;
  frontend)
    deploy_frontend
    ;;
  all)
    deploy_backend
    deploy_frontend
    ;;
  *)
    echo "Usage: $0 [backend|frontend|all]"
    echo ""
    echo "  backend   - Deploy backend to Render"
    echo "  frontend  - Deploy frontend to Vercel"
    echo "  all       - Deploy both (default)"
    exit 1
    ;;
esac

echo ""
ok "Done! Your demo is live."
