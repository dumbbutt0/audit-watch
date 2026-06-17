#!/usr/bin/env python3
"""
gate_duplicate.py — Gate 5: Duplicate / known-issue.

Requires that the submitter has:
  - searched local prior audit reports / internal findings (duplicate_check_status)
  - searched known issues / prior public disclosures (known_issue_check_status)
  - marked any possible duplicate risk (prior_audit_overlap)

Outcomes:
  - confirmed_duplicate (either source)          -> FAIL (DO_NOT_SUBMIT)
  - not_searched (either source)                 -> NEEDS_PROOF
  - possible_duplicate / non-empty overlap        -> WARN (human review)
"""
from __future__ import annotations

from _common import FAIL, NEEDS_PROOF, PASS, WARN, GateResult, is_empty

GATE = 5
NAME = "duplicate_known_issue"


def evaluate(candidate: dict) -> list[GateResult]:
    results: list[GateResult] = []

    dup = candidate.get("duplicate_check_status", "not_searched")
    known = candidate.get("known_issue_check_status", "not_searched")
    overlap = candidate.get("prior_audit_overlap") or []

    for label, status in (("local prior-audit", dup), ("known-issue", known)):
        if status == "confirmed_duplicate":
            results.append(GateResult(
                GATE, NAME, FAIL,
                f"Confirmed duplicate per {label} search.",
                tag="duplicate_finding",
            ))
        elif status == "not_searched":
            results.append(GateResult(
                GATE, NAME, NEEDS_PROOF,
                f"{label.capitalize()} search has not been performed.",
                tag="duplicate_unsearched",
            ))
        elif status == "possible_duplicate":
            results.append(GateResult(
                GATE, NAME, WARN,
                f"Possible duplicate flagged by {label} search; a human must "
                "compare before submission.",
                tag="possible_duplicate",
            ))

    if not is_empty(overlap):
        results.append(GateResult(
            GATE, NAME, WARN,
            "Prior-audit overlap recorded: " + "; ".join(overlap),
            tag="prior_audit_overlap",
            detail={"overlap": overlap},
        ))

    if not results:
        results.append(GateResult(
            GATE, NAME, PASS,
            "Both duplicate and known-issue searches done and clear; no overlap.",
        ))
    return results
