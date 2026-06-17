#!/usr/bin/env python3
"""
submission_gate.py — strict submission-readiness gate (orchestrator + CLI).

Consumes a self-contained submission_candidate.json and decides exactly one of:
    DO_NOT_SUBMIT
    NEEDS_MORE_PROOF
    READY_FOR_HUMAN_REVIEW
    READY_TO_SUBMIT_AFTER_APPROVAL

It NEVER autonomously submits. human_approval_required is always forced true.

Isolation: this layer imports nothing from the detection pipeline. It reads
only the candidate file(s) it is pointed at.

Usage:
    submission_gate.py --candidate path/to/candidate.json
    submission_gate.py --dir submission/examples/
    submission_gate.py --candidate c.json --json-out out.json --report-out report.md
    submission_gate.py --dir submission/examples/ --strict   # exit!=0 on NEEDS_MORE_PROOF too

Exit codes:
    0  every candidate is READY_FOR_HUMAN_REVIEW or READY_TO_SUBMIT_AFTER_APPROVAL
    1  at least one candidate is DO_NOT_SUBMIT (or, with --strict, NEEDS_MORE_PROOF)
    2  a candidate failed schema validation / could not be parsed
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_defense  # noqa: E402
import gate_duplicate  # noqa: E402
import gate_evidence  # noqa: E402
import gate_human_approval  # noqa: E402
import gate_impact_severity  # noqa: E402
import gate_poc  # noqa: E402
import gate_reachability  # noqa: E402
import gate_scope  # noqa: E402
from _common import (  # noqa: E402
    GateResult,
    aggregate,
    load_candidate,
    validate_schema,
)
from render import render_readiness_report  # noqa: E402

# ordered list of the 8 hard gates
GATES = [
    gate_scope,
    gate_reachability,
    gate_impact_severity,
    gate_poc,
    gate_duplicate,
    gate_evidence,
    gate_defense,
    gate_human_approval,
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_candidate(candidate: dict) -> dict:
    """Run all gates over one candidate and return the verdict report."""
    schema_errors = validate_schema(candidate)

    results: list[GateResult] = []
    if schema_errors:
        # A malformed candidate cannot be trusted; do not run partial gates as
        # if they were authoritative — block and report the schema errors.
        report = {
            "finding_id": candidate.get("finding_id", "<unknown>"),
            "title": candidate.get("title", ""),
            "recommended_status": "DO_NOT_SUBMIT",
            "overall_verdict": "FAIL",
            "human_approval_required": True,
            "blockers": ["candidate failed schema validation"],
            "needs_proof": [],
            "warnings": [],
            "schema_errors": schema_errors,
            "author_recommended_status": candidate.get("recommended_status"),
            "gates": [],
            "evaluated_at": _now(),
        }
        return report

    for mod in GATES:
        results.extend(mod.evaluate(candidate))

    agg = aggregate(results)
    agg.update({
        "finding_id": candidate.get("finding_id", "<unknown>"),
        "title": candidate.get("title", ""),
        "schema_errors": [],
        "author_recommended_status": candidate.get("recommended_status"),
        "evaluated_at": _now(),
    })
    # invariant, re-asserted: human approval always required, never auto-submit.
    agg["human_approval_required"] = True
    return agg


def _collect_paths(args) -> list[Path]:
    paths: list[Path] = []
    if args.candidate:
        paths.append(Path(args.candidate))
    if args.dir:
        d = Path(args.dir)
        paths.extend(sorted(p for p in d.glob("*.json")))
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict submission-readiness gate (never auto-submits).")
    ap.add_argument("--candidate", help="Path to a single submission_candidate.json")
    ap.add_argument("--dir", help="Directory of *.json candidate files")
    ap.add_argument("--json-out", help="Write the machine-readable verdict(s) here")
    ap.add_argument("--report-out", help="Write a markdown readiness report here (single candidate) "
                                         "or a directory (with --dir)")
    ap.add_argument("--strict", action="store_true",
                    help="Also exit non-zero when any candidate is NEEDS_MORE_PROOF")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    paths = _collect_paths(args)
    if not paths:
        print("error: provide --candidate FILE or --dir DIR", file=sys.stderr)
        return 2

    reports: list[dict] = []
    had_parse_error = False
    for path in paths:
        try:
            candidate = load_candidate(path)
        except (OSError, json.JSONDecodeError) as e:
            had_parse_error = True
            reports.append({
                "finding_id": str(path),
                "recommended_status": "DO_NOT_SUBMIT",
                "overall_verdict": "FAIL",
                "human_approval_required": True,
                "blockers": [f"could not parse candidate: {e}"],
                "schema_errors": [str(e)],
                "evaluated_at": _now(),
            })
            continue
        report = evaluate_candidate(candidate)
        report["source_file"] = str(path)
        reports.append(report)

    # markdown reports
    if args.report_out:
        out = Path(args.report_out)
        if args.dir or len(reports) > 1:
            out.mkdir(parents=True, exist_ok=True)
            for r in reports:
                fid = r.get("finding_id", "candidate").replace("/", "_")
                (out / f"{fid}.md").write_text(render_readiness_report(r))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_readiness_report(reports[0]))

    # machine-readable verdicts
    payload = {"candidates": reports, "evaluated_at": _now(),
               "tool": "submission_gate", "never_auto_submits": True}
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(payload, indent=2))

    if not args.quiet:
        for r in reports:
            print(f"{r.get('finding_id'):<24} {r.get('recommended_status')}")
            for b in r.get("blockers", []):
                print(f"    BLOCK : {b}")
            for n in r.get("needs_proof", []):
                print(f"    PROOF : {n}")
            for w in r.get("warnings", []):
                print(f"    WARN  : {w}")

    statuses = {r.get("recommended_status") for r in reports}
    if had_parse_error or any(r.get("schema_errors") for r in reports):
        return 2 if "DO_NOT_SUBMIT" not in statuses else 1
    if "DO_NOT_SUBMIT" in statuses:
        return 1
    if args.strict and "NEEDS_MORE_PROOF" in statuses:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
