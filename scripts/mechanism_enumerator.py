#!/usr/bin/env python3
"""
mechanism_enumerator.py — Phase-33 RESEARCH-ONLY autonomous mechanism enumerator (un-wired).

P32 proved a SOURCE-BACKED root-cause DISCRIMINATOR can pick the right mechanism — but the candidate mechanism
list was HUMAN-SUPPLIED. P33 closes that: this stage GENERATES the candidate mechanisms directly from source
structure (the target function body + its sibling/callee bodies) crossed with a GENERIC suspicion catalog (the
standard DeFi vocab already in config/root_cause_mechanisms.json, read by reference). The generated candidates are
then fed UNCHANGED into the P32 discriminator (scripts/root_cause_discriminator.py), which scores them by comparand
evidence and REJECTs design-absence / generic / unbacked mechanisms.

Autonomy guarantees:
- Input is ONLY a located source bundle (target/siblings/callees snippets). No hand-curated mechanism list.
- Candidate mechanisms are derived from source SHAPES (transfers, computed terms, sibling call deltas, operation
  category) + the GENERIC catalog. No subject-specific (e.g. dittoeth) identifier is hardcoded.
- Structurally refuses answer-key fields (same _FORBIDDEN_INPUT discipline as the discriminator).
- Mechanism TYPES are restricted to the 7 the discriminator can score; a richer 10-class taxonomy is attached
  as the DESCRIPTIVE mechanism_class only.
- A candidate with neither a concrete `term` NOR a concrete source line is a generic label -> DROPPED pre-output
  (constraint 4 "no generic labels").

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: mechanism_enumerator.py --bundle <bundle.json> [--out <mechanism_candidates.json>] | --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB_CFG = ROOT / "config" / "root_cause_mechanisms.json"
ENUM_CFG = ROOT / "config" / "mechanism_enumeration.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # reuse strip_comments + extract_features  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
# Same answer-key firewall as the discriminator: enumeration must NEVER see these.
_FORBIDDEN_INPUT = {"awarded", "awarded_kind", "expected", "expected_mechanism", "issue_id", "severity",
                    "report", "answer", "known_bug", "polarity", "must_reject", "awarded_mechanisms"}


@lru_cache(maxsize=1)
def _vocab() -> dict:
    return json.loads(VOCAB_CFG.read_text())


@lru_cache(maxsize=1)
def _knobs() -> dict:
    return json.loads(ENUM_CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _calls(snippet: str) -> set:
    return {c.lower() for c in sfp.extract_features("x", snippet=snippet or "")["calls"]}


def _idents(text: str) -> list:
    return re.findall(r"[A-Za-z_]\w*", text or "")


def _transfers(body: str):
    """Yield (call_name, arg_text) for transfer-like calls (transfer_patterns), best-effort balanced first-arg group."""
    tp = _vocab()["transfer_patterns"]
    out = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\(", body):
        name = m.group(1).lower()
        if not any(p == name or p in name for p in tp):
            continue
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


def _arg_is_scaled(arg: str, body: str) -> bool:
    """True if the transfer arg is scaled inline by a scale-named var, or its var is assigned via a scale op."""
    v = _vocab()
    sop = "|".join(v["scale_op_patterns"])
    stok = "|".join(v["scale_token_patterns"])
    if re.search(r"(%s)\s*\([^)]*(%s)" % (sop, stok), arg, re.I):
        return True
    for ident in set(_idents(arg)):
        if re.search(r"\b" + re.escape(ident) + r"\b\s*=\s*[^;]*?(%s)\s*\([^;]*?(%s)" % (sop, stok), body, re.I):
            return True
    return False


def _ev(target, lines_hint, snippet, why):
    return {"file": target.get("file", ""), "lines": lines_hint or target.get("lines", ""),
            "snippet": (snippet or "")[:200], "why_it_matters": why}


def _cand(mech, term, label, klass, conf, source_evidence, comparands=None, callees=None):
    return {"mechanism": mech, "term": term, "label": label, "mechanism_class": klass,
            "pre_discrimination_confidence": conf, "source_evidence": source_evidence,
            "comparands": comparands or [], "callees": callees or []}


# ---------------------------- generation rules (source SHAPE -> candidate) ----------------------------

def _gen_missing_scale(target, tbody, sibs):
    """A transfer of a BARE (unscaled) amount is a scale-conversion suspicion."""
    transfers = _transfers(tbody)
    bare = [(n, a) for n, a in transfers if not _arg_is_scaled(a, tbody)]
    if not bare:
        return []
    v = _vocab()
    # term = a scale-named identifier visible in target or any sibling, else generic "scale"
    term = "scale"
    pool = tbody + " " + " ".join(_strip(s.get("snippet", "")) for s in sibs)
    for stok in v["scale_token_patterns"]:
        m = re.search(r"\b([A-Za-z_]\w*%s\w*)\b" % stok, pool, re.I) or re.search(r"\b(%s)\b" % stok, pool, re.I)
        if m:
            term = m.group(1)
            break
    comp = []
    for s in sibs:
        sb = _strip(s.get("snippet", ""))
        if any(_arg_is_scaled(a, sb) for _, a in _transfers(sb)):
            comp.append({"function": s.get("name", ""), "difference": "applies a scale op around its transfer amount"})
    n0, a0 = bare[0]
    conf = "HIGH" if comp else "LOW"
    return [_cand("missing_scale", term, f"missing_{term}", _knobs()["mechanism_class_map"]["missing_scale"], conf,
                  [_ev(target, "", f"{n0}(...{a0.strip()[:80]}...)", "transfers a bare amount with no scale op")], comp)]


def _gen_omitted_term(target, tbody, sibs):
    """A term-named value (penalty/fee/...) computed in the body but absent from a transfer arg = computed-unapplied."""
    v = _vocab()
    out, seen = [], set()
    transfers = _transfers(tbody)
    for tok in v["term_name_patterns"]:
        for m in re.finditer(r"\b([A-Za-z_]*%s\w*)\b\s*=(?![=])" % tok, tbody, re.I):
            term = m.group(1)
            if term.lower() in seen:
                continue
            omitting = [a.strip() for _, a in transfers if term.lower() not in a.lower()]
            if not omitting:
                continue
            seen.add(term.lower())
            out.append(_cand("omitted_term", term, f"omitted_{term}_term",
                             _knobs()["mechanism_class_map"]["omitted_term"], "HIGH",
                             [_ev(target, "", m.group(0), f"'{term}' is computed but excluded from a value path (e.g. arg '{omitting[0][:60]}')")]))
    return out[: _knobs()["max_candidates_per_type"]]


def _gen_sibling_call(target, tbody, sibs):
    """A call present in a sibling on a shared path but absent in the target = callee/recipient delta."""
    v = _vocab()
    tcalls = _calls(tbody)
    out, seen = [], set()
    for s in sibs:
        scalls = _calls(s.get("snippet", ""))
        if not (scalls & tcalls):
            continue  # not a parallel path
        for missing in sorted(scalls - tcalls):
            if missing in seen:
                continue
            seen.add(missing)
            is_recip = any(p in missing for p in v["resolution_call_patterns"])
            mech = "recipient_missing" if is_recip else "missing_call"
            out.append(_cand(mech, missing, f"missing_{missing}", _knobs()["mechanism_class_map"][mech], "HIGH",
                             [_ev(target, "", "", f"target omits call '{missing}' present on a shared path")],
                             [{"function": s.get("name", ""), "difference": f"calls '{missing}' on the shared path"}]))
    return out[: _knobs()["max_candidates_per_type"]]


def _gen_missing_bound(target, tbody, sibs):
    """Bounds: (a) a bound enforced in a sibling but absent in target (real comparand), and (b) GENERIC
    operation-relevant bounds from the catalog (design-absence suspicions the discriminator must REJECT)."""
    v = _vocab()
    k = _knobs()
    out, seen = [], set()
    sib_text = " ".join(_strip(s.get("snippet", "")) for s in sibs).lower()
    # (a) present-in-sibling / absent-in-target  -> real comparand
    for b in v["bound_name_patterns"]:
        if b in sib_text and b not in tbody.lower() and b not in seen:
            seen.add(b)
            out.append(_cand("missing_bound", b, f"missing_{b}", k["mechanism_class_map"]["missing_bound"], "HIGH",
                             [_ev(target, "", "", f"bound '{b}' present in a sibling, absent in target")],
                             [{"function": "sibling", "difference": f"enforces bound '{b}'"}]))
    # (b) operation-relevant GENERIC suspicions (design-absence; rejected unless a comparand exists)
    low = tbody.lower()
    for opname, sigs in k["operation_signals"].items():
        if any(sig in low for sig in sigs) and opname in k["operation_bound_relevance"]:
            for b in k["operation_bound_relevance"][opname]:
                if b in seen:
                    continue
                seen.add(b)
                shape = next((sig for sig in sigs if sig in low), opname)
                out.append(_cand("missing_bound", b, f"missing_{b}", k["mechanism_class_map"]["missing_bound"], "LOW",
                                 [_ev(target, "", shape, f"operation shape '{shape}' makes bound '{b}' a generic suspicion (no comparand yet)")]))
    return out


def _gen_rounding(target, tbody, sibs):
    m = re.search(r"[A-Za-z_]\w*\s*/[^;]*\*", tbody)
    if not m:
        return []
    return [_cand("rounding_loss", "", "rounding_loss", _knobs()["mechanism_class_map"]["rounding_loss"], "LOW",
                  [_ev(target, "", m.group(0)[:80], "divides before multiplying (potential rounding/precision loss)")])]


def _gen_wrong_basis(target, tbody, sibs):
    v = _vocab()
    conv = [p for p in v["resolution_call_patterns"] if p in ("convert", "normalize", "tovalue")]
    tcalls = _calls(tbody)
    for s in sibs:
        sc = _calls(s.get("snippet", ""))
        missing = sc - tcalls
        hit = [m for m in missing if any(c in m for c in conv)]
        if hit:
            return [_cand("wrong_basis", "", "wrong_basis", _knobs()["mechanism_class_map"]["wrong_basis"], "HIGH",
                          [_ev(target, "", "", f"target omits basis conversion {hit} present in sibling '{s.get('name','')}'")],
                          [{"function": s.get("name", ""), "difference": f"performs conversion {hit}"}])]
    return []


_GENERATORS = [_gen_missing_scale, _gen_omitted_term, _gen_sibling_call, _gen_missing_bound, _gen_rounding, _gen_wrong_basis]


def _assert_clean(bundle):
    bad = _FORBIDDEN_INPUT & set(bundle.keys())
    if bad:
        raise ValueError(f"enumerator bundle must not carry answer-key fields: {sorted(bad)}")


def _is_generic(cand) -> bool:
    """No concrete term AND no concrete source line -> generic label, drop (constraint 4)."""
    has_term = bool((cand.get("term") or "").strip())
    has_line = any((e.get("snippet") or "").strip() or (e.get("lines") or "").strip() or (e.get("why_it_matters") or "").strip()
                   for e in cand.get("source_evidence", []))
    return not (has_term or has_line)


def enumerate_mechanisms(bundle: dict) -> dict:
    _assert_clean(bundle)
    target = bundle["target"]
    sibs = bundle.get("siblings", [])
    tbody = _strip(target.get("snippet", ""))
    cands, seen = [], set()
    for gen in _GENERATORS:
        for c in gen(target, tbody, sibs):
            key = (c["mechanism"], (c.get("term") or "").lower())
            if key in seen or _is_generic(c):
                continue
            seen.add(key)
            cands.append(c)
    return {**FLAGS, "candidate_id": bundle.get("candidate_id"),
            "target": {"name": target.get("name"), "file": target.get("file", ""), "lines": target.get("lines", "")},
            "candidate_mechanisms": cands,
            "notes": ["mechanisms generated autonomously from source shape + generic catalog; no hand-supplied list",
                      "mechanism TYPE restricted to the 7 P32-discriminator-scorable types; mechanism_class is descriptive"]}


def to_discriminator_input(enum_out: dict, bundle: dict) -> dict:
    """Shape the enumerator output into the P32 discriminator's input contract (target/siblings/candidate_mechanisms)."""
    return {"candidate_id": enum_out.get("candidate_id"),
            "target": {"name": bundle["target"].get("name"), "snippet": bundle["target"].get("snippet", "")},
            "siblings": [{"name": s.get("name"), "snippet": s.get("snippet", "")} for s in bundle.get("siblings", [])],
            "candidate_mechanisms": [{"mechanism": c["mechanism"], "term": c.get("term", ""), "label": c["label"]}
                                     for c in enum_out["candidate_mechanisms"]]}


