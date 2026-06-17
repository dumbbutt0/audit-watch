#!/usr/bin/env bash
# setup_rust_deps.sh — best-effort provisioning of the Rust/Solana static toolchain.
#
# Mirrors setup_solidity_deps.sh but for the Rust adapter. EVERYTHING here is best-effort:
# the static adapter (compile_for_analysis_rust.sh) degrades gracefully when a tool is
# absent (it always falls back to the Solana source-pattern pass), so this script never
# hard-fails the pipeline. It only tries to make richer signal available.
#
# Installs / verifies (in priority order):
#   - rustup component clippy   (lints; the primary structured signal)
#   - cargo-audit               (RustSec advisory DB over Cargo.lock)            [optional]
#   - cargo-geiger              (unsafe-code census)                              [optional]
#
# Usage:  ./scripts/setup_rust_deps.sh [project_dir]
# Prints a one-line availability summary; exit code is always 0 (advisory).

set -uo pipefail
PROJ="${1:-}"
log() { echo "[rust-deps] $*" >&2; }

have() { command -v "$1" >/dev/null 2>&1; }

if ! have cargo; then
  log "cargo not found — install rust via https://rustup.rs (the adapter will use the source-pattern fallback only)"
  echo "RUST_TOOLCHAIN=absent CLIPPY=absent CARGO_AUDIT=absent CARGO_GEIGER=absent"
  exit 0
fi

# clippy — via rustup component if available
if ! have clippy-driver && have rustup; then
  log "installing clippy component..."
  rustup component add clippy >/dev/null 2>&1 || log "clippy install failed — continuing"
fi

# cargo-audit / cargo-geiger — optional, only if the user wants them and network allows
if [[ "${RUST_DEPS_FULL:-0}" == "1" ]]; then
  have cargo-audit  || { log "installing cargo-audit...";  cargo install cargo-audit  >/dev/null 2>&1 || log "cargo-audit install skipped"; }
  have cargo-geiger || { log "installing cargo-geiger..."; cargo install cargo-geiger >/dev/null 2>&1 || log "cargo-geiger install skipped"; }
else
  log "set RUST_DEPS_FULL=1 to also install cargo-audit + cargo-geiger (network + build time)"
fi

# fetch deps for the project so clippy can typecheck (best-effort, time-boxed)
if [[ -n "$PROJ" && -f "$PROJ/Cargo.toml" ]]; then
  log "fetching crate deps for $PROJ (timeout 180s)..."
  ( cd "$PROJ" && timeout 180 cargo fetch >/dev/null 2>&1 ) || log "cargo fetch incomplete — clippy may be source-pattern-only"
fi

clip="absent"; have clippy-driver && clip="present"
caud="absent"; have cargo-audit && caud="present"
cgei="absent"; have cargo-geiger && cgei="present"
log "summary: clippy=$clip cargo-audit=$caud cargo-geiger=$cgei"
echo "RUST_TOOLCHAIN=present CLIPPY=$clip CARGO_AUDIT=$caud CARGO_GEIGER=$cgei"
exit 0
