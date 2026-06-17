#!/usr/bin/env python3
"""
poc_validation_prepare.py — Bundle PoC-required findings for the /poc-validation skill (deterministic, no LLM).

Packages everything the skill needs to reason about one finding's PoC in-session: the finding claim, the
affected source excerpt, the PoC test excerpt, the captured run log, and the current proof gaps. It RUNS NO
TESTS — it only packages context. The skill reads these bundles, applies prompts/poc_validation_review.md, and
writes reviewer notes; poc_validation_write.py then normalizes them and validate_poc.py decides proof.

Reads (each optional; skipped gracefully):
    output/poc_validation/poc_inventory.json          (worklist; run poc_inventory.py first)
    output/poc_validation/collected_results.json      (test command + exit code + raw log path)
    output/poc_validation/poc_validation_results.json (existing validation status + gaps)
    output/merged_findings.json                       (location.lines / impact for source excerpts)

Writes:
    output/poc_validation/bundles/<finding_id>.json
    output/poc_validation/bundles/index.json

Usage:
    python scripts/poc_validation_prepare.py
      [--finding-id ID] [--status missing_poc|poc_exists_unvalidated|invalid|partially_proven|all]
      [--max-items N] [--overwrite]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# default selection: everything that still needs review (not validated, not eval-only)
REVIEW_STATUSES = {"missing_poc", "poc_exists_unvalidated", "invalid", "partially_proven"}
PROOF_FIELDS = ("root_cause_proven", "attacker_reachability_proven", "impact_proven", "state_transition_proven")


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _read_excerpt(rel: str | None, lines: str | None = None, max_lines: int = 80) -> str:
    """Read a source/test file relative to repo root or audit root; optionally slice a line range."""
    if not rel:
        return ""
    for base in (Path(rel), ROOT / rel, audit_path(".") / rel):
        try:
            if base.exists() and base.is_file():
                text = base.read_text(errors="replace").splitlines()
                if lines:
                    nums = [int(n) for n in str(lines).replace("-", " ").split() if n.strip().isdigit()]
                    if nums:
                        lo = max(1, min(nums) - 5)
                        hi = min(len(text), max(nums) + 5)
                        return "\n".join(f"{i}: {text[i - 1]}" for i in range(lo, hi + 1))
                return "\n".join(text[:max_lines])
        except (OSError, ValueError):
            continue
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--finding-id", default=None)
    ap.add_argument("--status", default="review",
                    choices=["missing_poc", "poc_exists_unvalidated", "invalid", "partially_proven", "all", "review"])
    ap.add_argument("--max-items", type=int, default=0, help="0 = all selected")
    ap.add_argument("--overwrite", action="store_true", help="rewrite bundles that already exist")
    args = ap.parse_args()

    out = audit_path("output", "poc_validation")
    inv = _load_json(out / "poc_inventory.json", {"candidates": []}) or {"candidates": []}
    collected = _load_json(out / "collected_results.json", {"results": []}) or {"results": []}
    coll_by_fid = {r.get("finding_id"): r for r in collected.get("results", [])}
    vres = _load_json(out / "poc_validation_results.json", {"results": []}) or {"results": []}
    vres_by_fid = {r.get("finding_id"): r for r in vres.get("results", [])}
    merged = {f.get("id") or f.get("finding_id"): f
              for f in (_load_json(audit_path("output") / "merged_findings.json", {}) or {}).get("findings", [])}

    cands = [c for c in inv.get("candidates", []) if c.get("poc_required")]
    if args.finding_id:
        cands = [c for c in cands if c["finding_id"] == args.finding_id]
    elif args.status == "review":
        cands = [c for c in cands if c.get("status") in REVIEW_STATUSES]
    elif args.status != "all":
        cands = [c for c in cands if c.get("status") == args.status]
    if args.max_items:
        cands = cands[:args.max_items]

    bundle_dir = out / "bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    index, written, skipped = [], 0, 0
    for c in cands:
        fid = c["finding_id"]
        dest = bundle_dir / f"{fid}.json"
        if dest.exists() and not args.overwrite:
            skipped += 1
            index.append({"finding_id": fid, "bundle": dest.name, "status": "exists_skipped"})
            continue
        coll = coll_by_fid.get(fid, {})
        vr = vres_by_fid.get(fid, {})
        mf = merged.get(fid, {})
        loc = mf.get("location", {}) or {}
        source_excerpt = _read_excerpt(loc.get("file") or (c.get("affected_files") or [None])[0], loc.get("lines"))
        test_excerpt = _read_excerpt(coll.get("test_file"))
        missing = vr.get("failed_requirements") or [f for f in PROOF_FIELDS]  # default: all unproven
        bundle = {
            "finding_id": fid,
            "title": c.get("title", ""),
            "severity": c.get("severity_ceiling", "Unknown"),
            "claimed_impact": c.get("required_impact_assertion", "") or mf.get("impact", ""),
            "target_contracts": c.get("affected_files", []),
            "target_functions": c.get("affected_functions", []),
            "manifest_refs": c.get("manifest_refs", []),
            "required_attacker_entrypoint": c.get("required_attacker_entrypoint", ""),
            "required_proof_type": c.get("required_proof_type", "unit"),
            "source_spans": [f"{loc.get('file','')}:{loc.get('lines','')}".strip(":")] if loc else [],
            "test_file": coll.get("test_file"),
            "test_name": coll.get("test_name"),
            "command": coll.get("command"),
            "command_exit_code": coll.get("command_exit_code"),
            "raw_result_path": coll.get("raw_result_path"),
            "test_status": coll.get("test_status"),
            "existing_validation_status": vr.get("validation_status"),
            "missing_proof_fields": missing,
            "source_excerpt": source_excerpt,
            "test_excerpt": test_excerpt,
            "prompt_instructions": (
                "Apply prompts/poc_validation_review.md literally. A passing test is NOT proof. Be conservative: "
                "never set a *_proven boolean true unless the test demonstrates it on the REAL path; flag "
                "setup-only (vm.store), impossible privileges (prank as owner/admin), missing impact assertions, "
                "missing negative controls, and severity overclaim. Read the actual source and test with the Read "
                "tool — the excerpts here are only a starting point. Write JSON only to "
                f"output/poc_validation/skill_outputs/{fid}.json."),
            "allowed_classifications": [
                "proven", "partially_proven", "inconclusive", "invalid_poc", "setup_only",
                "duplicate_proof", "needs_better_assertions", "needs_fork_context", "needs_negative_control"],
        }
        dest.write_text(json.dumps(bundle, indent=2))
        written += 1
        index.append({"finding_id": fid, "bundle": dest.name, "severity": bundle["severity"],
                      "status": c.get("status"), "has_test": bool(coll.get("test_file"))})

    (bundle_dir / "index.json").write_text(json.dumps({
        "total": len(index), "written": written, "skipped_existing": skipped,
        "bundles": index,
        "instructions": ("For each bundle: read finding + source + test + raw log, apply "
                         "prompts/poc_validation_review.md, and write reviewer notes (JSON only) to "
                         "output/poc_validation/skill_outputs/<finding_id>.json with the *_proven booleans, "
                         "severity_supported, why_test_proves_claim, limitations, and recommended_validation_status. "
                         "Then run: python scripts/poc_validation_write.py && python scripts/validate_poc.py"),
    }, indent=2))

    print(f"[ok] poc-validation bundles → {bundle_dir}")
    print(f"     {written} written · {skipped} existing skipped · {len(cands)} selected")
    print("     Next: run the /poc-validation skill, then python scripts/poc_validation_write.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
