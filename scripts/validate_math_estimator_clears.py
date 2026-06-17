#!/usr/bin/env python3
"""
validate_math_estimator_clears.py — flag coverage clears of MATH-ESTIMATOR / guard / formula surfaces
that lack an independent formula re-derivation. Mirrors validate_dependency_clears.py.

A math estimator can be wrong even when NatSpec and code agree, if both deviate from the intended model
(QuantAMM strict-eval H-11: the covariance estimator was strong-cleared because "formulas match NatSpec").
So a math-estimator-sensitive item may NOT be cleared on NatSpec/code consistency alone — its clear must
carry a math_estimator_proof object with an independent re-derivation. See
documentation/math_estimator_proof_policy.md. This validator is READ-ONLY on dispositions; it only writes
output/math_estimator_clear_validation.{json,md}.

Statuses per cleared item:
  not_math_estimator_sensitive | finding_linked | duplicate_or_known | math_proof_valid |
  missing_math_proof | incomplete_math_proof | natspec_only_proof
Blocking (strict): missing_math_proof | incomplete_math_proof | natspec_only_proof
(Items the writer already routed to needs_deep_pass are status=assigned/deep — reported, never blocking.)

Modes:
  --mode advisory  (default) exit 0; report all math clears missing a proof
  --mode strict    exit nonzero if any blocking math clear exists
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import math_estimator_taxonomy as me  # noqa: E402

# all fields that must be present + non-empty for a complete proof (mirrors schema 'required').
# The first 14 are the structural proof; the last 5 (added 2026-05) make the proof ADVERSARIAL —
# they force an explicit diff, assumptions, monotonicity/economic direction, attacker-favorable
# parameter search, and economic impact. A schema-complete-but-confirmatory proof (the Swan/Dria
# getFee M-08 / QuantAMM H-11 failure mode) is rejected via the content checks below, not field count.
_STRUCTURAL_PROOF_FIELDS = [
    "math_domain", "intended_formula", "implemented_formula", "formula_source",
    "independent_rederivation", "input_domain", "output_domain", "scaling_precision",
    "rounding_behavior", "signedness_assumptions", "bounds_and_guards", "edge_cases_checked",
    "invariant_preserved", "evidence_span",
]
_ADVERSARIAL_PROOF_FIELDS = [
    "formula_diff", "assumptions", "monotonicity_and_economic_direction",
    "attacker_favorable_search", "economic_impact_if_wrong",
]
REQUIRED_PROOF_FIELDS = _STRUCTURAL_PROOF_FIELDS + _ADVERSARIAL_PROOF_FIELDS
BLOCKING_STATUSES = {"missing_math_proof", "incomplete_math_proof", "natspec_only_proof", "confirmatory_proof"}

# Economic variables a monotonicity/economic-direction analysis should reference. A formula's
# correctness is meaningless without knowing which way it should move with these — the getFee miss
# was an exponential `2 << difficulty` whose direction-vs-difficulty was never questioned.
ECONOMIC_VARS = {
    "difficulty", "risk", "time", "stake", "shares", "share", "debt", "collateral", "supply",
    "fee", "price", "reward", "weight", "amount", "balance", "rate", "deviation", "score",
    "duration", "interval", "round", "liquidity", "tvl", "yield", "interest",
}
# Confirmatory phrases: assertions of internal consistency masquerading as a re-derivation.
_CONFIRMATORY_PHRASES = [
    "appears intended", "appears correct", "appears consistent", "looks correct", "looks right",
    "seems intended", "seems correct", "matches intent", "matches the intent", "as intended",
    "internally consistent", "matches the code", "matches code", "matches natspec",
    "matches the natspec", "consistent with the code", "consistent with code", "code is consistent",
    "formula is consistent", "no issues found", "works as designed", "behaves as documented",
]
# Scaling/shift constructs whose attacker-favorable extremes MUST be searched.
_SCALING_TOKENS = ["<<", ">>", "**", ".pow", "* 1e", "/ 1e", "*1e", "/1e", "e18", "e9", "e36"]
# Tokens proving an attacker-favorable / boundary search was actually done.
_EXTREME_TOKENS = ["max", "min", "overflow", "underflow", "boundary", "extreme", "2**", "2 **",
                   "<<", "type(", "uint256", "zero", "saturat", "cliff"]
# Genuinely independent (non-code) formula sources. NOTE: derived_in_review is the reviewer's OWN
# derivation, not an independent source — when intended==implemented it means the code was derived from
# the code (the getFee/H-11 trap), so it does NOT count here.
_EXTERNAL_SOURCES = {"whitepaper", "protocol_docs"}


def _nonempty(v) -> bool:
    if v is None:
        return False
    if isinstance(v, (list, tuple, dict, str)):
        return len(v) > 0
    return True


def _text(v) -> str:
    """Flatten a proof field (str or list) to lowercased text for token/phrase checks."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return " ".join(str(x) for x in v).lower()
    return str(v).lower()


