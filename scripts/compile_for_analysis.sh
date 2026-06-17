#!/usr/bin/env bash
# compile_for_analysis.sh — Reliably compile a Solidity project for static analysis.
#
# Implements a layered fallback so a stack-too-deep / memoryguard contract never
# blocks analysis again:
#   Layer 1: forge build under [profile.audit] (project's pinned solc, via_ir=false)
#   Layer 2: retry with via_ir=true (env override, no file mutation)
#   Layer 3: AST-only — generate an aggregator that imports every in-scope contract,
#            run slither with `solc --stop-after parsing` (skips codegen entirely)
#
# Runs slither once on the WHOLE project (never per-file) and writes detector JSON.
#
# Usage:
#   ./scripts/compile_for_analysis.sh <protocol_dir> [output_json]
#
# Output:
#   Writes slither JSON to <output_json> (default /tmp/slither_<name>.json).
#   Prints "LAYER=<n>" and "SLITHER_JSON=<path>" on success for callers to parse.

set -uo pipefail

PROTO="${1:-}"
if [[ -z "$PROTO" ]]; then
  echo "Usage: $0 <protocol_dir> [output_json]" >&2
  exit 2
fi
PROTO="$(realpath "$PROTO")"
[[ -d "$PROTO" ]] || { echo "[compile] not a directory: $PROTO" >&2; exit 2; }

NAME="$(basename "$(dirname "$PROTO")")_$(basename "$PROTO")"
OUT_JSON="${2:-/tmp/slither_${NAME}.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILTER_PATHS="node_modules,mocks,test,lib,script"

log() { echo "[compile] $*" >&2; }

# ── Ensure dependencies are present ──────────────────────────────────────────
if [[ ! -d "$PROTO/node_modules" && ! -d "$PROTO/lib" ]]; then
  log "No node_modules/lib — running setup_solidity_deps.sh"
  "$SCRIPT_DIR/setup_solidity_deps.sh" "$PROTO" || log "dep setup returned nonzero — continuing"
fi

# ── Ensure an [profile.audit] exists ─────────────────────────────────────────
FTOML="$PROTO/foundry.toml"
if [[ -f "$FTOML" ]] && ! grep -q "\[profile\.audit\]" "$FTOML"; then
  log "No [profile.audit] in foundry.toml — running setup_solidity_deps.sh to add it"
  "$SCRIPT_DIR/setup_solidity_deps.sh" "$PROTO" || true
fi

# slither exits nonzero when it finds issues; success is judged by valid JSON.
json_ok() {
  python3 -c "
import json,sys
try:
    d=json.load(open('$1'))
    dets=d.get('results',{}).get('detectors',[])
    sys.exit(0 if (d.get('success') or dets) else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null
}

run_slither_framework() {
  local via_ir="$1"
  rm -f "$OUT_JSON"
  ( cd "$PROTO" && \
    FOUNDRY_PROFILE=audit FOUNDRY_VIA_IR="$via_ir" \
    slither . --filter-paths "$FILTER_PATHS" --json "$OUT_JSON" --disable-color \
    > /tmp/compile_slither.log 2>&1 )
  json_ok "$OUT_JSON"
}

# ── Layer 1: project-exact config (via_ir=false) ─────────────────────────────
log "Layer 1: forge/slither with project-pinned config (via_ir=false)..."
if run_slither_framework "false"; then
  log "Layer 1 succeeded."
  echo "LAYER=1"
  echo "SLITHER_JSON=$OUT_JSON"
  exit 0
fi
log "Layer 1 failed (see /tmp/compile_slither.log)."

# ── Layer 2: via_ir=true ─────────────────────────────────────────────────────
log "Layer 2: retry with via_ir=true..."
if run_slither_framework "true"; then
  log "Layer 2 succeeded."
  echo "LAYER=2"
  echo "SLITHER_JSON=$OUT_JSON"
  exit 0
fi
log "Layer 2 failed."

# ── Layer 3: AST-only (aggregator + solc --stop-after parsing) ───────────────
log "Layer 3: AST-only compile (no codegen — stack-too-deep impossible)..."

AGG="$PROTO/contracts/AuditAggregator.sol"
python3 - "$PROTO" "$AGG" << 'PYEOF'
import sys, os
from pathlib import Path
proto, agg = Path(sys.argv[1]), Path(sys.argv[2])
src = proto / "contracts"
EXCLUDE = ("mocks/", "test/", "/test", "interfaces/")
lines = ["// SPDX-License-Identifier: MIT", "pragma solidity ^0.8.0;", ""]
n = 0
for f in sorted(src.rglob("*.sol")):
    rel = f.relative_to(proto).as_posix()
    low = rel.lower()
    if any(x in low for x in EXCLUDE):
        continue
    if f.name == "AuditAggregator.sol":
        continue
    lines.append(f'import "{rel}";')
    n += 1
agg.write_text("\n".join(lines) + "\n")
print(f"[compile] aggregator imports {n} contracts", file=sys.stderr)
PYEOF

# Build remap string from remappings.txt (resolved to absolute paths)
REMAPS=$(python3 - "$PROTO" << 'PYEOF'
import sys
from pathlib import Path
proto = Path(sys.argv[1])
out = []
rmf = proto / "remappings.txt"
if rmf.exists():
    for line in rmf.read_text().splitlines():
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            pre, tgt = line.split("=", 1)
            abs_t = str((proto / tgt).resolve())
            if not abs_t.endswith("/"):
                abs_t += "/"
            out.append(f"{pre}={abs_t}")
# Ensure common scopes are mapped even if remappings.txt is incomplete
nm = proto / "node_modules"
if nm.is_dir():
    for scope in sorted(nm.glob("@*")):
        pref = scope.name + "/"
        if not any(o.startswith(pref) for o in out):
            out.append(f"{pref}={scope}/")
print(" ".join(out))
PYEOF
)

rm -f "$OUT_JSON"
( cd "$PROTO" && \
  slither contracts/AuditAggregator.sol \
    --compile-force-framework solc \
    --solc-args "--stop-after parsing --allow-paths ${PROTO}" \
    --solc-remaps "$REMAPS" \
    --filter-paths "$FILTER_PATHS" \
    --json "$OUT_JSON" --disable-color \
    > /tmp/compile_slither_ast.log 2>&1 )

# Clean up the aggregator (it's a build artifact, not source)
rm -f "$AGG"

if json_ok "$OUT_JSON"; then
  log "Layer 3 (AST-only) succeeded."
  echo "LAYER=3"
  echo "SLITHER_JSON=$OUT_JSON"
  exit 0
fi

log "ALL LAYERS FAILED. See /tmp/compile_slither.log and /tmp/compile_slither_ast.log"
exit 1
