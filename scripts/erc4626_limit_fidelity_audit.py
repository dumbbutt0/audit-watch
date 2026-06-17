#!/usr/bin/env python3
"""
erc4626_limit_fidelity_audit.py — ERC4626 LIMIT-FIDELITY research lens (read-only, is_gate:false, NOT wired into
routing). Generalized class of the P302 pooltogether M-02/M-03/M-07 misses. Anchored on PrizeVault maxDeposit /
_depositAndMint / _maxYieldVaultWithdraw / _withdraw.

Cross-function: per contract it builds function bodies (+1-level same-contract helper resolution), gathers the
underlying ERC4626 primitives used by the deposit-side and withdraw-side action paths and whether the contract
holds an accrued claimable balance, then runs erc4626_limit_fidelity_taxonomy.classify_limit() over each max*/limit
function. Writes output/erc4626_limit_fidelity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/erc4626_limit_fidelity_audit.py [--manifest <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import erc4626_limit_fidelity_taxonomy as elf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_LOCAL_CALL_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")


def _load(path: Path, key: str) -> list:
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def _function_body(file_rel, start, use_source) -> str:
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines:
        return ""
    i = max(0, (start or 1) - 1)
    n = len(lines)
    j = i
    while j < min(n, i + 25) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 25) or "{" not in lines[j]:
        return ""
    depth, out, started = 0, [], False
    for k in range(j, min(n, j + _BODY_MAX_LINES)):
        line = lines[k]
        out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started = True
        if started and depth <= 0:
            break
    return "\n".join(out)[:8000]


def _resolve(body: str, contract_bodies: dict, self_name: str) -> str:
    resolved = body
    for called in set(_LOCAL_CALL_RE.findall(body)):
        if called != self_name and called in contract_bodies:
            resolved += "\n" + contract_bodies[called]
    return resolved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[erc4626_limit_fidelity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    bodies: dict[str, dict[str, str]] = defaultdict(dict)
    item_by: dict[str, dict[str, dict]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        c, n = it.get("contract", ""), it.get("name", "")
        bodies[c][n] = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        item_by[c][n] = it

    dep_names = elf._t("deposit_side_names", [])
    wd_names = elf._t("withdraw_side_names", [])
    limit_fns = elf._t("limit_fns", [])
    claimable_terms = elf._t("claimable_terms", [])

    candidates = []
    for contract, fnmap in bodies.items():
        # contract-level: deposit/withdraw action primitives + has-claimable
        dep_actions, wd_actions = set(), set()
        contract_blob = " ".join(fnmap.values()).lower()
        has_claimable = any(t in contract_blob for t in claimable_terms)
        for nm, bd in fnmap.items():
            nlow = nm.lower()
            if nlow in limit_fns:
                continue
            prims = elf.vault_primitives(_resolve(bd, fnmap, nm))
            if any(s in nlow for s in dep_names):
                dep_actions |= prims
            if any(s in nlow for s in wd_names):
                wd_actions |= prims
        # classify each limit fn
        for nm, bd in fnmap.items():
            if nm.lower() not in limit_fns:
                continue
            resolved = _resolve(bd, fnmap, nm)
            it = item_by[contract][nm]
            mid = it.get("id")
            span = it.get("source_span", {})
            for c in elf.classify_limit(nm, contract, bd, resolved, dep_actions, wd_actions, has_claimable):
                c.update({"contract": contract, "function": nm, "file": it.get("file"),
                          "lens_id": f"{contract}:{nm}:{c['finding_shape']}",
                          "in_scope": mid in in_scope_ids, "manifest_id": mid,
                          "visibility": it.get("visibility", ""),
                          "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                          "false_positive_controls": "two-signal per sub-shape; consistent-vault / no-underlying / "
                                                     "claimable-accounted / library suppressed"})
                candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_shape = Counter(c["finding_shape"] for c in candidates)
    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "erc4626_limit_fidelity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "raw_candidates": len(candidates), "by_shape": dict(by_shape), "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    out = audit_path("output") / "erc4626_limit_fidelity_audit.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[erc4626_limit_fidelity_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· {dict(by_shape)} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['confidence']}] {c['finding_shape']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
