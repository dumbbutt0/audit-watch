#!/usr/bin/env python3
"""validate_p208_l3_readiness.py — DRY-RUN, RESEARCH-ONLY, UN-WIRED L3 HIGH-bar policy helper (P208).

Operationalizes the validated L3 realized-impact HIGH standard (P204 decent + P207 vultisig) as an ADVISORY
severity policy. It NEVER submits, routes, promotes, or demotes a real finding; never sets submission_ready /
routing_allowed; never edits canonical labels or answer keys. It only:
  * validate <record.json>   -> JSON-schema + required-field check of an L3 readiness record
  * decide   <record.json>   -> compute high_promotion_allowed / blocker / calibrated_severity / submission_state
  * backtest                 -> run the P204/P207 controls + regression fixtures, score, emit metrics

Invariants (mirrors scripts/submission_readiness_review.py): research_only, routes_in_production:false, fail-open on
reads, no production routing reference. Not wired into run_pipeline/agent_policy/router.
"""
from __future__ import annotations
import json, os, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PD = ROOT / "documentation/research/assisted_mode/p208_l3_high_policy_dryrun"
SCHEMA = PD / "L3_READINESS_SCHEMA.json"

RESEARCH_ONLY = True
ROUTES_IN_PRODUCTION = False

_EMPTY = {"", "none", "n/a", "na", "unspecified", "abstract", "unknown", "0", None}


def _present(v) -> bool:
    return v is not None and str(v).strip().lower() not in _EMPTY


# P214: deterministic core-path DoS carve-out (behind AUDITWATCH_L3_READINESS; default-off output-equivalent).
_DOS_CARVEOUT_CRITERIA = [
    "executed_l3_harness", "deterministic_failure", "core_protocol_path", "supported_asset_or_path",
    "no_practical_workaround", "permissionless_or_normal_user_trigger",
    "affects_user_class_or_protocol_function", "not_self_inflicted_only",
    "control_case_demonstrates_expected_success", "no_trusted_admin_prereq",
]


def _l3_flag_on() -> bool:
    return os.environ.get("AUDITWATCH_L3_READINESS") in ("1", "true", "True", "yes", "on")


def _apply_dos_carveout(rec: dict, cal: str, allowed: bool, notes: str):
    """PURE. Returns (carveout_fields, cal2, allowed2). Upgrades a medium-DoS case to high ONLY when it is a declared
    carve-out candidate, no never-upgrade guard fires, and all 10 criteria are explicitly True. Never upgrades
    invalid/refuted/unexecuted/missing. See P213/P214 CARVEOUT_POLICY."""
    cv = {"dos_carveout_evaluated": True, "dos_carveout_applied": False,
          "dos_carveout_missing_criteria": [], "dos_carveout_blocker": "",
          "dos_carveout_notes": rec.get("dos_carveout_notes", "")}
    if rec.get("dos_carveout_candidate") is not True:
        cv["dos_carveout_blocker"] = "not a dos_carveout_candidate"
        return cv, cal, allowed
    # never-upgrade guards
    if "refut" in notes:
        cv["dos_carveout_blocker"] = "source_refuted"; return cv, cal, allowed
    if rec.get("production_source_modified") is True:
        cv["dos_carveout_blocker"] = "production_source_modified"; return cv, cal, allowed
    if rec.get("l3_status") in ("NOT_ATTEMPTED", "NEEDS_HARNESS"):
        cv["dos_carveout_blocker"] = "l3 not executed"; return cv, cal, allowed
    if cal != "medium":
        cv["dos_carveout_blocker"] = f"base label {cal} is not a medium-DoS case"; return cv, cal, allowed
    if rec.get("dos_carveout_human_judgment_required") is True and not _present(rec.get("dos_carveout_notes")):
        cv["dos_carveout_blocker"] = "human_judgment_required without written dos_carveout_notes"; return cv, cal, allowed
    missing = [k for k in _DOS_CARVEOUT_CRITERIA if rec.get(k) is not True]
    if missing:
        cv["dos_carveout_missing_criteria"] = missing
        cv["dos_carveout_blocker"] = "missing criteria: " + ",".join(missing)
        return cv, cal, allowed
    cv["dos_carveout_applied"] = True
    return cv, "high", True


# P227: bounded griefing/DoS phrases (narrow notes fallback only). Structured flag `bounded_griefing_dos` is the
# primary signal; these are a secondary fallback for records that describe boundedness but predate the flag.
_BOUNDED_PHRASES = ("no principal", "self-scoped", "self scoped", "selective", "fee revenue", "fee-loss",
                    "fee loss", "fee avoidance", "alternatives exist", "bounded")
