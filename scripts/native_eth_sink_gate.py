#!/usr/bin/env python3
"""
native_eth_sink_gate.py — Phase-52 RESEARCH-ONLY native-ETH sink extension for the omitted-term dataflow lane (un-wired).

Runs AFTER the P47 dataflow gate (and P49), only on {omitted_term, computed_unapplied} candidates whose pre-decision is
ADVANCE/REVIEW_ONLY. Repairs the P51 gap: P47 recognizes ERC20-style sinks (transfer/mint/burn call args, state writes,
internal callees) but NOT native-ETH value transfers, so a fee paid via `payable(owner()).call{value: fee}("")` reads as
"computed but unapplied" (LamboWin `_sellQuote` false positive).

Demotion-only (ADVANCE -> REVIEW_ONLY/ABSTAIN, REVIEW_ONLY -> ABSTAIN); NEVER promotes. A computed term is APPLIED (so the
candidate is demoted) when the term — or a derived alias (reusing P47's `_derived_closure`) — is the AMOUNT of a native-ETH
value transfer:
  - low-level   `<recipient>.call{value: <amount>}(...)`  (incl. payable(...)/address(...))
  - native xfer `<recipient>.transfer(<amount>)`  with exactly ONE arg (ERC20 transfer(to,amt) has two -> excluded)
  - native send `<recipient>.send(<amount>)`      with exactly ONE arg
NOT counted: call with no {value:}; call{value: 0}; delegatecall/staticcall; term only in calldata (not the {value:}
expr); event/require-message-only usage; an amount expression not traceable to the term/alias.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: native_eth_sink_gate.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "native_eth_sink_gate.json"
sys.path.insert(0, str(ROOT / "scripts"))
import omitted_term_dataflow_gate as P47  # reuse _strip / _derived_closure / _calls / _split_args (byte-identical)

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _tok_ci(name: str, text: str) -> bool:
    return bool(name) and re.search(r"\b" + re.escape(name) + r"\b", text or "", re.I) is not None


def _recipient_before(body: str, idx: int) -> str:
    """Best-effort receiver expression immediately preceding a .call/.transfer/.send at position idx."""
    seg = body[max(0, idx - 60):idx]
    m = re.search(r"([A-Za-z_][\w.\(\)\[\]]*)\s*$", seg)
    return m.group(1) if m else ""


def _checked(body: str, idx: int):
    win = body[max(0, idx - 60):idx + 160].lower()
    for sig in _cfg()["check_evidence_signals"]:
        if sig in win:
            return True, sig
    return False, None


def _native_sinks(body: str, term: str, aliases):
    c = _cfg()
    names = {term.lower()} | {a.lower() for a in aliases}
    zero = set(c["zero_amount_literals"])
    sinks = []

    # 1. low-level .call{value: <amount>}
    for m in re.finditer(c["call_value_regex"], body, re.I):
        pre = body[max(0, m.start() - 12):m.start()].lower()
        if pre.endswith("delegate") or pre.endswith("static"):
            continue
        amount = m.group(1).strip()
        if amount.lower() in zero:
            continue
        applies = any(_tok_ci(n, amount) for n in names)
        checked, ev = _checked(body, m.start())
        sinks.append({"sink_kind": "native_call_value", "amount_expression": amount,
                      "recipient_expression": _recipient_before(body, m.start()), "checked": checked,
                      "check_evidence": ev, "source": body[max(0, m.start() - 28):m.end() + 4].strip()[:90],
                      "_applies": applies})

    # 2/3. native .transfer(x) / .send(x) — exactly ONE top-level arg (2-arg => ERC20, excluded)
    for name, arg_text in P47._calls(body):
        if name not in c["native_transfer_methods"]:
            continue
        args = P47._split_args(arg_text)
        if len(args) != 1:
            continue
        amount = args[0].strip()
        if not amount or amount.lower() in zero:
            continue
        applies = any(_tok_ci(n, amount) for n in names)
        kind = "native_transfer" if name == "transfer" else "native_send"
        sinks.append({"sink_kind": kind, "amount_expression": amount, "recipient_expression": "",
                      "checked": False, "check_evidence": None,
                      "source": f".{name}({arg_text.strip()[:50]})", "_applies": applies})
    return sinks


def gate(candidate: dict, target: dict) -> dict:
    c = _cfg()
    mech = candidate.get("mechanism", "")
    label = candidate.get("label") or mech
    pre = candidate.get("pre_decision", c["decisions"]["advance"])
    term = (candidate.get("term", "") or "").strip()
    base = {**FLAGS, "candidate_id": label, "target": {"file": target.get("file"), "function": target.get("name"),
            "lines": target.get("lines")}, "terms": [term] if term else [], "pre_dataflow_decision": pre}

    if mech not in c["processed_mechanisms"] or pre not in (c["decisions"]["advance"], c["decisions"]["review_only"]) or not term:
        return {**base, "post_dataflow_decision": pre, "native_eth_sinks": [], "term_flows": [],
                "decision_reason": "not a processed omitted/computed advance (pass-through)"}

    body = P47._strip(target.get("snippet", ""))
    derived, trace, _ = P47._derived_closure(body, term)
    sinks = _native_sinks(body, term, derived)
    applied = [s for s in sinks if s["_applies"]]

    # public sink rows (drop the internal _applies marker)
    pub = [{k: v for k, v in s.items() if k != "_applies"} for s in sinks]

    if applied:
        s0 = applied[0]
        # is the applied amount the term directly, or via a derived alias?
        via_alias = not _tok_ci(term, s0["amount_expression"])
        path = []
        if via_alias:
            alias = next((a for a in derived if _tok_ci(a, s0["amount_expression"])), None)
            if alias and alias in trace:
                path.append({"kind": "assignment", "source": trace[alias][:80]})
        path.append({"kind": "native_eth_value_arg", "source": s0["source"]})
        tf = [{"term": term, "path": path, "sink": {"kind": "native_eth_transfer", "source": s0["source"]},
               "applied": True}]
        return {**base, "post_dataflow_decision": c["decisions"]["abstain"], "native_eth_sinks": pub,
                "term_flows": tf,
                "decision_reason": f"computed '{term}' reaches native-ETH value transfer sink ({s0['sink_kind']}: {s0['amount_expression']})"}

    return {**base, "post_dataflow_decision": pre, "native_eth_sinks": pub,
            "term_flows": [{"term": term, "path": [], "sink": {"kind": "none", "source": None}, "applied": False}],
            "decision_reason": "no native-ETH value sink carries the term/alias; unchanged"}


# --------------------------------- self-test (11 required cases) ---------------------------------

def _t(name, snippet):
    return {"name": name, "snippet": snippet, "file": "src/C.sol", "lines": "1-9"}


def _g(term, body, mech="omitted_term", pre="ADVANCE", name="f"):
    return gate({"mechanism": mech, "term": term, "label": "omitted_" + term, "pre_decision": pre}, _t(name, body))


def _self_test():
    ok = True
    # 1 payable(to).call{value: fee}("") -> native sink, demote
    r1 = _g("fee", 'uint256 fee = x * r / d; (bool s,) = payable(owner()).call{value: fee}(""); require(s);', name="_sellQuote")
    c1 = r1["post_dataflow_decision"] == "ABSTAIN" and any(s["sink_kind"] == "native_call_value" for s in r1["native_eth_sinks"])
    print(f"  [{'PASS' if c1 else 'FAIL'}] payable.call{{value:fee}} -> demote ({r1['post_dataflow_decision']})"); ok &= c1
    # 2 to.call{value: amount}(data) -> native sink
    r2 = _g("amount", "uint256 amount = a - b; to.call{value: amount}(data);")
    c2 = r2["post_dataflow_decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c2 else 'FAIL'}] to.call{{value:amount}}(data) -> demote ({r2['post_dataflow_decision']})"); ok &= c2
    # 3 .transfer(amount) 1-arg native -> sink
    r3 = _g("amount", "uint256 amount = a / b; payable(to).transfer(amount);")
    c3 = r3["post_dataflow_decision"] == "ABSTAIN" and any(s["sink_kind"] == "native_transfer" for s in r3["native_eth_sinks"])
    print(f"  [{'PASS' if c3 else 'FAIL'}] .transfer(amount) 1-arg -> demote ({r3['post_dataflow_decision']})"); ok &= c3
    # 4 .send(amount) 1-arg native -> sink
    r4 = _g("amount", "uint256 amount = a + b; bool ok = payable(to).send(amount);")
    c4 = r4["post_dataflow_decision"] == "ABSTAIN" and any(s["sink_kind"] == "native_send" for s in r4["native_eth_sinks"])
    print(f"  [{'PASS' if c4 else 'FAIL'}] .send(amount) 1-arg -> demote ({r4['post_dataflow_decision']})"); ok &= c4
    # 5 call with NO value -> not a sink (and ERC20 2-arg transfer not native)
    r5 = _g("fee", "uint256 fee = x * r; token.transfer(to, fee); to.call(data);")
    c5 = r5["post_dataflow_decision"] == "ADVANCE" and not any(s["_applies"] if "_applies" in s else False for s in [])
    c5 = r5["post_dataflow_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c5 else 'FAIL'}] no-value call + 2-arg ERC20 transfer -> not native sink ({r5['post_dataflow_decision']})"); ok &= c5
    # 6 call{value: 0} -> not a candidate-term sink
    r6 = _g("fee", "uint256 fee = x * r; to.call{value: 0}(abi.encode(fee));")
    c6 = r6["post_dataflow_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c6 else 'FAIL'}] call{{value:0}} (fee only in calldata) -> not applied ({r6['post_dataflow_decision']})"); ok &= c6
    # 7 delegatecall/staticcall ignored
    r7 = _g("fee", "uint256 fee = x; impl.delegatecall(abi.encodeWithSelector(s, fee)); o.staticcall(d);")
    c7 = r7["post_dataflow_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c7 else 'FAIL'}] delegatecall/staticcall ignored ({r7['post_dataflow_decision']})"); ok &= c7
    # 8 alias: value = fee; call{value: value} -> demote via closure
    r8 = _g("fee", "uint256 fee = x * r; uint256 value = fee; payable(to).call{value: value}('');")
    c8 = r8["post_dataflow_decision"] == "ABSTAIN" and r8["term_flows"][0]["path"][0]["kind"] == "assignment"
    print(f"  [{'PASS' if c8 else 'FAIL'}] alias value=fee; call{{value:value}} -> demote ({r8['post_dataflow_decision']})"); ok &= c8
    # 9 require-checked call records check evidence
    r9 = _g("fee", 'uint256 fee = x; (bool success,) = payable(o).call{value: fee}(""); require(success, "fail");', name="_sellQuote")
    c9 = r9["post_dataflow_decision"] == "ABSTAIN" and any(s["checked"] for s in r9["native_eth_sinks"])
    print(f"  [{'PASS' if c9 else 'FAIL'}] require-checked call records check evidence ({[s['checked'] for s in r9['native_eth_sinks']]})"); ok &= c9
    # 10 SecondSwap-like event-only fee -> remains unapplied (no native sink)
    r10 = _g("referralFeeCost", "uint256 referralFeeCost = buyerFeeTotal - x; emit Purchased(a, b, referralFeeCost);", name="_handleTransfers")
    c10 = r10["post_dataflow_decision"] == "ADVANCE" and not r10["term_flows"][0]["applied"]
    print(f"  [{'PASS' if c10 else 'FAIL'}] event-only fee -> unchanged ({r10['post_dataflow_decision']})"); ok &= c10
    # 11 research-only / un-wired + no subject ids + never-promote
    cfg = CFG.read_text().lower()
    banned = ("reserve", "fixlib", "lambowin", "secondswap", "sentiment", "plaza", "traitforge", "dittoeth",
              "basin", "notional", "concrete", "ramses", "loopfi", "blackhole", "bakerfi", "sellquote", "referralfee")
    no_ids = not any(b in cfg for b in banned)
    r11 = _g("fee", "uint256 fee = x; emit E(fee);", pre="REVIEW_ONLY")  # no sink -> stays REVIEW_ONLY (never promote)
    flags_ok = FLAGS["research_only"] and not FLAGS["is_gate"] and not FLAGS["routes_in_production"] and _cfg().get("research_only") is True
    c11 = no_ids and flags_ok and r11["post_dataflow_decision"] == "REVIEW_ONLY"
    print(f"  [{'PASS' if c11 else 'FAIL'}] research-only/no-subject-ids/never-promote (no_ids={no_ids}, r11={r11['post_dataflow_decision']})"); ok &= c11
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p52)")


if __name__ == "__main__":
    raise SystemExit(main())