def _normalize_formula(s) -> str:
    """Lowercase, strip whitespace and // line comments, for an equality/overlap comparison."""
    t = _text(s)
    t = re.sub(r"//.*", " ", t)          # drop line comments
    t = re.sub(r"\s+", "", t)            # collapse all whitespace
    return t


def _formula_tokens(s) -> set[str]:
    """Identifier/number/operator tokens of a formula, for Jaccard overlap."""
    return set(re.findall(r"[a-z_][a-z0-9_]*|\d+|[<>*/+\-%&|^]+", _text(s)))


def _formulas_match(intended, implemented) -> bool:
    """True if intended ≈ implemented: normalized equality OR token-set Jaccard >= 0.85."""
    ni, nm = _normalize_formula(intended), _normalize_formula(implemented)
    if not ni or not nm:
        return False
    if ni == nm:
        return True
    a, b = _formula_tokens(intended), _formula_tokens(implemented)
    if not a or not b:
        return False
    jacc = len(a & b) / len(a | b)
    return jacc >= 0.85


def _has_external_support(proof: dict) -> bool:
    src = proof.get("formula_source") or []
    if isinstance(src, str):
        src = [src]
    return bool({str(s).strip().lower() for s in src} & _EXTERNAL_SOURCES)


def _economic_analysis_present(proof: dict) -> bool:
    """A genuine adversarial economic check: monotonicity names an economic variable AND both the
    attacker search and the impact-if-wrong are non-trivially populated. This is the escape that lets
    a clear stand when the formulas legitimately match but the reviewer adversarially confirmed it."""
    mono = _text(proof.get("monotonicity_and_economic_direction"))
    if not any(v in mono for v in ECONOMIC_VARS):
        return False
    return _nonempty(proof.get("attacker_favorable_search")) and _nonempty(proof.get("economic_impact_if_wrong"))


