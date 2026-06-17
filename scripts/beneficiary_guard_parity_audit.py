#!/usr/bin/env python3
"""
beneficiary_guard_parity_audit.py — BENEFICIARY-GUARD PARITY research lens (read-only, is_gate:false, NOT wired into
routing). Generalized class of the P304 centrifuge M-04 miss. Anchored on centrifuge LiquidityPool.deposit/mint.

Per-contract: gathers each function's signature + body + visibility, computes S1 (does the contract own-guard any
beneficiary function?), then emits S2 candidates (unguarded beneficiary siblings) via
beneficiary_guard_parity_taxonomy.classify_function(). Writes output/beneficiary_guard_parity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/beneficiary_guard_parity_audit.py [--manifest <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import beneficiary_guard_parity_taxonomy as bgp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[beneficiary_guard_parity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") == "function"]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    by_contract: dict[str, list] = defaultdict(list)
    for it in fn_items:
        span = it.get("source_span", {})
        it = dict(it, _body=_function_body(it.get("file", ""), span.get("start_line"), use_source))
        by_contract[it.get("contract", "")].append(it)

    suppress_suffixes = bgp._t("suppress_contract_suffixes", [])
    candidates = []
    for contract, fns in by_contract.items():
        # skip interface type-aliases (e.g. the `*Like` convention) — not real deployable contracts
        if any((contract or "").lower().endswith(s) for s in suppress_suffixes):
            continue
        # require a real implementation body (excludes interface/abstract declarations with no body)
        fns = [it for it in fns if it["_body"]]
        if not fns:
            continue
        # S1: does the contract own-guard any beneficiary function?
        contract_has_owner_guard = any(
            bgp.beneficiary_param(it.get("signature", "")) and bgp.owner_guarded(it.get("signature", ""), it["_body"])
            for it in fns)
        if not contract_has_owner_guard:
            continue
        for it in fns:
            for c in bgp.classify_function(it.get("name", ""), it.get("signature", ""), it["_body"],
                                           it.get("visibility", ""), contract_has_owner_guard):
                span = it.get("source_span", {})
                mid = it.get("id")
                c.update({"contract": contract, "function": it.get("name", ""), "file": it.get("file"),
                          "lens_id": f"{contract}:{it.get('name','')}:{c['finding_shape']}",
                          "in_scope": mid in in_scope_ids, "manifest_id": mid,
                          "visibility": it.get("visibility", ""),
                          "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                          "false_positive_controls": "two-signal (owner-guarded beneficiary sibling exists + this "
                                                     "beneficiary fn external/mutating/unguarded); view/admin-guarded/"
                                                     "no-guarded-sibling suppressed"})
                candidates.append(c)

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "beneficiary_guard_parity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "raw_candidates": len(candidates), "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    out = audit_path("output") / "beneficiary_guard_parity_audit.json"
    out.write_text(json.dumps(report, indent=2))
    if not args.quiet:
        print(f"[beneficiary_guard_parity_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· medium {report['medium']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['confidence']}] benef={c['beneficiary_role']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
