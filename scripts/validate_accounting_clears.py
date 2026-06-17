#!/usr/bin/env python3
"""
validate_accounting_clears.py — Enforce the conservation-note rule for high-risk DeFi accounting clears.

Makes the Zaros Part 2 recall failure a permanent workflow rule: a high-risk debt/credit/vault/market
accounting function (per scripts/defi_accounting_taxonomy.is_high_risk) may be `cleared`/`examined` only if
its disposition carries a COMPLETE `accounting_conservation_note` (schemas/accounting_conservation_note.schema.json).
A clear that just says "looks locally safe" is flagged.

ADDITIVE + READ-ONLY: reads output/coverage_manifest.json, output/coverage_dispositions.json, and
output/defi_accounting_audit.json (if present; else classifies inline). Writes ONLY
output/accounting_clear_validation.json. Never mutates dispositions, findings, gates, or frozen artifacts.

Modes:
  --mode advisory  (default) — report; always exit 0.
  --mode strict             — exit nonzero if any high-risk accounting clear is missing/incomplete its note.

Per-item statuses:
  pass                        high-risk accounting clear WITH a complete conservation note
  missing_conservation_note   high-risk accounting clear with NO note
  incomplete_conservation_note note present but missing/empty required fields
  not_accounting_sensitive    not a high-risk accounting item (rule does not apply)
  covered_by_finding          disposition is a finding (no clear note needed)
  duplicate_or_known          marked duplicate/known (no clear note needed)
  needs_review                high-risk accounting item not confirmably cleared or found (ambiguous → human)

Usage:
  python scripts/validate_accounting_clears.py --mode advisory
  python scripts/validate_accounting_clears.py --mode strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import defi_accounting_taxonomy as acct  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}

# default required-nonempty fields (overridden by the schema's x_completeness list if readable)
_DEFAULT_REQUIRED = [
    "accounting_domains", "value_in", "value_out", "ledger_side_updated", "matching_ledger_side",
    "conservation_property", "why_conserved", "stale_state_risk", "oracle_or_price_dependency",
    "signed_unsigned_or_precision_risk", "global_vs_local_consistency", "evidence_span",
    "duplicate_or_existing_finding_check",
]


def _required_fields() -> list[str]:
    sp = ROOT / "schemas" / "accounting_conservation_note.schema.json"
    try:
        s = json.loads(sp.read_text())
        return s.get("x_completeness_required_nonempty") or _DEFAULT_REQUIRED
    except (OSError, json.JSONDecodeError):
        return _DEFAULT_REQUIRED


def _load(path: Path, key: str | None):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _snippet(file_rel, start, end, use_source):
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
    lo = max(0, (start or 1) - 1)
    hi = min(len(lines), (end or start or 1) + 25)
    return "\n".join(lines[lo:hi])[:6000]


def _note_completeness(note, required) -> tuple[bool, list[str]]:
    """Return (complete, missing_fields). A field counts as present if non-empty (str/list/etc.)."""
    if not isinstance(note, dict):
        return False, list(required)
    missing = []
    for f in required:
        v = note.get(f)
        if v is None or (isinstance(v, (str, list, dict)) and len(v) == 0) or (isinstance(v, str) and not v.strip()):
            missing.append(f)
    return (len(missing) == 0), missing


_FINDING_ID_RE = re.compile(r"\b[A-Za-z]{1,5}-\d{1,4}\b")  # DT-001, H-01, SWP-003, DPF-012


def _is_duplicate_or_known(disp: dict, note) -> bool:
    """True only when a real dup/known reference is named — NOT for placeholder/negative text. A bare
    'dup' substring is insufficient (it appears in the field name itself); require an actual finding id or
    an explicit 'duplicate of' / 'known issue' / 'covered by' phrase, and never on a 'no existing' answer."""
    if disp.get("duplicate_of") or disp.get("known_ref"):
        return True
    if isinstance(note, dict):
        chk = (note.get("duplicate_or_existing_finding_check") or "")
        low = chk.lower()
        if not low.strip() or low.strip() in ("none", "n/a", "na") or "no existing" in low or "not a duplicate" in low:
            return False
        if _FINDING_ID_RE.search(chk) or "duplicate of" in low or "known issue" in low or "covered by" in low:
            return True
    return False


def classify_high_risk_set(manifest_items, use_source):
    """Prefer the defi_accounting_audit.json detected/high-risk set; else classify inline."""
    audit = _load(audit_path("output") / "defi_accounting_audit.json", None)
    detected = audit.get("detected") if isinstance(audit, dict) else None
    hr = {}
    if detected:
        for d in detected:
            if d.get("high_risk"):
                hr[d["manifest_id"]] = {"category": d.get("category"),
                                        "accounting_domains": d.get("accounting_domains", [])}
        return hr, "defi_accounting_audit.json"
    # inline fallback
    tax = acct.load_taxonomy()
    for it in manifest_items:
        if it.get("kind") not in ("function", "constructor", "initializer") or not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = acct.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                            it.get("contract", ""), snippet=snip)
        if cls.get("defi_accounting_sensitive") and acct.is_high_risk(cls, tax):
            hr[it["id"]] = {"category": cls.get("category"), "accounting_domains": cls.get("accounting_domains", [])}
    return hr, "inline_classification"


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate conservation notes on high-risk accounting clears")
    ap.add_argument("--mode", choices=["advisory", "strict"], default="advisory")
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[validate_accounting_clears] no manifest items at {man_path}")
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    required = _required_fields()
    hr_set, hr_source = classify_high_risk_set(items, not args.no_source)
    items_by_id = {it["id"]: it for it in items}

    results = []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer") or not it.get("in_scope", True):
            continue
        mid = it["id"]
        meta = hr_set.get(mid)
        d = disp.get(mid, {})
        st = d.get("status")
        note = d.get("accounting_conservation_note")
        row = {"manifest_id": mid, "name": it.get("name"), "contract": it.get("contract"),
               "file": it.get("file"),
               "category": (meta or {}).get("category"),
               "accounting_domains": (meta or {}).get("accounting_domains", []),
               "disposition_status": st}

        if meta is None:
            # not a high-risk accounting item → the conservation-note rule does not apply
            row["status"] = "not_accounting_sensitive"
        elif st == "finding" or d.get("finding_refs") or d.get("finding_ref"):
            row["status"] = "covered_by_finding"
        elif _is_duplicate_or_known(d, note):
            row["status"] = "duplicate_or_known"
        elif st in ("cleared", "examined"):
            if note is None:
                row["status"] = "missing_conservation_note"
            else:
                complete, missing = _note_completeness(note, required)
                if complete:
                    row["status"] = "pass"
                else:
                    row["status"] = "incomplete_conservation_note"
                    row["missing_fields"] = missing
        elif st in (None, "unassigned", "assigned", "deferred_out_of_scope"):
            # high-risk accounting item not confirmably cleared/found → human must look (never auto-pass)
            row["status"] = "needs_review" if st != "deferred_out_of_scope" else "not_accounting_sensitive"
            if st == "deferred_out_of_scope":
                row["note"] = "deferred out of scope; conservation rule not applicable"
        else:
            row["status"] = "needs_review"
        results.append(row)

    counts = Counter(r["status"] for r in results)
    offenders = [r for r in results if r["status"] in ("missing_conservation_note", "incomplete_conservation_note")]
    failing = len(offenders)
    passed = (args.mode == "advisory") or (failing == 0)
    high_risk_total = sum(1 for r in results if r["status"] != "not_accounting_sensitive")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "manifest": str(man_path),
        "high_risk_source": hr_source,
        "required_note_fields": required,
        "is_gate": args.mode == "strict",
        "in_scope_items_evaluated": len(results),
        "high_risk_accounting_items": high_risk_total,
        "counts": dict(counts),
        "passed": passed,
        "failing_count": failing,
        "offenders": offenders,
        "results": results,
    }
    out = audit_path("output") / "accounting_clear_validation.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        verdict = "PASS" if passed else "BLOCK"
        print(f"Accounting-clear validation ({args.mode}): {verdict}")
        print(f"  in-scope evaluated: {len(results)}  ·  high-risk accounting: {high_risk_total}")
        print(f"  " + " · ".join(f"{k} {v}" for k, v in counts.most_common()))
        print(f"  missing/incomplete notes: {failing}")
        for r in offenders[:15]:
            mf = f" missing={','.join(r.get('missing_fields', []))}" if r.get("missing_fields") else ""
            print(f"    {r['status'].upper()} {r['name']} ({r['contract']}) [{r['category']}]{mf}")
        if failing > 15:
            print(f"    … +{failing - 15} more (see {out})")
        print(f"  report: {out}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
