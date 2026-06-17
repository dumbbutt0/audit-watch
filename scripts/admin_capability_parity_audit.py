#!/usr/bin/env python3
"""
admin_capability_parity_audit.py — ADMIN CAPABILITY-PARITY research lens (read-only, is_gate:false, NOT wired into
routing). Generalized class of the P304 centrifuge M-06 miss. Anchored on centrifuge admins/PauseAdmin.sol.

Per-contract: collects external/public function names + a contract blob (sigs+bodies, for the admin-marker check),
then runs admin_capability_parity_taxonomy.classify_contract(). Writes output/admin_capability_parity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/admin_capability_parity_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import admin_capability_parity_taxonomy as acp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 120


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
    return "\n".join(out)[:4000]


def _is_external(it) -> bool:
    v = (it.get("visibility", "") or "").lower()
    if v in ("external", "public"):
        return True
    s = (it.get("signature", "") or "").lower()
    return " external" in s or " public" in s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[admin_capability_parity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    names_by: dict[str, list] = defaultdict(list)
    blob_by: dict[str, list] = defaultdict(list)
    file_by: dict[str, str] = {}
    for it in fn_items:
        c = it.get("contract", "")
        span = it.get("source_span", {})
        blob_by[c].append((it.get("signature", "") or "") + " " +
                           _function_body(it.get("file", ""), span.get("start_line"), use_source))
        file_by.setdefault(c, it.get("file", ""))
        if it.get("kind") == "function" and _is_external(it) and it.get("name"):
            names_by[c].append(it["name"])

    candidates = []
    for contract, names in names_by.items():
        if (contract or "").lower().endswith("like"):     # skip interface type-aliases
            continue
        blob = "\n".join(blob_by.get(contract, []))
        for c in acp.classify_contract(contract, names, blob):
            c.update({"contract": contract, "file": file_by.get(contract, ""),
                      "lens_id": f"{contract}:{c['missing_inverse']}",
                      "false_positive_controls": "two-signal (admin/role contract + capability-pair half present "
                                                 "without inverse); camelCase boundary; both-halves/non-admin suppressed"})
            candidates.append(c)

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "admin_capability_parity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "raw_candidates": len(candidates), "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    out = audit_path("output") / "admin_capability_parity_audit.json"
    out.write_text(json.dumps(report, indent=2))
    if not args.quiet:
        print(f"[admin_capability_parity_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']} [{c['confidence']}] has {c['present_capability']} missing {c['missing_inverse']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
