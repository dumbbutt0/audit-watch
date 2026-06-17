"""
Gate 5 — invariant_gate.

Reads the final batch-validation function and the skipped per-call check from real source, and converts them into a
precise, human-readable invariant claim + a coverage analysis. Read-only.

CAUTION: this gate does NOT claim a bug. Acceptable conclusions only:
  - final invariant appears complete for the known skipped check(s)
  - final invariant appears incomplete for at least one skipped check
  - cannot determine without sequence generation / a PoC
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts as A  # noqa: E402
import policy as P  # noqa: E402
from gates import source_resolve_gate as SRG  # noqa: E402


def _find_function(target_root: Path, fn: str) -> Optional[Dict[str, Any]]:
    for f in sorted(target_root.rglob("*.sol")):
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        ext = SRG.extract_function(lines, fn, None)
        if ext:
            ext["file"] = str(f.relative_to(A.ROOT))
            return ext
    return None


def run(cand: Dict[str, Any], target_root: Optional[str],
        state_mut: Optional[Dict[str, Any]] = None,
        defense_body: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    state_mut = state_mut or {}
    defense_body = defense_body or {}
    troot = (A.ROOT / target_root) if target_root else A.ROOT
    req = P.detector_requirements(cand.get("detector", ""))
    final_fns = req.get("final_invariant_functions", ["validateBorrowATokenIncreaseLteDebtTokenDecrease"])
    per_call_checks = req.get("per_call_checks", ["validateBorrowATokenCap"])

    final_fn = final_fns[0] if final_fns else None
    final = _find_function(troot, final_fn) if final_fn else None
    if final is None:
        return ({"status": "NEEDS_CONTEXT",
                 "summary_plain_english": f"could not locate final validation function {final_fn} under the target root",
                 "final_validation_function": final_fn, "unresolved_assumptions": ["final validation source not found"],
                 "next_required_gate": "sequence_gate"}, "NEEDS_CONTEXT")

    skipped = []
    for fn in per_call_checks:
        ex = _find_function(troot, fn)
        skipped.append({
            "name": fn, "file": ex["file"] if ex else None,
            "line": ex["start_line"] if ex else None,
            "code_excerpt": ex["snippet"] if ex else None,
            "basis": "absolute (borrowAToken.totalSupply() > borrowATokenCap -> revert)"
            if fn == "validateBorrowATokenCap" else "per-call validation",
            "skipped_when_isMulticall": any(fn in (b.get("check_skipped_or_changed") or "")
                                            for b in defense_body.get("is_multicall_branches", [])),
        })

    excerpt = final["snippet"]
    # accounting basis facts derived from the real excerpt (string evidence, not a verdict)
    cond_on_cap = "borrowATokenCap" in excerpt and ">" in excerpt
    relative = "Before" in excerpt and "After" in excerpt

    coverage_analysis = []
    for s in skipped:
        if s["name"] == "validateBorrowATokenCap":
            coverage_analysis.append({
                "skipped_check": s["name"],
                "skipped_basis": "absolute cap on total borrowAToken supply",
                "final_check": final_fn,
                "final_basis": "relative increase vs debt decrease, only evaluated when supply is already above the cap",
                "coverage_status": "partially_covers / cannot_determine",
                "reasoning": ("The skipped check forbids supply > cap outright. The final check does NOT re-impose "
                              "that absolute limit; it only requires that any above-cap increase be matched by a "
                              "debt decrease. These are different accounting bases, so the final check does not "
                              "obviously replace the per-call cap. Whether an interleaving can end above-cap without "
                              "a matching debt decrease is UNDETERMINED here and needs sequence generation."),
            })

    body = {
        "status": "INVARIANT_ANALYZED",
        "summary_plain_english": (
            "After the multicall batch, Size enforces a RELATIVE/CONDITIONAL check "
            "(validateBorrowATokenIncreaseLteDebtTokenDecrease): only if borrowAToken supply ends above the cap, the "
            "increase must be <= the debt-token decrease. During the batch the ABSOLUTE per-call cap check "
            "(validateBorrowATokenCap) is skipped. The two checks use different accounting bases, so it is NOT "
            "established that the final check fully covers the skipped cap — that is the open question for the "
            "sequence gate. No vulnerability is claimed at this stage."),
        "invariant_claim": ("If the multicall batch leaves borrowAToken supply above borrowATokenCap, then "
                            "(supplyAfter - supplyBefore) must be <= (debtSupplyBefore - debtSupplyAfter); otherwise "
                            "the batch reverts. Below the cap, no constraint is imposed."),
        "pre_state_variables": ["borrowATokenSupplyBefore = borrowAToken.balanceOf(address(this))",
                                "debtTokenSupplyBefore = debtToken.totalSupply()"],
        "post_state_variables": ["borrowATokenSupplyAfter = borrowAToken.balanceOf(address(this))",
                                 "debtTokenSupplyAfter = debtToken.totalSupply()"],
        "final_validation_function": final_fn,
        "final_validation_location": f'{final["file"]}:{final["start_line"]}',
        "final_validation_code_excerpt": excerpt,
        "final_validation_plain_english": (
            "Only acts when borrowATokenSupplyAfter > borrowATokenCap; then requires the borrow increase to be no "
            "greater than the debt decrease, else reverts BORROW_ATOKEN_INCREASE_EXCEEDS_DEBT_TOKEN_DECREASE."),
        "skipped_or_deferred_checks": skipped,
        "coverage_analysis": coverage_analysis,
        "accounting_basis_analysis": {
            "final_check_conditional_on_cap": cond_on_cap,
            "final_check_uses_before_after_delta": relative,
            "skipped_check_basis": "absolute (totalSupply vs cap)",
            "final_check_basis": "relative delta (increase vs debt decrease), conditional on above-cap",
            "same_basis": False,
        },
        "what_invariant_covers": [
            "The 'deposit-to-repay' flow: an above-cap supply increase matched by an equal-or-greater debt decrease.",
        ],
        "what_invariant_may_not_cover": [
            "The absolute per-call cap that is skipped in multicall (different accounting basis).",
            "Interleavings that end above the cap WITHOUT a matching debt decrease — undetermined here.",
        ],
        "candidate_risk_statement": (
            "HYPOTHESIS (unconfirmed; not a vulnerability claim): because the per-call absolute cap is deferred in "
            "multicall and the final check is relative/conditional, an attacker-controlled batch MIGHT leave the "
            "protocol above the borrowAToken cap without a matching debt decrease. A concrete exploit sequence is "
            "required to confirm or refute this, and the behavior may be fully covered or intended."),
        "exploit_sequence_prerequisites": [
            "A callable sub-call that increases borrowAToken supply without a matching debt decrease.",
            "Ability to keep the batch's final (increase vs debt-decrease) relation satisfied or below-cap.",
        ],
        "blockers_before_sequence_generation": [
            "Need to enumerate which sub-calls move borrowAToken up vs debtToken down (sequence_gate).",
            "Need to confirm the final check cannot be satisfied trivially while leaving an invalid state.",
        ],
        "unresolved_assumptions": [
            "borrowAToken.balanceOf(address(this)) tracks total protocol borrow supply for the cap intent.",
            "No other post-batch guard re-imposes the absolute cap.",
        ],
        "next_required_gate": "sequence_gate",
        # ---- alias keys for existing dashboard reader (no UI change) ----
        "invariant_statement": ("If multicall leaves borrowAToken supply above the cap, the supply increase must be "
                                "<= the debt-token decrease; below the cap, unconstrained."),
        "expected_relationship": "borrowATokenSupplyIncrease <= debtTokenSupplyDecrease (only when above cap)",
        "covers": ["above-cap increase matched by debt decrease (deposit-to-repay)"],
        "may_not_cover": ["the skipped absolute per-call cap (validateBorrowATokenCap), different accounting basis"],
        "sufficient_or_incomplete": "POSSIBLY_INCOMPLETE (cannot determine without sequence generation)",
        "security_property": "borrowAToken cap / accounting solvency invariant",
    }
    return body, "INVARIANT_ANALYZED"
