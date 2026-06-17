#!/usr/bin/env python3
"""
validate_poc.py — Decide whether a candidate PoC actually proves the finding claim (deterministic, no LLM).

A passing test is NOT proof. This validator enforces the "required-for-proven" contract and runs structural
heuristics that only ever DOWNGRADE a claim — it never invents a proof. Deep semantic judgment (is the caller
a realistic attacker? does the assertion map to the claimed invariant?) is supplied by a reviewer via an
optional notes file (output/poc_validation/validation_notes/<finding_id>.json, shaped like
schemas/poc_validation.schema.json) — typically written by a human or the /poc-validation skill using
prompts/poc_validation_review.md. With no reviewer notes the status stays conservative (never `proven`).

Reads:
    output/poc_validation/poc_inventory.json
    output/poc_validation/collected_results.json
    output/poc_validation/validation_notes/<finding_id>.json   (optional, per finding)
    output/merged_findings.json, output/coverage_manifest.json (linkage)

Writes:
    output/poc_validation/poc_validation_results.json
    output/poc_validation/poc_validation_results.md

Usage:
    python scripts/validate_poc.py [--finding-id <id>] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SEV_RANK = {"Informational": 0, "Info": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4, "Unknown": 2}

try:
    import jsonschema  # noqa: E402
    _SCHEMA = json.loads((ROOT / "schemas" / "poc_validation.schema.json").read_text())
except Exception:  # pragma: no cover - jsonschema is a declared dep
    jsonschema = None
    _SCHEMA = None

# --- heuristic patterns (text scans of the test file + raw log) ---
RE_STORAGE_WRITE = re.compile(r"\bvm\.store\s*\(")
RE_PRANK = re.compile(r"\bvm\.(prank|startPrank)\s*\(")
RE_PRIV_TOKEN = re.compile(r"\b(owner|admin|governance|governor|deployer|timelock|guardian|multisig)\b", re.IGNORECASE)
RE_EXPECT_REVERT = re.compile(r"\bvm\.expectRevert\b")
RE_VALUE_ASSERT = re.compile(r"\bassert(Eq|Gt|Lt|Ge|Le|Approx\w*)\s*\(")
RE_FORK = re.compile(r"\b(createSelectFork|createFork)\b")
RE_FORK_BLOCK = re.compile(r"\b(rollFork|block\.number|\b\d{6,}\b)")
DOS_RE = re.compile(r"\b(dos|denial|freeze|frozen|lock|stuck|griefing|liveness|revert)\w*", re.IGNORECASE)


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _read_text(rel_or_abs: str | None) -> str:
    if not rel_or_abs:
        return ""
    for base in (Path(rel_or_abs), ROOT / rel_or_abs, audit_path(".") / rel_or_abs):
        try:
            if base.exists() and base.is_file():
                return base.read_text(errors="replace")
        except OSError:
            continue
    return ""


def _bool(note: dict, key: str) -> bool:
    return bool(note.get(key)) if note else False


def severity_overclaim(claimed: str, supported: str | None) -> bool:
    if not supported:
        return False
    return SEV_RANK.get(claimed, 2) > SEV_RANK.get(supported, 2)


def validate_one(inv: dict, collected: dict | None, note: dict | None) -> dict:
    fid = inv["finding_id"]
    claimed_sev = inv.get("severity_ceiling", "Unknown")
    claim_is_dos = bool(DOS_RE.search(inv.get("title", "") + " " + inv.get("required_impact_assertion", "")))

    failed: list[str] = []
    warnings: list[str] = []

    test_file = (note or {}).get("test_file") or (collected or {}).get("test_file")
    test_name = (note or {}).get("test_name") or (collected or {}).get("test_name")
    command = (note or {}).get("command") or (collected or {}).get("command")
    exit_code = (collected or {}).get("command_exit_code")
    if exit_code is None:
        exit_code = (note or {}).get("command_exit_code")

    test_src = _read_text(test_file)
    log_src = _read_text((collected or {}).get("raw_result_path"))
    scan = test_src + "\n" + log_src

    # 1. test existence
    test_exists = bool(test_file) and bool(test_src)
    name_in_file = bool(test_name) and bool(test_name in test_src) if test_src else False
    cmd_refs_test = bool(command and test_name and test_name in command)
    if not test_exists:
        failed.append("test_file_missing")
    if test_file and not name_in_file:
        failed.append("test_name_not_in_file")
    if command and test_name and not cmd_refs_test:
        warnings.append("command_does_not_reference_test_name")

    # 2. finding linkage
    if not inv.get("manifest_refs") and not inv.get("affected_functions"):
        warnings.append("finding_has_no_manifest_refs_or_functions")

    # execution outcome
    if exit_code is not None and exit_code != 0:
        failed.append("command_exit_nonzero")

    # --- heuristic downgraders (only ever weaken) ---
    storage_write = bool(RE_STORAGE_WRITE.search(test_src))
    disclosed_setup = bool((note or {}).get("setup_assumptions"))
    if storage_write and not disclosed_setup:
        warnings.append("direct_storage_mutation_not_disclosed_as_setup")
    prank_priv = bool(RE_PRANK.search(test_src) and RE_PRIV_TOKEN.search(test_src))
    finding_allows_priv = bool((note or {}).get("privilege_assumptions"))
    if prank_priv and not finding_allows_priv:
        warnings.append("prank_as_privileged_actor_not_declared")
    revert_only = bool(RE_EXPECT_REVERT.search(test_src) and not RE_VALUE_ASSERT.search(test_src))
    if revert_only and not claim_is_dos:
        warnings.append("revert_only_no_value_assertion_for_nondos_claim")
    fork_undisclosed = bool(RE_FORK.search(scan) and not RE_FORK_BLOCK.search(scan)
                            and not (note or {}).get("fork_assumptions"))
    if fork_undisclosed:
        warnings.append("fork_without_disclosed_block")
    if test_src and not RE_VALUE_ASSERT.search(test_src) and not claim_is_dos:
        warnings.append("no_value_assertion_detected")

    # --- reviewer attestations (semantic; default False without notes) ---
    rc = _bool(note, "root_cause_proven")
    reach = _bool(note, "attacker_reachability_proven")
    impact = _bool(note, "impact_proven")
    transition = _bool(note, "state_transition_proven")
    severity_supported = (note or {}).get("severity_supported")
    why = (note or {}).get("why_test_proves_claim") or ""
    limitations = (note or {}).get("limitations")
    reviewer_status = (note or {}).get("validation_status")

    if not rc:
        failed.append("root_cause_not_proven")
    if not reach:
        failed.append("attacker_reachability_not_proven")
    if not impact and not claim_is_dos:
        failed.append("impact_not_proven")
    if not transition:
        failed.append("state_transition_not_proven")

    # --- determine validation_status (conservative) ---
    hard_invalid = ("test_name_not_in_file" in failed)
    storage_as_attack = storage_write and not disclosed_setup
    if reviewer_status == "duplicate_proof" or inv.get("status") == "duplicate":
        status = "duplicate_proof"
    elif exit_code is not None and exit_code != 0:
        status = "failed"
    elif hard_invalid:
        status = "invalid_poc"
    elif storage_as_attack:
        # storage mutation standing in for the attacker action: not a real PoC
        status = "setup_only"
    elif not test_exists and not note:
        status = "inconclusive"
    else:
        all_core = rc and reach and transition and (impact or claim_is_dos)
        proven_ok = (
            all_core and (exit_code == 0) and bool(why.strip()) and (limitations not in (None, ""))
            and test_exists and name_in_file and severity_supported is not None
        )
        if proven_ok:
            status = "proven"
        elif any([rc, reach, impact, transition]) and (note is not None):
            status = "partially_proven"
        else:
            status = "inconclusive"

    # reviewer may force a weaker status, never a stronger one
    order = ["proven", "partially_proven", "failed", "inconclusive", "setup_only", "invalid_poc", "duplicate_proof"]
    if reviewer_status in order and order.index(reviewer_status) > order.index(status):
        status = reviewer_status

    # --- proof score 0..100 ---
    score = 0
    score += 10 if test_exists else 0
    score += 5 if name_in_file else 0
    score += 5 if (inv.get("manifest_refs") or inv.get("affected_functions")) else 0
    score += 20 if rc else 0
    score += 20 if reach else 0
    score += 15 if transition else 0
    score += 20 if (impact or (claim_is_dos and revert_only)) else 0
    score += 5 if severity_supported else 0
    score -= 15 if storage_as_attack else 0
    score -= 5 * len([w for w in warnings if w in (
        "prank_as_privileged_actor_not_declared", "fork_without_disclosed_block",
        "revert_only_no_value_assertion_for_nondos_claim")])
    score = max(0, min(100, score))

    # --- severity supported / overclaim ---
    overclaim = severity_overclaim(claimed_sev, severity_supported)
    if overclaim:
        failed.append("severity_overclaim")

    submission_ready = (status == "proven" and not overclaim and (limitations not in (None, "")))

    # --- recommended next action ---
    if status == "proven" and submission_ready:
        action = "accept_for_submission"
    elif status in ("invalid_poc",):
        action = "reject_poc"
    elif status == "setup_only":
        action = "reject_poc"
    elif status == "duplicate_proof":
        action = "mark_inconclusive"
    elif overclaim:
        action = "downgrade_severity"
    elif not reach:
        action = "add_reachability_assertion"
    elif not (impact or claim_is_dos):
        action = "add_impact_assertion"
    elif "no_value_assertion_detected" in warnings or "revert_only_no_value_assertion_for_nondos_claim" in warnings:
        action = "add_impact_assertion"
    elif inv.get("required_proof_type") == "fork" and not RE_FORK.search(scan):
        action = "needs_fork_test"
    elif not test_exists:
        action = "needs_unit_test"
    elif status == "partially_proven":
        action = "add_negative_control"
    else:
        action = "mark_inconclusive"
    if "negative_control" not in scan.lower() and status in ("proven", "partially_proven"):
        warnings.append("no_negative_control_detected")

    return {
        "poc_id": (note or {}).get("poc_id") or f"POCV-{fid}",
        "finding_id": fid,
        "title": inv.get("title", ""),
        "claimed_severity": claimed_sev,
        "test_type": (note or {}).get("test_type") or inv.get("required_proof_type", "unit"),
        "test_file": test_file,
        "test_name": test_name,
        "command_exit_code": exit_code,
        "validation_status": status,
        "proof_score": score,
        "root_cause_proven": rc,
        "attacker_reachability_proven": reach,
        "impact_proven": impact,
        "state_transition_proven": transition,
        "guard_bypass_proven": (note or {}).get("guard_bypass_proven"),
        "severity_supported": severity_supported,
        "severity_overclaim": overclaim,
        "failed_requirements": sorted(set(failed)),
        "warnings": sorted(set(warnings)),
        "submission_ready": submission_ready,
        "recommended_next_action": action,
        "limitations": limitations,
        "why_test_proves_claim": why,
        "has_reviewer_notes": note is not None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--finding-id", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out = audit_path("output", "poc_validation")
    out.mkdir(parents=True, exist_ok=True)
    inv = _load_json(out / "poc_inventory.json", {"candidates": []}) or {"candidates": []}
    collected = _load_json(out / "collected_results.json", {"results": []}) or {"results": []}
    coll_by_fid: dict[str, dict] = {}
    for r in collected.get("results", []):
        coll_by_fid.setdefault(r.get("finding_id"), r)  # first/most-recent kept

    schema_errors: list[str] = []
    results = []
    for cand in inv.get("candidates", []):
        if not cand.get("poc_required"):
            continue
        fid = cand["finding_id"]
        if args.finding_id and fid != args.finding_id:
            continue
        note = _load_json(out / "validation_notes" / f"{fid}.json")
        if note is not None and jsonschema is not None and _SCHEMA is not None:
            try:
                jsonschema.validate(instance=note, schema=_SCHEMA)
            except jsonschema.ValidationError as e:
                schema_errors.append(f"{fid}: {e.message}")
                note = None  # malformed note is ignored (conservative)
        results.append(validate_one(cand, coll_by_fid.get(fid), note))

    summary = {s: sum(1 for r in results if r["validation_status"] == s)
               for s in ("proven", "partially_proven", "failed", "inconclusive", "invalid_poc", "setup_only", "duplicate_proof")}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reviewed": len(results),
        "summary": summary,
        "submission_ready_count": sum(1 for r in results if r["submission_ready"]),
        "schema_errors": schema_errors,
        "results": results,
    }
    (out / "poc_validation_results.json").write_text(json.dumps(report, indent=2))

    md = ["# PoC Validation Results", "",
          f"Reviewed {len(results)} PoC-required findings · "
          f"submission-ready {report['submission_ready_count']}", "",
          "| Finding | Sev | Status | Score | Sub-ready | Next action |",
          "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda x: (-x["proof_score"], x["finding_id"])):
        md.append(f"| {r['finding_id']} | {r['claimed_severity']} | {r['validation_status']} | "
                  f"{r['proof_score']} | {'yes' if r['submission_ready'] else 'no'} | {r['recommended_next_action']} |")
    md += ["", "## Failed requirements / warnings", ""]
    for r in results:
        if r["failed_requirements"] or r["warnings"]:
            md.append(f"- **{r['finding_id']}** ({r['validation_status']}): "
                      f"failed={r['failed_requirements'] or '—'}; warnings={r['warnings'] or '—'}")
    (out / "poc_validation_results.md").write_text("\n".join(md) + "\n")

    if not args.quiet:
        print(f"PoC validation: reviewed {len(results)} · " +
              " · ".join(f"{k}={v}" for k, v in summary.items() if v))
        if schema_errors:
            print(f"  schema errors (notes ignored): {len(schema_errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