# Unambiguous theft/principal phrases (avoid bare "principal loss"/"permanent loss" — they collide with the
# negation "no principal loss"; a genuine permanent_loss/theft finding is excluded by the impact_class gate anyway).
_PRINCIPAL_PHRASES = ("principal theft", "theft of", "steals", "steal ", "drains", "insolvency",
                      "protocol-wide loss")


def _is_bounded_griefing_dos(rec: dict) -> bool:
    """PURE. True iff the record is an explicitly BOUNDED griefing/DoS (fee-loss / self-scoped / selective /
    no principal theft). Primary signal = the structured `bounded_griefing_dos` flag; secondary = a narrow
    bounded phrase in victim_or_protocol_loss / magnitude_basis / source_validity_notes WITHOUT any principal/
    permanent-loss phrase. Used by the P227 cap to keep such cases at Medium even when base conditions allow."""
    if rec.get("bounded_griefing_dos") is True:
        return True
    if rec.get("bounded_griefing_dos") is False:
        return False  # author explicitly says NOT bounded -> never cap (e.g. a real core-path DoS)
    blob = " ".join(str(rec.get(k, "")).lower() for k in
                    ("victim_or_protocol_loss", "magnitude_basis", "source_validity_notes"))
    if any(p in blob for p in _PRINCIPAL_PHRASES):
        return False
    return any(p in blob for p in _BOUNDED_PHRASES)


def decide(rec: dict) -> dict:
    """Pure policy function. Returns derived advisory fields; mutates nothing external."""
    l3 = rec.get("l3_status", "NOT_ATTEMPTED")
    tier = rec.get("poc_tier", "NONE")
    notes = str(rec.get("source_validity_notes", "")).lower()
    ic = rec.get("impact_class", "unknown")
    blockers = []

    if l3 not in ("PASS", "HUMAN_OVERRIDE"):
        blockers.append(f"l3_status={l3} (need PASS or HUMAN_OVERRIDE)")
    if not _present(rec.get("affected_asset_or_state")):
        blockers.append("affected_asset_or_state not concrete")
    material = (_present(rec.get("actual_delta")) and _present(rec.get("victim_or_protocol_loss"))
               and _present(rec.get("magnitude_basis")))
    if not material:
        blockers.append("material delta not demonstrated (actual_delta/victim_loss/magnitude_basis)")
    if rec.get("attacker_model") not in ("permissionless", "program_accepted"):
        blockers.append(f"attacker_model={rec.get('attacker_model')} (need permissionless/program_accepted)")
    if rec.get("production_source_modified") is True:
        blockers.append("production_source_modified=true")
    if rec.get("dependency_mocks") == "creates_vulnerable_condition":
        blockers.append("mocks create the vulnerable condition")
    if not _present(rec.get("expected_delta_or_control")):
        blockers.append("no control / expected-vs-actual comparison")
    if l3 == "HUMAN_OVERRIDE" and not (_present(rec.get("source_validity_notes")) or _present(rec.get("poc_result"))):
        blockers.append("HUMAN_OVERRIDE without written rationale")

    allowed = len(blockers) == 0

    # P227: bounded griefing/DoS cap (flag-INDEPENDENT base calibration; narrow). A proven, permissionless,
    # material griefing/DoS whose impact is explicitly bounded (fee-loss / self-scoped / selective / no principal
    # theft) must NOT auto-promote to High. Disjoint from the P214 carve-out below: that UPGRADES a base-medium
    # core-path DoS (flag-on, dos_carveout_candidate + 10 criteria, never bounded); this cap only fires on a
    # base-ALLOWED griefing/DoS with an explicit bounded signal, so the two never apply to the same record.
    if allowed and ic in ("dos", "griefing") and _is_bounded_griefing_dos(rec):
        allowed = False
        blockers.append("P227 bounded griefing/DoS cap: bounded/self-scoped impact (no principal theft) — capped at medium")

    if allowed:
        cal = "high"
    elif l3 == "FAIL":
        cal = "invalid" if "refut" in notes else "medium"
    elif "refut" in notes:
        cal = "invalid"
    elif l3 == "NEEDS_HARNESS" or not _present(rec.get("magnitude_basis")):
        cal = "needs_harness_for_severity"
    elif ic in ("dos", "griefing", "precision", "bounded_local", "auth_only"):
        cal = "medium"   # unless L3 proves permanent loss/insolvency (which would make allowed=True above)
    else:
        cal = "medium"   # MEDIUM_OR_LOWER_CALIBRATED default

    if allowed:
        submission_state = "ready_for_submission_package"   # advisory; human review STILL required
    elif any(b.startswith("l3_status") or "control" in b or "HUMAN_OVERRIDE" in b for b in blockers):
        submission_state = "blocked_by_missing_poc"
    elif any("material delta" in b for b in blockers):
        submission_state = "blocked_by_missing_impact"
    else:
        submission_state = "blocked_by_missing_poc"

    result = {
        "candidate_id": rec.get("candidate_id"),
        "threat_ceiling": rec.get("threat_ceiling"),
        "high_promotion_allowed": allowed,
        "high_promotion_blocker": "" if allowed else "; ".join(blockers),
        "calibrated_severity": cal,
        "submission_state": submission_state,
        "human_review_required": True,
        "research_only": RESEARCH_ONLY,
        "routes_in_production": ROUTES_IN_PRODUCTION,
    }
    # P214: flag-guarded deterministic core-path DoS carve-out. Flag-off => result is byte-identical to pre-P214
    # (no carve-out keys, no severity change). Flag-on => may upgrade a qualifying medium-DoS case to high.
    if _l3_flag_on():
        cv, cal2, allowed2 = _apply_dos_carveout(rec, cal, allowed, notes)
        if cv["dos_carveout_applied"]:
            result["calibrated_severity"] = cal2
            result["high_promotion_allowed"] = allowed2
            result["high_promotion_blocker"] = ""
            result["submission_state"] = "ready_for_submission_package"
        result["calibrated_severity_after_l3"] = result["calibrated_severity"]
        result.update(cv)
    return result


