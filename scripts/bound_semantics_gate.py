#!/usr/bin/env python3
"""
bound_semantics_gate.py — Phase-49 RESEARCH-ONLY semantic bound guard (un-wired).

Runs AFTER the P45 advancement gate and the P47 dataflow gate, only on candidates whose mechanism is in
{missing_bound, missing_floor, missing_ceil, missing_scale} with a pre-decision of ADVANCE/REVIEW_ONLY. It repairs the
P48 Reserve OVERFIT: P45's missing_bound corroborator advanced on a *spelling* match of a bound-term word ("floor"),
but in fixed-point math `floor`/`ceil` are RoundingMode directions, not security bounds.

Demotion-only (ADVANCE -> REVIEW_ONLY/ABSTAIN, REVIEW_ONLY -> ABSTAIN); NEVER promotes (non-processed mechanisms / no
pre-advance pass through unchanged). Core rule: the candidate may stay ADVANCE only if the alleged bound term is
SEMANTICALLY used as a value-domain constraint, not merely present as overloaded math/rounding vocabulary.

Two demotion rules:
  Rule 1 (overloaded vocabulary; floor/ceil/ceiling): the term, scanned across target + siblings, appears only as
         rounding/math-helper vocabulary with NO genuine bound use -> ABSTAIN.
  Rule 2 (generalized view/pure design-absence; all processed mechanisms): a view/pure target is demoted unless it makes
         a genuine bound use of the term AND its return feeds a source-visible mutating value/authority path -> ABSTAIN.
         (Generalizes P45's getter-regex exemption to ANY view/pure target; catches `status` and `shiftl_toFix`.)

Preserves A1 `tokenScale` (missing_scale term is not rounding-overloaded; liquidatePosition is not view/pure) and is
out of scope for omitted_term (A1 `penalty`) / recipient_missing (A2). Generic only — NO subject identifiers.
is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: bound_semantics_gate.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "bound_semantics_gate.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _tok(term: str, text: str) -> bool:
    return bool(term) and re.search(r"\b" + re.escape(term) + r"\b", text or "", re.I) is not None


def _genuine_bound_use(term: str, text: str) -> tuple[bool, str]:
    """True if `term` is used as a value-domain constraint in `text` (inequality / min-max-limit / domain config)."""
    if not term:
        return False, ""
    t = term.lower()
    low = text.lower()
    c = _cfg()
    # term adjacent to an inequality comparison (either side)
    if re.search(r"\b" + re.escape(t) + r"\b\s*(>=|<=|<|>)", low) or \
       re.search(r"(>=|<=|<|>)\s*[\w\.\(\)]*\b" + re.escape(t) + r"\b", low):
        return True, f"inequality constraint on '{term}'"
    # term as a min/max/clamp argument
    if re.search(r"(min|max|clamp)\s*\([^)]*\b" + re.escape(t) + r"\b", low):
        return True, f"'{term}' used as a min/max/clamp limit"
    # term participates in a domain limit-config compound (collateralfloor, debtceiling, floorprice, ...)
    flat = re.sub(r"[^a-z0-9]", "", low)
    for d in c["domain_limit_config_terms"]:
        if t in d and d in flat:
            return True, f"domain limit-config '{d}'"
    # term is itself a limit word used in the text
    if t in ("cap", "limit", "threshold", "bound", "minimum", "maximum", "lowerbound", "upperbound") and t in low:
        return True, f"'{term}' is a value-limit term"
    return False, ""


def _rounding_evidence(term: str, text: str) -> tuple[bool, str]:
    """True if `term` occurs only in rounding/math vocabulary context."""
    if not _tok(term, text):
        return False, ""
    low = text.lower()
    for sig in _cfg()["rounding_vocab_signals"]:
        if sig in low:
            return True, f"rounding vocabulary '{sig}'"
    return False, ""


def _is_math_helper(name: str) -> bool:
    n = (name or "").lower()
    return any(sig in n for sig in _cfg()["math_helper_name_signals"])


def _return_feeds_mutation(target, downstream_users) -> bool:
    if downstream_users:
        return True
    low = _strip(target.get("snippet", "")).lower()
    return any(sig in low for sig in _cfg()["downstream_value_authority_signals"])


def gate(candidate: dict, target: dict, siblings=None, downstream_users=None) -> dict:
    c = _cfg()
    siblings = siblings or []
    mech = candidate.get("mechanism", "")
    label = candidate.get("label") or mech
    pre = candidate.get("pre_decision", c["decisions"]["advance"])
    term = (candidate.get("term", "") or "").strip()
    mech_class = label if str(label).startswith("missing_") else mech

    base = {**FLAGS, "candidate_id": label or candidate.get("candidate_id"), "mechanism_class": mech_class,
            "target": {"file": target.get("file"), "function": target.get("name"), "lines": target.get("lines")},
            "pre_gate_decision": pre, "bound_term": term}

    if mech not in c["processed_mechanisms"] or pre not in (c["decisions"]["advance"], c["decisions"]["review_only"]):
        return {**base, "post_gate_decision": pre, "semantic_bound_evidence": [], "overloaded_vocab_evidence": [],
                "design_absence": {}, "decision_reason": "not a processed bound/scale mechanism (pass-through)"}

    body = _strip(target.get("snippet", ""))
    sib_bodies = [_strip(s.get("snippet", "")) for s in siblings]
    all_text = " \n ".join([body] + sib_bodies)
    mut = (target.get("mutability", "") or "").lower()
    name = target.get("name", "")

    # ---- evidence ----
    sem_ev, ovr_ev = [], []
    gb_target, gb_target_why = _genuine_bound_use(term, body)
    gb_any, gb_any_why = _genuine_bound_use(term, all_text)
    if gb_any:
        sem_ev.append({"kind": "inequality" if "inequality" in gb_any_why else
                       ("min_max" if "min/max" in gb_any_why else
                        ("domain_config" if "domain" in gb_any_why else "cap_limit")),
                       "source": gb_any_why, "why_it_is_a_bound": "term used as a value-domain constraint"})
    if _return_feeds_mutation(target, downstream_users):
        sem_ev.append({"kind": "downstream_effect", "source": "downstream/value signals present",
                       "why_it_is_a_bound": "return/effect reaches a mutating value/authority path"})

    rounding_overloaded = term.lower() in c["rounding_overloaded_terms"]
    re_ok, re_why = _rounding_evidence(term, all_text)
    if rounding_overloaded and re_ok:
        ovr_ev.append({"kind": "rounding_mode", "source": re_why,
                       "why_it_is_not_a_security_bound": f"'{term}' is a fixed-point rounding direction, not a value bound"})
    if _is_math_helper(name):
        ovr_ev.append({"kind": "math_helper", "source": f"helper-name '{name}'",
                       "why_it_is_not_a_security_bound": "pure math/conversion helper, not a bounded value operation"})

    is_view_pure = mut in c["view_pure_mutabilities"]
    feeds = _return_feeds_mutation(target, downstream_users)
    design_absence = {"is_view_or_pure": is_view_pure, "return_feeds_mutation": bool(feeds),
                      "reason": ""}

    # ---- Rule 1: overloaded vocabulary (floor/ceil/ceiling) ----
    rule1 = rounding_overloaded and re_ok and not gb_any
    # ---- Rule 2: generalized view/pure design-absence ----
    rule2 = is_view_pure and not (gb_target and feeds)
    if is_view_pure:
        design_absence["reason"] = ("view/pure with genuine in-body bound use feeding mutation -> exempt"
                                    if not rule2 else
                                    "view/pure target does not enforce a numeric bound on the term feeding a mutating path")

    if rule1 or rule2:
        reasons = []
        if rule1:
            reasons.append(f"overloaded vocabulary: '{term}' only appears as rounding/math vocab, no genuine bound use")
        if rule2:
            reasons.append(f"design-absence: {mut or 'view/pure'} target cannot be 'missing a bound' without enforcing one that feeds mutation")
        return {**base, "post_gate_decision": c["decisions"]["abstain"], "semantic_bound_evidence": sem_ev,
                "overloaded_vocab_evidence": ovr_ev, "design_absence": design_absence,
                "decision_reason": " ; ".join(reasons)}

    return {**base, "post_gate_decision": pre, "semantic_bound_evidence": sem_ev,
            "overloaded_vocab_evidence": ovr_ev, "design_absence": design_absence,
            "decision_reason": "alleged bound term has genuine value-domain bound use; not demoted"}


# --------------------------------- self-test (9 required cases) ---------------------------------

def _t(name, snippet, mut="", file="src/C.sol", contract="C"):
    return {"name": name, "snippet": snippet, "mutability": mut, "file": file, "contract": contract}


def _g(term, body, mech="missing_bound", label=None, mut="", pre="ADVANCE", name="f", siblings=None, down=None):
    return gate({"mechanism": mech, "term": term, "label": label or ("missing_" + term), "pre_decision": pre},
                _t(name, body, mut=mut), siblings=siblings, downstream_users=down)


def _self_test():
    ok = True
    # 1 RoundingMode.FLOOR rejected as bound evidence (pure helper)
    r1 = _g("floor", "return shiftl_toFix(x, shiftLeft, RoundingMode.FLOOR);", mut="pure", name="shiftl_toFix")
    c1 = r1["post_gate_decision"] == "ABSTAIN" and any(e["kind"] == "rounding_mode" for e in r1["overloaded_vocab_evidence"])
    print(f"  [{'PASS' if c1 else 'FAIL'}] RoundingMode.FLOOR rejected ({r1['post_gate_decision']})"); ok &= c1
    # 2 RoundingMode.CEIL rejected
    r2 = _g("ceil", "uint y = mulDiv(a, b, c, RoundingMode.CEIL);", mut="pure", name="mulDivCeil")
    c2 = r2["post_gate_decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c2 else 'FAIL'}] RoundingMode.CEIL rejected ({r2['post_gate_decision']})"); ok &= c2
    # 3 pure fixed-point conversion helper missing_floor rejected
    r3 = _g("floor", "if (x == 0) return 0; uint256 coeff = 10**abs(shiftLeft); return _safeWrap(x * coeff, FLOOR);",
            mut="pure", name="shiftl_toFix")
    c3 = r3["post_gate_decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c3 else 'FAIL'}] pure conversion helper missing_floor rejected ({r3['post_gate_decision']})"); ok &= c3
    # 4 public view status getter missing_bound rejected (no 'floor' in body; view design-absence)
    r4 = _g("floor", "uint256 size = basket.length; for (uint256 i = 0; i < size; ++i) { if (s.worseThan(st)) return DISABLED; } return st;",
            mut="view", name="status", down=["isReady"])
    c4 = r4["post_gate_decision"] == "ABSTAIN" and r4["design_absence"]["is_view_or_pure"]
    print(f"  [{'PASS' if c4 else 'FAIL'}] view status getter missing_bound rejected ({r4['post_gate_decision']})"); ok &= c4
    # 5 real inequality lower-bound accepted (non-view, term adjacent to >=)
    r5 = _g("floor", "require(price >= floor, 'below floor'); token.safeTransfer(to, amount);", mut="", name="settle")
    c5 = r5["post_gate_decision"] == "ADVANCE" and any(e["kind"] == "inequality" for e in r5["semantic_bound_evidence"])
    print(f"  [{'PASS' if c5 else 'FAIL'}] real inequality lower-bound accepted ({r5['post_gate_decision']})"); ok &= c5
    # 6 real cap/limit/threshold accepted (non-view, non-rounding term)
    r6 = _g("cap", "require(totalSupply + amt <= cap); _mint(to, amt);", mut="", name="mint")
    c6 = r6["post_gate_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c6 else 'FAIL'}] cap/limit/threshold accepted ({r6['post_gate_decision']})"); ok &= c6
    # 7 view fn whose return feeds mutating path WITH genuine in-body bound -> survives (reviewable/advance)
    r7 = _g("floor", "require(p >= floor); return p;", mut="view", name="priceWithFloor", down=["borrow"])
    c7 = r7["post_gate_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c7 else 'FAIL'}] view+downstream+genuine-bound survives ({r7['post_gate_decision']})"); ok &= c7
    # 8 A1-like missing_scale with scale/value effect on a non-view fn -> not demoted
    r8 = _g("tokenScale", "uint amount = wmul(delta, tokenScale); token.safeTransfer(to, amount);",
            mech="missing_scale", label="missing_tokenScale", mut="", name="liquidate")
    c8 = r8["post_gate_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c8 else 'FAIL'}] A1-like missing_scale not demoted ({r8['post_gate_decision']})"); ok &= c8
    # 9 research-only / un-wired markers + no subject ids + never-promote
    cfg = CFG.read_text().lower()
    banned = ("reserve", "fixlib", "shiftl", "basket", "notional", "sablier", "secondswap", "sentiment",
              "plaza", "traitforge", "dittoeth", "basin", "loopfi", "blackhole", "bakerfi")
    no_ids = not any(b in cfg for b in banned)
    # never promotes: a REVIEW_ONLY pre with no demotion trigger stays REVIEW_ONLY (not ADVANCE)
    r9 = _g("cap", "require(x <= cap); _mint(a, x);", mut="", name="mint", pre="REVIEW_ONLY")
    flags_ok = FLAGS["research_only"] and not FLAGS["is_gate"] and not FLAGS["routes_in_production"] and _cfg().get("research_only") is True
    c9 = no_ids and flags_ok and r9["post_gate_decision"] == "REVIEW_ONLY"
    print(f"  [{'PASS' if c9 else 'FAIL'}] research-only/no-subject-ids/never-promote (no_ids={no_ids}, r9={r9['post_gate_decision']})"); ok &= c9
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p49)")


if __name__ == "__main__":
    raise SystemExit(main())
