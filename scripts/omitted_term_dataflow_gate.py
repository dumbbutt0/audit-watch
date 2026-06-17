#!/usr/bin/env python3
"""
omitted_term_dataflow_gate.py — Phase-47 RESEARCH-ONLY dataflow-aware demotion gate (un-wired).

Runs AFTER the P45 mechanism_advancement_gate, on candidates whose pre-decision is ADVANCE/REVIEW_ONLY and whose
mechanism is omitted_term / computed_unapplied. It makes the omitted/computed corroboration a DATAFLOW judgement instead
of P45's syntactic literal-name check, repairing the P46 false positive (TraitForge DevFund.claim: `pending =
pendingRewards + …; transfer(pending)` — both terms ARE applied via the intermediate aggregate `pending`).

It can ONLY demote (ADVANCE -> REVIEW_ONLY/ABSTAIN, REVIEW_ONLY -> ABSTAIN); it NEVER promotes. A non-processed mechanism
or a missing pre-decision passes through unchanged.

Core rule: a computed term is APPLIED (so the omitted/computed candidate is REFUTED and demoted) when it flows — via
>=1 intermediate DERIVED VARIABLE, or a source-visible INTERNAL CALLEE — into a value/state/authority sink. Direct
in-arg appearance of the term itself is NOT treated here as newly-applied (the P45 gate already evaluates that), which
is exactly what preserves A1's `penalty` (used directly in call args, never carried by a derived variable to a sink)
while demoting DevFund's `pending` aggregate. Flow only to events/logging, require/revert, view-only returns, or unknown
external calls is NOT applied.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: omitted_term_dataflow_gate.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "omitted_term_dataflow_gate.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _tok(name: str, text: str) -> bool:
    """\\bname\\b match (tolerates obj.name / mapping[name] because '.'/'[' are word boundaries)."""
    if not name:
        return False
    return re.search(r"\b" + re.escape(name) + r"\b", text or "") is not None


def _statements(body: str):
    return [s.strip() for s in body.split(";") if s.strip()]


_ASSIGN_OPS = ("+=", "-=", "*=", "/=", "=")


def _split_assignment(stmt: str):
    """Return (lhs_raw, op, rhs) for the FIRST top-level assignment op, skipping ==,<=,>=,!=. Else None."""
    for m in re.finditer(r"(\+=|-=|\*=|/=|==|<=|>=|!=|=)", stmt):
        op = m.group(1)
        if op in ("==", "<=", ">=", "!="):
            continue
        return stmt[:m.start()].strip(), op, stmt[m.end():].strip()
    return None


def _lhs_name(lhs_raw: str) -> str:
    """Last identifier of a simple local-var lhs (e.g. 'uint256 pending' -> 'pending'). '' if member/index lhs."""
    if "." in lhs_raw or "[" in lhs_raw:
        return ""
    ids = re.findall(r"[A-Za-z_]\w*", lhs_raw)
    return ids[-1] if ids else ""


def _is_state_write_lhs(lhs_raw: str) -> bool:
    return ("." in lhs_raw) or ("[" in lhs_raw)


def _calls(body: str):
    """Yield (call_name_lower, arg_text) with balanced first-group args."""
    out = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\(", body):
        name = m.group(1)
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
        out.append((name.lower(), body[i + 1:j]))
    return out


def _is_sink_call(name_lower: str) -> bool:
    return any(sig in name_lower for sig in _cfg()["sink_call_signatures"])


def _derived_closure(body: str, term: str):
    """Variables the term flows into via >=1 intermediate assignment (fixpoint). Excludes the term itself."""
    assigns = []
    for stmt in _statements(body):
        sp = _split_assignment(stmt)
        if sp:
            assigns.append((sp[0], sp[1], sp[2], stmt))
    derived, trace = set(), {}
    changed = True
    while changed:
        changed = False
        for lhs_raw, op, rhs, stmt in assigns:
            name = _lhs_name(lhs_raw)
            if not name or name == term or name in derived:
                continue
            if _tok(term, rhs) or any(_tok(d, rhs) for d in derived):
                derived.add(name)
                trace[name] = stmt
                changed = True
    return derived, trace, assigns


def _internal_callee_sink(body, term, derived, callees):
    """If term/derived is passed to a source-visible internal callee that sinks the corresponding param -> sink."""
    by_name = {(c.get("name") or "").lower(): c for c in (callees or [])}
    for cname, arg_text in _calls(body):
        callee = by_name.get(cname)
        if not callee:
            continue
        args = [a.strip() for a in _split_args(arg_text)]
        params = callee.get("params") or []
        cbody = _strip(callee.get("snippet", ""))
        for k, a in enumerate(args):
            carries = _tok(term, a) or any(_tok(d, a) for d in derived)
            if not carries:
                continue
            param = params[k] if k < len(params) else None
            if param and _param_is_sunk(cbody, param):
                return {"kind": "internal_callee", "source": f"{callee.get('name')}({arg_text.strip()[:60]})"}
    return None


def _split_args(arg_text: str):
    """Top-level comma split respecting nested parens."""
    out, depth, cur = [], 0, ""
    for ch in arg_text:
        if ch == "(":
            depth += 1; cur += ch
        elif ch == ")":
            depth -= 1; cur += ch
        elif ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def _param_is_sunk(callee_body: str, param: str) -> bool:
    # transfer-style sink carrying the param
    for name, args in _calls(callee_body):
        if _is_sink_call(name) and _tok(param, args):
            return True
    # state write whose rhs carries the param
    for stmt in _statements(callee_body):
        sp = _split_assignment(stmt)
        if sp and _is_state_write_lhs(sp[0]) and _tok(param, sp[2]):
            return True
    return False


def _find_sink(body, term, derived, callees):
    """Return the sink dict if a DERIVED variable reaches a value/state sink, or the term/derived hits an internal
    callee sink. Direct term-in-arg (no derived) is intentionally NOT a sink here (P45's domain)."""
    # A) transfer-style call carrying a derived variable
    for name, args in _calls(body):
        if _is_sink_call(name) and any(_tok(d, args) for d in derived):
            return {"kind": "transfer", "source": f"{name}({args.strip()[:60]})"}
    # B) state write whose rhs carries a derived variable
    for stmt in _statements(body):
        sp = _split_assignment(stmt)
        if sp and _is_state_write_lhs(sp[0]) and any(_tok(d, sp[2]) for d in derived):
            return {"kind": "state_write", "source": stmt[:70]}
    # C) source-visible internal callee that sinks the term/derived
    ics = _internal_callee_sink(body, term, derived, callees)
    if ics:
        return ics
    return None


def _term_flow(body, term, callees):
    derived, trace, _ = _derived_closure(body, term)
    sink = _find_sink(body, term, derived, callees)
    path = []
    flows_to = term
    if derived:
        # report the first derived carrier on the path
        first = sorted(derived, key=lambda d: body.find(trace[d]))[0]
        flows_to = first
        path.append({"kind": "aggregate" if "+" in trace[first] or "-" in trace[first] else "assignment",
                     "source": trace[first][:80]})
    if sink and sink["kind"] == "internal_callee" and not derived:
        flows_to = term
        path.append({"kind": "call_arg", "source": sink["source"]})
    applied = sink is not None
    if applied and sink["kind"] in ("transfer", "state_write"):
        path.append({"kind": "transfer_arg" if sink["kind"] == "transfer" else "state_write", "source": sink["source"]})
    elif applied and sink["kind"] == "internal_callee" and derived:
        path.append({"kind": "internal_callee", "source": sink["source"]})
    return {"term": term, "flows_to": flows_to if applied else None,
            "path": path, "sink": sink or {"kind": "unknown", "source": None}, "applied": applied}


def gate(candidate: dict, target: dict, callees=None) -> dict:
    c = _cfg()
    mech = candidate.get("mechanism", "")
    pre = candidate.get("pre_decision", c["decisions"]["advance"])
    terms = candidate.get("terms")
    if not terms:
        t = candidate.get("term", "")
        terms = [t] if t else []

    base = {**FLAGS, "candidate_id": candidate.get("label") or candidate.get("candidate_id"),
            "mechanism_class": mech,
            "target": {"file": target.get("file"), "function": target.get("name"), "lines": target.get("lines")},
            "terms": terms, "pre_dataflow_decision": pre}

    # Only processed mechanisms with a real pre-advance and at least one term are analyzed; else pass through unchanged.
    if mech not in c["processed_mechanisms"] or pre not in (c["decisions"]["advance"], c["decisions"]["review_only"]) or not terms:
        return {**base, "post_dataflow_decision": pre, "term_flows": [], "unapplied_terms": terms,
                "rejection_reason": None, "review_reason": None}

    body = _strip(target.get("snippet", ""))
    flows = [_term_flow(body, t, callees) for t in terms]
    applied_terms = [f["term"] for f in flows if f["applied"]]
    unapplied = [f["term"] for f in flows if not f["applied"]]

    # Demote ONLY when confident the omitted/computed premise is refuted: EVERY listed term is applied via dataflow.
    if terms and not unapplied:
        return {**base, "post_dataflow_decision": c["decisions"]["abstain"], "term_flows": flows,
                "unapplied_terms": [],
                "rejection_reason": f"term(s) {applied_terms} are applied via dataflow (derived/aggregate or internal callee reaches a value/state sink); omitted/computed premise refuted",
                "review_reason": None}
    # Otherwise unchanged (at least one term has no resolved sink path -> genuine omission may stand; never promote).
    return {**base, "post_dataflow_decision": pre, "term_flows": flows, "unapplied_terms": unapplied,
            "rejection_reason": None, "review_reason": None}


# --------------------------------- self-test (8 required cases) ---------------------------------

def _t(name, snippet, contract="C", mut="", file="src/C.sol"):
    return {"name": name, "snippet": snippet, "contract": contract, "mutability": mut, "file": file}


def _self_test():
    ok = True
    ADV = _cfg()["decisions"]["advance"]
    # 1 term -> aggregate var -> transfer amount: DEMOTED
    b1 = "uint256 pending = info.pendingRewards + (totalRewardDebt - info.rewardDebt) * info.weight; uint256 claimed = safeRewardTransfer(msg.sender, pending); info.pendingRewards = pending - claimed;"
    r1 = gate({"mechanism": "omitted_term", "term": "pendingRewards", "label": "omitted_pendingRewards_term", "pre_decision": ADV}, _t("claim", b1))
    c1 = r1["post_dataflow_decision"] == "ABSTAIN" and r1["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c1 else 'FAIL'}] aggregate->transfer -> demoted ({r1['post_dataflow_decision']})"); ok &= c1
    # 2 term -> aggregate var -> state write: DEMOTED
    b2 = "uint256 acc = base + reward; totalDebt[user] = acc;"
    r2 = gate({"mechanism": "omitted_term", "term": "reward", "label": "omitted_reward", "pre_decision": ADV}, _t("upd", b2))
    c2 = r2["post_dataflow_decision"] == "ABSTAIN" and r2["term_flows"][0]["sink"]["kind"] == "state_write"
    print(f"  [{'PASS' if c2 else 'FAIL'}] aggregate->state_write -> demoted ({r2['post_dataflow_decision']}, {r2['term_flows'][0]['sink']['kind']})"); ok &= c2
    # 3 term flows only to event/logging: NOT demoted
    b3 = "uint256 acc = base + fee; emit Logged(acc); token.safeTransfer(to, take);"
    r3 = gate({"mechanism": "omitted_term", "term": "fee", "label": "omitted_fee", "pre_decision": ADV}, _t("ev", b3))
    c3 = r3["post_dataflow_decision"] == ADV and not r3["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c3 else 'FAIL'}] event-only flow -> unchanged ({r3['post_dataflow_decision']})"); ok &= c3
    # 4 term flows only to require/revert: NOT demoted
    b4 = "uint256 acc = base + penalty; require(acc > 0, 'x'); token.safeTransfer(to, take);"
    r4 = gate({"mechanism": "omitted_term", "term": "penalty", "label": "omitted_penalty", "pre_decision": ADV}, _t("rq", b4))
    c4 = r4["post_dataflow_decision"] == ADV and not r4["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c4 else 'FAIL'}] require-only flow -> unchanged ({r4['post_dataflow_decision']})"); ok &= c4
    # 5 computed penalty with NO derived-variable sink path (A1 shape): preserved (ADVANCE)
    b5 = ("uint256 takeCollateral = wdiv(repayAmount, discountedPrice); uint256 penalty = wmul(repayAmount, WAD - liqConfig_.liquidationPenalty); "
          "poolUnderlying.safeTransferFrom(msg.sender, address(pool), repayAmount - penalty); token.safeTransfer(msg.sender, takeCollateral); "
          "poolUnderlying.safeTransferFrom(msg.sender, address(pool), penalty); IPoolV3Loop(address(pool)).mintProfit(penalty);")
    r5 = gate({"mechanism": "omitted_term", "term": "penalty", "label": "omitted_penalty_term", "pre_decision": ADV}, _t("liquidatePosition", b5))
    c5 = r5["post_dataflow_decision"] == ADV and not r5["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c5 else 'FAIL'}] A1 penalty (direct-arg, no derived) -> ADVANCE preserved ({r5['post_dataflow_decision']})"); ok &= c5
    # 6 term -> source-visible internal callee with a state/value sink: DEMOTED
    b6 = "uint256 reward = computeReward(msg.sender); creditUser(reward);"
    callees6 = [{"name": "creditUser", "params": ["amt"], "snippet": "balances[msg.sender] += amt;"}]
    r6 = gate({"mechanism": "computed_unapplied", "term": "reward", "label": "computed_reward", "pre_decision": ADV}, _t("h", b6), callees=callees6)
    c6 = r6["post_dataflow_decision"] == "ABSTAIN" and r6["term_flows"][0]["sink"]["kind"] == "internal_callee"
    print(f"  [{'PASS' if c6 else 'FAIL'}] internal-callee sink -> demoted ({r6['post_dataflow_decision']}, {r6['term_flows'][0]['sink']['kind']})"); ok &= c6
    # 7 term -> unknown external callee (no body provided): NOT demoted
    r7 = gate({"mechanism": "computed_unapplied", "term": "reward", "label": "computed_reward", "pre_decision": ADV}, _t("h", b6), callees=[])
    c7 = r7["post_dataflow_decision"] == ADV and not r7["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c7 else 'FAIL'}] unknown external callee -> not applied ({r7['post_dataflow_decision']})"); ok &= c7
    # 8 markers + no subject identifiers in config
    cfg = CFG.read_text().lower()
    banned = ("sentiment", "plaza", "traitforge", "dittoeth", "basin", "devfund", "pending", "loopfi", "blackhole", "bakerfi")
    c8 = (FLAGS["research_only"] and not FLAGS["is_gate"] and not FLAGS["routes_in_production"]
          and _cfg().get("research_only") is True and not any(b in cfg for b in banned))
    print(f"  [{'PASS' if c8 else 'FAIL'}] research-only markers + no subject identifiers in config"); ok &= c8
    # never-promote sanity: a REVIEW_ONLY pre with no applied flow stays REVIEW_ONLY (not ADVANCE)
    r9 = gate({"mechanism": "omitted_term", "term": "fee", "label": "x", "pre_decision": "REVIEW_ONLY"}, _t("ev", b3))
    c9 = r9["post_dataflow_decision"] == "REVIEW_ONLY"
    print(f"  [{'PASS' if c9 else 'FAIL'}] never promotes (REVIEW_ONLY stays) ({r9['post_dataflow_decision']})"); ok &= c9
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p47)")


if __name__ == "__main__":
    raise SystemExit(main())
