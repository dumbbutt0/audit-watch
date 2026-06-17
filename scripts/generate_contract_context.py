#!/usr/bin/env python3
"""
generate_contract_context.py — Build notes/contract_context.md for the primary contract dir.

Pure deterministic parsing (regex over Solidity source) — NO Anthropic API, works with no key.
Optionally enriches from output/static.json if present, but never requires it.

Emits:
    notes/contract_context.md          — the deep navigation index (human-facing)
    notes/points_of_interest.jsonl     — attacker-reachable entrypoints, one per line

Inventories produced: files, contracts/interfaces/libraries, functions by visibility/mutability,
modifiers, inheritance, library usage, external/delegate/low-level calls, token transfers,
oracle reads, permission checks, initializers, attacker-reachable vs privileged entrypoints,
security-sensitive state variables.

Usage:
    python scripts/generate_contract_context.py
    python scripts/generate_contract_context.py --audit-id xterio-2026-05
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import _AUDITS_DIR, get_active_audit

SOL_GLOB = "**/*.sol"

RE_CONTRACT = re.compile(r"\b(contract|interface|library|abstract\s+contract)\s+(\w+)([^{]*)\{")
RE_IMPORT = re.compile(r'^\s*import\s+.*?["\']([^"\']+)["\']', re.M)
RE_FUNC = re.compile(
    r"function\s+(\w+)\s*\(([^)]*)\)\s*([^{;]*)", re.S)
RE_MODIFIER_DEF = re.compile(r"\bmodifier\s+(\w+)")
RE_INITIALIZER = re.compile(r"function\s+(initialize|init|__\w+_init)\w*\s*\(", re.I)

# call / transfer / oracle / permission signals
SIG = {
    "delegatecall":  re.compile(r"\.delegatecall\s*\("),
    "low_level_call": re.compile(r"\.call\s*[\({]"),
    "staticcall":    re.compile(r"\.staticcall\s*\("),
    "token_transfer": re.compile(r"\.(safeTransfer|safeTransferFrom|transferFrom|transfer)\s*\("),
    "oracle_read":   re.compile(r"\b(latestRoundData|latestAnswer|getReserves|slot0|getPrice|consult|peek)\b"),
    "selfdestruct":  re.compile(r"\bselfdestruct\s*\("),
    "ecrecover":     re.compile(r"\becrecover\s*\("),
    "create2":       re.compile(r"\bcreate2\b"),
}
RE_PERM = re.compile(r"\b(onlyOwner|onlyAdmin|onlyRole|onlyGovernance|require\s*\(\s*msg\.sender)")
RE_VISIBILITY = re.compile(r"\b(external|public|internal|private)\b")
RE_MUTABILITY = re.compile(r"\b(view|pure|payable)\b")
RE_STATE_SENSITIVE = re.compile(
    r"\b(owner|admin|governance|paused|implementation|oracle|priceFeed|merkleRoot|"
    r"totalSupply|balances?|allowances?|nonce|threshold|rate|fee)\b", re.I)


def _fn_modifiers(tail: str) -> list[str]:
    # strip known keywords; remaining identifiers before returns/{ are modifiers
    cleaned = re.sub(r"\b(external|public|internal|private|view|pure|payable|virtual|override|returns)\b",
                     " ", tail)
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)  # drop returns(...) / modifier args
    return [m for m in re.findall(r"\b([a-zA-Z_]\w*)\b", cleaned)]


def parse_file(path: Path, root: Path) -> dict:
    text = path.read_text(errors="ignore")
    rel = str(path.relative_to(root))
    contracts = [(kind, name) for kind, name, _ in RE_CONTRACT.findall(text)]
    inherits: dict[str, list[str]] = {}
    for kind, name, decl in RE_CONTRACT.findall(text):
        m = re.search(r"\bis\s+([^{]+)", decl)
        if m:
            inherits[name] = [b.strip().split("(")[0] for b in m.group(1).split(",") if b.strip()]
    imports = RE_IMPORT.findall(text)
    modifiers_defined = RE_MODIFIER_DEF.findall(text)
    initializers = [m for m in RE_INITIALIZER.findall(text)]

    funcs = []
    for fname, fargs, ftail in RE_FUNC.findall(text):
        vis_m = RE_VISIBILITY.search(ftail)
        vis = vis_m.group(1) if vis_m else "internal"  # solidity default for funcs is internal
        mut = RE_MUTABILITY.search(ftail)
        mutability = mut.group(1) if mut else ""
        mods = [m for m in _fn_modifiers(ftail)
                if m not in (fname,) and m not in ("internal", "external", "public", "private")]
        funcs.append({
            "name": fname, "visibility": vis, "mutability": mutability,
            "modifiers": mods,
        })

    signals = {k: len(rx.findall(text)) for k, rx in SIG.items()}
    perm_hits = len(RE_PERM.findall(text))
    sensitive = sorted(set(m.lower() for m in RE_STATE_SENSITIVE.findall(text)))

    return {
        "file": rel,
        "contracts": contracts,
        "inherits": inherits,
        "imports": imports,
        "modifiers_defined": modifiers_defined,
        "initializers": initializers,
        "functions": funcs,
        "signals": signals,
        "perm_hits": perm_hits,
        "sensitive": sensitive,
    }


def build(audit_id: str) -> int:
    root = _AUDITS_DIR / audit_id
    meta_path = root / "meta.json"
    if not meta_path.exists():
        raise SystemExit(f"[error] Workspace not found for '{audit_id}'")
    meta = json.loads(meta_path.read_text())
    rel_primary = meta.get("primary_contract_dir")
    if rel_primary:
        primary = root / rel_primary
    else:
        primary = root / "contracts"
    if not primary.exists():
        raise SystemExit(f"[error] Primary contract dir missing: {primary}\n"
                         f"        Run intake_contracts.py first.")

    sol_files = [p for p in primary.glob(SOL_GLOB) if p.is_file()]
    if not sol_files:
        raise SystemExit(f"[error] No .sol files under {primary}")

    parsed = [parse_file(p, primary) for p in sorted(sol_files)]

    # Aggregate
    total_contracts = sum(len(p["contracts"]) for p in parsed)
    all_funcs = [(p["file"], f) for p in parsed for f in p["functions"]]
    by_vis = Counter(f["visibility"] for _, f in all_funcs)
    state_changing = [(fl, f) for fl, f in all_funcs
                      if f["visibility"] in ("external", "public") and f["mutability"] not in ("view", "pure")]
    views = [(fl, f) for fl, f in all_funcs
             if f["visibility"] in ("external", "public") and f["mutability"] in ("view", "pure")]

    # Attacker-reachable = external/public, state-changing, NO permission modifier on the fn
    PERM_MODS = {"onlyOwner", "onlyAdmin", "onlyRole", "onlyGovernance", "onlyGovernor", "auth", "restricted"}
    reachable, privileged = [], []
    for fl, f in state_changing:
        if set(f["modifiers"]) & PERM_MODS:
            privileged.append((fl, f))
        else:
            reachable.append((fl, f))

    sig_totals = Counter()
    for p in parsed:
        for k, v in p["signals"].items():
            sig_totals[k] += v

    # ── Write points_of_interest.jsonl (attacker-reachable entrypoints, ranked) ──
    poi_path = root / "notes" / "points_of_interest.jsonl"
    poi_path.parent.mkdir(parents=True, exist_ok=True)
    with poi_path.open("w") as fh:
        for fl, f in reachable:
            fh.write(json.dumps({
                "file": fl, "function": f["name"], "visibility": f["visibility"],
                "mutability": f["mutability"], "modifiers": f["modifiers"],
                "kind": "attacker_reachable_entrypoint",
            }) + "\n")

    # ── Write contract_context.md ──
    L = []
    L.append(f"# Contract Context — {audit_id}")
    L.append(f"\n_Primary dir: `{rel_primary or 'contracts'}` · {len(sol_files)} Solidity files · "
             f"{total_contracts} contract/interface/library declarations · deterministic parse (no API)._\n")

    L.append("## Function inventory (entrypoints)\n")
    L.append(f"- external/public: {by_vis.get('external',0)+by_vis.get('public',0)} "
             f"(state-changing: {len(state_changing)}, view/pure: {len(views)})")
    L.append(f"- **attacker-reachable** (external/public, state-changing, no permission modifier): "
             f"**{len(reachable)}**")
    L.append(f"- privileged (guarded by onlyOwner/onlyRole/etc): {len(privileged)}\n")

    L.append("### Attacker-reachable entrypoints (start here)\n")
    if reachable:
        L.append("| File | Function | Mutability | Modifiers |")
        L.append("|---|---|---|---|")
        for fl, f in reachable[:60]:
            L.append(f"| {fl} | `{f['name']}` | {f['mutability'] or '—'} | {', '.join(f['modifiers']) or '—'} |")
        if len(reachable) > 60:
            L.append(f"\n_…and {len(reachable)-60} more (full list in notes/points_of_interest.jsonl)._")
    else:
        L.append("_None detected._")
    L.append("")

    L.append("### Privileged entrypoints\n")
    if privileged:
        L.append("| File | Function | Guard |")
        L.append("|---|---|---|")
        for fl, f in privileged[:40]:
            L.append(f"| {fl} | `{f['name']}` | {', '.join(set(f['modifiers']) & PERM_MODS)} |")
    else:
        L.append("_None detected._")
    L.append("")

    L.append("## Security-sensitive signals (counts across primary dir)\n")
    L.append("| Signal | Count |")
    L.append("|---|---|")
    for k in ("delegatecall", "low_level_call", "staticcall", "token_transfer",
              "oracle_read", "selfdestruct", "ecrecover", "create2"):
        L.append(f"| {k} | {sig_totals.get(k,0)} |")
    L.append("")

    L.append("## Initializers (upgrade/migration surface)\n")
    inits = [(p["file"], i) for p in parsed for i in p["initializers"]]
    if inits:
        for fl, i in inits:
            L.append(f"- `{i}` — {fl}")
    else:
        L.append("_None detected._")
    L.append("")

    L.append("## Inheritance\n")
    any_inh = False
    for p in parsed:
        for name, bases in p["inherits"].items():
            L.append(f"- `{name}` is {', '.join(bases)}  ({p['file']})")
            any_inh = True
    if not any_inh:
        L.append("_None detected._")
    L.append("")

    L.append("## Per-file summary\n")
    L.append("| File | Contracts | Funcs | ext/pub | sensitive state |")
    L.append("|---|---|---|---|---|")
    for p in parsed:
        ext = sum(1 for f in p["functions"] if f["visibility"] in ("external", "public"))
        decls = ", ".join(n for _, n in p["contracts"]) or "—"
        L.append(f"| {p['file']} | {decls} | {len(p['functions'])} | {ext} | "
                 f"{', '.join(p['sensitive'][:6]) or '—'} |")
    L.append("")

    out = root / "notes" / "contract_context.md"
    out.write_text("\n".join(L) + "\n")
    print(f"[ok] Wrote {out}")
    print(f"[ok] Wrote {poi_path}  ({len(reachable)} attacker-reachable entrypoints)")
    print(f"     files={len(sol_files)} contracts={total_contracts} "
          f"reachable={len(reachable)} privileged={len(privileged)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate notes/contract_context.md (deterministic)")
    ap.add_argument("--audit-id", default=None, help="Target audit (default: active)")
    args = ap.parse_args()
    audit_id = args.audit_id or get_active_audit().get("audit_id")
    if not audit_id:
        raise SystemExit("[error] No active audit.")
    return build(audit_id)


if __name__ == "__main__":
    sys.exit(main())
