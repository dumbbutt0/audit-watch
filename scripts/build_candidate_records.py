#!/usr/bin/env python3
"""build_candidate_records.py — the ONE canonical per-finding record.

Finding state is currently a star-join across ~12 files (merged_findings.json + data/triage/*.jsonl +
gate_results.jsonl + pattern_check_results.jsonl + findings_confirmed.json + min_confirm_gate.json +
runtime_poc/results.jsonl + poc_completeness + confirm_gate.json). The dashboard, triage and report each re-derive
state from different subsets, which desyncs. This builds a single normalized record per finding at
`output/candidates/<id>.json` (+ `output/candidates_index.json`) joining all of them on finding id, and computes
ONE derived `state` enum so READY has a single definition.

Precision enforcement baked into `state` (review task 1): a High/Critical finding that is NOT multi-pass
confirmed (no `findings_confirmed.json` entry, or `human_review_required`, or score < threshold) can NEVER be
`ready` — it routes to `human_pending`. So skipping confirmation (the api-free default) no longer lets unconfirmed
High/Critical look submission-ready.

Read-only over the audit; deterministic; no LLM. Writes only under output/candidates/.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_context as ac  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HIGH = {"high", "critical"}


def _json(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _jsonl_by_id(p: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not p.exists():
        return out
    for ln in p.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        fid = r.get("finding_id") or r.get("id")
        if fid:
            out[fid] = r
    return out


def _threshold() -> float:
    pol = _json(ROOT / "config" / "agent_policy.json", {})
    return float((pol.get("multi_pass") or {}).get("confirmation_threshold", 0.6))


def _gate_summary(row: dict | None) -> dict:
    if not row:
        return {"present": False, "any_fail": False, "warn_count": 0, "fail_gates": []}
    gates = row.get("gate_results", [])
    fails = [g["name"] for g in gates if g.get("verdict") == "FAIL"]
    warns = sum(1 for g in gates if g.get("verdict") == "WARN")
    return {"present": True, "any_fail": bool(fails), "warn_count": warns, "fail_gates": fails}


def build() -> dict:
    adir = ac.get_audit_root()
    out_dir = adir / "output"
    merged = _json(out_dir / "merged_findings.json", {})
    findings = merged.get("findings", []) if isinstance(merged, dict) else (merged or [])
    if not findings:
        print(f"[build_candidate_records] no merged_findings.json findings in {adir}", file=sys.stderr)
        return {"records": [], "by_state": {}}

    lang = ac.audit_language()
    thr = _threshold()

    fp_by_id = _jsonl_by_id(adir / "data" / "fp_autopsies" / "pattern_check_results.jsonl")
    gate_by_id = _jsonl_by_id(adir / "data" / "triage" / "gate_results.jsonl")
    poc_by_id = _jsonl_by_id(adir / "data" / "runtime_poc" / "results.jsonl")
    triage_status: dict[str, str] = {}
    triage_row: dict[str, dict] = {}
    for bucket in ("submit", "poc_required", "downgraded", "rejected", "merged"):
        for fid, r in _jsonl_by_id(adir / "data" / "triage" / f"{bucket}.jsonl").items():
            triage_status[fid] = r.get("triage_status", bucket)
            triage_row[fid] = r  # carries impact.victim / attacker_model.attacker_type for who_loses/who_gains
    conf_doc = _json(out_dir / "findings_confirmed.json", {})
    conf_by_id = {f["id"]: f for f in conf_doc.get("findings", []) if "confirmation_score" in f}
    conf_skipped = bool(conf_doc.get("skipped"))
    minconf = _json(out_dir / "min_confirm_gate.json", {})
    minconf_blocking = set(minconf.get("blocking", [])) if isinstance(minconf, dict) else set()
    confirm_gate = _json(out_dir / "confirm" / "confirm_gate.json", {})
    reach_blocking = {b.get("finding_id"): b.get("status") for b in confirm_gate.get("blocking", [])} \
        if isinstance(confirm_gate, dict) else {}
    # ADVISORY-ONLY pre-READY submission-risk flags (reachability/novelty/design). These are surfaced as
    # readiness_ADVISORIES (non-blocking) — they never enter `state` derivation or readiness_blockers.
    srisk = _json(out_dir / "submission_risk.json", {})
    srisk_by_id = {r.get("finding_id"): r for r in srisk.get("findings", [])} if isinstance(srisk, dict) else {}

    out_records_dir = out_dir / "candidates"
    out_records_dir.mkdir(parents=True, exist_ok=True)
    # clear stale records
    for old in out_records_dir.glob("*.json"):
        old.unlink()

    records = []
    for f in findings:
        fid = f.get("id")
        if not fid:
            continue
        ice = f.get("ice_chain") or {}
        ite = f.get("ite") or {}
        loc = f.get("location") or {}
        sev = (ice.get("severity_ceiling") or f.get("severity") or "").strip()
        is_high = sev.lower() in HIGH

        fp_action = (fp_by_id.get(fid) or {}).get("recommended_action", "proceed")
        gates = _gate_summary(gate_by_id.get(fid))
        tstatus = triage_status.get(fid)
        conf = conf_by_id.get(fid)
        conf_ok_high = bool(conf) and conf.get("confirmation_score", 0) >= thr \
            and not conf.get("human_review_required")
        poc = poc_by_id.get(fid) or {}
        poc_proved = poc.get("status") == "proved" or poc.get("runtime_level", 0) >= 3

        # report-readiness fields (T10): who loses / who gains / suggested fix. Derive from triage when present.
        trow = triage_row.get(fid, {})
        who_loses = (trow.get("impact") or {}).get("victim") or (ice.get("who_loses"))
        who_gains = (trow.get("attacker_model") or {}).get("attacker_type") or (ice.get("who_gains"))
        suggested_fix = f.get("recommendation")
        evidence_missing = is_high and not (who_loses and who_gains and suggested_fix)

        blockers: list[str] = []
        if fp_action == "reject":
            blockers.append("fp_pattern_check: matched a rejection rule")
        if gates["any_fail"]:
            blockers.append(f"pre_submission_gate FAIL: {', '.join(gates['fail_gates'])}")
        if fid in minconf_blocking:
            blockers.append("min_confirm_gate: missing required confirmation fields")
        if fid in reach_blocking:
            blockers.append(f"confirm_gate: reachability {reach_blocking[fid]}")
        if is_high and not conf_ok_high:
            blockers.append("unconfirmed High/Critical — multi-pass confirmation missing/below-threshold (run /confirm)"
                            if not conf_skipped else
                            "unconfirmed High/Critical — confirmation was SKIPPED (run /confirm before submission)")
        if is_high and not poc_proved:
            blockers.append("High/Critical without an L3 PoC proving the awarded mechanism")
        if evidence_missing:
            miss = [k for k, v in (("who_loses", who_loses), ("who_gains", who_gains),
                                   ("suggested_fix", suggested_fix)) if not v]
            blockers.append(f"missing report fields for High/Critical: {', '.join(miss)}")

        # ---- single derived state ----
        if fp_action == "reject" or gates["any_fail"] or tstatus == "rejected":
            state = "rejected"
        elif tstatus in ("merged", "duplicate"):
            state = "duplicate"
        elif is_high and not conf_ok_high:
            state = "human_pending"            # confirmation enforcement: never ready unconfirmed
        elif fid in minconf_blocking or fid in reach_blocking:
            state = "human_pending"
        elif evidence_missing:
            state = "human_pending"            # High/Critical must carry who_loses/who_gains/suggested_fix
        elif tstatus == "submit" and (poc_proved or not is_high) and not blockers:
            state = "ready"
        elif is_high and not poc_proved:
            state = "poc_required"
        elif tstatus == "poc_required":
            state = "poc_required"
        elif tstatus is None:
            state = "candidate"                # awaiting triage
        else:
            state = "candidate"

        rec = {
            "id": fid,
            "schema": "candidate_record/v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "language": lang,
            "title": f.get("title", ""),
            "location": {"file": loc.get("file"), "function": loc.get("function"),
                         "contract": loc.get("contract"), "line_start": loc.get("line_start")},
            "classification": {"severity": f.get("severity"), "severity_ceiling": ice.get("severity_ceiling"),
                               "vuln_type": f.get("vuln_type"), "confidence": f.get("confidence")},
            "ice": {"impact": ice.get("impact"), "confidence": ice.get("confidence"),
                    "exploitability": ice.get("exploitability"), "exploit_path": ice.get("exploit_path")},
            "evidence": {  # report-readiness fields (review task 7/T10); null when not yet derived
                "attacker_model": ite.get("intent"), "entrypoint": loc.get("function"),
                "preconditions": ice.get("exploit_path"), "who_loses": who_loses, "who_gains": who_gains,
                "impact": f.get("impact"), "constraints": ice.get("exploitability"),
                "poc_result": (f"{poc.get('status')} L{poc.get('runtime_level')}" if poc else f.get("proof_of_concept")),
                "suggested_fix": suggested_fix,
            },
            "confirmation": {"present": bool(conf), "skipped": conf_skipped,
                             "score": (conf or {}).get("confirmation_score"),
                             "passes": (conf or {}).get("confirmation_passes"),
                             "human_review_required": (conf or {}).get("human_review_required"),
                             "threshold": thr, "required": is_high},
            "gates": {"fp_action": fp_action, "any_fail": gates["any_fail"], "fail_gates": gates["fail_gates"],
                      "warn_count": gates["warn_count"], "min_confirm_blocked": fid in minconf_blocking,
                      "reachability_status": reach_blocking.get(fid)},
            "poc": {"status": poc.get("status"), "level": poc.get("runtime_level"), "proved": poc_proved},
            "triage_status": tstatus,
            "state": state,
            "readiness_blockers": blockers,
            # ADVISORY-ONLY: flags likely bounty-rejection axes; does NOT affect `state` above.
            "readiness_advisories": (srisk_by_id.get(fid) or {}).get("advisories", []),
        }
        (out_records_dir / f"{fid}.json").write_text(json.dumps(rec, indent=2) + "\n")
        records.append(rec)

    by_state: dict[str, int] = {}
    for r in records:
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1
    index = {
        "audit_id": ac.get_active_audit().get("audit_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(records), "by_state": by_state,
        "records": [{"id": r["id"], "state": r["state"], "severity": r["classification"]["severity"],
                     "title": r["title"], "blockers": len(r["readiness_blockers"])} for r in records],
    }
    (out_dir / "candidates_index.json").write_text(json.dumps(index, indent=2) + "\n")
    return {"records": records, "by_state": by_state, "index": index}


if __name__ == "__main__":
    d = build()
    bs = d["by_state"]
    print(f"[build_candidate_records] {sum(bs.values())} record(s) -> output/candidates/ : "
          + (", ".join(f"{k}={v}" for k, v in sorted(bs.items())) or "(none)"))
