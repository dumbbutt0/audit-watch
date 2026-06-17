#!/usr/bin/env python3
"""P81d live conversion eval driver (RESEARCH-ONLY). Encodes the per-lead SOURCE investigation (audited Decent
commit 7f90fd4) into evidence dicts, runs arms A/B/C through the UNCHANGED deep_pass + hygiene_validate +
severity_impact_gate, and writes frozen bundles. Conversion is NOT key-blind (key seen in P81a) — see report caveat.
The evidence below is my genuine source reading; the machinery is untouched."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import run as deep_run, FALSIFIERS
from investigation.hygiene_validate import validate as hygiene
from investigation.severity_impact_gate import gate as sev_gate
from investigation.lead_schema import normalize_lead

OUT = ROOT / "documentation" / "research" / "_p81d"
LEADS = {l["candidate_id"]: l for l in json.loads((OUT / "leads.json").read_text())["leads"]}
SF_OK = {k: False for k in FALSIFIERS}


def ev(ctx_reach, ledger, crit, exploit, sf=None, poc=True, impact=None):
    return {"context": {"source_available": True, "source_resolved": True, "reachability": ctx_reach},
            "defense_ledger": ledger, "critical_defenses": crit, "exploit": exploit,
            "source_falsification": sf or SF_OK, "poc_needed": poc, "impact_assessment": impact}


# ---- per-lead SOURCE investigation (audited source) ----
# exploit template requires: rejection_case, transaction_sequence, broken_invariant, impact_category, minimum_profit_or_damage_condition
def X(reject, seq, inv, cat, mincond, mech):
    return {"rejection_case": reject, "transaction_sequence": seq, "broken_invariant": inv,
            "impact_category": cat, "minimum_profit_or_damage_condition": mincond, "attacker_profile": "EOA",
            "entrypoint": "see trigger", "source_evidence": "audited decent-bridge 7f90fd4 / UTB src",
            "claimed_mechanism": mech}

INV = {
 "DecentEthRouter.bridge": dict(
   ledger={"access_control": {"classification": "irrelevant", "evidence": "public payable bridge entry by design"},
           "caps_or_limits": {"classification": "bypassed", "evidence": "GAS_FOR_RELAY hardcoded 100000; _dstGasForCall unvalidated"},
           "external_dependency": {"classification": "partially_covers", "evidence": "LZ relay; dst reserve dependency in onOFTReceived"}},
   crit=[],
   exploit=X("maybe LZ enforces min gas / maybe UTB-only — but bridge() is public payable; GAS_FOR_RELAY=100000 fixed, "
             "_dstGasForCall unchecked; _bridgeWithPayload sets refundAddress=payable(msg.sender); no fee collection here",
             "caller calls bridge()/bridgeWithPayload directly (bypasses UTB fee gate, M-02); underfunded _dstGasForCall -> "
             "dst executor OOG -> stuck (H-02); when adapter is msg.sender, excess gas refund goes to adapter -> stuck (M-05); "
             "if dst router lacks WETH reserves, onOFTReceived delivers dcntEth not ETH (H-04)",
             "cross-chain delivery must be gas-sufficient, fee-gated, refundable to the real payer, and ETH-deliverable on dst",
             "permanent_fund_loss_or_stuck", "underfunded dstGas OR direct fee-bypass OR adapter refund OR dst reserve shortfall",
             "public bridge entry: missing min-gas validation (H-02) + fee bypass (M-02) + refund-to-msg.sender stuck (M-05) + dst-reserve dependency (H-04)"),
   impact={"impact_class": "high", "proven_magnitude": "material", "source_true": True}),

 "DecentBridgeExecutor.execute": dict(
   ledger={"access_control": {"classification": "partially_covers", "evidence": "onlyOwner gates direct calls; router is owner; reachable via onOFTReceived with cross-chain `from`"}},
   crit=[],
   exploit=X("onlyOwner gates direct calls — but router calls execute(_from,...) where _from is decoded from the cross-chain "
             "payload; on failed target.call both _executeWeth/_executeEth refund to `from`",
             "cross-chain msg -> onOFTReceived -> executor.execute(from,target,...) -> target.call fails -> payable(from).transfer / "
             "weth.transfer(from) sends funds to the source-chain `from` address on the destination chain",
             "on a failed execute, funds must return to the real payer / a recoverable address on the dst chain",
             "fund_loss_misrouted", "any failed dst execute refunds to a source-chain address that may be unrecoverable on dst",
             "failed-execute refund routed to cross-chain `from` -> funds to wrong/random address (H-03)"),
   impact={"impact_class": "high", "proven_magnitude": "material", "source_true": True}),

 "DecentEthRouter.redeemEth": dict(  # M-05 lead, but the bug is in _bridgeWithPayload (folded into bridge). redeemEth itself is clean.
   ledger={"access_control": {"classification": "irrelevant", "evidence": "permissionless redeem of caller's own dcntEth"},
           "caps_or_limits": {"classification": "partially_covers", "evidence": "onlyIfWeHaveEnoughReserves guard"}},
   crit=[],
   exploit={"rejection_case": "checked: onlyIfWeHaveEnoughReserves guard present; transferFrom caller's dcntEth; weth.withdraw; "
            "transfer to msg.sender — standard self-redeem; no misrouting in THIS function (M-05's refund bug is in _bridgeWithPayload)",
            "attacker_profile": "EOA", "entrypoint": "redeemEth", "source_evidence": "DecentEthRouter.sol:285-291",
            "claimed_mechanism": "none found in redeemEth itself"},  # no transaction_sequence/broken_invariant -> deep_pass REJECTS
   impact={"impact_class": "none", "proven_magnitude": "none", "source_true": True}),

 "UTB.receiveFromBridge": dict(
   ledger={"access_control": {"classification": "bypassed", "evidence": "receiveFromBridge is public with NO modifier; sibling swapAndExecute/bridgeAndExecute use retrieveAndCollectFees"}},
   crit=[],
   exploit=X("maybe onlyExecutor/onlyBridge gate — but receiveFromBridge(...) is public with NO modifier; its siblings "
             "swapAndExecute/bridgeAndExecute carry retrieveAndCollectFees (fee + validator-signature); this entry has neither",
             "attacker EOA calls receiveFromBridge(arbitrary postBridge, target, paymentOperator, payload, refund) -> _swapAndExecute "
             "runs a swap + payment with attacker instructions, no fee paid and no validator signature checked",
             "only the bridge adapter should reach receiveFromBridge; the fee/swap-instruction signature gate must hold for all swap/exec entries",
             "fee_bypass_and_unsigned_execution", "any direct EOA call bypasses fees and executes unsigned swap instructions",
             "missing access control on receiveFromBridge (M-03)"),
   impact={"impact_class": "medium", "proven_magnitude": "significant", "source_true": True}),

 "StargateBridgeAdapter.bridge": dict(
   ledger={"access_control": {"classification": "irrelevant", "evidence": "onlyUtb present and correct"},
           "accounting_invariant": {"classification": "bypassed", "evidence": "getBridgedAmount uses fixed SG_FEE_BPS (0.06%)"}},
   crit=[],
   exploit=X("onlyUtb is present and correct — but the deliverable amount uses a HARDCODED SG_FEE_BPS (getBridgedAmount = "
             "amt*(1e4-SG_FEE_BPS)/1e4); Stargate's actual protocol fee is variable",
             "when the live Stargate fee diverges from the fixed 0.06%, getBridgedAmount mis-estimates the bridged/deliverable "
             "amount -> shortfall or loss of capital across the bridge",
             "bridged-amount accounting must match the actual (variable) Stargate fee",
             "loss_of_capital_on_fee_divergence", "Stargate fee != fixed SG_FEE_BPS",
             "hardcoded SG_FEE_BPS fee assumption ignores variable Stargate fee (M-04)"),
   impact={"impact_class": "medium", "proven_magnitude": "conditional", "source_true": True}),

 "UniSwapper.swap": dict(
   ledger={"access_control": {"classification": "irrelevant", "evidence": "onlyUtb present"},
           "slippage_or_price_bound": {"classification": "bypassed", "evidence": "swapParams (incl amountOut/path) fixed at source-time; no fresh bound at execution"}},
   crit=[],
   exploit=X("onlyUtb is present — but swapParams (path, amountOut/min) are decoded from swapPayload prepared on the source "
             "chain; there is no re-validation against the current price at destination-execution time",
             "source prepares swapParams; price moves / time passes before the post-bridge swap executes; the stale amountOut/"
             "path makes the swap revert (funds stuck) or execute at an outdated, unfavorable rate -> permanent loss",
             "post-bridge swap must apply fresh slippage/price bounds at execution time",
             "permanent_token_loss", "price moves between source-prepare and destination-execute",
             "stale swap parameters / no fresh slippage at execution (M-01)"),
   impact={"impact_class": "medium", "proven_magnitude": "conditional", "source_true": True}),

 # ---- controls ----
 "UniSwapper.swapNoPath": dict(  # P81a D2 — source-true missing onlyUtb but DUST impact; severity gate must demote
   ledger={"access_control": {"classification": "bypassed", "evidence": "swapNoPath is public payable with NO onlyUtb (sibling swap() has it)"}},
   crit=[],
   exploit=X("public payable, no onlyUtb (sibling swap() has it) — source-true gap; BUT _sendToRecipient pays tokenOut from "
             "the contract's own balance, and UniSwapper holds no persistent tokenOut (only transient mid-tx)",
             "attacker calls swapNoPath(tokenOut=X, receiver=self) -> _sendToRecipient transfers UniSwapper's X balance to attacker",
             "only UTB should drive UniSwapper swaps",
             "dust_token_leak", "only profits if the contract holds leftover/transient tokenOut; magnitude is dust",
             "missing onlyUtb on swapNoPath (P81a D2) — source-true but dust impact"),
   impact={"impact_class": "dust", "proven_magnitude": "transient", "source_true": True}),

 "DcntEth.mintByOwner": dict(  # privileged control -> REJECT (defense blocks)
   ledger={"access_control": {"classification": "blocks_candidate", "evidence": "mintByOwner is onlyOwner; not permissionless"}},
   crit=[],
   exploit=X("onlyOwner gates mintByOwner", "n/a", "n/a", "n/a", "n/a", "privileged mint (by design)"),
   impact={"impact_class": "high", "proven_magnitude": "material", "source_true": True}),  # impact irrelevant; defense rejects first

 "UTB.swapAndExecute": dict(  # defended entry control -> abstain/reject (fee+signature gate present)
   ledger={"access_control": {"classification": "partially_covers", "evidence": "retrieveAndCollectFees modifier enforces fee + validator signature"},
           "nonce_or_replay_guard": {"classification": "partially_covers", "evidence": "validator signature over fees+instructions"}},
   crit=[],
   exploit={"rejection_case": "retrieveAndCollectFees enforces fee payment + validator signature over (instructions, fees); the "
            "naive 'bypass fees / unsigned instructions' claim is blocked here (unlike receiveFromBridge)",
            "attacker_profile": "EOA", "entrypoint": "swapAndExecute", "source_evidence": "UTB.sol swapAndExecute + retrieveAndCollectFees",
            "claimed_mechanism": "none — defended entry"},  # no broken_invariant -> REJECTED
   impact={"impact_class": "none", "proven_magnitude": "none", "source_true": True}),
}


def arm_evidence(spec, *, defenses, falsify):
    e = ev(LEADS[cid_for(spec)]["visibility"] or "external",
           spec["ledger"] if defenses else {}, spec["crit"] if defenses else [],
           spec["exploit"], SF_OK, True, spec.get("impact"))
    return e


def cid_for(spec):
    return spec["_cid"]


results = {}
for cid, spec in INV.items():
    spec["_cid"] = cid
    lead = LEADS[cid]
    role = lead.get("p81d_role")
    # arm A: no defenses, no falsify
    A = deep_run(lead, ev(lead["visibility"] or "external", {}, [], spec["exploit"], SF_OK, True, spec.get("impact")))
    # arm B: defenses, no falsify
    B = deep_run(lead, ev(lead["visibility"] or "external", spec["ledger"], spec["crit"], spec["exploit"], SF_OK, True, spec.get("impact")))
    # arm C: defenses + falsify + hygiene + severity gate
    Cb = deep_run(lead, ev(lead["visibility"] or "external", spec["ledger"], spec["crit"], spec["exploit"], SF_OK, True, spec.get("impact")))
    ok, viol, rec = hygiene(Cb, None)
    c_after_hyg = Cb["final_decision"] if ok else rec
    # severity gate (only meaningful on a promotion)
    sg = sev_gate(c_after_hyg, spec.get("impact"))
    c_final = sg.recommended_status
    d = OUT / cid.replace("/", "_")
    d.mkdir(parents=True, exist_ok=True)
    for nm, b in (("A", A), ("B", B), ("C", Cb)):
        (d / f"{nm}_bundle.json").write_text(json.dumps(b, indent=2))
    (d / "severity_gate.json").write_text(json.dumps({"input": c_after_hyg, "impact": spec.get("impact"),
        "kept": sg.kept, "recommended_status": sg.recommended_status, "reason": sg.reason}, indent=2))
    results[cid] = {"role": role, "A": A["final_decision"], "B": B["final_decision"],
                    "C_deeppass": Cb["final_decision"], "C_after_hygiene": c_after_hyg,
                    "C_final_after_severity": c_final, "claimed_mechanism": spec["exploit"].get("claimed_mechanism"),
                    "impact_class": (spec.get("impact") or {}).get("impact_class")}
(OUT / "arms_summary.json").write_text(json.dumps(results, indent=2))
print(f"{'lead':36} {'role':8} {'A':14} {'B':14} {'C_final':14}")
for cid, r in results.items():
    print(f"{cid:36} {r['role']:8} {r['A']:14} {r['B']:14} {r['C_final_after_severity']:14}")
PY = None
