#!/usr/bin/env python3
"""
root_cause_discriminator.py — Phase-32 RESEARCH-ONLY root-cause discrimination pass (un-wired).

Given a candidate that PASSED the validity gate, SCORE each enumerated defect mechanism by SOURCE-BACKED
comparand evidence and REJECT mechanisms that have none. Fixes the P31 "right function, wrong mechanism"
(IMPACT_WRONG) class: discrimination, not selection.

Engine input (constraint 1): ONLY source snippets (target + siblings/callees) + the enumerated candidate
mechanisms + generic comparand patterns (config/root_cause_mechanisms.json). It NEVER reads award labels,
issue IDs, contest text, or expected_mechanism.json.

Confidence (constraint 4):
  STRONG  = sibling/parallel comparand (present-elsewhere/absent-here on the same path) OR a units requirement
  MEDIUM  = a value the target itself computes but does not apply in the relevant value path
  WEAK    = local suspicion only (no source comparand)
Only STRONG/MEDIUM advance; WEAK is rejected. A design-absence (a missing feature/bound/term whose identifier
appears NOWHERE in target or siblings) is REJECT (constraint 6). If >1 mechanism advances with source backing
=> MULTI_MECHANISM_NEEDS_PROOF (constraint 5). If 0 advance => ABSTAIN (constraint 3/8).

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: root_cause_discriminator.py --input <input.json> [--out <out.json>] | --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "root_cause_mechanisms.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # reuse extract_features (calls/writes)  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
_FORBIDDEN_INPUT = {"awarded", "awarded_kind", "expected", "expected_mechanism", "issue_id", "severity",
                    "report", "answer", "known_bug", "polarity"}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CONFIG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _has(patterns, text) -> bool:
    t = (text or "").lower()
    return any(p.lower() in t for p in patterns)


def _calls(snippet: str) -> set:
    return sfp.extract_features("x", snippet=snippet)["calls"]


def _transfer_lines(body: str):
    """Yield (call, arg_text) for transfer-like calls; arg_text is the best-effort first balanced arg group."""
    c = _cfg()
    tp = c["transfer_patterns"]
    out = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\(", body):
        name = m.group(1).lower()
        if not any(p == name or p in name for p in tp):
            continue
        # capture the parenthesised arg region (best-effort, single level)
        i = m.end() - 1
        depth, j = 0, i
        while j < len(body):
            if body[j] == "(":
                depth += 1
            elif body[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((name, body[i + 1:j]))
    return out


def _has_scaled_transfer(body: str) -> bool:
    """True if a transfer's AMOUNT is scaled by a scale-named var (scale_token_patterns) via a scale op —
    either inline in the transfer arg, or in the assignment of the transferred variable. Linking the arg var
    to its assignment avoids false positives from unrelated scale ops elsewhere in the body."""
    c = _cfg()
    b = _strip(body)
    sop = "|".join(c["scale_op_patterns"])
    stok = "|".join(c["scale_token_patterns"])
    for _, arg in _transfer_lines(b):
        if re.search(r"(%s)\s*\([^)]*(%s)" % (sop, stok), arg, re.I):   # inline scale in the transfer arg
            return True
        for ident in set(re.findall(r"[A-Za-z_]\w*", arg)):            # transferred var assigned via a scale op
            if re.search(r"\b" + re.escape(ident) + r"\b\s*=\s*[^;]*?(%s)\s*\([^;]*?(%s)" % (sop, stok), b, re.I):
                return True
    return False


# ---- per-mechanism comparand rules (operate ONLY on provided source snippets) ----

def _rule_missing_scale(term, target, siblings):
    tb = _strip(target["snippet"])
    if not _transfer_lines(tb):
        return "WEAK", "target has no transfer to scale"
    if _has_scaled_transfer(tb):
        return "WEAK", "target already scales its transfer"
    for s in siblings:
        if _has_scaled_transfer(s["snippet"]):
            ev = f"sibling '{s['name']}' applies a scale op ({term or 'scale'}) around its transfer; target '{target['name']}' transfers a bare amount with no scale op"
            return "STRONG", ev
    return "WEAK", "no sibling scales the same transfer (no present-elsewhere comparand)"


def _rule_self_computed_unapplied(term, target, siblings):
    tb = _strip(target["snippet"])
    if not term:
        return "WEAK", "no term identifier supplied"
    assigned = re.search(r"\b" + re.escape(term) + r"\b\s*=(?![=])", tb)
    if not assigned:
        return "WEAK", f"term '{term}' is not computed in the target"
    transfers = _transfer_lines(tb)
    if not transfers:
        return "WEAK", f"term '{term}' computed but the target has no value path to omit it from"
    # "some value path omits the computed term": >=1 transfer whose amount arg excludes the term
    omitting = [arg.strip() for _, arg in transfers if term.lower() not in arg.lower()]
    if omitting:
        return "MEDIUM", f"target computes '{term}' but at least one value/transfer path excludes it (e.g. arg '{omitting[0][:60]}') — self-computed-unapplied"
    return "WEAK", f"term '{term}' is applied in every value path (no omission)"


def _rule_sibling_call(term, target, siblings, resolution_only=False):
    c = _cfg()
    tcalls = {x.lower() for x in _calls(target["snippet"])}
    shared_transfer = bool(_transfer_lines(_strip(target["snippet"])))
    for s in siblings:
        scalls = {x.lower() for x in _calls(s["snippet"])}
        if not (scalls & tcalls):
            continue  # not a parallel path
        missing = scalls - tcalls
        if resolution_only:
            missing = {m for m in missing if _has(c["resolution_call_patterns"], m)}
        if term:
            missing = {m for m in missing if term.lower() in m or m in term.lower()}
        if missing and (shared_transfer or (scalls & tcalls)):
            ev = f"sibling '{s['name']}' calls {sorted(missing)} on a shared path that target '{target['name']}' omits"
            return "STRONG", ev
    return "WEAK", "no sibling call is present-elsewhere/absent-here on a shared path"


def _rule_design_absence(term, target, siblings):
    """missing_bound: score only if the bound identifier exists in a sibling but not the target.
    If it appears NOWHERE (target+siblings) it is a DESIGN ABSENCE -> REJECT (constraint 6)."""
    c = _cfg()
    needles = [term] if term else c["bound_name_patterns"]
    in_target = _has(needles, target["snippet"])
    in_sibling = any(_has(needles, s["snippet"]) for s in siblings)
    if in_sibling and not in_target:
        return "STRONG", f"bound '{term or 'bound'}' is enforced in a sibling but absent in target (present-elsewhere/absent-here)"
    if not in_sibling and not in_target:
        return "REJECT", f"design-absence: identifier '{term or 'bound'}' appears in NO sibling/callee or the target — no source-backed comparand that it should exist on this path"
    return "WEAK", f"bound '{term or 'bound'}' present in target; no omission comparand"


def _rule_basis(term, target, siblings):
    c = _cfg()
    conv = [p for p in c["resolution_call_patterns"] if p in ("convert", "normalize", "tovalue")]
    for s in siblings:
        sc = {x.lower() for x in _calls(s["snippet"])}
        tc = {x.lower() for x in _calls(target["snippet"])}
        if (sc - tc) and any(any(k in m for k in conv) for m in (sc - tc)):
            return "STRONG", f"sibling '{s['name']}' performs an explicit basis conversion the target omits"
    return "WEAK", "no distinct basis-conversion comparand (likely subsumed by scale)"


def _rule_rounding(term, target, siblings):
    tb = _strip(target["snippet"])
    div_then_mul = re.search(r"/[^;]*\*", tb)
    for s in siblings:
        sb = _strip(s["snippet"])
        if div_then_mul and re.search(r"\*[^;]*/", sb):
            return "STRONG", f"target divides-before-multiplies where sibling '{s['name']}' multiplies-before-divides"
    return "WEAK", "no rounding-order comparand in any sibling"


_RULES = {
    "missing_scale": lambda t, tg, sb: _rule_missing_scale(t, tg, sb),
    "wrong_basis": lambda t, tg, sb: _rule_basis(t, tg, sb),
    "omitted_term": lambda t, tg, sb: _rule_self_computed_unapplied(t, tg, sb),
    "missing_call": lambda t, tg, sb: _rule_sibling_call(t, tg, sb, resolution_only=False),
    "recipient_missing": lambda t, tg, sb: _rule_sibling_call(t, tg, sb, resolution_only=True),
    "missing_bound": lambda t, tg, sb: _rule_design_absence(t, tg, sb),
    "rounding_loss": lambda t, tg, sb: _rule_rounding(t, tg, sb),
}


def _assert_clean(inp):
    bad = _FORBIDDEN_INPUT & set(inp.keys())
    if bad:
        raise ValueError(f"engine input must not carry answer-key fields: {sorted(bad)}")


def run(inp: dict) -> dict:
    _assert_clean(inp)
    c = _cfg()
    order = c["confidence_order"]
    adv_min = order[c["advance_min_confidence"]]
    target = inp["target"]
    siblings = inp.get("siblings", [])
    results = []
    for cand in inp["candidate_mechanisms"]:
        mech = cand["mechanism"]
        term = cand.get("term", "")
        label = cand.get("label", mech)
        rule = _RULES.get(mech)
        if not rule:
            conf, ev = "REJECT", f"unknown mechanism type '{mech}'"
        else:
            conf, ev = rule(term, target, siblings)
        results.append({"label": label, "mechanism": mech, "term": term, "confidence": conf, "evidence": ev})
    advanced = [r for r in results if order[r["confidence"]] >= adv_min]
    rejected = [{"label": r["label"], "confidence": r["confidence"], "reason": r["evidence"]}
                for r in results if order[r["confidence"]] < adv_min]
    advanced.sort(key=lambda r: -order[r["confidence"]])
    if not advanced:
        decision = "ABSTAIN"
    elif len(advanced) == 1:
        decision = "SINGLE_MECHANISM"
    else:
        decision = "MULTI_MECHANISM_NEEDS_PROOF"
    return {**FLAGS, "candidate_id": inp.get("candidate_id"), "function": target.get("name"),
            "decision": decision, "selected": [r["label"] for r in advanced],
            "advanced": advanced, "rejected": rejected, "all_mechanisms": results,
            "advances_to_impact_gate": decision != "ABSTAIN"}


# --------------------------- self-test ---------------------------

def _self_test():
    ok = True
    # PROBE 1 — engine-not-lookup: a NON-scale fn whose only source-backed mechanism is a missing sibling call.
    p1 = {"candidate_id": "probe-nonscale", "function": "claim_many",
          "target": {"name": "claim_many", "snippet": "address o = escrow.ownerOf(id); token.transfer(o, amt);"},
          "siblings": [{"name": "claim", "snippet": "address o = escrow.ownerOf(id); o = avm.getOriginalOwner(id); token.transfer(o, amt);"}],
          "candidate_mechanisms": [
              {"mechanism": "recipient_missing", "term": "getOriginalOwner", "label": "missing_recipient_resolution"},
              {"mechanism": "missing_scale", "term": "scale", "label": "missing_scale"},
              {"mechanism": "missing_bound", "term": "cap", "label": "missing_cap"}]}
    r1 = run(p1)
    c1 = r1["decision"] == "SINGLE_MECHANISM" and r1["selected"] == ["missing_recipient_resolution"]
    print(f"  [{'PASS' if c1 else 'FAIL'}] engine-not-lookup: non-scale fn -> picks recipient resolution, NOT scale ({r1['selected']})")
    ok &= c1
    # PROBE 2 — abstain: a fn with only a local suspicion, no comparand anywhere.
    p2 = {"candidate_id": "probe-abstain", "function": "f",
          "target": {"name": "f", "snippet": "uint p = oracle.getSafeLatestPrice(age).price; return p * bal / eth;"},
          "siblings": [{"name": "g", "snippet": "uint q = oracle.getSafeLatestPrice(age).price; return q;"}],
          "candidate_mechanisms": [
              {"mechanism": "missing_bound", "term": "closeFactor", "label": "missing_close_factor"},
              {"mechanism": "missing_scale", "term": "scale", "label": "missing_scale"},
              {"mechanism": "omitted_term", "term": "fee", "label": "omitted_fee"}]}
    r2 = run(p2)
    c2 = r2["decision"] == "ABSTAIN" and not r2["advances_to_impact_gate"]
    print(f"  [{'PASS' if c2 else 'FAIL'}] abstain: only local suspicion, no comparand -> ABSTAIN ({r2['decision']})")
    ok &= c2
    # PROBE 3 — design-absence reject + scale advance distinguished.
    p3 = {"candidate_id": "probe-scale", "function": "seize",
          "target": {"name": "seize", "snippet": "uint take = wdiv(repay, price); token.safeTransfer(to, take);"},
          "siblings": [{"name": "modify", "snippet": "uint amt = wmul(delta, tokenScale); token.safeTransfer(to, amt);"}],
          "candidate_mechanisms": [
              {"mechanism": "missing_scale", "term": "tokenScale", "label": "missing_tokenScale"},
              {"mechanism": "missing_bound", "term": "closeFactor", "label": "missing_close_factor"}]}
    r3 = run(p3)
    sel = set(r3["selected"]); rej = {x["label"] for x in r3["rejected"]}
    c3 = "missing_tokenScale" in sel and "missing_close_factor" in rej
    print(f"  [{'PASS' if c3 else 'FAIL'}] scale STRONG advances, close-factor design-absence rejected (sel={sorted(sel)} rej={sorted(rej)})")
    ok &= c3
    # PROBE 4 — answer-key smuggling refused.
    try:
        run({"awarded": True, "target": {"name": "x", "snippet": ""}, "candidate_mechanisms": []})
        c4 = False
    except ValueError:
        c4 = True
    print(f"  [{'PASS' if c4 else 'FAIL'}] refuses answer-key fields in input")
    ok &= c4
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.input:
        ap.error("--input required (or --self-test)")
    res = run(json.load(open(args.input)))
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"[discriminator] {res['candidate_id']}: {res['decision']} | selected={res['selected']} | "
          f"rejected={[r['label'] for r in res['rejected']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
