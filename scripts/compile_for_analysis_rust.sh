#!/usr/bin/env bash
# compile_for_analysis_rust.sh — Rust/Solana counterpart of compile_for_analysis.sh.
#
# Runs the available Rust static tools over a Solana/Anchor project and emits a single
# NORMALIZED JSON ({"tool_findings":[...], "layer":N, "tools":{...}}) that
# tools/static_analysis_rust.py folds into the SHARED static.json schema. Layered fallback
# so a missing toolchain never blocks analysis:
#   Layer 1: cargo clippy --message-format=json  (structured lints over the whole workspace)
#   Layer 2: cargo check --message-format=json    (compiler diagnostics only, if clippy absent)
#   Layer 3: none — emit empty tool_findings; the Python adapter's Solana source-pattern pass
#            (always run, independent of this script) carries the signal.
# Plus, best-effort and additive: cargo-audit (advisory DB) and cargo-geiger (unsafe census).
#
# Usage:   ./scripts/compile_for_analysis_rust.sh <project_dir> [output_json]
# Output:  writes normalized JSON to <output_json> (default /tmp/rust_static_<name>.json);
#          prints LAYER=<n> and RUST_STATIC_JSON=<path> for callers to parse.

set -uo pipefail
PROJ="${1:-}"
[[ -z "$PROJ" ]] && { echo "Usage: $0 <project_dir> [output_json]" >&2; exit 2; }
PROJ="$(realpath "$PROJ")"
[[ -d "$PROJ" ]] || { echo "[rust-compile] not a directory: $PROJ" >&2; exit 2; }
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="$(basename "$PROJ")"
OUT_JSON="${2:-/tmp/rust_static_${NAME}.json}"
log() { echo "[rust-compile] $*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

# Locate the Cargo workspace/package root (walk down to the first Cargo.toml if needed).
CARGO_DIR="$PROJ"
if [[ ! -f "$CARGO_DIR/Cargo.toml" ]]; then
  found="$(find "$PROJ" -name Cargo.toml -not -path '*/target/*' 2>/dev/null | head -1)"
  [[ -n "$found" ]] && CARGO_DIR="$(dirname "$found")"
fi
log "cargo dir: $CARGO_DIR"

CLIPPY_RAW="$(mktemp)"; CHECK_RAW="$(mktemp)"; AUDIT_RAW="$(mktemp)"; GEIGER_RAW="$(mktemp)"
LAYER=3
CLIPPY_OK=false; CHECK_OK=false

if have cargo && [[ -f "$CARGO_DIR/Cargo.toml" ]]; then
  if have clippy-driver; then
    log "Layer 1: cargo clippy (json)..."
    ( cd "$CARGO_DIR" && timeout 600 cargo clippy --message-format=json --workspace --all-targets 2>/dev/null ) >"$CLIPPY_RAW" || true
    [[ -s "$CLIPPY_RAW" ]] && { CLIPPY_OK=true; LAYER=1; }
  fi
  if [[ "$CLIPPY_OK" != true ]]; then
    log "Layer 2: cargo check (json)..."
    ( cd "$CARGO_DIR" && timeout 600 cargo check --message-format=json --workspace 2>/dev/null ) >"$CHECK_RAW" || true
    [[ -s "$CHECK_RAW" ]] && { CHECK_OK=true; LAYER=2; }
  fi
  # additive, best-effort
  if have cargo-audit; then ( cd "$CARGO_DIR" && timeout 120 cargo audit --json 2>/dev/null ) >"$AUDIT_RAW" || true; fi
  if have cargo-geiger; then ( cd "$CARGO_DIR" && timeout 300 cargo geiger --output-format Json 2>/dev/null ) >"$GEIGER_RAW" || true; fi
else
  log "Layer 3: no cargo toolchain — source-pattern pass (in the Python adapter) only"
fi

CLIPPY_RAW="$CLIPPY_RAW" CHECK_RAW="$CHECK_RAW" AUDIT_RAW="$AUDIT_RAW" GEIGER_RAW="$GEIGER_RAW" \
LAYER="$LAYER" OUT_JSON="$OUT_JSON" CARGO_DIR="$CARGO_DIR" python3 - <<'PY'
import json, os
def lines(p):
    try:
        with open(p) as f:
            return [l for l in f if l.strip()]
    except Exception:
        return []

findings = []
# clippy/check JSON: stream of {"reason":"compiler-message","message":{...}}
for raw in (os.environ["CLIPPY_RAW"], os.environ["CHECK_RAW"]):
    for l in lines(raw):
        try:
            obj = json.loads(l)
        except Exception:
            continue
        if obj.get("reason") != "compiler-message":
            continue
        m = obj.get("message", {})
        level = m.get("level")              # error|warning|note
        if level not in ("error", "warning"):
            continue
        code = (m.get("code") or {}).get("code") or ""
        spans = m.get("spans") or []
        primary = next((s for s in spans if s.get("is_primary")), spans[0] if spans else {})
        findings.append({
            "tool": "clippy" if code.startswith("clippy::") else "cargo",
            "check": code or level,
            "severity": "High" if level == "error" else "Medium",
            "message": (m.get("message") or "")[:300],
            "file": primary.get("file_name"),
            "line": primary.get("line_start"),
        })

# cargo-audit advisories
for l in lines(os.environ["AUDIT_RAW"]):
    try:
        d = json.loads(l)
    except Exception:
        continue
    for v in (d.get("vulnerabilities", {}) or {}).get("list", []) or []:
        adv = v.get("advisory", {})
        findings.append({"tool": "cargo-audit", "check": adv.get("id", "RUSTSEC"),
                         "severity": "High", "message": (adv.get("title") or "")[:300],
                         "file": (v.get("package", {}) or {}).get("name"), "line": None})

out = {
    "layer": int(os.environ["LAYER"]),
    "cargo_dir": os.environ["CARGO_DIR"],
    "tools": {
        "clippy": bool(lines(os.environ["CLIPPY_RAW"])),
        "cargo_check": bool(lines(os.environ["CHECK_RAW"])),
        "cargo_audit": bool(lines(os.environ["AUDIT_RAW"])),
        "cargo_geiger": bool(lines(os.environ["GEIGER_RAW"])),
    },
    "tool_findings": findings,
}
with open(os.environ["OUT_JSON"], "w") as f:
    json.dump(out, f, indent=2)
PY

rm -f "$CLIPPY_RAW" "$CHECK_RAW" "$AUDIT_RAW" "$GEIGER_RAW"
echo "LAYER=$LAYER" >&2
echo "RUST_STATIC_JSON=$OUT_JSON"
exit 0
