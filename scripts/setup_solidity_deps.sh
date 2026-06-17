#!/usr/bin/env bash
# setup_solidity_deps.sh — Install Solidity project dependencies for audit
#
# Usage:
#   ./scripts/setup_solidity_deps.sh <protocol_dir>
#
# What it does:
#   1. Scans all .sol files under <protocol_dir>/contracts/ for @-prefixed imports
#   2. Reads package.json for declared dep versions / git URLs
#   3. Installs each package to <protocol_dir>/node_modules/ (copies, never symlinks)
#   4. Clones git-sourced packages (e.g. uniswap 0.8-branch) directly
#   5. Patches pragma upper bounds (<0.8.0 → remove cap) so forge compiles under 0.8.x
#   6. Handles forge submodule deps (forge-std) via git clone
#   7. Runs `forge build` with FOUNDRY_PROFILE=audit to confirm success
#
# Requirements: npm, git, forge, python3

set -euo pipefail

PROTO="${1:-}"
if [[ -z "$PROTO" ]]; then
  echo "Usage: $0 <protocol_dir>"
  exit 1
fi
PROTO="$(realpath "$PROTO")"
NM="$PROTO/node_modules"

log()  { echo "[deps] $*"; }
warn() { echo "[deps] WARNING: $*" >&2; }

# ── 1. Read declared deps from package.json ──────────────────────────────────
PKG="$PROTO/package.json"
if [[ ! -f "$PKG" ]]; then
  warn "No package.json found at $PROTO — skipping npm step"
fi

# ── 2. Ensure forge-std submodule / lib ──────────────────────────────────────
FORGESTD="$PROTO/lib/forge-std"
if [[ ! -f "$FORGESTD/src/Test.sol" ]]; then
  log "Cloning forge-std..."
  rm -rf "$FORGESTD"
  git clone --depth 1 https://github.com/foundry-rs/forge-std "$FORGESTD" 2>&1 | tail -2
else
  log "forge-std already present"
fi

# ── 3. Helper: install an npm package (real copy, no symlinks) ───────────────
npm_install_copy() {
  local pkg="$1"
  local ver="$2"
  local dest_scope
  dest_scope="$(dirname "$pkg")"    # e.g. @openzeppelin
  local TMP
  TMP="$(mktemp -d)"
  log "  npm install $pkg@$ver -> $NM/$pkg"
  npm install --prefix "$TMP" "${pkg}@${ver}" --prefer-offline 2>&1 | grep -v "^npm warn" | tail -3 || true
  mkdir -p "$NM/$dest_scope"
  local basename_pkg
  basename_pkg="$(basename "$pkg")"
  if [[ -d "$TMP/node_modules/$pkg" ]]; then
    rm -rf "$NM/$pkg"
    cp -r "$TMP/node_modules/$pkg" "$NM/$pkg"
    # also pull in any transitive deps this package needs into our node_modules
    if [[ -d "$TMP/node_modules" ]]; then
      for d in "$TMP/node_modules"/*/; do
        local dname
        dname="$(basename "$d")"
        if [[ "$dname" != "$dest_scope" && ! -d "$NM/$dname" ]]; then
          cp -r "$d" "$NM/$dname" 2>/dev/null || true
        fi
      done
      for d in "$TMP/node_modules/@"*/*/; do
        local scope basepkg full
        scope="$(basename "$(dirname "$d")")"
        basepkg="$(basename "$d")"
        full="$scope/$basepkg"
        if [[ "$full" != "$pkg" && ! -d "$NM/$full" ]]; then
          mkdir -p "$NM/$scope"
          cp -r "$d" "$NM/$scope/$basepkg" 2>/dev/null || true
        fi
      done
    fi
  else
    warn "  $pkg not found in npm output — skipping"
  fi
  rm -rf "$TMP"
}

