#!/usr/bin/env bash
# Lean live deploy to Alpaca PAPER only. Never pass live keys.
# Required env (paper):
#   ALPACA_API_KEY
#   ALPACA_API_SECRET
# Optional:
#   ALPACA_DATA_FEED=iex|sip  (paper usually iex)
set -euo pipefail

if [[ "${ALPACA_LIVE:-}" == "1" ]]; then
  echo "Refusing: ALPACA_LIVE=1. This script is paper-only." >&2
  exit 1
fi
: "${ALPACA_API_KEY:?Set ALPACA_API_KEY (paper key)}"
: "${ALPACA_API_SECRET:?Set ALPACA_API_SECRET (paper secret)}"

echo "Deploying to Alpaca PAPER via Lean CLI..."
lean live deploy . \
  --brokerage "Alpaca" \
  --alpaca-environment Paper \
  --alpaca-api-key "$ALPACA_API_KEY" \
  --alpaca-api-secret "$ALPACA_API_SECRET"
