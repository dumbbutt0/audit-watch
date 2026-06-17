#!/usr/bin/env python3
"""
enumerate_candidate_invariants.py — P101 autonomous invariant ENUMERATION (RESEARCH-ONLY, UN-WIRED).

Broad RECALL layer. For one suspicious function it generates 3–10 candidate invariants across many categories so
the historically-correct invariant is (almost) always among the candidates — directly targeting the P97 failure
where the system tested a TRUE-BUT-IRRELEVANT invariant (token-sum) instead of the relevant one (per-buyer claim
schedule).

This is a deterministic, category-complete HEURISTIC generator (keyword / state-variable / detector signals) — it
is NOT an LLM that "understands" arbitrary code, and it NEVER validates, promotes, sets severity, or creates a
submission. Every output is `status="HYPOTHESIS_ONLY"` and `precision_gate_required=true`: hypotheses are NOT
findings. Precision is enforced downstream by auto_validate_invariants -> the frozen reject-first gates.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

HYPOTHESIS_ONLY = "HYPOTHESIS_ONLY"

# the invariant categories this layer can emit.
CATEGORIES = [
    "value_conservation", "per_user_accounting", "cap_limit", "role_access",
    "lifecycle_state_transition", "ordering_race", "index_array_integrity",
    "reward_fee_distribution", "cross_contract_consistency", "recovery_availability",
    "negative_space_missing_update",
]

# the "core" categories always emitted (cheap insurance against omitting the relevant one).
_CORE = ["value_conservation", "per_user_accounting", "lifecycle_state_transition", "role_access"]

# signal keywords -> extra categories to emit when seen in the source/state-vars/function name.
_SIGNALS = {
    "cap_limit": ["cap", "limit", "max", "percent", "bps", "maxsell", "maxtotal", "ceiling", "threshold"],
    "ordering_race": ["status", "phase", "order", "settle", "close", "expire", "pending", "batch", "snapshot",
                      "before", "after", "deadline", "timestamp"],
    "index_array_integrity": ["index", "array", "length", "[", "push", "pop", "ids", "idx", "slot", "_add", "_remove"],
    "reward_fee_distribution": ["fee", "reward", "referral", "payout", "distribute", "collect", "yield", "accrue"],
    "cross_contract_consistency": ["staticcall", ".call", "external", "interface", "i" + "erc", "manager", "hook",
                                   "oracle", "vesting", "factory"],
    "recovery_availability": ["withdraw", "claim", "redeem", "release", "unlock", "exit", "rescue"],
    "role_access": ["onlyowner", "onlyadmin", "onlymanager", "require(msg.sender", "role", "auth", "whitelist",
                    "_grantrole", "tokenissuer"],
    "per_user_accounting": ["balance", "shares", "bought", "sold", "amount", "allocation", "vesting", "account",
                            "stepsclaimed", "amountclaimed", "user"],
    "value_conservation": ["total", "supply", "transfer", "mint", "burn", "balance", "amount"],
    "negative_space_missing_update": ["reset", "update", "set", "delete", "clear", "flag", "dirty"],
}

_FN_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)")


def _text_of(intake: Dict[str, Any]) -> str:
    parts = [str(intake.get("function") or ""), str(intake.get("source_snippet") or ""),
             str(intake.get("source_text") or "")]
    parts += [str(x) for x in (intake.get("source_refs") or [])]
    parts += [str(x) for x in (intake.get("state_variables") or [])]
    parts += [str(intake.get("detector_signal") or ""), str(intake.get("human_notes") or "")]
    return " \n ".join(parts).lower()


# per-category statement templates, parameterized by contract.function + state vars.
def _statement(cat: str, fn: str, sv: str) -> Dict[str, str]:
    S = {
        "value_conservation": (
            f"the total of all balances/amounts tracked by {fn} is conserved across the operation (sum in == sum out)",
            "an actor receives more than was funded / a rounding or denominator change lets totals diverge"),
        "per_user_accounting": (
            f"each user's individual accounting in {fn} ({sv}) matches the assets/schedule they are actually entitled to",
            "a per-user counter is credited/inherited from the wrong source so one user over- or under-accounts (P97 class)"),
        "cap_limit": (
            f"{fn} cannot let a holder exceed the intended cap/limit ({sv})",
            "the cap is computed from an inflatable counter or wrong basis, so repeated/ordered calls exceed it"),
        "role_access": (
            f"only the intended privileged principal may take the protected action in {fn}",
            "missing buyer!=seller / role / auth check, or an inter-principal boundary is bypassable"),
        "lifecycle_state_transition": (
            f"{fn} behaves correctly across every lifecycle/phase ordering (open/closed, active/expired, pre/post-settle)",
            "a closed/expired/early-execution ordering breaks an accounting or liveness assumption (P95 class)"),
        "ordering_race": (
            f"{fn} is safe under adversarial transaction ordering / third-party interleaving",
            "a first-vs-last actor or third-party tx between setup and execution changes the outcome"),
        "index_array_integrity": (
            f"index/array bookkeeping in {fn} ({sv}) stays consistent (no corruption on add/remove/global-vs-scoped)",
            "a public add/remove or global-vs-per-scope index is mutable by the wrong party / off by one (P89 class)"),
        "reward_fee_distribution": (
            f"fees/rewards in {fn} are computed AND actually routed to the correct recipient",
            "a reward/fee is computed but never transferred, or routed to the wrong party"),
        "cross_contract_consistency": (
            f"{fn} and the in-scope contracts it calls agree on the value/state across the boundary",
            "an in-scope callee returns a value {fn} mis-reads; exact arithmetic must be traced (P93 class)"),
        "recovery_availability": (
            f"funds/rewards reachable via {fn} (withdraw/claim/redeem) remain recoverable for every entitled user",
            "a state/ordering leaves the last user unable to withdraw / under-withdrawing"),
        "negative_space_missing_update": (
            f"every state variable {fn} should update is updated (no missing reset/clear of {sv})",
            "a flag/counter is never reset so a later call reuses stale state (P85 class)"),
    }
    stmt, brk = S.get(cat, (f"{fn} preserves its intended {cat} invariant", "the invariant is violated"))
    return {"statement": stmt, "suspected_break": brk}


def enumerate_invariants(intake: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate candidate invariants for one function. Pure; recall-only; never validates."""
    c = intake or {}
    fn_full = f"{c.get('contract') or '?'}.{c.get('function') or '?'}"
    sv = ", ".join(str(x) for x in (c.get("state_variables") or [])) or "its state variables"
    text = _text_of(c)
    have_src = bool(c.get("source_snippet") or c.get("source_refs"))
    have_fn = bool(c.get("function"))

    cats = list(_CORE)
    for cat, kws in _SIGNALS.items():
        if any(k in text for k in kws) and cat not in cats:
            cats.append(cat)
    # cap at 10, keep order (core first, then signal-triggered)
    cats = cats[:10]

    base_conf = "low" if not (have_src and have_fn) else "medium"
    out: List[Dict[str, Any]] = []
    for cat in cats:
        s = _statement(cat, fn_full, sv)
        out.append({
            **FLAGS,
            "invariant_type": cat,
            "invariant_statement": s["statement"],
            "affected_actor": c.get("affected_actor") or "(unspecified — set before validation)",
            "trigger_actor": c.get("trigger_actor") or "(unspecified — attacker/third-party/sequencing)",
            "entrypoint": c.get("entrypoint") or c.get("function") or "(EOA entrypoint)",
            "source_refs": list(c.get("source_refs") or []),
            "state_variables": list(c.get("state_variables") or []),
            "suspected_break": s["suspected_break"],
            "why_this_invariant_matters": f"{cat} is a security-relevant property of {fn_full}; if it fails the "
                                          f"break above is the mechanism to validate from source.",
            "confidence": base_conf,
            "precision_gate_required": True,
            "validation_required": True,
            "poc_required_before_submission": True,
            "human_final_gate_required": True,
            "status": HYPOTHESIS_ONLY,
        })

    return {
        **FLAGS,
        "subject": c.get("subject"),
        "contract": c.get("contract"),
        "function": c.get("function"),
        "generated_count": len(out),
        "source_present": have_src,
        "note": "Generated hypotheses are NOT findings. They are HYPOTHESIS_ONLY and must pass the reject-first "
                "validation gates before becoming candidates.",
        "candidate_invariants": out,
    }


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    # resale/listing flow -> must include per_user_accounting AND cap_limit (NOT only value_conservation)
    r = enumerate_invariants({
        "subject": "secondswap-2024-12", "contract": "SecondSwap_VestingManager", "function": "listVesting",
        "state_variables": ["bought", "sold", "maxSellPercent", "allocation"],
        "source_snippet": "sellLimit = bought + maxSellPercent*(currentAlloc+sold-bought)/BASE; require(sold<=sellLimit)",
    })
    types = {i["invariant_type"] for i in r["candidate_invariants"]}
    chk(len(types) >= 4, f"emits >=4 categories ({len(types)})")
    chk("per_user_accounting" in types, "resale flow includes per_user_accounting (buyer-claim-schedule class)")
    chk("cap_limit" in types, "resale flow includes cap_limit (maxSellPercent class)")
    chk(types != {"value_conservation"}, "token-sum is NOT the only invariant")
    chk(all(i["status"] == HYPOTHESIS_ONLY for i in r["candidate_invariants"]), "all HYPOTHESIS_ONLY")
    chk(all(i["precision_gate_required"] and i["validation_required"] for i in r["candidate_invariants"]),
        "all require validation + precision gate")

    # withdrawal/closed-market flow -> ordering_race + recovery_availability
    w = enumerate_invariants({"contract": "WildcatMarket", "function": "executeWithdrawal",
                              "state_variables": ["batch", "scaledTotalAmount", "status"],
                              "source_snippet": "mulDiv(batch.normalizedAmountPaid, status.scaledAmount, batch.scaledTotalAmount); market closed"})
    wt = {i["invariant_type"] for i in w["candidate_invariants"]}
    chk("ordering_race" in wt, "withdrawal flow includes ordering_race (closed-market class)")
    chk("recovery_availability" in wt, "withdrawal flow includes recovery_availability")

    # index/access flow (Phi) -> index_array_integrity + role_access
    p = enumerate_invariants({"contract": "Cred", "function": "_addCredIdPerAddress",
                              "source_snippet": "public _add/_removeCredIdPerAddress index array push"})
    pt = {i["invariant_type"] for i in p["candidate_invariants"]}
    chk("index_array_integrity" in pt, "Phi flow includes index_array_integrity")
    chk("role_access" in pt, "Phi flow includes role_access")

    # missing function/source -> low confidence
    lo = enumerate_invariants({"contract": "X"})
    chk(all(i["confidence"] == "low" for i in lo["candidate_invariants"]), "missing source/function -> low confidence")

    chk(3 <= r["generated_count"] <= 10, "3..10 invariants generated")
    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--intake", help="intake JSON")
    ap.add_argument("--out", help="write candidate_invariants.json here")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    intake = json.loads(Path(args.intake).read_text()) if args.intake else {}
    res = enumerate_invariants(intake)
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"wrote {args.out} ({res['generated_count']} HYPOTHESIS_ONLY invariants)")
    else:
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