# ── 4. Helper: install a git-sourced package (clone, real copy) ──────────────
git_install_copy() {
  local pkg="$1"
  local url="$2"
  local branch_or_commit="${3:-}"
  log "  git clone $url${branch_or_commit:+ (${branch_or_commit})} -> $NM/$pkg"
  local TMP
  TMP="$(mktemp -d)"
  if [[ -n "$branch_or_commit" && ${#branch_or_commit} -lt 20 ]]; then
    # short string = branch name
    git clone --depth 1 --branch "$branch_or_commit" "$url" "$TMP/repo" 2>&1 | tail -2
  elif [[ -n "$branch_or_commit" ]]; then
    # long string = commit hash
    git clone "$url" "$TMP/repo" 2>&1 | tail -2
    git -C "$TMP/repo" checkout "$branch_or_commit" 2>&1 | tail -2
  else
    git clone --depth 1 "$url" "$TMP/repo" 2>&1 | tail -2
  fi
  local scope
  scope="$(dirname "$pkg")"
  mkdir -p "$NM/$scope"
  rm -rf "$NM/$pkg"
  cp -r "$TMP/repo" "$NM/$pkg"
  rm -rf "$TMP"
}

# ── 5. Patch pragma upper bounds (in-place, non-destructive for 0.8.x) ───────
patch_pragma() {
  local dir="$1"
  local count=0
  while IFS= read -r -d '' f; do
    if grep -q "pragma solidity.*<0\.8\." "$f" 2>/dev/null; then
      sed -i \
        -e 's/pragma solidity >=0\.4\.0 <0\.8\.0/pragma solidity >=0.4.0/g' \
        -e 's/pragma solidity >=0\.5\.0 <0\.8\.0/pragma solidity >=0.5.0/g' \
        -e 's/pragma solidity >=0\.6\.0 <0\.8\.0/pragma solidity >=0.6.0/g' \
        -e 's/pragma solidity >=0\.7\.0 <0\.8\.0/pragma solidity >=0.7.0/g' \
        -e 's/pragma solidity =0\.7\.6/pragma solidity >=0.7.6/g' \
        "$f"
      count=$((count + 1))
    fi
  done < <(find "$dir" -name "*.sol" -print0 2>/dev/null)
  [[ $count -gt 0 ]] && log "  patched $count files with <0.8.x pragma caps in $dir"
}

# ── 6. Read package.json and install each dep ────────────────────────────────
log "Parsing $PKG for Solidity dependencies..."
python3 - "$PKG" "$NM" << 'PYEOF'
import json, sys, os, subprocess, shutil, re

pkg_json = sys.argv[1]
nm = sys.argv[2]

with open(pkg_json) as f:
    data = json.load(f)

deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

# Only Solidity-relevant packages (skip JS tooling)
SOL_SCOPES = {"@openzeppelin", "@uniswap", "@beanstalk", "@prb", "@aave",
              "@chainlink", "@compound", "@balancer", "@rari-capital"}

for pkg, ver in deps.items():
    scope = pkg.split("/")[0] if "/" in pkg else ""
    if scope not in SOL_SCOPES:
        continue

    dest = os.path.join(nm, pkg)
    if os.path.isdir(dest):
        print(f"  [skip] {pkg} already installed")
        continue

    # Detect git-sourced packages
    git_match = re.match(r'https://github\.com/([^/]+/[^/.]+)(?:\.git)?(?:#(.+))?', ver)
    if git_match:
        # Emit a marker file for the bash layer to pick up
        scope_dir = os.path.dirname(dest)
        os.makedirs(scope_dir, exist_ok=True)
        marker = dest + ".git-install"
        with open(marker, "w") as mf:
            repo = f"https://github.com/{git_match.group(1)}.git"
            ref = git_match.group(2) or ""
            mf.write(f"{repo}\t{ref}\n")
        print(f"  [git] {pkg} <- {repo} @ {ref or 'HEAD'}")
    else:
        # Strip 'v' prefix from version if present
        ver_clean = ver.lstrip("v") if ver.startswith("v") else ver
        print(f"  [npm] {pkg}@{ver_clean}")
        scope_dir = os.path.dirname(dest)
        os.makedirs(scope_dir, exist_ok=True)
        tmp = dest + ".tmp"
        result = subprocess.run(
            ["npm", "install", "--prefix", tmp, f"{pkg}@{ver_clean}", "--prefer-offline"],
            capture_output=True, text=True
        )
        src = os.path.join(tmp, "node_modules", pkg)
        if os.path.isdir(src):
            shutil.copytree(src, dest)
            # pull in transitive deps
            nm_tmp = os.path.join(tmp, "node_modules")
            for entry in os.listdir(nm_tmp):
                if entry.startswith("@"):
                    for sub in os.listdir(os.path.join(nm_tmp, entry)):
                        full = f"{entry}/{sub}"
                        if full != pkg and not os.path.exists(os.path.join(nm, full)):
                            os.makedirs(os.path.join(nm, entry), exist_ok=True)
                            shutil.copytree(os.path.join(nm_tmp, entry, sub),
                                            os.path.join(nm, full))
                elif not os.path.exists(os.path.join(nm, entry)):
                    shutil.copytree(os.path.join(nm_tmp, entry),
                                    os.path.join(nm, entry))
        else:
            print(f"  [warn] {pkg} not in npm output")
        shutil.rmtree(tmp, ignore_errors=True)

PYEOF

# Process git-install markers left by Python
while IFS= read -r -d '' marker; do
  pkg="${marker%.git-install}"
  pkg="${pkg#"$NM"/}"
  IFS=$'\t' read -r url ref < "$marker"
  rm -f "$marker"
  if [[ -d "$NM/$pkg" ]]; then
    log "  [skip] $pkg (git) already installed"
    continue
  fi
  git_install_copy "$pkg" "$url" "$ref"
done < <(find "$NM" -name "*.git-install" -print0 2>/dev/null)

# ── 7. Patch pragma caps in all installed node_modules Solidity files ─────────
log "Patching pragma upper bounds in node_modules..."
patch_pragma "$NM"

# ── 8. Detect the project's pinned solc version ──────────────────────────────
# Priority: hardhat.config(.js|.ts) `version:` → foundry.toml solc → highest pragma.
# Matching the CI compiler avoids the auto-detect trap (forge picks the newest
# installed solc, whose codegen may stack-too-deep where the pinned version does not).
detect_solc_version() {
  local v=""
  for hh in "$PROTO/hardhat.config.js" "$PROTO/hardhat.config.ts"; do
    if [[ -f "$hh" ]]; then
      v="$(grep -oE 'version:\s*"[0-9]+\.[0-9]+\.[0-9]+"' "$hh" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)"
      [[ -n "$v" ]] && { echo "$v"; return; }
    fi
  done
  if [[ -f "$PROTO/foundry.toml" ]]; then
    v="$(grep -oE "solc(_version)?\s*=\s*['\"][0-9]+\.[0-9]+\.[0-9]+['\"]" "$PROTO/foundry.toml" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
    [[ -n "$v" ]] && { echo "$v"; return; }
  fi
  # Fallback: highest concrete pragma in contracts/
  v="$(grep -rhoE 'pragma solidity[^;]*[0-9]+\.[0-9]+\.[0-9]+' "$PROTO/contracts" 2>/dev/null \
        | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)"
  echo "$v"
}

SOLC_VER="$(detect_solc_version)"
if [[ -n "$SOLC_VER" ]]; then
  log "Detected project solc version: $SOLC_VER"
  solc-select install "$SOLC_VER" 2>/dev/null || true
else
  warn "Could not detect a pinned solc version — forge will auto-detect (may stack-too-deep)"
fi

# ── 9. Add audit profile to foundry.toml if missing ──────────────────────────
# via_ir=false matches typical CI; compile_for_analysis.sh flips it on as Layer 2
# only if the pinned-config build stack-too-deeps.
FTOML="$PROTO/foundry.toml"
if [[ -f "$FTOML" ]] && ! grep -q "\[profile\.audit\]" "$FTOML"; then
  log "Adding [profile.audit] to foundry.toml (solc=${SOLC_VER:-auto}, via_ir=false)..."
  {
    echo ""
    echo "[profile.audit]"
    echo "src = 'contracts'"
    echo "test = 'test_nonexistent'"
    echo "script = 'script_nonexistent'"
    echo "out = 'out'"
    echo "libs = ['node_modules', 'lib']"
    echo "evm_version = 'shanghai'"
    [[ -n "$SOLC_VER" ]] && echo "solc = '$SOLC_VER'"
    echo "optimizer = true"
    echo "optimizer_runs = 100"
    echo "via_ir = false"
    echo "ignored_error_codes = [2462]"
  } >> "$FTOML"
fi

# ── 10. Smoke-test build (non-fatal — compile_for_analysis.sh owns the fallback ladder) ──
log "Smoke-testing forge build (FOUNDRY_PROFILE=audit)..."
cd "$PROTO"
if FOUNDRY_PROFILE=audit forge build 2>&1 | grep -qE "Unable to resolve imports|Source .* not found"; then
  warn "Unresolved imports remain — a dependency is still missing. Check output above."
  exit 1
fi
log "Dependencies resolve. Compile + analyze with:"
log "  ./scripts/compile_for_analysis.sh $PROTO"
