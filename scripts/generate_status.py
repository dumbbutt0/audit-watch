#!/usr/bin/env python3
"""
generate_status.py — Compact audit status for phone/remote control.

Reads all pipeline JSONL files, computes derived state, writes
output/status.json, and prints a phone-readable summary to stdout.

Usage:
    python scripts/generate_status.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── path bootstrap (same pattern as every other script) ──────────────────────
_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))
import audit_context  # noqa: E402

_ROOT = _SCRIPTS_DIR.parent

# ── helpers ───────────────────────────────────────────────────────────────────

def _read_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except (FileNotFoundError, OSError):
        pass
    return out


def _read_dir_json(directory: Path, key: str = "finding_id") -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not directory.exists():
        return out
    for p in sorted(directory.glob("*.json")):
        data = _read_json(p)
        if isinstance(data, dict):
            k = data.get(key) or p.stem
            out[k] = data
    return out


def _jsonl_by(path: Path, key: str = "finding_id") -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in _read_jsonl(path):
        k = row.get(key)
        if k is not None:
            out[k] = row
    return out


_SEV_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0, "info": 0}


def _sev_rank(s: Optional[str]) -> int:
    return _SEV_ORDER.get((s or "").lower(), 0)


def _layer_label(n: int) -> str:
    labels = {
        0: "Not started",
        1: "Static Analysis",
        2: "Agent Discovery",
        3: "Report Generation",
        4: "Triage",
        5: "Specialist Review",
        6: "PoC",
        7: "Quality Checklist",
        8: "Completeness Gate",
        9: "Final Submission",
    }
    return labels.get(n, f"Layer {n}")


# ── main ──────────────────────────────────────────────────────────────────────

def build_status() -> Dict[str, Any]:
    try:
        active_cfg = audit_context.get_active_audit()
        audit_id = active_cfg.get("audit_id") or ""
    except Exception:
        audit_id = ""

    if not audit_id:
        return {
            "error": "No active audit. Run: python scripts/audit_manager.py new <id>",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    meta = audit_context.get_audit_meta()

    # ── structured scope flag (custom-delta / partial runs) ───────────────────
    # A run that intentionally skips the full pipeline (e.g. a custom-delta
    # review) otherwise falls through to layer=0 / "Not started" — a silent 0
    # indistinguishable from a never-started audit. Read an explicit scope flag
    # so build_status can emit a disposition instead of a bare 0. Additive:
    # absent on normal full-pipeline audits (scope_tag == "", full_pipeline True).
    scope_tag = str(meta.get("scope") or "").strip()
    full_pipeline = meta.get("full_pipeline", True)
    if isinstance(full_pipeline, str):
        full_pipeline = full_pipeline.strip().lower() not in ("false", "0", "no")

    def _ap(*parts: str) -> Path:
        return audit_context.audit_path(*parts)

    # ── load all pipeline files ───────────────────────────────────────────────
    finding_defs   = _read_dir_json(_ap("data/findings"), key="finding_id")
    defined_ids    = set(finding_defs)

    triage_submit  = [r for r in _read_jsonl(_ap("data/triage", "submit.jsonl"))  if r.get("finding_id") in defined_ids]
    triage_poc     = [r for r in _read_jsonl(_ap("data/triage", "poc_required.jsonl")) if r.get("finding_id") in defined_ids]
    triage_down    = [r for r in _read_jsonl(_ap("data/triage", "downgraded.jsonl"))   if r.get("finding_id") in defined_ids]
    triage_rej     = [r for r in _read_jsonl(_ap("data/triage", "rejected.jsonl"))     if r.get("finding_id") in defined_ids]

    exploit_by_id  = _jsonl_by(_ap("data/exploitability", "models.jsonl"))
    severity_by_id = _jsonl_by(_ap("data/severity", "calibrated.jsonl"))
    poc_by_id      = _jsonl_by(_ap("data/runtime_poc", "results.jsonl"))
    judge_by_id    = _jsonl_by(_ap("data/judge_simulation", "results.jsonl"))
    checklist_by_id = _jsonl_by(_ap("data/quality_checklist", "results.jsonl"))
    completeness   = _read_dir_json(_ap("output/poc_completeness"), key="finding_id")

    static_done    = _ap("output", "static.json").exists()
    merged_done    = _ap("output", "merged_findings.json").exists()

    ice_manual     = _read_jsonl(_ap("output", "ice_manual_review.jsonl"))

    submissions_dir = _ap("output/submissions")
    submission_files = {p.stem.replace("_submission", "") for p in submissions_dir.glob("*.md")} if submissions_dir.exists() else set()

    # ── per-finding compact rows ──────────────────────────────────────────────
    triage_by_id: Dict[str, str] = {}
    for status, rows in (
        ("submit", triage_submit),
        ("poc_required", triage_poc),
        ("downgraded", triage_down),
        ("rejected", triage_rej),
    ):
        for r in rows:
            fid = r.get("finding_id")
            if fid:
                triage_by_id[fid] = r.get("triage_status") or status

    finding_rows: List[Dict[str, Any]] = []
    for fid, defn in sorted(finding_defs.items()):
        tri_status = triage_by_id.get(fid)
        exp = exploit_by_id.get(fid, {})
        sev = severity_by_id.get(fid, {})
        rp  = poc_by_id.get(fid, {})
        jg  = judge_by_id.get(fid, {})
        cl  = checklist_by_id.get(fid, {})
        cg  = completeness.get(fid, {})

        raw_sev = defn.get("severity") or "Unknown"
        cal_sev = sev.get("calibrated_severity") or raw_sev
        ceiling = cg.get("severity_ceiling")
        display_sev = ceiling or cal_sev

        fallback = None
        if (display_sev or "").lower() == "critical":
            fallback = "High"

        poc_status  = rp.get("status")
        judge_verdict = (
            jg.get("predicted_outcome")
            or jg.get("simulated_outcome")
            or jg.get("verdict")
        )
        checklist_ok  = cl.get("overall") not in ("failed", "block")
        upgrade_req   = bool(cg.get("upgrade_required"))
        submission_ready = bool(
            tri_status == "submit"
            and checklist_ok
            and not upgrade_req
        )
        has_submission = fid in submission_files

        finding_rows.append({
            "id":               fid,
            "title":            defn.get("title") or fid,
            "triage_status":    tri_status,
            "severity":         display_sev,
            "fallback":         fallback,
            "exploitability":   exp.get("exploitability_score"),
            "duplicate_risk":   (jg.get("duplicate_risk") or exp.get("duplicate_risk")),
            "poc_status":       poc_status,
            "poc_level":        cg.get("poc_level_achieved") or rp.get("poc_level"),
            "judge_verdict":    judge_verdict,
            "checklist":        cl.get("overall"),
            "upgrade_required": upgrade_req,
            "submission_ready": submission_ready,
            "has_submission":   has_submission,
        })

    # ── derived counts ────────────────────────────────────────────────────────
    poc_proved  = sum(1 for r in poc_by_id.values() if r.get("status") == "proved" and r.get("finding_id") in defined_ids)
    poc_failed  = sum(1 for r in poc_by_id.values() if r.get("status") == "failed"  and r.get("finding_id") in defined_ids)
    poc_pending = max(0, len(triage_poc) - poc_proved - poc_failed)

    submit_ready_ids = [f["id"] for f in finding_rows if f["submission_ready"]]

    blockers = [
        {"id": f["id"], "reason": "upgrade_required" if f["upgrade_required"] else "checklist_failed"}
        for f in finding_rows
        if f["triage_status"] == "submit" and (f["upgrade_required"] or f["checklist"] in ("failed", "block"))
    ]

    # ICE manual review items block progress — surface them alongside hard blockers
    ice_review_ids = [
        r.get("finding_id") or r.get("id", "?")
        for r in ice_manual
        if not (r.get("manual_override") or {}).get("enabled")
    ]

    # ── current_layer + next_action ───────────────────────────────────────────
    layer = 0
    last_completed = "Nothing yet"
    next_action = "Run static analysis"
    next_command = "python tools/static_analysis.py <contract_path>"

    if static_done:
        layer = 1
        last_completed = "Static analysis complete"
        next_action = "Run specialist agents"
        next_command = "(spawn agents via Task tool)"

    if merged_done or finding_rows:
        layer = 2
        last_completed = "Agent discovery complete"
        next_action = "Run report generator"
        next_command = "python tools/report_generator.py"

    if merged_done:
        layer = 3
        last_completed = "Report generated"
        next_action = "Run triage"
        next_command = "python scripts/triage_findings.py"

    if triage_submit or triage_poc or triage_down or triage_rej:
        layer = 4
        last_completed = f"Triage complete ({len(triage_submit)} submit, {len(triage_poc)} poc_required)"
        next_action = "Run specialist review"
        next_command = "python scripts/run_specialist_review.py"

    if exploit_by_id or severity_by_id or judge_by_id:
        total = len(finding_rows)
        done = len([fid for fid in defined_ids if fid in exploit_by_id])
        layer = 5
        last_completed = f"Specialist review: {done}/{total} findings scored"
        next_action = "Run PoC generation for poc_required findings"
        next_command = "python scripts/run_integrated_poc.py --all"

    if poc_by_id:
        layer = 6
        last_completed = f"{poc_proved}/{poc_proved + poc_failed + poc_pending} PoC tests passing"
        next_action = "Run quality checklist"
        next_command = "python scripts/run_quality_checklist.py --all"

    if checklist_by_id:
        layer = 7
        cl_passed = sum(1 for v in checklist_by_id.values() if v.get("overall") == "passed")
        layer_total = len(checklist_by_id)
        last_completed = f"Quality checklist: {cl_passed}/{layer_total} passed"
        next_action = "Run PoC completeness gate"
        next_command = "python scripts/analyze_poc_completeness.py --all"

    if completeness:
        layer = 8
        last_completed = f"Completeness gate: {len(completeness)} findings assessed"
        next_action = "Build final submission pack"
        next_command = "python scripts/final_submission_pack.py"

    if submission_files and not blockers and submit_ready_ids:
        layer = 9
        last_completed = f"Submission pack ready ({len(submit_ready_ids)} findings)"
        next_action = "Review and submit"
        next_command = "# Review output/submission_pack.md then submit"

    # ── scope disposition (explicit, never a silent 0) ────────────────────────
    disposition = None
    if scope_tag or full_pipeline is False:
        disp_scope = scope_tag or "custom-delta"
        disposition = f"scope={disp_scope}, full pipeline skipped"
        if layer == 0:
            # nothing on the standard pipeline ran — say so explicitly instead
            # of the default "Not started" that reads like an abandoned audit
            last_completed = f"Custom-scope run ({disp_scope}) — full pipeline intentionally skipped"
            next_action = "Review custom-scope findings directly (no standard pipeline layer applies)"
            next_command = "# custom-delta review — see data/findings/ and output/"

    # ── sort top findings ─────────────────────────────────────────────────────
    def _sort_key(f: Dict[str, Any]):
        is_submit = (f["triage_status"] == "submit")
        exp_score = f["exploitability"] or 0
        sev_score = _sev_rank(f["severity"])
        return (is_submit, exp_score, sev_score)

    top_findings = sorted(finding_rows, key=_sort_key, reverse=True)[:10]

    # ── assemble status dict ──────────────────────────────────────────────────
    status: Dict[str, Any] = {
        "audit_id":          audit_id,
        "audit_name":        meta.get("name", audit_id),
        "platform":          meta.get("platform", ""),
        "deadline":          meta.get("deadline", ""),
        "current_layer":     layer,
        "current_layer_label": disposition if (disposition and layer == 0) else _layer_label(layer),
        "scope":             scope_tag or None,
        "full_pipeline":     bool(full_pipeline),
        "disposition":       disposition,
        "last_completed":    last_completed,
        "next_action":       next_action,
        "next_command":      next_command,
        "triage": {
            "submit":       len(triage_submit),
            "poc_required": len(triage_poc),
            "downgraded":   len(triage_down),
            "rejected":     len(triage_rej),
        },
        "poc": {
            "proved":  poc_proved,
            "failed":  poc_failed,
            "pending": poc_pending,
        },
        "submit_ready_count": len(submit_ready_ids),
        "submit_ready_ids":   submit_ready_ids,
        "blockers":           blockers,
        "ice_review_queue":   ice_review_ids,
        "top_findings":       top_findings,
        "timestamp":          datetime.now(timezone.utc).isoformat(),
    }

    return status


def _print_summary(s: Dict[str, Any]) -> None:
    if "error" in s:
        print(s["error"])
        return

    deadline = s["deadline"] or "—"
    print(f"=== Audit Watch — {s['audit_id']} ===")
    print(f"Platform: {s['platform'] or '—'}  |  Deadline: {deadline}")
    print()
    print(f"Pipeline:  Layer {s['current_layer']} ({s['current_layer_label']})")
    print(f"Last done: {s['last_completed']}")
    print(f"Next:      {s['next_action']}")
    print(f"           {s['next_command']}")
    print()
    t = s["triage"]
    print(f"Triage:  {t['submit']} submit  |  {t['poc_required']} poc_required  |  {t['downgraded']} downgraded  |  {t['rejected']} rejected")
    p = s["poc"]
    print(f"PoC:     {p['proved']} proved  |  {p['failed']} failed  |  {p['pending']} pending")
    print(f"Submit-ready: {s['submit_ready_count']}")
    print()
    blockers = s["blockers"]
    ice_queue = s.get("ice_review_queue", [])
    if blockers or ice_queue:
        print("Blockers:")
        for b in blockers:
            print(f"  {b['id']}: {b['reason']}")
        if ice_queue:
            print(f"  ICE manual review needed ({len(ice_queue)}): {', '.join(ice_queue)}")
            print("    → Run: python scripts/run_impact_chain_escalation.py  then manually trace consumers")
    else:
        print("Blockers: none")
    print()
    if s["top_findings"]:
        print("Top findings:")
        for f in s["top_findings"]:
            sev = f["severity"] or "?"
            fallback = f"→{f['fallback']}" if f["fallback"] else ""
            poc = f"poc={f['poc_status']}" if f["poc_status"] else "poc=—"
            judge = f"judge={f['judge_verdict']}" if f["judge_verdict"] else "judge=—"
            ready = "✓ ready" if f["submission_ready"] else ("- no submission" if not f["has_submission"] else "- missing checks")
            print(f"  {f['id']:<12} {sev+fallback:<18} {poc:<14} {judge:<18} {ready}")


def main() -> None:
    status = build_status()

    if "error" not in status:
        try:
            out_path = audit_context.audit_path("output", "status.json")
            out_path.write_text(json.dumps(status, indent=2, default=str), encoding="utf-8")
        except Exception as exc:
            print(f"[generate_status] Warning: could not write status.json: {exc}", file=sys.stderr)

    _print_summary(status)

    # ── Hermes: write session recap ───────────────────────────────────────────
    try:
        from scripts.hermes_bridge import write_audit_recap, is_hermes_enabled
        if is_hermes_enabled():
            _t = status.get("triage", {})
            _p = status.get("poc", {})
            write_audit_recap({
                "audit_id": status.get("audit_id", ""),
                "session_timestamp": status.get("generated_at", ""),
                "pipeline_state": status,
                "findings_summary": {
                    "total": len(status.get("top_findings", [])),
                    "submitted": _t.get("submit", 0),
                    "rejected": _t.get("rejected", 0),
                    "poc_required": _t.get("poc_required", 0),
                    "proved": _p.get("proved", 0),
                },
                "human_escalations_triggered": [],
                "memory_events_written": 0,
                "open_questions_for_hermes": [],
            })
    except Exception:
        pass


if __name__ == "__main__":
    main()
