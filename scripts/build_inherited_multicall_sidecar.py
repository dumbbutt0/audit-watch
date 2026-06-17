#!/usr/bin/env python3
"""
build_inherited_multicall_sidecar.py — B1 MULTICALL-ONLY inherited-executor sidecar (RESEARCH-ONLY, ISOLATED).

Purpose: emit `inherited_executors.json`, a sidecar that attributes a KNOWN inherited Solidity-level multicall
executor (OZ / Uniswap-v3-periphery / in-repo `base/Multicall`) to the in-scope contracts that derive from it
(`contract X is ..., Multicall, ...`). The research-only `multicall_invariant` audit runner can OPTIONALLY merge
this sidecar at read-time (`--inherited-sidecar`) so it can SEE inherited multicall executors that the per-file
manifest builder never attributes to the deriving contract (the B1 visibility gap).

ISOLATION / SAFETY:
- Reads the canonical coverage_manifest.json READ-ONLY (only to learn which files are in scope). NEVER writes it.
- Output is a SEPARATE file. It is NOT a manifest, NOT consumed by the Step 3.9 coverage gate, NOT routed.
- Every entry is tagged synthetic_attribution:true / source_kind:"inherited_multicall_sidecar" / research_only:true.

SUPPORTED (allowlist + structural gate): OZ Multicall, UniV3 Multicall, in-repo Solidity-level Multicall bases
using `bytes[]` + `address(this).delegatecall` (or OZ `Address.functionDelegateCall(address(this), ...)`) in a
parenthesised loop. EXPLICITLY UNSUPPORTED (skipped, not guessed): solady `Multicallable` assembly delegatecall,
arbitrary inheritance, diamond/facet inheritance, typed-struct dispatch, internal-call batch systems.

Fail-safe: if inheritance can't be resolved, the base source can't be read, or pattern confidence is low → SKIP.

Usage:
  python scripts/build_inherited_multicall_sidecar.py --manifest <coverage_manifest.json> \
      [--workspace-root <dir>] --out inherited_executors.json [--quiet]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Base CONTRACT names we will attribute. Solidity-level multicall bases are named "Multicall" across OZ / UniV3 /
# common in-repo forks. "Multicallable" (solady/solmate, assembly) is deliberately EXCLUDED.
BASE_ALLOWLIST = frozenset({"Multicall"})

_TYPE_DECL = re.compile(r"\b(?:abstract\s+contract|contract)\s+([A-Za-z_]\w*)\s+is\s+([^{]+)\{")
_CONTRACT_MULTICALL = re.compile(r"\b(?:abstract\s+contract|contract)\s+Multicall\b")
_FUNC_MC = re.compile(r"\bfunction\s+multicall\s*\(")
_IMPORT_RE = re.compile(r'import\s+(?:\{[^}]*\}\s+from\s+)?["\']([^"\']+)["\']')
_LOOP_RE = re.compile(r"\b(for|while)\s*\(")
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


def _read(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _brace_body(lines: list[str], start_idx: int) -> tuple[str, int, int, str]:
    """From a line containing a function signature, gather sig until '{', then brace-match the body.
    Returns (signature, start_line_1based, end_line_1based, body_text). ('' , 0, 0, '') if no body."""
    n = len(lines)
    sig_parts, i, opened = [], start_idx, False
    while i < n and i - start_idx <= 25:
        sig_parts.append(lines[i])
        if "{" in lines[i]:
            opened = True
            break
        if ";" in lines[i]:
            return "", 0, 0, ""
        i += 1
    if not opened:
        return "", 0, 0, ""
    sig = " ".join(s.strip() for s in sig_parts).split("{", 1)[0].strip()
    depth, j, body = 0, i, []
    while j < n:
        body.append(lines[j])
        depth += lines[j].count("{") - lines[j].count("}")
        if depth <= 0 and "{" in "".join(body):
            return sig, start_idx + 1, j + 1, "\n".join(body)
        j += 1
        if j - i > 2000:
            break
    return sig, start_idx + 1, min(j, n), "\n".join(body)


def is_solidity_multicall(signature: str, body: str) -> bool:
    """Structural confidence gate: a Solidity-level bytes[] + address(this).delegatecall loop multicall.
    Excludes assembly multicalls (solady uses `address()` + assembly `for {}` — no literal address(this),
    no parenthesised loop) and any low-confidence base."""
    sig = (signature or "").lower()
    b = _strip_comments(body or "").lower()
    has_bytes_array = "bytes[]" in sig or "bytes[]" in b
    has_self = "address(this)" in b or "address (this)" in b
    has_delegate = "delegatecall" in b or "functiondelegatecall" in b
    has_paren_loop = bool(_LOOP_RE.search(b))
    return has_bytes_array and has_self and has_delegate and has_paren_loop


def _sol_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".sol" else []
    return sorted(p for p in root.rglob("*.sol") if p.is_file())


def find_base_multicalls(root: Path) -> list[dict]:
    """Find every file under root that defines `contract Multicall` with a Solidity-level multicall(bytes[])."""
    out = []
    for f in _sol_files(root):
        lines = _read(f)
        if not lines:
            continue
        src = "\n".join(lines)
        if not _CONTRACT_MULTICALL.search(src):
            continue
        for idx, ln in enumerate(lines):
            if ln.lstrip().startswith(("//", "*", "/*", "///")):
                continue
            if _FUNC_MC.search(ln):
                sig, s, e, body = _brace_body(lines, idx)
                if body and is_solidity_multicall(sig, body):
                    rel = _rel(f)
                    out.append({
                        "base_source_file": rel, "base_contract": "Multicall",
                        "signature": sig, "start_line": s, "end_line": e,
                        "body_hash": hashlib.sha256(_strip_comments(body).encode()).hexdigest()[:16],
                    })
                break
    return out


def parse_inheritance(text: str) -> dict[str, list[str]]:
    """{contract_name: [base names]} from `contract X is A, B, ... {`."""
    out: dict[str, list[str]] = {}
    for m in _TYPE_DECL.finditer(_strip_comments(text)):
        name, bases = m.group(1), m.group(2)
        toks = re.findall(r"[A-Za-z_]\w*", bases.split(" is ")[-1])
        out[name] = toks
    return out


def parse_imports(text: str) -> list[str]:
    return _IMPORT_RE.findall(_strip_comments(text))


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def resolve_base(deriver_text: str, base_name: str, base_index: list[dict]) -> dict | None:
    """Pick the base entry for `base_name` inherited by this deriver. Fail-safe: return None when ambiguous."""
    if base_name not in BASE_ALLOWLIST:          # e.g. Multicallable -> skip (assembly / unsupported)
        return None
    if not base_index:
        return None
    # token-overlap scoring against the deriver's Multicall import path (handles remap aliases like @base/)
    imports = [p for p in parse_imports(deriver_text)
               if p.split("/")[-1] == "Multicall.sol"]  # exclude Multicallable.sol etc.
    best = base_index
    if imports:
        imp_tokens = set()
        for p in imports:
            imp_tokens |= {t.lower() for t in re.findall(r"[A-Za-z_]\w*", p) if t.lower() != "sol"}
        scored = []
        for b in base_index:
            comps = {c.lower() for c in re.split(r"[\\/]", b["base_source_file"])}
            scored.append((len(imp_tokens & comps), b))
        top = max(s for s, _ in scored)
        if top > 0:
            best = [b for s, b in scored if s == top]
    if len(best) == 1:
        return best[0]
    # multiple candidates: accept iff they are the SAME code (identical multicall body) -> deterministic pick
    if best and len({b["body_hash"] for b in best}) == 1:
        return sorted(best, key=lambda b: b["base_source_file"])[0]
    return None                                   # genuinely ambiguous -> skip, do not guess


def build_sidecar(manifest_path: Path, workspace_root: Path | None = None) -> dict:
    man = json.loads(manifest_path.read_text())
    items = man.get("items", [])
    in_scope_files = sorted({it["file"] for it in items
                             if it.get("in_scope") and it.get("file")})
    # scan root for base contracts: explicit > manifest contracts_root > common parent of in-scope files
    if workspace_root is not None:
        root = workspace_root if workspace_root.is_absolute() else ROOT / workspace_root
    else:
        croot = (man.get("source") or {}).get("contracts_root")
        root = Path(croot) if croot and Path(croot).exists() else (ROOT / croot if croot and (ROOT / croot).exists() else None)
        if root is None and in_scope_files:
            root = ROOT / Path(in_scope_files[0]).parts[0] if Path(in_scope_files[0]).parts else ROOT
    base_index = find_base_multicalls(root) if root else []

    entries, seen = [], set()
    skipped = []
    for frel in in_scope_files:
        fpath = ROOT / frel
        text = "\n".join(_read(fpath))
        if not text:
            continue
        inh = parse_inheritance(text)
        for contract, bases in inh.items():
            for base_name in bases:
                if base_name not in BASE_ALLOWLIST:
                    continue
                base = resolve_base(text, base_name, base_index)
                if base is None:
                    skipped.append({"contract": contract, "file": frel, "base": base_name,
                                    "reason": "unresolved/ambiguous/unsupported base"})
                    continue
                sig = base["signature"]
                sid = f"sidecar:{frel}:{contract}:{base['base_contract']}:{sig}"
                if sid in seen:
                    continue
                seen.add(sid)
                entries.append({
                    "id": sid,
                    # detector-consumable manifest-item shape (body read from the base source):
                    "kind": "function", "contract": contract, "name": "multicall",
                    "file": base["base_source_file"], "signature": sig,
                    "source_span": {"start_line": base["start_line"], "end_line": base["end_line"],
                                    "method": "inherited_attribution"},
                    "in_scope": True, "visibility": "",
                    # sidecar metadata:
                    "target_contract": contract, "target_file": frel,
                    "base_contract": base["base_contract"], "base_source_file": base["base_source_file"],
                    "attribution_reason": (f"{contract} (in-scope, {frel}) inherits Solidity-level multicall "
                                           f"executor from {base['base_contract']} ({base['base_source_file']}); "
                                           f"surfaced for research visibility (B1)."),
                    "synthetic_attribution": True, "source_kind": "inherited_multicall_sidecar",
                    "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
                })
    return {
        "schema_version": 1, "source_kind": "inherited_multicall_sidecar",
        "research_only": True, "routes_in_production": False, "is_gate": False,
        "_note": "RESEARCH-ONLY isolated sidecar — NOT the canonical manifest, NOT consumed by gates/routing. "
                 "Multicall-only inherited-executor attribution (B1).",
        "manifest": str(manifest_path), "workspace_root": str(root) if root else None,
        "base_multicalls_found": base_index, "items": entries, "skipped": skipped,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the research-only inherited-multicall sidecar (B1).")
    ap.add_argument("--manifest", required=True, help="canonical coverage_manifest.json (read-only)")
    ap.add_argument("--workspace-root", help="dir to scan for base Multicall sources (default: manifest contracts_root)")
    ap.add_argument("--out", required=True, help="output sidecar path (inherited_executors.json)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest)
    if not man_path.is_absolute() and not man_path.exists():
        man_path = ROOT / args.manifest
    wr = Path(args.workspace_root) if args.workspace_root else None
    sidecar = build_sidecar(man_path, wr)
    Path(args.out).write_text(json.dumps(sidecar, indent=2))
    if not args.quiet:
        print(f"[inherited_multicall_sidecar] RESEARCH-ONLY · bases_found {len(sidecar['base_multicalls_found'])} "
              f"· attributed {len(sidecar['items'])} · skipped {len(sidecar['skipped'])} · wrote {args.out}")
        for e in sidecar["items"]:
            print(f"   • {e['target_contract']}.multicall  ← {e['base_contract']} ({e['base_source_file']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
