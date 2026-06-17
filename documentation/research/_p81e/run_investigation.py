#!/usr/bin/env python3
"""P81e BLIND conversion eval driver (RESEARCH-ONLY). Encodes my KEY-BLIND source investigation of Vultisig 2024-06
(commit befb1b1170) into evidence dicts and runs arms A/B/C through the UNCHANGED post-P81f stack (deep_pass ->
hygiene -> severity_impact_gate). The answer key (-findings repo) is NOT opened until all bundles are frozen. Evidence
below is my genuine blind source reading (no web, no findings); machinery untouched."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import run as deep_run, FALSIFIERS
from investigation.hygiene_validate import validate as hygiene
from investigation.severity_impact_gate import gate as sev_gate
OUT = ROOT / "documentation" / "research" / "_p81e"
LEADS = {l["candidate_id"]: l for l in json.loads((OUT / "leads.json").read_text())["leads"]}
SF = {k: False for k in FALSIFIERS}


def ev(ledger, crit, exploit, impact=None):
    return {"context": {"source_available": True, "source_resolved": True, "reachability": "external"},
            "defense_ledger": ledger, "critical_defenses": crit, "exploit": exploit,
            "source_falsification": SF, "poc_needed": True, "impact_assessment": impact}


def X(reject, seq, inv, cat, mincond, mech):
    return {"rejection_case": reject, "transaction_sequence": seq, "broken_invariant": inv, "impact_category": cat,
            "minimum_profit_or_damage_condition": mincond, "attacker_profile": "EOA", "entrypoint": "see trigger",
            "source_evidence": "vultisig befb1b1170", "claimed_mechanism": mech}

# no-flaw-found rejection (rejection_case but no tx_seq/invariant -> deep_pass REJECT)
def NF(reason):
    return {"rejection_case": reason, "attacker_profile": "EOA", "entrypoint": "see trigger",
            "source_evidence": "vultisig befb1b1170", "claimed_mechanism": "none found"}

PRIV = {"access_control": {"classification": "blocks_candidate", "evidence": "onlyOwner/onlyProjectAdmin privileged"}}

INV = {
 # ---- conversion-expectation leads ----
 "ILOManager.claimRefund": dict(ledger={"access_control": {"classification": "partially_covers", "evidence": "onlyProjectAdmin + refundDeadline gate"}}, crit=[],
   exploit=NF("onlyProjectAdmin + require(refundDeadline < now); iterates pools calling claimProjectRefund; no flaw found blind in the manager-level refund aggregation")),
 "ILOPool.claimProjectRefund": dict(ledger={"access_control": {"classification": "partially_covers", "evidence": "OnlyManager + refundable() deadline gate"}}, crit=[],
   exploit=NF("OnlyManager + refundable(); returns SALE_TOKEN balance to projectAdmin; refund (SALE) and user refunds (RAISE) are different tokens so no contention; no flaw found blind")),
 "ILOPool.claimRefund": dict(ledger={"access_control": {"classification": "partially_covers", "evidence": "refundable() + isAuthorizedForToken"}}, crit=[],
   exploit=NF("refundable() requires !launchSucceeded && now>=refundDeadline; isAuthorizedForToken; refunds position.raiseAmount in RAISE_TOKEN, deletes/burns; looks consistent; no clear flaw found blind")),
 "ILOPool.launch": dict(ledger={"access_control": {"classification": "bypassed", "evidence": "ILOPool.launch is OnlyManager but ILOManager.launch is PERMISSIONLESS (no access control) -> effectively anyone can trigger after launchTime"},
                                "slippage_or_price_bound": {"classification": "bypassed", "evidence": "addLiquidity amount0Min/amount1Min set ONLY on the RAISE side; the SALE side Min stays 0"}}, crit=[],
   exploit=X("maybe Manager.launch is gated / maybe price check protects — but ILOManager.launch() has NO access modifier (only requires now>launchTime and pool price==initial), and in ILOPool.launch the addLiquidity Min is set on the RAISE side only; the SALE side amountMin=0",
             "anyone calls ILOManager.launch(pool) at launchTime; addLiquidity deploys with 0 min on the sale side; an attacker can move the pool within the allowed band / sandwich the liquidity add to skim value (sale-side has no slippage floor)",
             "launch liquidity deployment must enforce slippage on BOTH token sides",
             "protocol_value_loss_via_slippage", "permissionless launch + 0 min on sale side",
             "permissionless launch + missing sale-side slippage bound"),
   impact={"impact_class": "medium", "proven_magnitude": "conditional", "source_true": True, "material_consequence": ["protocol_loss", "denial_of_asset_movement"]}),
 "Multicall.multicall": dict(ledger={"external_dependency": {"classification": "unknown", "evidence": "delegatecall loop; whether a payable msg.value-consuming function is reachable to exploit value-reuse is unresolved blind"}}, crit=["external_dependency"],
   exploit=NF("Uniswap-style address(this).delegatecall loop, payable; classic risk is msg.value reuse across calls, but no clearly reachable msg.value-consuming payable function found (claim is payable but ignores msg.value; PeripheryPayments.receive only accepts WETH9). Uncertain -> needs context")),
 "Whitelist.receive": dict(ledger={"access_control": {"classification": "irrelevant", "evidence": "permissionless self-whitelist by design, gated by _isSelfWhitelistDisabled"},
                                   "external_dependency": {"classification": "unknown", "evidence": "whether self-whitelist meaningfully bypasses the intended controlled whitelist / index rate-limit is unresolved blind"}}, crit=["external_dependency"],
   exploit=NF("receive() self-whitelists then refunds msg.value (even 0); intended during self-whitelist period; index rate-limit via _allowedWhitelistIndex; no clear exploitable flaw found blind -> needs context")),
 "ILOPool.claim": dict(ledger={"access_control": {"classification": "irrelevant", "evidence": "isAuthorizedForToken — each user claims own position"},
                               "accounting_invariant": {"classification": "bypassed", "evidence": "pool.collect(this, max, max) collects the WHOLE shared position; only claimer's share goes to user, residual -> feeTaker"}}, crit=[],
   exploit=X("isAuthorizedForToken gates per-NFT — but the ILOPool holds ONE Uniswap position for ALL users; claim() does pool.collect(max,max) which collects every owed token/fee for the whole position, hands the claimer their computed amount0/amount1, and sends amountCollected-amount (which contains OTHER non-claiming users' fee/token shares) to feeTaker",
             "user A calls claim(tokenIdA); collect(max) pulls all accrued fees/owed tokens for the shared position; A receives only A's share; the remainder belonging to other un-claimed positions is transferred to feeTaker -> other users' funds siphoned",
             "a user's claim must not transfer other users' unclaimed liquidity/fees to the fee taker",
             "user_fund_loss", "more than one position exists and fees/tokens have accrued for non-claiming users",
             "shared-position collect(max) routes non-claimers' funds to feeTaker"),
   impact={"impact_class": "high", "proven_magnitude": "material", "source_true": True, "material_consequence": ["user_loss", "fund_loss"]}),
 # ---- control-expectation leads (privileged setters) ----
 "ILOManager.setPerformanceFee": dict(ledger=PRIV, crit=[], exploit=X("onlyOwner", "n/a", "n/a", "n/a", "n/a", "privileged setter")),
 "Whitelist.addBatchWhitelist": dict(ledger=PRIV, crit=[], exploit=X("onlyOwner", "n/a", "n/a", "n/a", "n/a", "privileged setter")),
 "ILOManager.setFeeTaker": dict(ledger=PRIV, crit=[], exploit=X("onlyOwner", "n/a", "n/a", "n/a", "n/a", "privileged setter")),
 "ILOManager.setPlatformFee": dict(ledger=PRIV, crit=[], exploit=X("onlyOwner", "n/a", "n/a", "n/a", "n/a", "privileged setter (no cap = centralization, but privileged)")),
 "ILOManager.setRefundDeadlineForProject": dict(ledger=PRIV, crit=[], exploit=X("onlyOwner", "n/a", "n/a", "n/a", "n/a", "privileged setter")),
}

results = {}
for cid, spec in INV.items():
    lead = LEADS[cid]
    A = deep_run(lead, ev({}, [], spec["exploit"], spec.get("impact")))
    B = deep_run(lead, ev(spec["ledger"], spec["crit"], spec["exploit"], spec.get("impact")))
    Cb = deep_run(lead, ev(spec["ledger"], spec["crit"], spec["exploit"], spec.get("impact")))
    ok, viol, rec = hygiene(Cb, None)
    c_after = Cb["final_decision"] if ok else rec
    sg = sev_gate(c_after, spec.get("impact"))
    c_final = sg.recommended_status
    d = OUT / cid.replace("/", "_"); d.mkdir(parents=True, exist_ok=True)
    for nm, b in (("A", A), ("B", B), ("C", Cb)):
        (d / f"{nm}_bundle.json").write_text(json.dumps(b, indent=2))
    (d / "severity_gate.json").write_text(json.dumps({"input": c_after, "impact": spec.get("impact"),
        "kept": sg.kept, "recommended_status": sg.recommended_status, "reason": sg.reason}, indent=2))
    results[cid] = {"role": lead.get("p81e_role_expectation"), "A": A["final_decision"], "B": B["final_decision"],
                    "C_deeppass": Cb["final_decision"], "C_final": c_final,
                    "claimed_mechanism": spec["exploit"].get("claimed_mechanism"),
                    "impact_class": (spec.get("impact") or {}).get("impact_class")}
(OUT / "arms_summary.json").write_text(json.dumps(results, indent=2))
print(f"{'lead':42}{'role':28}{'A':13}{'B':13}{'C_final':13}")
for cid, r in results.items():
    print(f"{cid:42}{r['role']:28}{r['A']:13}{r['B']:13}{r['C_final']:13}")
promos = [c for c, r in results.items() if r["C_final"] in ("POC_REQUIRED", "READY_FOR_HUMAN_REVIEW")]
print("\nC promotions (-> isolated key-blind adversarial):", promos)
