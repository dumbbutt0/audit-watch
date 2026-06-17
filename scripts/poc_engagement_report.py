#!/usr/bin/env python3
"""
poc_engagement_report.py — Operator view of PoC readiness for real engagements (deterministic, no LLM).

Answers the only question that matters before submitting: "What can I submit now, what is blocked, and exactly
what must I fix before submitting the rest?" Buckets every PoC-required finding, computes summary metrics, and
writes a small dashboard-facing status artifact. It reuses the authoritative gate rules
(poc_validation_gate.evaluate) so the report never diverges from the gate. It changes no proof verdict and
overwrites no validation note.

Reads:
    output/poc_validation/poc_inventory.json
    output/poc_validation/collected_results.json
    output/poc_validation/poc_validation_results.json
    output/poc_validation/poc_validation_gate.json   (informational)
    output/poc_validation/validation_notes/<id>.json (presence -> note path)
    output/merged_findings.json, output/coverage_manifest.json

Writes:
    output/poc_validation/engagement_report.json
    output/poc_validation/engagement_report.md
    output/dashboard/poc_validation_status.json   (small, dashboard-friendly)

Usage:
    python scripts/poc_engagement_report.py [--quiet]
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
import poc_validation_gate as gate  # noqa: E402  (reuse evaluate() + SEV_RANK)

BUCKETS = [
    "submission_ready", "engagement_ready_but_not_submission_ready",
    "needs_better_assertions", "needs_negative_control", "needs_fork_context",
    "missing_poc", "missing_collected_log", "invalid_poc", "setup_only",
    "severity_overclaim", "duplicate_proof", "inconclusive", "eval_only_not_required",
]
INPUT_RELPATHS = [
    "output/poc_validation/poc_inventory.json",
    "output/poc_validation/collected_results.json",
    "output/poc_validation/poc_validation_results.json",
    "output/poc_validation/poc_validation_gate.json",
    "output/merged_findings.json",
    "output/coverage_manifest.json",
]


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _short_reason(bucket: str, vr: dict, eng_reason: str) -> str:
    table = {
        "submission_ready": "proven and passes the submission gate — submit as-is",
        "engagement_ready_but_not_submission_ready": "usable for the engagement but not yet submission-grade",
        "needs_better_assertions": "test lacks a real impact/value assertion",
        "needs_negative_control": "no negative control (unauthorized/patched path) demonstrated",
        "needs_fork_context": "needs a fork test with a disclosed block / real deployment",
        "missing_poc": "no PoC test exists yet",
        "missing_collected_log": "test referenced but no captured run — run poc-collect",
        "invalid_poc": "the test does not prove the claim",
        "setup_only": "the 'attack' is performed by test setup, not the real path",
        "severity_overclaim": f"demonstrated impact below claimed severity (supported: {vr.get('severity_supported')})",
        "duplicate_proof": "proves a finding already proven elsewhere",
        "inconclusive": "no usable proof yet",
        "eval_only_not_required": "eval-only — no PoC required",
    }
    return table.get(bucket, eng_reason or bucket)


# fix-list action vocabulary (what to DO next), mapped from the finding's bucket / recommended_next_action.
FIX_ACTIONS = [
    "write_missing_poc", "add_collected_log", "add_reachability_assertion", "add_impact_assertion",
    "add_negative_control", "add_fork_context", "downgrade_severity", "remove_invalid_setup",
    "resolve_duplicate", "reject_poc", "manual_review",
]
_FIX_BY_BUCKET = {
    "missing_poc": "write_missing_poc",
    "missing_collected_log": "add_collected_log",
    "needs_fork_context": "add_fork_context",
    "needs_negative_control": "add_negative_control",
    "needs_better_assertions": "add_impact_assertion",
    "severity_overclaim": "downgrade_severity",
    "setup_only": "remove_invalid_setup",
    "invalid_poc": "reject_poc",
    "duplicate_proof": "resolve_duplicate",
    "inconclusive": "manual_review",
}
_FIX_BY_RNA = {
    "add_reachability_assertion": "add_reachability_assertion",
    "add_impact_assertion": "add_impact_assertion",
    "add_negative_control": "add_negative_control",
    "needs_fork_test": "add_fork_context",
    "downgrade_severity": "downgrade_severity",
    "reject_poc": "reject_poc",
    "needs_unit_test": "write_missing_poc",
}
_NEXT_STEP = {
    "write_missing_poc": "Write a Foundry PoC that calls the real entrypoint as an unprivileged EOA and asserts the impact.",
    "add_collected_log": "Run + capture: ./run_pipeline.sh poc-collect --finding-id {fid} --test-file {tf} --test-name {tn} --command \"forge test --match-test {tn} -vvv\".",
    "add_reachability_assertion": "Drive the path from an unprivileged EOA (no owner/admin prank); assert the attacker reaches the sink.",
    "add_impact_assertion": "Add a before/after value assertion proving the claimed loss/freeze/overmint/DoS.",
    "add_negative_control": "Add a negative control: the unauthorized/patched path must behave differently.",
    "add_fork_context": "Convert to a fork test at a disclosed block with real deployed addresses.",
    "downgrade_severity": "Lower the claimed severity to the demonstrated impact, or strengthen the PoC to support it.",
    "remove_invalid_setup": "Remove the vm.store/setup that manufactures the bug; reproduce via the real path.",
    "resolve_duplicate": "Mark as duplicate of the already-proven finding; do not double-submit.",
    "reject_poc": "Rewrite or drop — the test does not prove the claim.",
    "manual_review": "Inspect manually — no usable proof yet.",
}


def fix_action(f: dict) -> str:
    bucket, rna = f["bucket"], f.get("recommended_next_action")
    if bucket == "needs_better_assertions" and rna == "add_reachability_assertion":
        return "add_reachability_assertion"
    if bucket in _FIX_BY_BUCKET:
        return _FIX_BY_BUCKET[bucket]
    if bucket == "engagement_ready_but_not_submission_ready":
        return _FIX_BY_RNA.get(rna, "manual_review")
    return "manual_review"


def shortest_next_step(action: str, f: dict) -> str:
    return _NEXT_STEP.get(action, "Inspect manually.").format(
        fid=f["finding_id"], tf=f.get("test_file") or "<test_file>", tn=f.get("test_name") or "<test_name>")


def classify(cand: dict, vr: dict | None, coll: dict | None, has_note: bool, waived: set, mode: str):
    sev = cand.get("severity_ceiling", "Unknown")
    test_file = (coll or {}).get("test_file") or (vr or {}).get("test_file")
    raw_log = (coll or {}).get("raw_result_path")
    vs = (vr or {}).get("validation_status")
    overclaim = bool((vr or {}).get("severity_overclaim"))
    rna = (vr or {}).get("recommended_next_action")
    warnings = (vr or {}).get("warnings", [])

    # authoritative gate verdicts (reuse the gate's own rules)
    row = vr or {"finding_id": cand["finding_id"], "claimed_severity": sev,
                 "validation_status": "inconclusive", "severity_overclaim": False, "limitations": None}
    eng_blocks, eng_reason = gate.evaluate(row, "engagement", waived)
    sub_blocks, _ = gate.evaluate(row, "submission", waived)

    if not cand.get("poc_required"):
        bucket = "eval_only_not_required"
    elif overclaim:
        bucket = "severity_overclaim"
    elif vs == "invalid_poc":
        bucket = "invalid_poc"
    elif vs == "setup_only":
        bucket = "setup_only"
    elif vs == "duplicate_proof":
        bucket = "duplicate_proof"
    elif not test_file:
        bucket = "missing_poc"
    elif not raw_log and not (coll and coll.get("command_exit_code") is not None):
        bucket = "missing_collected_log"
    elif not sub_blocks:
        bucket = "submission_ready"
    elif mode == "engagement" and not eng_blocks:
        # in submission mode this finding fails the (stricter) submission gate, so fall through to its
        # specific gap bucket instead of resting in "engagement_ready_but_not_submission_ready".
        bucket = "engagement_ready_but_not_submission_ready"
    elif rna == "add_negative_control" or "no_negative_control_detected" in warnings:
        bucket = "needs_negative_control"
    elif rna == "needs_fork_test" or "fork_without_disclosed_block" in warnings:
        bucket = "needs_fork_context"
    elif rna in ("add_impact_assertion", "add_reachability_assertion") \
            or "no_value_assertion_detected" in warnings \
            or "revert_only_no_value_assertion_for_nondos_claim" in warnings:
        bucket = "needs_better_assertions"
    else:
        bucket = "inconclusive"

    return bucket, eng_blocks, eng_reason, sub_blocks, row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["engagement", "submission"], default="engagement",
                    help="engagement (default) buckets vs the engagement gate; submission uses the stricter "
                         "submission gate")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    mode = args.mode
    blkkey = "submission_blocked" if mode == "submission" else "engagement_blocked"

    pv = audit_path("output", "poc_validation")
    inv = _load_json(pv / "poc_inventory.json", {"candidates": []}) or {"candidates": []}
    coll = _load_json(pv / "collected_results.json", {"results": []}) or {"results": []}
    coll_by = {r.get("finding_id"): r for r in coll.get("results", [])}
    vres = _load_json(pv / "poc_validation_results.json", {"results": []}) or {"results": []}
    vres_by = {r.get("finding_id"): r for r in vres.get("results", [])}
    waivers = _load_json(pv / "waivers.json", {}) or {}
    waived = set(waivers.get("waived", []))
    notes_dir = pv / "validation_notes"

    stale = [rel for rel in INPUT_RELPATHS if not (audit_path(".") / rel).exists()]

    findings = []
    buckets: dict[str, list[str]] = defaultdict(list)
    for cand in inv.get("candidates", []):
        fid = cand["finding_id"]
        vr = vres_by.get(fid)
        c = coll_by.get(fid)
        note_path = notes_dir / f"{fid}.json"
        has_note = note_path.exists()
        bucket, eng_blocks, eng_reason, sub_blocks, row = classify(cand, vr, c, has_note, waived, mode)
        buckets[bucket].append(fid)
        findings.append({
            "finding_id": fid,
            "title": cand.get("title", ""),
            "severity": cand.get("severity_ceiling", "Unknown"),
            "validation_status": (vr or {}).get("validation_status", "inconclusive"),
            "proof_score": (vr or {}).get("proof_score", 0),
            "submission_ready": bool((vr or {}).get("submission_ready")) and not sub_blocks,
            "recommended_next_action": (vr or {}).get("recommended_next_action"),
            "missing_requirements": (vr or {}).get("failed_requirements", []),
            "warnings": (vr or {}).get("warnings", []),
            "test_file": (c or {}).get("test_file") or (vr or {}).get("test_file"),
            "test_name": (c or {}).get("test_name") or (vr or {}).get("test_name"),
            "command": (c or {}).get("command"),
            "raw_log_path": (c or {}).get("raw_result_path"),
            "validation_note_path": str(note_path.relative_to(audit_path("."))) if has_note else None,
            "manifest_refs": cand.get("manifest_refs", []),
            "bucket": bucket,
            "engagement_blocked": eng_blocks,
            "submission_blocked": sub_blocks,
            "short_reason": _short_reason(bucket, vr or {}, eng_reason),
        })

    def rank(sev):  # for sorting blocking items
        return gate.SEV_RANK.get(sev, 2)

    required = [f for f in findings if f["bucket"] != "eval_only_not_required"]
    high_crit_blocked = [f for f in required if f[blkkey] and rank(f["severity"]) >= 3]
    medium_blocked = [f for f in required if f[blkkey] and rank(f["severity"]) == 2]
    top_actions = Counter(f["recommended_next_action"] for f in required if f["recommended_next_action"])
    blocking_items = sorted(
        [{"finding_id": f["finding_id"], "severity": f["severity"], "reason": f["short_reason"]}
         for f in required if f[blkkey]],
        key=lambda x: -rank(x["severity"]))

    # ---- fix-list: exactly what to do next, ordered by urgency -------------
    def fix_tier(f: dict) -> int:
        r = rank(f["severity"])
        if f[blkkey] and r >= 3:   # High/Critical blocked
            return 0
        if f[blkkey] and r == 2:   # Medium blocked
            return 1
        if f["bucket"] == "engagement_ready_but_not_submission_ready" or f["validation_status"] == "partially_proven":
            return 2               # closest to submission_ready
        if f["bucket"] in ("missing_poc", "missing_collected_log"):
            return 3
        return 4                   # low-priority cleanup

    fixable = [f for f in findings if f["bucket"] not in ("submission_ready", "eval_only_not_required")]
    fixable.sort(key=lambda f: (fix_tier(f), -rank(f["severity"]), -f["proof_score"], f["finding_id"]))
    fix_items = []
    for f in fixable:
        action = fix_action(f)
        fix_items.append({
            "finding_id": f["finding_id"], "title": f["title"], "severity": f["severity"],
            "current_bucket": f["bucket"], "recommended_next_action": action,
            "why_blocked": f["short_reason"], "exact_missing_requirements": f["missing_requirements"],
            "test_file": f["test_file"], "test_name": f["test_name"], "raw_log_path": f["raw_log_path"],
            "validation_note_path": f["validation_note_path"],
            "shortest_next_step": shortest_next_step(action, f),
            "tier": fix_tier(f), "proof_score": f["proof_score"], "blocked": f[blkkey],
        })
    fix_groups: dict[str, list] = defaultdict(list)
    for it in fix_items:
        fix_groups[it["recommended_next_action"]].append(it)
    closest_to_ready = sorted([f for f in fixable if fix_tier(f) == 2],
                              key=lambda f: -f["proof_score"])
    submission_blockers = [{"finding_id": f["finding_id"], "severity": f["severity"], "reason": f["short_reason"]}
                           for f in sorted(required, key=lambda x: -rank(x["severity"])) if f["submission_blocked"]]

    summary = {
        "total_findings_needing_poc": len(required),
        "submission_ready": len(buckets["submission_ready"]),
        "engagement_ready": sum(1 for f in required if not f["engagement_blocked"]),
        "missing_poc": len(buckets["missing_poc"]),
        "missing_collected_log": len(buckets["missing_collected_log"]),
        "invalid_or_setup_only": len(buckets["invalid_poc"]) + len(buckets["setup_only"]),
        "severity_overclaim": len(buckets["severity_overclaim"]),
        "high_critical_blocked": len(high_crit_blocked),
        "medium_blocked": len(medium_blocked),
    }
    # extra metrics for the engagement report (Phase 7)
    metrics = {
        **summary,
        "validated_proven": sum(1 for f in required if f["validation_status"] == "proven"),
        "partially_proven": sum(1 for f in required if f["validation_status"] == "partially_proven"),
        "duplicate_proof": len(buckets["duplicate_proof"]),
        "inconclusive": len(buckets["inconclusive"]),
        "eval_only_not_required": len(buckets["eval_only_not_required"]),
        "top_next_actions": top_actions.most_common(5),
    }

    generated_at = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": generated_at,
        "mode": mode,
        "note": f"Operator readiness view (mode={mode}). submission_ready = passes the submission gate; "
                f"*_blocked = fails the {mode} gate. Reuses poc_validation_gate.evaluate; changes no proof verdict.",
        "metrics": metrics,
        "buckets": {b: buckets.get(b, []) for b in BUCKETS},
        "findings": findings,
        "blocking_items": blocking_items,
        "stale_or_missing_inputs": stale,
    }
    (pv / "engagement_report.json").write_text(json.dumps(report, indent=2))

    # ---- fix-list artifacts -----------------------------------------------
    fix_json_path = pv / "fix_list.json"
    fix_md_path = pv / "fix_list.md"
    fix_json_path.write_text(json.dumps({
        "generated_at": generated_at, "mode": mode, "total_items": len(fix_items),
        "groups": {a: fix_groups.get(a, []) for a in FIX_ACTIONS if fix_groups.get(a)},
        "ordered_items": fix_items,
    }, indent=2))
    TIER_NAME = {0: "High/Critical blocked", 1: "Medium blocked", 2: "Closest to submission-ready",
                 3: "Missing PoC", 4: "Cleanup"}
    fm = [f"# PoC Fix-List ({mode} mode)", "", f"_generated {generated_at}_", "",
          f"{len(fix_items)} finding(s) need work to reach submission-ready. "
          "Grouped by next action, ordered by urgency.", ""]
    for action in FIX_ACTIONS:
        items = fix_groups.get(action, [])
        if not items:
            continue
        fm.append(f"## {action} ({len(items)})")
        fm.append("")
        for it in items:
            fm.append(f"- [ ] **{it['finding_id']}** ({it['severity']}, tier {it['tier']}·{TIER_NAME[it['tier']]}) — "
                      f"{it['shortest_next_step']}")
            if it["exact_missing_requirements"]:
                fm.append(f"      missing: {', '.join(it['exact_missing_requirements'])}")
        fm.append("")
    if not fix_items:
        fm.append("Nothing to fix — every required finding is submission-ready. ✅")
    fix_md_path.write_text("\n".join(fm) + "\n")

    # dashboard-facing artifact (small)
    rel = lambda p: str(p.relative_to(audit_path(".")))  # noqa: E731
    dash = {
        "generated_at": generated_at,
        "mode": mode,
        "source_files": INPUT_RELPATHS,
        "fix_list_path": rel(fix_md_path),
        "summary": summary,
        "buckets": {b: buckets.get(b, []) for b in BUCKETS},
        "top_next_actions": top_actions.most_common(5),
        "top_fix_items": [{"finding_id": it["finding_id"], "severity": it["severity"],
                           "recommended_next_action": it["recommended_next_action"],
                           "shortest_next_step": it["shortest_next_step"]} for it in fix_items[:5]],
        "submission_blockers": submission_blockers[:10],
        "closest_to_ready": [{"finding_id": f["finding_id"], "severity": f["severity"],
                              "proof_score": f["proof_score"], "bucket": f["bucket"]}
                             for f in closest_to_ready[:5]],
        "blocking_items": blocking_items[:10],
        "stale_or_missing_inputs": stale,
    }
    # operator worklist pointers (populated by poc_fix_all.py; dashboard never depends on it existing).
    wl = _load_json(pv / "operator_worklist.json")
    dash["operator_worklist_path"] = rel(pv / "operator_worklist.md")
    dash["operator_worklist_count"] = (wl or {}).get("total", 0)
    dash["next_batch_actions"] = (wl or {}).get("next_batch_actions", [])
    dash_path = audit_path("output", "dashboard", "poc_validation_status.json")
    dash_path.parent.mkdir(parents=True, exist_ok=True)
    dash_path.write_text(json.dumps(dash, indent=2))

    # markdown
    md = [f"# PoC {'Submission' if mode == 'submission' else 'Engagement'} Readiness ({mode} mode)", "",
          f"_generated {generated_at} · *_blocked = fails the {mode} gate · see `fix_list.md` for next steps_", "",
          f"**{summary['submission_ready']} submission-ready** · "
          f"**{summary['engagement_ready']} engagement-ready** · "
          f"**{summary['high_critical_blocked']} High/Critical blocked** · "
          f"**{summary['missing_poc']} missing PoC** · "
          f"**{summary['invalid_or_setup_only']} invalid/setup-only** · "
          f"**{summary['severity_overclaim']} severity overclaim**", "",
          "## Buckets", "", "| Bucket | Count | Findings |", "|---|---|---|"]
    for b in BUCKETS:
        ids = buckets.get(b, [])
        if ids:
            md.append(f"| {b} | {len(ids)} | {', '.join(ids[:12])}{' …' if len(ids) > 12 else ''} |")
    md += ["", "## Most urgent blocked (engagement gate)", ""]
    if blocking_items:
        md += ["| Finding | Severity | Fix |", "|---|---|---|"]
        for b in blocking_items[:15]:
            md.append(f"| {b['finding_id']} | {b['severity']} | {b['reason']} |")
    else:
        md.append("None — nothing is blocked at the engagement gate.")
    md += ["", "## Top next actions", ""]
    for action, n in top_actions.most_common(5):
        md.append(f"- **{action}** × {n}")
    if stale:
        md += ["", "## Stale / missing inputs", ""] + [f"- `{s}`" for s in stale]
    (pv / "engagement_report.md").write_text("\n".join(md) + "\n")

    # reconciliation guard
    assert sum(len(v) for v in buckets.values()) == len(findings), "bucket counts must reconcile"

    if not args.quiet:
        print(f"PoC {mode} report: {len(findings)} findings · "
              f"{summary['submission_ready']} submission-ready · "
              f"{summary['high_critical_blocked']} High/Critical blocked ({mode} gate) · "
              f"{len(fix_items)} on the fix-list")
        print(f"  → {pv/'engagement_report.md'}")
        print(f"  → {fix_md_path}")
        print(f"  → {dash_path}  (dashboard: python scripts/dashboard.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