def validate_proof(proof: dict, adversarial: bool = True) -> tuple[str, list[str], list[str]]:
    """Return (status, missing_fields, reasons).
    status in {math_proof_valid, missing_math_proof, incomplete_math_proof, natspec_only_proof,
               confirmatory_proof}. `reasons` explains a confirmatory_proof. When adversarial=False the
    content checks are skipped (advisory/normal mode); structural + natspec-only checks always run."""
    if not isinstance(proof, dict):
        return "missing_math_proof", list(REQUIRED_PROOF_FIELDS), []
    missing = [f for f in REQUIRED_PROOF_FIELDS if not _nonempty(proof.get(f))]
    # NatSpec-only proof: formula_source is only NatSpec/code with no external/derived source and no
    # limitations justification — exactly the H-11 failure mode ("code matches comments").
    src = proof.get("formula_source") or []
    if isinstance(src, str):
        src = [src]
    src_l = {str(s).strip().lower() for s in src}
    natspec_only = src_l and src_l.issubset({"natspec", "code"}) and not _nonempty(proof.get("limitations"))
    # an independent re-derivation is the heart of the proof; absent it, never valid even if other fields set
    if natspec_only:
        return "natspec_only_proof", missing, []
    if missing:
        return "incomplete_math_proof", missing, []

    # --- adversarial content checks (the getFee M-08 / QuantAMM H-11 fix) -----------------------
    # A schema-complete proof can still be CONFIRMATORY: it restates the implemented formula and
    # declares it intended. Reject these so they route to needs_deep_pass instead of clearing.
    if adversarial:
        reasons: list[str] = []
        intended, implemented = proof.get("intended_formula"), proof.get("implemented_formula")
        # 1) intended ≈ implemented with no independent support and no genuine economic analysis.
        if _formulas_match(intended, implemented) and not _has_external_support(proof) \
                and not _economic_analysis_present(proof):
            reasons.append("intended_formula matches implemented_formula without an external source "
                           "(whitepaper/protocol_docs/derived_in_review) or an independent economic-direction analysis")
        # 2) confirmatory "appears intended"-style language with no external source.
        confirm_text = " ".join(_text(proof.get(f)) for f in
                                 ("independent_rederivation", "formula_diff", "intended_formula"))
        if not _has_external_support(proof) and any(p in confirm_text for p in _CONFIRMATORY_PHRASES):
            reasons.append("re-derivation asserts internal consistency ('appears intended'/'matches the code') "
                           "without citing a non-code source")
        # 3) economic direction not checked.
        if not any(v in _text(proof.get("monotonicity_and_economic_direction")) for v in ECONOMIC_VARS):
            reasons.append("monotonicity_and_economic_direction names no economic variable "
                           "(fee/stake/difficulty/price/reward/weight/…) — direction never checked")
        # 4) scaling/shift behavior not tested with attacker-favorable / boundary values.
        impl_text = _text(implemented)
        if any(tok in impl_text for tok in _SCALING_TOKENS):
            if not any(tok in _text(proof.get("attacker_favorable_search")) for tok in _EXTREME_TOKENS):
                reasons.append("implemented_formula uses shift/scaling (<<, >>, **, 1e..) but "
                               "attacker_favorable_search names no extreme/boundary value")
        if reasons:
            return "confirmatory_proof", missing, reasons
    return "math_proof_valid", [], []


