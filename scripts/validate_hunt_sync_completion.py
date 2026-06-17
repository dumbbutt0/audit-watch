#!/usr/bin/env python3
"""validate_hunt_sync_completion.py — P218 completion guard (research-only, read-only).

A hunt/rehearsal/eval may be marked complete ONLY if every candidate in the register has a current, schema-valid,
safe synced dashboard record and the dashboard readers/cards can see it. Exits non-zero on any failure (or on a
warning under --strict). Never routes/submits/promotes; reads only.

Structured so the core logic is a PURE function `run_checks(...)` over in-memory data (fast, hermetic, unit-testable),
with the live reader/card checks layered in `main()` (and injectable for tests).
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds  # noqa: E402

DEFAULT_MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"
DEFAULT_METRICS = ROOT / "output_research/funnel/sync_hook_metrics.json"
HIGH = {"High", "Critical"}
L3_OK = {"PASS", "HUMAN_OVERRIDE"}
# P222: valid human-review priority values ("NONE" is a real value, not absence).
_PRIORITY_VALUES = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL_HUMAN_REVIEW"}


def _read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def run_checks(candidates, synced_records, drq_ids, opts=None):
    """PURE. candidates: list of register rows (need 'id', optional 'claimed_severity'). synced_records: list of
    synced-1 records. drq_ids: set of dry-run-queue candidate ids. Returns (failures, warnings, report)."""
    opts = opts or {}
    prefix = opts.get("prefix", "")
    allow_extra = opts.get("allow_extra", False)
    failures, warnings = [], []

    by_cid = {}
    dup_ids = []
    seen_rid = set()
    for r in synced_records:
        rid = r.get("record_id")
        if rid in seen_rid:
            dup_ids.append(rid)
        seen_rid.add(rid)
        by_cid.setdefault(r.get("candidate_id"), []).append(r)
    if dup_ids:
        failures.append(f"duplicate record_ids: {sorted(set(dup_ids))}")  # check 11

    reg_ids = [c["id"] for c in candidates]
    sev_by_id = {c["id"]: c.get("claimed_severity") for c in candidates}

    for cid in reg_ids:
        recs = by_cid.get(cid, [])
        if not recs:
            failures.append(f"{cid}: missing from synced mirror")  # check 1/2
            continue
        rec = recs[0]
        # schema + safety
        errs = ds.validate_synced(rec)
        if errs:
            failures.append(f"{cid}: schema invalid: {errs}")  # check 7
        if not _safety_ok(rec):
            failures.append(f"{cid}: unsafe flags")  # check 9
        # triage decision explicit
        if not _present(rec.get("final_triager_decision")):
            failures.append(f"{cid}: final_triager_decision missing (no triage status / no-triage reason)")  # check 3
        # High/Critical blocked unless L3 PASS/override
        if sev_by_id.get(cid) in HIGH:
            l3 = rec.get("l3_status")
            allowed = rec.get("high_promotion_allowed") is True
            if allowed and l3 not in L3_OK:
                failures.append(f"{cid}: High/Critical high_promotion_allowed without L3 PASS/override (l3={l3})")  # check 7
            if not allowed and not _present(rec.get("high_promotion_blocker")) and l3 not in L3_OK:
                failures.append(f"{cid}: High/Critical blocked but no high_promotion_blocker recorded")  # explicit blocker
        # P222: human-review priority lane invariants (display/prioritization only — never implies submission).
        # NB: "NONE" is a VALID priority value (not absence), so validate against the value set, not _present().
        hrp_prio = rec.get("human_review_priority")
        if hrp_prio is None or str(hrp_prio).upper() not in _PRIORITY_VALUES:
            failures.append(f"{cid}: human_review_priority missing or invalid ({hrp_prio!r})")  # P222 (a)
        elif str(hrp_prio).upper() in ("HIGH", "CRITICAL_HUMAN_REVIEW"):
            if rec.get("submission_ready") is not False:
                failures.append(f"{cid}: high human-review priority must not imply submission_ready")  # P222 (b)
            if rec.get("routing_allowed") is not False:
                failures.append(f"{cid}: HIGH_PRIORITY_HUMAN_REVIEW must keep routing_allowed=false")  # P222 (c)
            if rec.get("high_promotion_allowed") is True and rec.get("l3_status") not in L3_OK:
                failures.append(f"{cid}: high human-review priority set high_promotion_allowed without L3 PASS")  # P222 (c)

    # stale extra phase records
    if prefix and not allow_extra:
        for r in synced_records:
            rid = str(r.get("record_id", ""))
            if rid.startswith(prefix) and r.get("candidate_id") not in reg_ids:
                failures.append(f"stale synced record not in register: {rid}")  # check 10

    # dry-run queue entries require a synced record  (check 12 — reviewer-added)
    for qid in sorted(drq_ids):
        if qid not in by_cid:
            failures.append(f"dry-run-queue entry {qid} has no synced dashboard record")
        else:
            # package link present where available (warn)
            sr = by_cid[qid][0].get("source_refs") or {}
            if not (sr.get("dry_run_queue") or sr.get("report_package") or sr.get("harness")):
                warnings.append(f"{qid}: queued candidate has no package/queue link in source_refs")  # check 9 (soft)

    report = {
        "phase": opts.get("phase"), "audit": opts.get("audit"),
        "register_candidates": len(reg_ids), "synced_records": len(synced_records),
        "synced_unique_candidates": len(by_cid), "dry_run_queue_ids": sorted(drq_ids),
        "duplicate_record_ids": sorted(set(dup_ids)),
        "failures": failures, "warnings": warnings,
        "ok": len(failures) == 0, "research_only": True, "routes_in_production": False,
    }
    return failures, warnings, report


def _present(v):
    return v is not None and str(v).strip().lower() not in ("", "none", "n/a")


def _safety_ok(rec):
    flags = [("research_only", True), ("review_only", True), ("routes_in_production", False),
             ("routing_allowed", False), ("submission_ready", False), ("no_submit_controls", True),
             ("browser_computes_severity", False), ("human_review_required", True)]
    if not all(rec.get(k) is want for k, want in flags):
        return False
    return _present(rec.get("canonical_submission_ready_source"))


# ---- live reader/card checks (injectable for tests) ----
def check_readers(cids, loader=None):
    """Confirm funnel.load_records() + findings_overview.load_overview() see every candidate. Returns failures."""
    fails = []
    try:
        import funnel, findings_overview as fo
        recs = (loader or funnel.load_records)()["records"]
        seen = {r.get("candidate_id") for r in recs} | {r.get("finding_id") for r in recs}
        rows = fo.load_overview()["rows"]
        row_ids = {r.get("id") for r in rows}
        for cid in cids:
            if cid not in seen:
                fails.append(f"{cid}: not visible in funnel.load_records()")
            if cid not in row_ids:
                fails.append(f"{cid}: not visible in findings_overview.load_overview()")
    except Exception as e:  # noqa: BLE001
        fails.append(f"reader check raised: {e!r}")
    return fails


_CARD_SECTIONS = {"report_summary", "mechanism", "function_map", "attacker_model", "exploit_steps", "defense_map",
                  "poc_verification", "impact_severity", "intent_scope_operator", "novelty_duplicate", "conversion",
                  "main_blocker", "final_triage", "red_flags", "evidence_backup"}


def _blank_contract_fields(ve):
    """(P225) Return contracted card fields that are BLANK (None/""/[]/{}) — i.e. NOT sealed to a designated
    answer. Honest placeholders (unknown/MISSING_EVIDENCE/HUMAN_PENDING/NOT_APPLICABLE/REACHABILITY_UNKNOWN) are
    NOT blanks and do NOT fail the gate. Uses finding_detail.CARD_CONTRACT as the single source of truth."""
    import finding_detail as fd
    blanks = []
    for section, spec in fd.CARD_CONTRACT.items():
        node = ve.get(section)
        kind = spec["kind"]
        if kind in ("flat_list", "row_list"):
            if fd._is_blank(node):
                blanks.append(section)
        elif kind == "dict_of_lists":
            sec = node if isinstance(node, dict) else {}
            for lname in spec["lists"]:
                if fd._is_blank(sec.get(lname)):
                    blanks.append(f"{section}.{lname}")
        else:  # dict
            sec = node if isinstance(node, dict) else {}
            fields = (spec.get("scalar", []) + spec.get("proof", []) + spec.get("human", [])
                      + spec.get("severity", []) + spec.get("reach", [])
                      + spec.get("proof_list", []) + spec.get("na_list", [])
                      + list(spec.get("row_list_fields", {})))
            for f in fields:
                if fd._is_blank(sec.get(f)):
                    blanks.append(f"{section}.{f}")
            # bool fields are structural (never blank); not checked
    return blanks


def check_cards(cids, loader=None):
    """Confirm each detail card loads with all 15 verifier sections, safe flags, and — P225 — a DESIGNATED
    ANSWER in every contracted field (the seal guarantees this; the gate hard-fails on any blank/unsealed field,
    NOT on honest placeholders). Returns failures."""
    fails = []
    if loader is None:
        import finding_detail
        loader = finding_detail.load_unified_detail
    for cid in cids:
        try:
            d = loader(f"funnel:{cid}")
            ve = d.get("verifier_evidence") or {}
            if not _CARD_SECTIONS.issubset(set(ve.keys())):
                fails.append(f"{cid}: detail card missing sections {_CARD_SECTIONS - set(ve.keys())}")
            if d.get("submission_ready") is not False or d.get("routing_allowed") is not False:
                fails.append(f"{cid}: detail card unsafe flags")
            blanks = _blank_contract_fields(ve)
            if blanks:
                fails.append(f"{cid}: detail card has blank (un-designated) fields: {blanks[:8]}"
                             + (" …" if len(blanks) > 8 else ""))
        except Exception as e:  # noqa: BLE001
            fails.append(f"{cid}: detail card failed to load: {e!r}")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description="P218 hunt-sync completion guard")
    ap.add_argument("--phase", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--candidate-register", default=None)
    ap.add_argument("--synced-mirror", default=str(DEFAULT_MIRROR))
    ap.add_argument("--l3-dir", default="output_research/l3_readiness")
    ap.add_argument("--dry-run-queue", default="output_research/dry_run_submission_queue")
    ap.add_argument("--metrics", default=str(DEFAULT_METRICS))
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--allow-extra", action="store_true")
    ap.add_argument("--skip-live", action="store_true", help="skip reader/card checks (data-only)")
    ap.add_argument("--report", default=None, help="optional path to write the JSON report")
    args = ap.parse_args(argv)

    ws = ROOT / args.workspace
    reg_path = Path(args.candidate_register) if args.candidate_register else ws / "CANDIDATE_REGISTER.json"
    reg = _read_json(reg_path) or {}
    candidates = reg.get("candidates", [])
    mirror = _read_json(args.synced_mirror) or {}
    synced = mirror.get("findings", [])
    drq_dir = ROOT / args.dry_run_queue
    drq_ids = {p.stem for p in drq_dir.glob("ZETA-*.json")} if drq_dir.exists() else set()
    prefix = f"zetachain-2023-10:{args.phase}:"

    failures, warnings, report = run_checks(candidates, synced, drq_ids,
                                            {"phase": args.phase, "audit": args.audit, "prefix": prefix,
                                             "allow_extra": args.allow_extra})
    cids = [c["id"] for c in candidates]
    if not args.skip_live:
        rfail = check_readers(cids)
        cfail = check_cards(cids)
        failures += rfail + cfail
        report["reader_failures"] = rfail
        report["card_failures"] = cfail
    # sync metrics presence (check 10) — informational NOTE (the hook owns metrics writing), never a strict-fatal
    notes = []
    if not Path(args.metrics).exists():
        notes.append(f"sync metrics file not yet written: {args.metrics}")
    else:
        notes.append(f"sync metrics present: {args.metrics}")
    report["notes"] = notes
    report["failures"] = failures
    report["warnings"] = warnings
    report["ok"] = len(failures) == 0 and (not args.strict or len(warnings) == 0)

    print(json.dumps(report, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    if failures:
        print(f"[completion-guard] FAIL — {len(failures)} failure(s)", file=sys.stderr)
        return 1
    if args.strict and warnings:
        print(f"[completion-guard] FAIL (strict) — {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print("[completion-guard] PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