def _schema_validate(rec: dict):
    try:
        import jsonschema
    except Exception:
        return None  # fail-open: schema lib absent
    schema = json.loads(SCHEMA.read_text())
    try:
        jsonschema.validate(rec, schema)
        return True
    except jsonschema.ValidationError as e:
        return f"SCHEMA_FAIL: {e.message}"


def cmd_validate(path):
    rec = json.loads(Path(path).read_text())
    r = _schema_validate(rec)
    print(json.dumps({"file": path, "schema": ("PASS" if r is True else r)}, indent=2))


def cmd_decide(path):
    rec = json.loads(Path(path).read_text())
    print(json.dumps(decide(rec), indent=2))


def _panel(rec, d):
    return (f"[{rec.get('candidate_id')}] ceiling={rec.get('threat_ceiling')} "
            f"awarded={rec.get('awarded_severity','-')} l3={rec.get('l3_status')}/{rec.get('poc_tier')} "
            f"-> calibrated={d['calibrated_severity']} high_allowed={d['high_promotion_allowed']} "
            f"submission={d['submission_state']}"
            + ("" if d['high_promotion_allowed'] else f"\n      blocker: {d['high_promotion_blocker']}"))


def cmd_backtest():
    rows = sorted(glob.glob(str(PD / "backtest" / "*.json"))) + sorted(glob.glob(str(PD / "regression" / "*.json")))
    n = matches = false_allow = false_block = schema_ok = schema_fail = 0
    blocked_static_high = allowed_l3_high = 0
    details = []
    for f in rows:
        rec = json.loads(Path(f).read_text())
        exp = rec.get("expected", {})
        sv = _schema_validate(rec)
        if sv is True or sv is None:
            schema_ok += 1
        else:
            schema_fail += 1
        d = decide(rec)
        n += 1
        ok = (d["high_promotion_allowed"] == exp.get("high_promotion_allowed"))
        if "calibrated_severity" in exp:
            ok = ok and (d["calibrated_severity"] == exp["calibrated_severity"])
        matches += 1 if ok else 0
        if d["high_promotion_allowed"] and not exp.get("high_promotion_allowed"):
            false_allow += 1
        if (not d["high_promotion_allowed"]) and exp.get("high_promotion_allowed"):
            false_block += 1
        if d["high_promotion_allowed"]:
            allowed_l3_high += 1
        if (not d["high_promotion_allowed"]) and rec.get("threat_ceiling") in ("HIGH_THREAD", "CRITICAL_THREAD"):
            blocked_static_high += 1
        status = "OK " if ok else "XX "
        details.append(status + _panel(rec, d))
    print("\n".join(details))
    metrics = {
        "phase": "P208", "candidates_tested": n, "expected_matches": matches,
        "false_allows": false_allow, "false_blocks": false_block,
        "blocked_static_or_ceiling_highs": blocked_static_high, "allowed_l3_highs": allowed_l3_high,
        "schema_validation_pass": schema_ok, "schema_validation_fail": schema_fail,
        "all_match": matches == n and false_allow == 0 and false_block == 0,
        "research_only": RESEARCH_ONLY, "routes_in_production": ROUTES_IN_PRODUCTION,
    }
    print("\nMETRICS " + json.dumps(metrics))
    (PD / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    return 0 if metrics["all_match"] else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backtest"
    if cmd == "validate":
        cmd_validate(sys.argv[2])
    elif cmd == "decide":
        cmd_decide(sys.argv[2])
    else:
        sys.exit(cmd_backtest())
