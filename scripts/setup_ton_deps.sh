#!/usr/bin/env bash
# setup_ton_deps.sh — install the TON/FunC PoC toolchain (Blueprint + @ton/sandbox stack) for a target repo.
#
# TON's FunC compiler and the in-process TVM ship as npm packages via Blueprint, so "setup" = `npm install`
# inside a Blueprint project. Most TON bounty repos (e.g. ston-fi/dex-core-v2) already declare these as
# devDependencies; this just installs them. PoCs then run with `npx blueprint test` / `npx jest` — local,
# in-process, NO network/keys/testnet.
#
# Usage:  bash scripts/setup_ton_deps.sh [target_repo_dir]
#   target_repo_dir defaults to the active audit's contract repo root if it is a Blueprint project,
#   else the current directory.
set -euo pipefail

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  REPO="$(pwd)"
fi
if [[ ! -d "$REPO" ]]; then
  echo "[setup-ton] not a directory: $REPO" >&2
  exit 1
fi

echo "[setup-ton] node: $(node --version 2>/dev/null || echo 'MISSING — install Node >=18')"
echo "[setup-ton] npm:  $(npm --version 2>/dev/null || echo 'MISSING')"

if [[ -f "$REPO/package.json" ]]; then
  echo "[setup-ton] installing project deps in $REPO (Blueprint + @ton/sandbox + @ton/test-utils + funcbox)…"
  ( cd "$REPO" && npm install )
else
  echo "[setup-ton] no package.json in $REPO — scaffolding a standalone PoC project from templates/ton_poc/"
  TPL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/templates/ton_poc"
  cp "$TPL/package.json" "$TPL/jest.config.js" "$TPL/tsconfig.json" "$REPO/" 2>/dev/null || true
  mkdir -p "$REPO/tests" && cp "$TPL/tests/poc.spec.ts" "$REPO/tests/" 2>/dev/null || true
  ( cd "$REPO" && npm install )
fi

echo "[setup-ton] done. Run a PoC with:  ( cd $REPO && npx blueprint test )   or   npx jest"
echo "[setup-ton] (local @ton/sandbox only — no broadcasts, no keys, no testnet/mainnet)"
