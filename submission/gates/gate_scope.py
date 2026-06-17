#!/usr/bin/env python3
"""
gate_scope.py — Gate 1: Scope.

Rejects (FAIL -> DO_NOT_SUBMIT) when:
  - the target asset is not in scope
  - the impact category is not accepted by the program
  - the exploit DEPENDS on excluded assumptions
  - the exploit requires admin/governance privilege unless the program
    explicitly accepts privileged-role attacks
  - the exploit depends on social engineering, leaked/compromised keys,
    phishing, or compromised infrastructure

Marks WARN when scope is merely uncertain (-> human review).
"""
from __future__ import annotations

from _common import FAIL, PASS, WARN, GateResult, contains_any, text_blob

GATE = 1
NAME = "scope"

# excluded attacker preconditions that almost every program puts out of scope
EXCLUDED_VECTOR_KEYWORDS = [
    "social engineering",
    "phishing",
    "leaked key",
    "leaked private key",
    "stolen key",
    "compromised key",
    "compromised private key",
    "compromised admin",
    "compromised infrastructure",
    "compromised infra",
    "compromised server",
    "rogue admin",
    "malicious admin",
    "insider",
    "supply chain",
    "dns hijack",
    "frontend compromise",
]


def evaluate(candidate: dict) -> list[GateResult]:
    results: list[GateResult] = []

    scope_status = candidate.get("scope_status", "")
    if scope_status == "out_of_scope":
        results.append(GateResult(
            GATE, NAME, FAIL,
            "Affected asset is marked out_of_scope.",
            tag="out_of_scope",
        ))
    elif scope_status == "uncertain":
        results.append(GateResult(
            GATE, NAME, WARN,
            "Scope status is uncertain; a human must confirm the asset is in scope "
            "before submission.",
            tag="scope_uncertain",
        ))

    # impact category accepted by the program?
    mapping = candidate.get("bounty_program_mapping") or {}
    if mapping.get("impact_in_scope") is False:
        results.append(GateResult(
            GATE, NAME, FAIL,
            f"Impact category '{candidate.get('impact_category')}' is not accepted "
            "by the program (bounty_program_mapping.impact_in_scope == false).",
            tag="impact_out_of_scope",
        ))

    # excluded assumptions that the exploit DEPENDS on
    oos_risks = candidate.get("out_of_scope_risks") or []
    depended = [r for r in oos_risks if _depends_phrase(r)]
    if depended:
        results.append(GateResult(
            GATE, NAME, FAIL,
            "Exploit depends on excluded/out-of-scope assumptions: "
            + "; ".join(depended),
            tag="excluded_assumption",
            detail={"depended_risks": depended},
        ))

    # excluded attacker vectors (social engineering, leaked keys, phishing, infra)
    blob = text_blob(
        candidate.get("attacker_capabilities"),
        candidate.get("attacker_entrypoint"),
        candidate.get("out_of_scope_risks"),
        candidate.get("assumptions"),
        candidate.get("invalidating_conditions"),
    )
    hit = contains_any(blob, EXCLUDED_VECTOR_KEYWORDS)
    if hit:
        results.append(GateResult(
            GATE, NAME, FAIL,
            "Exploit relies on an out-of-scope attack vector: " + ", ".join(hit),
            tag="excluded_vector",
            detail={"vectors": hit},
        ))

    # privilege requirement (admin/governance) unless program allows it
    priv = candidate.get("privilege_required", "none")
    if priv in ("admin", "governance"):
        if mapping.get("privileged_roles_in_scope") is True:
            results.append(GateResult(
                GATE, NAME, WARN,
                f"Exploit requires '{priv}' privilege; program marks privileged-role "
                "attacks in scope. Human must confirm the role mapping.",
                tag="privileged_in_scope",
            ))
        else:
            results.append(GateResult(
                GATE, NAME, FAIL,
                f"Exploit requires '{priv}' privilege and the program does not "
                "explicitly accept privileged-role attacks "
                "(bounty_program_mapping.privileged_roles_in_scope != true).",
                tag="privileged_only",
            ))

    if not results:
        results.append(GateResult(GATE, NAME, PASS, "Asset, impact and attack vector are in scope."))
    return results


def _depends_phrase(risk: str) -> bool:
    """A risk string represents a dependency unless it is explicitly negated
    (e.g. 'does not require admin key')."""
    r = risk.lower()
    negations = ["does not require", "not required", "no need", "independent of", "without"]
    return not any(n in r for n in negations)