def classify_clear(disp: dict, item: dict, tax: dict, adversarial: bool = True) -> dict:
    cls = me.classify_manifest_item(item, taxonomy=tax) if item else \
        {"math_estimator_sensitive": False, "math_domain": None, "risk_tags": [], "review_hint": "", "severity_ceiling_hint": None}
    if not cls["math_estimator_sensitive"]:
        return {"status": "not_math_estimator_sensitive", "math_domain": None, "missing": [],
                "high_risk": False, "review_hint": "", "reasons": []}
    high_risk = me.is_high_risk(cls, tax)
    base = {"math_domain": cls["math_domain"], "high_risk": high_risk, "review_hint": cls["review_hint"],
            "missing": [], "reasons": []}
    if disp.get("finding_refs"):
        return {**base, "status": "finding_linked"}
    if disp.get("duplicate_of") or disp.get("known_ref"):
        return {**base, "status": "duplicate_or_known"}
    proof = disp.get("math_estimator_proof")
    if not proof:
        return {**base, "status": "missing_math_proof", "missing": list(REQUIRED_PROOF_FIELDS)}
    status, missing, reasons = validate_proof(proof, adversarial=adversarial)
    return {**base, "status": status, "missing": missing, "reasons": reasons}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["advisory", "strict"], default="advisory")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not disp_path.exists():
        raise SystemExit("[validate_math_estimator_clears] coverage_dispositions.json missing — run the coverage pipeline first.")
    man_path = audit_path("output") / "coverage_manifest.json"
    items = {}
    if man_path.exists():
        try:
            items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
        except (json.JSONDecodeError, OSError):
            items = {}
    tax = me.load_taxonomy()
    # adversarial content checks are on by default; config can disable them (advisory tuning).
    try:
        pol = json.loads((Path(__file__).resolve().parent.parent / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except (OSError, json.JSONDecodeError):
        pol = {}
    adversarial = pol.get("math_adversarial_proof", True)

    dispositions = json.loads(disp_path.read_text()).get("dispositions", [])
    rows = []
    routed = 0
    for d in dispositions:
        mid = d.get("manifest_id")
        item = items.get(mid)
        # report (non-blocking) math items already routed to deep pass by the writer
        if d.get("status") == "assigned" and d.get("assigned_pass") == "deep":
            cls = me.classify_manifest_item(item, taxonomy=tax) if item else {"math_estimator_sensitive": False}
            if cls.get("math_estimator_sensitive"):
                routed += 1
                rows.append({"manifest_id": mid, "status": "needs_deep_pass",
                             "math_domain": cls.get("math_domain"), "high_risk": me.is_high_risk(cls, tax),
                             "attack_surface_score": (item or {}).get("attack_surface_score", 0),
                             "missing": [], "clear_reason": (d.get("routed_reason") or "")[:200]})
            continue
        if d.get("status") != "cleared":
            continue
        c = classify_clear(d, item, tax, adversarial=adversarial)
        if c["status"] == "not_math_estimator_sensitive":
            continue
        rows.append({"manifest_id": mid, "status": c["status"], "math_domain": c["math_domain"],
                     "high_risk": c["high_risk"], "attack_surface_score": (item or {}).get("attack_surface_score", 0),
                     "missing": c["missing"], "reasons": c.get("reasons", []),
                     "clear_reason": (d.get("clear_reason") or "")[:200]})

    counts = Counter(r["status"] for r in rows)
    blocking = [r for r in rows if r["status"] in BLOCKING_STATUSES]
    math_sensitive_clears = [r for r in rows if r["status"] != "needs_deep_pass"]

    out = {
        "mode": args.mode,
        "adversarial": adversarial,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "math_estimator_sensitive_clears": len(math_sensitive_clears),
        "blocking": len(blocking),
        "routed_to_deep_pass": routed,
        "by_status": dict(counts),
        "rows": rows,
    }
    (audit_path("output") / "math_estimator_clear_validation.json").write_text(json.dumps(out, indent=2))

    md = ["# Math-estimator clear validation", "",
          f"- mode: **{args.mode}**",
          f"- math-estimator-sensitive clears: {len(math_sensitive_clears)}",
          f"- blocking (missing/incomplete/natspec-only proof): **{len(blocking)}**",
          f"- already routed to deep pass: {routed}", "",
          "## By classification", "", "| status | count |", "|---|---|"]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        md.append(f"| {k} | {v} |")
    md += ["", "## Blocking math-estimator clears", "",
           "| manifest_id | score | domain | high_risk | status | missing / why | reason |",
           "|---|---|---|---|---|---|---|"]
    for r in sorted(blocking, key=lambda r: -r["attack_surface_score"]):
        why = ", ".join(r["missing"][:4]) if r["missing"] else "; ".join(r.get("reasons", []))[:160]
        md.append(f"| {r['manifest_id']} | {r['attack_surface_score']} | {r['math_domain']} | "
                  f"{r['high_risk']} | {r['status']} | {why} | {r['clear_reason'][:80]} |")
    (audit_path("output") / "math_estimator_clear_validation.md").write_text("\n".join(md) + "\n")

    if not args.quiet:
        print(f"[math-estimator-clears] mode={args.mode} · math-sensitive-clears={len(math_sensitive_clears)} "
              f"· blocking={len(blocking)} · routed_to_deep_pass={routed}")
        print(f"  by_status: {dict(counts)}")
        for r in blocking[:12]:
            print(f"   BLOCK {r['manifest_id']} [{r['status']}] domain={r['math_domain']}")

    if args.mode == "strict" and blocking:
        print(f"[FAIL] strict mode: {len(blocking)} math-estimator clear(s) lack an independent formula "
              f"re-derivation (missing/incomplete/NatSpec-only proof). See output/math_estimator_clear_validation.md.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
