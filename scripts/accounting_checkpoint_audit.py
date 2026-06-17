#!/usr/bin/env python3
"""
accounting_checkpoint_audit.py — P249 ACCOUNTING examine-time reasoning checkpoint (runner).

RESEARCH-ONLY, default-off, un-wired. Per in-scope manifest function it brace-matches the body (+1-level
same-contract helper resolution) and runs accounting_checkpoint_taxonomy.classify() to emit interrogative
ACCOUNTING_CHECKPOINT *reasoning records* (questions + empty hypothesis fields). It NEVER emits a finding,
NEVER sets severity/confidence, NEVER concludes a vulnerability — `emits_findings:false`,
`concludes_vulnerability:false`. The operator answers the six questions to construct a candidate, which then
routes through the EXISTING precision pipeline (this script does not route anything).

Usage: python scripts/accounting_checkpoint_audit.py [--manifest <path>] [--out <path>] [--no-source] [--quiet]
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
import accounting_checkpoint_taxonomy as act  # noqa: E402

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
    return "\n".join(out)[:12000]


def _is_test_path(f: str) -> bool:
    fl = (f or "").lower()
    return ("/test/" in fl or "/tests/" in fl or "/mocks/" in fl or fl.endswith(".t.sol") or "/mock" in fl)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    patterns = json.loads((ROOT / "config" / "accounting_checkpoint_patterns.json").read_text())
    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[accounting_checkpoint_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    fn_items = [it for it in items
                if it.get("kind") in ("function", "initializer", "constructor")
                and it.get("id") in in_scope_ids and not _is_test_path(it.get("file", ""))]

    bodies_by_contract: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        bodies_by_contract[it.get("contract", "")][it.get("name", "")] = \
            _function_body(it.get("file", ""), span.get("start_line"), use_source)

    records = []
    for it in fn_items:
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        body = bodies_by_contract[contract].get(name, "")
        if not body:
            continue
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        span = it.get("source_span", {})
        for rec in act.classify(contract, name, it.get("signature", ""), resolved, patterns=patterns):
            rec.update({
                "record_id": f"{contract}:{name}:{rec['accounting_family']}",
                "file": it.get("file"), "manifest_id": mid, "in_scope": mid in in_scope_ids,
                "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
            })
            records.append(rec)

    # dedup one record per (contract, function, family)
    seen, uniq = set(), []
    for r in records:
        if r["record_id"] in seen:
            continue
        seen.add(r["record_id"]); uniq.append(r)
    records = uniq

    by_family = Counter(r["accounting_family"] for r in records)
    # invariant self-check: a checkpoint record must never carry a conclusion
    assert all(r.get("severity") is None and r.get("concluded") is False for r in records), \
        "INVARIANT VIOLATION: accounting checkpoint emitted a conclusion (severity/concluded) — this is a detector, not a checkpoint"

    report = {
        "checkpoint": "accounting",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "emits_findings": False, "concludes_vulnerability": False,
        "output_type": "reasoning_records", "routed_manifest_ids": [],
        "question_records": len(records),
        "by_family": dict(by_family),
        "records": records,
    }
    out = Path(args.out) if args.out else audit_path("output") / "accounting_checkpoint_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[accounting_checkpoint] CHECKPOINT (reasoning aid, emits_findings=false) · "
              f"question-records {len(records)} · by-family {dict(by_family)} · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
