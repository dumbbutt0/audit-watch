#!/usr/bin/env python3
"""
poc_validation_write.py — Normalize /poc-validation skill outputs into reviewer notes (deterministic, no LLM).

Reads the per-finding reviewer notes the skill wrote, validates their shape, rejects bad/unknown items
(without raising), normalizes each into a schema-valid poc_validation note, and writes it to
output/poc_validation/validation_notes/<finding_id>.json. It NEVER decides proof — validate_poc.py re-derives
the validation_status from the booleans + structure. A passing test is still never automatically proof.

Reads:
    output/poc_validation/skill_outputs/<finding_id>.json
    output/poc_validation/poc_inventory.json   (to reject unknown finding ids)

Writes:
    output/poc_validation/validation_notes/<finding_id>.json   (schema-valid notes)
    output/poc_validation/poc_validation_write_summary.json

Usage:
    python scripts/poc_validation_write.py [--allow-unknown] [--overwrite] [--run-validate]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

SCHEMA_STATUS = {"proven", "partially_proven", "failed", "inconclusive", "invalid_poc", "setup_only", "duplicate_proof"}
# the skill may use richer recommendations; map the extra ones onto a schema-valid validation_status
STATUS_MAP = {
    "proven": "proven", "partially_proven": "partially_proven", "inconclusive": "inconclusive",
    "invalid_poc": "invalid_poc", "setup_only": "setup_only", "duplicate_proof": "duplicate_proof",
    "failed": "failed",
    "needs_better_assertions": "partially_proven",
    "needs_negative_control": "partially_proven",
    "needs_fork_context": "inconclusive",
}
SEV_ENUM = {"Critical", "High", "Medium", "Low", "Informational", None}

try:
    import jsonschema
    _SCHEMA = json.loads((ROOT / "schemas" / "poc_validation.schema.json").read_text())
except Exception:  # pragma: no cover
    jsonschema = None
    _SCHEMA = None


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def normalize(skill_out: dict, inv_entry: dict | None) -> dict:
    """Build a schema-valid poc_validation note from a skill output (filling conservative defaults)."""
    fid = skill_out["finding_id"]
    rec = skill_out.get("recommended_validation_status") or skill_out.get("validation_status") or "inconclusive"
    status = STATUS_MAP.get(rec, "inconclusive")
    sev = skill_out.get("severity_supported")
    if sev not in SEV_ENUM:
        sev = None
    note = {
        "poc_id": skill_out.get("poc_id") or f"POCV-{fid}",
        "finding_id": fid,
        "title": skill_out.get("title") or (inv_entry or {}).get("title", ""),
        "target_contracts": skill_out.get("target_contracts") or (inv_entry or {}).get("affected_files", []),
        "target_functions": skill_out.get("target_functions") or (inv_entry or {}).get("affected_functions", []),
        "manifest_refs": skill_out.get("manifest_refs") or (inv_entry or {}).get("manifest_refs", []),
        "test_file": skill_out.get("test_file"),
        "test_name": skill_out.get("test_name"),
        "test_type": skill_out.get("test_type") or (inv_entry or {}).get("required_proof_type", "unit"),
        "command": skill_out.get("command"),
        "command_exit_code": skill_out.get("command_exit_code"),
        "raw_result_path": skill_out.get("raw_result_path"),
        "validation_status": status,
        # booleans default False (conservative) when the skill omits them
        "root_cause_proven": bool(skill_out.get("root_cause_proven", False)),
        "attacker_reachability_proven": bool(skill_out.get("attacker_reachability_proven", False)),
        "impact_proven": bool(skill_out.get("impact_proven", False)),
        "state_transition_proven": bool(skill_out.get("state_transition_proven", False)),
        "guard_bypass_proven": skill_out.get("guard_bypass_proven"),
        "severity_supported": sev,
        "privilege_assumptions": skill_out.get("privilege_assumptions", []),
        "fork_assumptions": skill_out.get("fork_assumptions", []),
        "setup_assumptions": skill_out.get("setup_assumptions", []),
        "excluded_assumptions": skill_out.get("excluded_assumptions", []),
        "pre_state": skill_out.get("pre_state"),
        "actions": skill_out.get("actions", []),
        "post_state": skill_out.get("post_state"),
        "observed_delta": skill_out.get("observed_delta"),
        "expected_delta": skill_out.get("expected_delta"),
        "invariant_violated": skill_out.get("invariant_violated"),
        "why_test_proves_claim": skill_out.get("why_test_proves_claim") or "",
        "what_test_does_not_prove": skill_out.get("what_test_does_not_prove"),
        "limitations": skill_out.get("limitations") or "",
        "evidence": skill_out.get("evidence") or {},
        "reviewer_notes": (skill_out.get("reviewer_notes") or "")
        + (f" [skill recommended: {rec}]" if rec != status else ""),
    }
    return note


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-unknown", action="store_true", help="accept notes for ids not in the inventory")
    ap.add_argument("--overwrite", action="store_true", help="overwrite existing validation_notes")
    ap.add_argument("--run-validate", action="store_true", help="run validate_poc.py after writing")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out = audit_path("output", "poc_validation")
    skill_dir = out / "skill_outputs"
    notes_dir = out / "validation_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    if not skill_dir.exists():
        raise SystemExit(f"[poc_validation_write] no skill outputs at {skill_dir} — run the /poc-validation skill first.")

    inv = _load_json(out / "poc_inventory.json", {"candidates": []}) or {"candidates": []}
    inv_by_fid = {c["finding_id"]: c for c in inv.get("candidates", [])}

    applied, rejected = [], []
    for fp in sorted(skill_dir.glob("*.json")):
        raw = _load_json(fp)
        if not isinstance(raw, dict):
            rejected.append(f"{fp.name}: not a JSON object")
            continue
        fid = raw.get("finding_id")
        if not fid:
            rejected.append(f"{fp.name}: missing finding_id")
            continue
        if fid not in inv_by_fid and not args.allow_unknown:
            rejected.append(f"{fid}: not in inventory (use --allow-unknown to accept)")
            continue
        note = normalize(raw, inv_by_fid.get(fid))
        if jsonschema is not None and _SCHEMA is not None:
            try:
                jsonschema.validate(instance=note, schema=_SCHEMA)
            except jsonschema.ValidationError as e:
                rejected.append(f"{fid}: normalized note fails schema — {e.message}")
                continue
        dest = notes_dir / f"{fid}.json"
        if dest.exists() and not args.overwrite:
            rejected.append(f"{fid}: validation_note exists (use --overwrite)")
            continue
        dest.write_text(json.dumps(note, indent=2))
        applied.append({"finding_id": fid, "validation_status": note["validation_status"],
                        "recommended": raw.get("recommended_validation_status")})

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "applied": len(applied), "rejected": len(rejected),
        "applied_notes": applied, "rejected_reasons": rejected,
        "note": "validation_notes are staged only — validate_poc.py decides the final validation_status.",
    }
    (out / "poc_validation_write_summary.json").write_text(json.dumps(summary, indent=2))

    if not args.quiet:
        print(f"[ok] poc-validation notes applied: {len(applied)} · rejected: {len(rejected)}")
        for r in rejected[:15]:
            print(f"     [rejected] {r}")
        print("     Next: python scripts/validate_poc.py  (the deterministic validator decides proof)")

    if args.run_validate:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_poc.py")], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