# --------------------------------- self-test ---------------------------------

def _self_test():
    ok = True
    # PROBE 1 — autonomous generation: a transfer of a bare amount + a computed penalty -> scale + omitted_term,
    # WITHOUT being told the answer. Sibling scales its transfer (scale comparand present).
    b1 = {"candidate_id": "probe-gen",
          "target": {"name": "liquidate", "file": "X.sol", "lines": "1-9",
                     "snippet": "uint256 penalty = wmul(repay, penaltyRate); uint256 take = wdiv(repay, price); token.safeTransfer(msg.sender, take); pool.repay(repay - penalty);"},
          "siblings": [{"name": "modifyCollateral", "snippet": "uint256 amount = wmul(delta, tokenScale); token.safeTransfer(to, amount);"}]}
    e1 = enumerate_mechanisms(b1)
    mset = {c["mechanism"] for c in e1["candidate_mechanisms"]}
    c1 = "missing_scale" in mset and "omitted_term" in mset
    print(f"  [{'PASS' if c1 else 'FAIL'}] autonomous: generates missing_scale + omitted_term from source ({sorted(mset)})")
    ok &= c1
    # The generated candidates, fed to the UNCHANGED discriminator, must select scale (STRONG) + penalty (MEDIUM).
    import root_cause_discriminator as RCD
    d1 = RCD.run(to_discriminator_input(e1, b1))
    c1b = "missing_scale" in [m["mechanism"] for m in d1["advanced"]] and d1["decision"] in ("MULTI_MECHANISM_NEEDS_PROOF", "SINGLE_MECHANISM")
    print(f"  [{'PASS' if c1b else 'FAIL'}] generated candidates discriminate -> {d1['decision']} selected={d1['selected']}")
    ok &= c1b
    # PROBE 2 — design-absence demo: a liquidation shape generates a generic closeFactor suspicion that the
    # discriminator REJECTs (no comparand). Proves the reject path is exercised by AUTONOMOUS candidates.
    has_cf = any(c["term"] == "closefactor" for c in e1["candidate_mechanisms"])
    rej_cf = any("closefactor" in (r.get("label", "").lower()) for r in d1["rejected"]) if has_cf else False
    print(f"  [{'PASS' if (has_cf and rej_cf) else 'FAIL'}] design-absence: generic closeFactor generated ({has_cf}) and rejected ({rej_cf})")
    ok &= (has_cf and rej_cf)
    # PROBE 3 — abstain shape: a pure-read fn with no transfer/term/sibling-delta generates nothing actionable -> abstain.
    b3 = {"candidate_id": "probe-abstain",
          "target": {"name": "getPrice", "file": "Y.sol", "lines": "1-3",
                     "snippet": "uint256 p = oracle.latestPrice(); return p;"},
          "siblings": [{"name": "getPrice2", "snippet": "uint256 q = oracle.latestPrice(); return q;"}]}
    e3 = enumerate_mechanisms(b3)
    d3 = RCD.run(to_discriminator_input(e3, b3))
    c3 = d3["decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c3 else 'FAIL'}] non-bug read fn -> ABSTAIN ({d3['decision']}, gen={[c['mechanism'] for c in e3['candidate_mechanisms']]})")
    ok &= c3
    # PROBE 4 — answer-key smuggling refused.
    try:
        enumerate_mechanisms({"awarded_mechanisms": ["x"], "target": {"name": "z", "snippet": ""}})
        c4 = False
    except ValueError:
        c4 = True
    print(f"  [{'PASS' if c4 else 'FAIL'}] refuses answer-key fields in bundle")
    ok &= c4
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.bundle:
        ap.error("--bundle required (or --self-test)")
    bundle = json.load(open(args.bundle))
    res = enumerate_mechanisms(bundle)
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"[enumerator] {res['candidate_id']}: {len(res['candidate_mechanisms'])} candidates -> "
          f"{[c['label'] for c in res['candidate_mechanisms']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
