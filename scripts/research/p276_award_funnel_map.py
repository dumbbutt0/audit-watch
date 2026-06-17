#!/usr/bin/env python3
"""P276 — SUPERVISED_EVAL award-funnel mapper (Pass B).

RESEARCH-ONLY / ADVISORY. Opens a contest's award key (PASS B only) and maps every awarded H/M finding through the
Pass-A funnel artifacts, recording the furthest stage reached and the first_failed_stage. Award key is used for
SCORING + FAILURE LOCALIZATION ONLY — never to fabricate a blind claim and never to set severity/reportable/etc.

Award-key adapter handles the heterogeneous corpus schemas:
  - output/eval_ready/answer_key_normalization.json  {findings:[{answer_key_id,severity,title,affected,functions,root_cause}]}
  - answer_key/answer_key_raw.json (list)            {severity,title,affected_contracts,affected_functions,root_cause}
  - output/answer_key/answer_key.json (ark)          {families:[{ak_id,severity,title,location,root_cause}]}
  - output/answer_key/raw_answer_key.json (captured_rows)  title-only (severity,title) -> no locus funnel
Filters to awarded High/Medium.

Usage:
  python scripts/research/p276_award_funnel_map.py --audit-id <id> --replay-dir <dir> --out <map.json> [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABEL = "SUPERVISED_EVAL"

STAGES = ["MISSED", "ADVISORY_SURFACED", "CLASS_ROUTED", "LOCUS_TRIAGED", "MECHANISM_GENERATED",
          "MECHANISM_SELECTED_OR_KEPT", "CHAIN_COMPLETED", "POC_INTENT_CORRECT", "POC_SUPPORTED",
          "EXACT_RECOVERED", "STRONG_RECOVERED", "FAMILY_RECOVERED", "SUBSYSTEM_ONLY"]
FIRST_FAILED = ["TARGET_SCOPE_GAP", "MANIFEST_GAP", "CHECKPOINT_GAP", "RECALL_GAP", "COVERAGE_CLASS_GAP",
                "TRIAGE_GAP", "SELECTOR_GAP", "COMPLETION_GAP", "CHECKLIST_GAP", "POC_HARNESS_GAP",
                "GATE_GAP", "TRUE_NEGATIVE_OR_OUT_OF_SCOPE", "DUPLICATE_OR_REPORT_ONLY_AMBIGUITY"]

_CONTRACT = re.compile(r"\b([A-Z][A-Za-z0-9]{2,})\b")
_FUNC = re.compile(r"\b([a-z_][A-Za-z0-9_]{2,})\b")
_AWARDED_SEV = {"high", "medium"}


def _load(p: Path):
    return json.loads(p.read_text()) if p and p.exists() else None


# ---------------- award-key adapter ----------------
def _award_key_path(audit: Path):
    for rel in ("answer_key/answer_key_raw.json", "output/answer_key/answer_key.json",
                "output/eval_ready/answer_key_normalization.json", "output/answer_key/raw_answer_key.json"):
        p = audit / rel
        if p.exists():
            return p
    return None


def _g(d: dict, *aliases, default=""):
    for a in aliases:
        if a in d and d[a] not in (None, ""):
            return d[a]
    return default


def _join(v):
    return " ".join(v) if isinstance(v, list) else str(v or "")


def normalize_award_key(audit: Path) -> tuple[list[dict], str]:
    """Return (awarded_HM[list of {id,severity,title,contracts[],functions[],root_cause,locus_info}], schema).

    Alias-tolerant across the corpus schemas (findings/families/answer_key/captured_rows/top-level list; field name
    variants severity|sev, affected|affected_contracts|location|file|fn, functions|affected_functions|fn,
    root_cause|root)."""
    p = _award_key_path(audit)
    if not p:
        return [], "none"
    d = _load(p)
    schema = p.name
    if isinstance(d, dict):
        items = (d.get("findings") or d.get("families") or d.get("answer_key") or d.get("captured_rows") or [])
    elif isinstance(d, list):
        items = d
    else:
        items = []
    title_only = bool(isinstance(d, dict) and "captured_rows" in d)
    out = []
    for i, f in enumerate(items):
        if not isinstance(f, dict):
            continue
        sev = _g(f, "severity", "sev", "Severity")
        if str(sev).strip().lower() not in _AWARDED_SEV:
            continue
        aid = _g(f, "answer_key_id", "ak_id", "id", "report_finding_id", default=f"AK-{i}")
        title = _g(f, "title", "name")
        affected = _join(_g(f, "affected_contracts", "affected", "location", "file", "contracts", default=""))
        functions = _join(_g(f, "affected_functions", "functions", "fn", default=""))
        rc = _g(f, "root_cause", "root", "impact", default="")
        contracts = sorted(set(_CONTRACT.findall(f"{affected} {functions} {rc}")))
        funcs = sorted(set(_FUNC.findall(f"{functions} {affected}")))
        has_locus = (not title_only) and bool(contracts or funcs)
        out.append({"id": aid, "severity": sev, "title": title,
                    "contracts": contracts, "functions": funcs, "root_cause": rc,
                    "has_locus_info": has_locus})
    return out, schema


# ---------------- funnel matcher ----------------
def _manifest_contracts(audit: Path) -> set[str]:
    man = _load(audit / "output" / "coverage_manifest.json") or {}
    return {str(i.get("contract", "")).lower() for i in man.get("items", []) if i.get("contract")}


def _match_candidates(award: dict, cands: list[dict]) -> list[str]:
    awc = {c.lower() for c in award["contracts"]}
    awf = {f.lower() for f in award["functions"]}
    hits = []
    for c in cands:
        cc = str(c.get("contract", "")).lower()
        cf = str(c.get("function", "")).lower()
        if cc and cc in awc:
            if not awf or cf in awf or not cf:
                hits.append(c["id"])
            elif cf in awf:
                hits.append(c["id"])
    # contract-only fallback
    if not hits:
        for c in cands:
            if str(c.get("contract", "")).lower() in awc:
                hits.append(c["id"])
    return hits


def map_award(award: dict, bundle: dict, manifest_contracts: set[str], sampled: bool) -> dict:
    cands = bundle.get("advisory_candidates", [])
    handoff = set(bundle.get("coverage_handoff", []))
    triaged = set(bundle.get("triage_selected", []))
    matched = _match_candidates(award, cands)

    stage, first_failed, notes = "MISSED", None, ""
    if not award["has_locus_info"]:
        # title-only key: cannot do locus funnel
        return {"id": award["id"], "severity": award["severity"], "title": award["title"],
                "stage": "MISSED", "first_failed_stage": "DUPLICATE_OR_REPORT_ONLY_AMBIGUITY",
                "matched_candidates": [], "note": "title-only award key (no affected contract/function) -> locus funnel N/A"}

    award_in_manifest = bool({c.lower() for c in award["contracts"]} & manifest_contracts)

    if matched:
        stage = "ADVISORY_SURFACED"
        if any(m in handoff for m in matched):
            stage = "CLASS_ROUTED"
            if any(m in triaged for m in matched):
                stage = "LOCUS_TRIAGED"
                # mechanism_generated: harness emits mechanisms for every surfaced candidate
                if any((next((c for c in cands if c["id"] == m), {}) or {}).get("mechanisms", 0) for m in matched):
                    stage = "MECHANISM_GENERATED"
                if sampled:
                    notes = "sampled: completion/PoC evaluated separately in AWARD_FUNNEL_MAP narrative"
                else:
                    first_failed = "COMPLETION_GAP"  # upstream OK; completion/PoC not sampled
                    notes = "NOT_SAMPLED beyond MECHANISM_GENERATED (sampled-tail policy)"
            else:
                first_failed = "TRIAGE_GAP"
        else:
            first_failed = "COVERAGE_CLASS_GAP"
    else:
        if not award_in_manifest:
            first_failed = "MANIFEST_GAP" if award["contracts"] else "TARGET_SCOPE_GAP"
            notes = "award contract(s) absent from coverage manifest"
        else:
            first_failed = "RECALL_GAP"
            notes = "award contract in manifest but no advisory candidate surfaced its locus"

    return {"id": award["id"], "severity": award["severity"], "title": award["title"],
            "stage": stage, "first_failed_stage": first_failed,
            "matched_candidates": matched, "note": notes}


def run(audit_id: str, replay_dir: Path, out: Path, sampled_ids: set[str], quiet: bool) -> dict:
    audit = ROOT / "audits" / audit_id
    awards, schema = normalize_award_key(audit)
    bundle = _load(replay_dir / "replay_bundle.json") or {}
    man_contracts = _manifest_contracts(audit)
    mapped = [map_award(a, bundle, man_contracts, a["id"] in sampled_ids) for a in awards]
    from collections import Counter
    res = {"label": LABEL, "mode": "SUPERVISED_EVAL_PASS_B", "audit_id": audit_id, "award_key_schema": schema,
           "awarded_hm_total": len(awards),
           "with_locus_info": sum(1 for a in awards if a["has_locus_info"]),
           "stage_tally": dict(Counter(m["stage"] for m in mapped)),
           "first_failed_tally": dict(Counter(m["first_failed_stage"] for m in mapped if m["first_failed_stage"])),
           "is_gate": False, "research_only": True, "emits_findings": False,
           "findings": mapped}
    out.write_text(json.dumps(res, indent=1))
    if not quiet:
        print(f"[p276:B] {audit_id} ({schema}): awarded_HM={len(awards)} "
              f"stages={res['stage_tally']} first_failed={res['first_failed_tally']}")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-id", required=True)
    ap.add_argument("--replay-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sampled", default="", help="comma-separated award ids evaluated through completion/PoC")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    sampled = {x.strip() for x in a.sampled.split(",") if x.strip()}
    run(a.audit_id, Path(a.replay_dir), Path(a.out), sampled, a.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
