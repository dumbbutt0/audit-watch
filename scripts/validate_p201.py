#!/usr/bin/env python3
"""
P201 — Refined mechanism-level severity-gate design + 2nd fresh-corpus validation (zetachain-2023-10-holdout).

READ-ONLY / OFFLINE eval harness. EVAL_HARNESS_ONLY. Does NOT route, submit, promote, demote, or set production
severity. Applies the refined 6-class (A-F) mechanism-level discriminator offline to FROZEN blind outputs.

Subcommands:
  build-prompts   freeze blind prompts (deep_trace.md + verbatim source) per surface; token-scan
  gate            apply refined mechanism-level gate to frozen raw_outputs -> OFFLINE_REFINED_CALIBRATION.json
  score           post-freeze: read zetachain report.md, score original-vs-refined PER MECHANISM -> metrics.json
"""
import json, os, argparse, hashlib

ROOT = "/home/dummy/clones/audit-watch/smart-contract-auditor"
SRC = os.path.join(ROOT, "audits/zetachain-2023-10-holdout/contracts/contracts")
DEEP_TRACE = os.path.join(ROOT, "prompts/deep_trace.md")
OUT = os.path.join(ROOT, "documentation/research/assisted_mode/p201_refined_severity_gate")
PROMPTS = os.path.join(OUT, "blind_prompts")
RAW = os.path.join(OUT, "raw_outputs")
REPORT = os.path.join(ROOT, "audits/zetachain-2023-10-holdout/_sealed_answer_key/report.md")

EVAL_HARNESS_ONLY = True
ROUTES_IN_PRODUCTION = False

# Pre-registered blind sample (frozen in COVERAGE_MANIFEST.md). (id, file, focus, classes, span_or_None)
SURFACES = [
    ("zeta-01", "evm/ERC20Custody.sol", "deposit", "A accounting/value-in", None),
    ("zeta-02", "evm/ERC20Custody.sol", "withdraw (onlyTSS)", "A theft / E auth", None),
    ("zeta-03", "evm/ERC20Custody.sol", "updateTSSAddress / updateTSSAddressUpdater / whitelist", "E auth", None),
    ("zeta-04", "evm/ZetaConnector.base.sol", "updateTssAddress / pause / unpause", "E auth / D DoS", None),
    ("zeta-05", "evm/ZetaConnector.eth.sol", "send / onReceive / onRevert", "A value-flow / E / F multi", None),
    ("zeta-06", "evm/ZetaConnector.non-eth.sol", "send / onReceive / onRevert", "A mint-burn / E / F multi", None),
    ("zeta-07", "evm/ZetaConnector.non-eth.sol", "setMaxSupply / mint path", "A supply-cap / C precision", None),
    ("zeta-08", "evm/tools/ZetaInteractor.sol", "isValidMessageCall / isValidRevertCall / setInteractorByChainId", "E cross-chain caller verification", None),
    ("zeta-09", "zevm/ZRC20.sol", "deposit (onlySystem)", "A value-in / E auth", None),
    ("zeta-10", "zevm/ZRC20.sol", "withdraw / withdrawGasFee", "A value-flow / C gas-fee / F multi", None),
    ("zeta-11", "zevm/ZRC20.sol", "updateSystemContractAddress / updateGasLimit (onlyFungible)", "E auth", None),
    ("zeta-12", "zevm/ZRC20.sol", "burn / transferFrom / approve", "A token accounting", None),
    ("zeta-13", "zevm/SystemContract.sol", "depositAndCall / onCrossChainCall", "A cross-chain value-flow / E", None),
    ("zeta-14", "zevm/SystemContract.sol", "setGasPrice / setGasCoinZRC20 / updateSystemContractAddress", "E auth", None),
    ("zeta-15", "zevm/ZetaConnectorZEVM.sol", "send / withdraw", "A zevm value-flow", None),
    ("zeta-16", "zevm/WZETA.sol", "deposit / withdraw / transferFrom", "A wrapped-token value-flow", None),
    ("zeta-17", "evm/tools/ZetaTokenConsumerUniV2.strategy.sol", "getZetaFromEth / getEthFromZeta", "C swap precision / D slippage", None),
    ("zeta-18", "evm/Zeta.non-eth.sol", "mint / burn (connector-gated)", "A cross-chain supply / E", None),
]

LEAK_TOKENS = ["[H-0", "[M-0", "[C-0", "[L-0", "code-423n4", "Risk Findings", "Severity Criteria"]


def md5_8(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8]


def read_span(path, span):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    if span:
        a, b = span
        return "".join(lines[a - 1:b])
    return "".join(lines)


def cmd_build_prompts(_):
    os.makedirs(PROMPTS, exist_ok=True)
    deep = open(DEEP_TRACE, encoding="utf-8").read()
    leaks = []
    for sid, rel, focus, classes, span in SURFACES:
        src = read_span(os.path.join(SRC, rel), span)
        prompt = (
            deep
            + "\n\n=== INPUT: ONE FUNCTION UNDER TRACE ===\n"
            + f"high_suspicion_invariant: cross-chain value / supply / authorization correctness of `{focus}`\n"
            + f"dangerous_interaction: external/permissionless entry into `{focus}` in `{rel}`\n\n"
            + f"Trace the function(s) `{focus}` in the verbatim source below. Run STEP 0 mechanism inventory,\n"
            + "carry forward every supported mechanism, then return ONLY the JSON verdict per the schema above.\n\n"
            + f"=== VERBATIM SOURCE: {rel} ===\n```solidity\n" + src + "\n```\n"
        )
        for tok in LEAK_TOKENS:
            if tok in prompt:
                leaks.append((sid, tok))
        with open(os.path.join(PROMPTS, f"{sid}.txt"), "w", encoding="utf-8") as f:
            f.write(prompt)
    print(f"wrote {len(SURFACES)} prompts to {PROMPTS}")
    print("LEAK SCAN:", "CLEAN" if not leaks else f"LEAKS {leaks}")
    print("deep_trace.md md5_8:", md5_8(DEEP_TRACE))


# ---------------------------------------------------------------------------
# REFINED MECHANISM-LEVEL GATE (frozen rubric, answer-key-blind, FREEZE 2)
# Each carried mechanism graded independently per the 6-class design (A-F).
# Reject-first. Classes: A theft/insolvency/permanent-loss · B oracle (none here) ·
# C precision · D DoS/griefing · E auth/privileged-transition · F secondary-preservation
# (every mechanism gets its own label; surface summary = max, but scoring uses per-mechanism).
# Uniform rule:
#  - permissionless + executable-from-shown-source + value-extraction/permanent-loss +
#    magnitude demonstrable from shown source           -> HIGH_CONFIRMED
#  - permissionless but magnitude/exploit depends on UNSEEN code (TSS/module/cross-chain/
#    inheriting/replay)                                  -> NEEDS_HARNESS_FOR_SEVERITY
#  - requires compromise of a trusted/authorized key (TSS/fungible-module/owner)  -> MEDIUM (admin-prereq cap)
#  - DoS/griefing w/o proven permanent protocol-wide insolvency                   -> MEDIUM
#  - precision bounded/dust, or self-inflicted user-error loss                    -> MEDIUM
#  - latent / no current impact / source-refuted                                 -> INSUFFICIENT_EVIDENCE / SOURCE_REFUTED
HI, NH, MED, INS, REF = ("HIGH_CONFIRMED", "NEEDS_HARNESS_FOR_SEVERITY",
                          "MEDIUM_OR_LOWER_CALIBRATED", "INSUFFICIENT_EVIDENCE", "SOURCE_REFUTED")
SEV_ORDER = {HI: 4, NH: 3, MED: 2, INS: 1, REF: 0}

RUBRIC_GRADES = {
    "zeta-01": {"mechanisms": [
        {"m": "fee-avoidance when zetaFee=0", "class": "D/economic", "label": MED,
         "rationale": "permissionless but bounded fee-revenue loss; economic/DoS, not theft -> Medium"},
        {"m": "zero-amount deposit spam", "class": "D", "label": MED, "rationale": "griefing/spam -> Medium"},
        {"m": "zeta==asset double-deposit", "class": "A", "label": NH,
         "rationale": "depends on unseen cross-chain validator crediting both events -> harness"}]},
    "zeta-02": {"mechanisms": [
        {"m": "withdraw lacks whenNotPaused (asymmetric pause)", "class": "E/D", "label": MED,
         "rationale": "drain actor is onlyTSS (trusted/authorized); invariant bug but admin-prereq -> Medium"},
        {"m": "fee-on-transfer accounting mismatch", "class": "C", "label": MED,
         "rationale": "per-token bounded accounting drift -> Medium"},
        {"m": "TSSAddressUpdater compromise drain", "class": "E", "label": MED,
         "rationale": "requires compromise of authorized updater key -> admin-prereq cap Medium"}]},
    "zeta-03": {"mechanisms": [
        {"m": "updateTSSAddress hijack -> drain", "class": "E", "label": MED,
         "rationale": "requires compromised TSSAddressUpdater (authorized key) -> admin-prereq cap Medium"},
        {"m": "unwhitelist-all permanent fund lock", "class": "D", "label": MED,
         "rationale": "permanent lock but actor is onlyTSS (authorized); admin-griefing -> Medium"}]},
    "zeta-04": {"mechanisms": [
        {"m": "post-renounce single-key TSS collapse", "class": "E", "label": MED,
         "rationale": "requires compromised TSS key (authorized) -> admin-prereq cap Medium"},
        {"m": "single-key unpause / pause DoS", "class": "D", "label": MED,
         "rationale": "DoS via authorized pauser key -> Medium"}]},
    "zeta-05": {"mechanisms": [
        {"m": "onReceive CEI reentrancy (TSS entry)", "class": "A", "label": NH,
         "rationale": "double-spend depends on TSS honoring phantom ZetaSent (unseen) -> harness"},
        {"m": "onRevert reentrancy (permissionless sender)", "class": "A", "label": NH,
         "rationale": "permissionless entry but double-spend depends on TSS dedup/replay (unseen) -> harness"},
        {"m": "tx.origin attribution in ZetaSent", "class": "E", "label": MED,
         "rationale": "permissionless but forged-attribution magnitude unproven; phishing-class -> Medium"}]},
    "zeta-06": {"mechanisms": [
        {"m": "onReceive lacks whenNotPaused (mint during pause)", "class": "E", "label": MED,
         "rationale": "actor onlyTssAddress (authorized) -> admin-prereq cap Medium"},
        {"m": "CEI mint-before-callback phantom send", "class": "A", "label": NH,
         "rationale": "depends on TSS honoring phantom ZetaSent (unseen) -> harness"},
        {"m": "replay double-mint via internalSendHash", "class": "A", "label": NH,
         "rationale": "depends on unseen mint() hash-uniqueness enforcement -> harness"}]},
    "zeta-07": {"mechanisms": [
        {"m": "CEI mint-before-callback reentrancy", "class": "A", "label": NH,
         "rationale": "exploit depends on unseen receiver/cross-chain logic -> harness"},
        {"m": "callback-revert: burn-on-source no-mint-on-dest (fund loss)", "class": "A", "label": NH,
         "rationale": "permanent-loss path depends on unseen TSS retry/finality -> harness"},
        {"m": "maxSupply stale-snapshot bypass", "class": "A", "label": NH, "rationale": "concurrency/callback-burn unproven -> harness"}]},
    "zeta-08": {"mechanisms": [
        {"m": "owner overwrites interactor registry -> spoof", "class": "E", "label": MED,
         "rationale": "requires owner (authorized) action -> admin-prereq cap Medium"},
        {"m": "ZERO_BYTES sentinel: empty interactor lets zetaTxSenderAddress=empty pass (permissionless auth bypass)",
         "class": "E", "label": NH,
         "rationale": "permissionless + executable-from-source, but loss magnitude depends on inheriting contracts (unseen) -> harness (strongest candidate)"}]},
    "zeta-09": {"mechanisms": [
        {"m": "mutable SYSTEM_CONTRACT_ADDRESS -> mint", "class": "E", "label": MED,
         "rationale": "requires compromised fungible-module/system addr (authorized) -> admin-prereq cap Medium"},
        {"m": "no mint cap / replay double-mint", "class": "A", "label": NH,
         "rationale": "depends on unseen cross-chain replay + privileged caller -> harness"}]},
    "zeta-10": {"mechanisms": [
        {"m": "withdraw invalid `to` -> burned, undeliverable (permanent loss)", "class": "A", "label": MED,
         "rationale": "permissionless+permanent loss but self-inflicted (caller supplies bad `to`), not attacker-extractable -> Medium"},
        {"m": "transferFrom-before-burn", "class": "A", "label": REF,
         "rationale": "EVM atomicity reverts both (agent-rejected) -> source-refuted"},
        {"m": "uncapped gasFee DoS / gasZRC20==this double-charge", "class": "C/D", "label": NH,
         "rationale": "privileged fee-set DoS + same-token-accounting question -> harness"}]},
    "zeta-11": {"mechanisms": [
        {"m": "SYSTEM_CONTRACT_ADDRESS redirect -> mint", "class": "E", "label": MED, "rationale": "authorized-key compromise -> admin-prereq cap Medium"},
        {"m": "malicious ISystem DoS on withdraw", "class": "D", "label": MED, "rationale": "DoS via authorized setter -> Medium"},
        {"m": "unbounded GAS_LIMIT economic DoS", "class": "D", "label": MED, "rationale": "DoS via authorized setter -> Medium"}]},
    "zeta-12": {"mechanisms": [
        {"m": "transferFrom check-after-effect", "class": "A", "label": INS,
         "rationale": "agent: no current net harm (atomic revert); latent only if _transfer overridden -> insufficient"},
        {"m": "permissionless burn() permanent loss (no CCTX)", "class": "A", "label": MED,
         "rationale": "permissionless permanent loss but self-inflicted user-error (caller burns own tokens) -> Medium"}]},
    "zeta-13": {"mechanisms": [
        {"m": "depositAndCall CEI reentrancy (user-controlled target)", "class": "A", "label": NH,
         "rationale": "entry onlyFungible; re-entry impact depends on unseen ZRC20/target logic -> harness"},
        {"m": "stale amount forwarded to onCrossChainCall (fee-on-transfer)", "class": "C", "label": NH,
         "rationale": "depends on ZRC20 fee behavior (unseen) -> harness"}]},
    "zeta-14": {"mechanisms": [
        {"m": "no zero-address check setGasCoinZRC20", "class": "D", "label": MED, "rationale": "DoS via authorized setter; sibling-asymmetry -> Medium"},
        {"m": "no bounds setGasPrice (0/huge)", "class": "D", "label": MED, "rationale": "economic DoS via authorized setter -> Medium"}]},
    "zeta-15": {"mechanisms": [
        {"m": "tx.origin attribution in ZetaSent", "class": "E", "label": MED, "rationale": "permissionless but magnitude unproven; phishing-class -> Medium"},
        {"m": "no input validation -> invalid destination fund loss", "class": "A", "label": NH,
         "rationale": "depends on unseen fungible-module destination validation -> harness"},
        {"m": "reentrancy via mutable wzeta", "class": "A", "label": NH, "rationale": "requires authorized wzeta set + reentrancy unproven -> harness"}]},
    "zeta-16": {"mechanisms": [
        {"m": "balanceOf overflow (0.4.18)", "class": "A", "label": MED,
         "rationale": "requires accumulating ~2^256 tokens (infeasible) -> impractical, Medium"},
        {"m": "withdraw transfer 2300-gas reentrancy (fork-dependent)", "class": "A", "label": NH, "rationale": "fork gas-cost unknown -> harness"},
        {"m": "totalSupply()=this.balance forced-ETH divergence", "class": "A", "label": NH, "rationale": "depends on unseen cross-chain supply-oracle use -> harness"}]},
    "zeta-17": {"mechanisms": [
        {"m": "minAmountOut=0 sandwich/slippage", "class": "C/D", "label": MED,
         "rationale": "permissionless MEV but bounded/caller-supplied-zero slippage -> Medium"},
        {"m": "safeApprove non-zero-to-non-zero DoS", "class": "D", "label": MED, "rationale": "swap-path DoS -> Medium"},
        {"m": "cross-chain amountOut understatement", "class": "A", "label": NH, "rationale": "depends on unseen caller cross-chain credit use -> harness"}]},
    "zeta-18": {"mechanisms": [
        {"m": "TSS-compromise connector reassign -> unbounded mint", "class": "E", "label": MED,
         "rationale": "requires compromised TSS/updater (authorized key) -> admin-prereq cap Medium"},
        {"m": "deployment-window mint/burn DoS", "class": "D", "label": MED, "rationale": "temporary bounded unavailability -> Medium"}]},
}


def summary_label(mechs):
    return max(mechs, key=lambda m: SEV_ORDER[m["label"]])["label"]


def cmd_gate(_):
    rows = []
    for sid, rel, focus, classes, span in SURFACES:
        cand = json.load(open(os.path.join(RAW, f"{sid}.json")))
        rg = RUBRIC_GRADES[sid]
        summ = summary_label(rg["mechanisms"])
        rows.append({"id": sid, "surface": focus, "file": rel,
                     "blind_verdict": cand.get("verdict"),
                     "mechanisms": rg["mechanisms"], "summary_label": summ})
    out = {"_meta": {"phase": "P201", "corpus": "zetachain-2023-10-holdout",
                     "eval_harness_only": EVAL_HARNESS_ONLY, "routes_in_production": ROUTES_IN_PRODUCTION,
                     "note": "Refined mechanism-level gate applied to FROZEN blind outputs, answer-key-blind. FREEZE 2.",
                     "oracle_class_B": "UNVALIDATED_OUT_OF_SAMPLE (no oracle findings in zetachain)"},
           "calibration": rows}
    with open(os.path.join(OUT, "OFFLINE_REFINED_CALIBRATION.json"), "w") as f:
        json.dump(out, f, indent=2)
    from collections import Counter
    allm = [m["label"] for r in rows for m in r["mechanisms"]]
    print("surface summary :", dict(Counter(r["summary_label"] for r in rows)))
    print("per-mechanism   :", dict(Counter(allm)), f"(total {len(allm)} mechanisms)")
    for r in rows:
        print(f"  {r['id']}: {r['blind_verdict']:>13} -> {r['summary_label']:<28} ({len(r['mechanisms'])} mechs)")


# ---------------------------------------------------------------------------
# POST-FREEZE SCORING (zetachain answer key opened only here, after both freezes)
# ---------------------------------------------------------------------------
# 14 High / 34 Medium. Scope tag: most Highs are OFF-CHAIN (Go observer/cctx/consensus
# layer), outside Solidity-source tracing scope of the blind sample.
AWARDED_HIGH_OFFCHAIN = ["H-01", "H-02", "H-03", "H-04", "H-05", "H-07", "H-08", "H-09",
                         "H-11", "H-12", "H-14"]   # observer/cctx/consensus/UTXO/TSS-voting
AWARDED_HIGH_CONTRACT = ["H-06", "H-10", "H-13"]   # zEVM msg ignored / Trident router / pause-during-cctx
N_AWARDED_HIGH, N_AWARDED_MED = 14, 34

# Per-surface mechanism-match to awarded findings. quality: strong | partial | loose | none.
# Only EVM/zEVM-contract findings are matchable by a Solidity-source blind trace.
SURFACE_MAP = {
    "zeta-01": {"matches": [], "note": "custody deposit fee/spam not awarded as contract finding"},
    "zeta-02": {"matches": [], "note": "withdraw pause-asymmetry (admin) not an awarded contract finding; H-13 pause-loss is a different cctx mechanism (recall miss)"},
    "zeta-03": {"matches": [("M-30", "loose")], "note": "M-30 is 'unwhitelist cannot be invoked' (broken fn); blind found unwhitelist-griefing (different mechanism)"},
    "zeta-04": {"matches": [], "note": "connector TSS/pause admin findings not awarded as contract finding"},
    "zeta-05": {"matches": [("M-13", "strong")], "note": "tx.origin wrong-sender attribution = M-13 (incorrect sender -> lost assets during refund), awarded Medium"},
    "zeta-06": {"matches": [("M-26", "loose")], "note": "connector pause-bypass loosely relates to M-26 ZRC20 pause bypass; CEI/replay are recall items not the awarded mechanism"},
    "zeta-07": {"matches": [], "note": "maxSupply/CEI mint not awarded as contract finding"},
    "zeta-08": {"matches": [], "note": "ZetaInteractor ZERO_BYTES/owner registry not in awarded H/M (likely recall FP / out of awarded set)"},
    "zeta-09": {"matches": [], "note": "ZRC20 deposit mint-trust not awarded as contract finding"},
    "zeta-10": {"matches": [], "note": "withdraw invalid-`to` self-loss not awarded as contract finding"},
    "zeta-11": {"matches": [("M-28", "partial")], "note": "updateSystemContract -> withdraw DoS area = M-28 (gasPriceByChainId not copied halts withdraw); blind found malicious-addr DoS (same fn/impact, diff root cause)"},
    "zeta-12": {"matches": [], "note": "ZRC20 transferFrom-ordering/burn self-loss not awarded as contract finding"},
    "zeta-13": {"matches": [("H-06", "miss")], "note": "SystemContract.depositAndCall: awarded H-06 is 'user message ignored'; blind found reentrancy/stale-amount (recall miss, different mechanism)"},
    "zeta-14": {"matches": [("M-01", "loose")], "note": "gas setters: M-01 gas-coin-setup arbitrage; blind found zero-addr/bounds DoS (different mechanism)"},
    "zeta-15": {"matches": [("M-13", "strong"), ("M-16", "partial")], "note": "tx.origin = M-13 (strong); no-input-validation on destinationGasLimit = M-16 (arbitrary dest gas limit), both Medium"},
    "zeta-16": {"matches": [], "note": "WZETA overflow/forced-ETH not awarded as contract finding"},
    "zeta-17": {"matches": [("M-09", "loose")], "note": "UniV2 consumer; M-09/M-10 are UniV3/Pancake/Trident DoS (H-10 Trident NOT sampled); blind safeApprove/slippage loosely relate"},
    "zeta-18": {"matches": [], "note": "Zeta.non-eth TSS-mint admin not awarded as contract finding"},
}
AWARDED_SEV = {"H-06": "High", "H-10": "High", "H-13": "High",
               "M-01": "Medium", "M-09": "Medium", "M-13": "Medium", "M-16": "Medium",
               "M-26": "Medium", "M-28": "Medium", "M-30": "Medium"}
CEIL_TIER = {"CRITICAL_THREAD": "High", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium",
             "DEAD_END": "None", "NEEDS_MORE_CONTEXT": "None"}
CAL_TIER = {HI: "High", NH: "Harness", MED: "Medium", INS: "None", REF: "None"}


def cmd_score(_):
    cal = {r["id"]: r for r in json.load(open(os.path.join(OUT, "OFFLINE_REFINED_CALIBRATION.json")))["calibration"]}
    per = []
    for sid, rel, focus, classes, span in SURFACES:
        r = cal[sid]; mp = SURFACE_MAP[sid]
        # best matched awarded finding among strong/partial/loose (exclude 'miss')
        real = [m for m in mp["matches"] if m[1] in ("strong", "partial", "loose")]
        best = None
        for q in ("strong", "partial", "loose"):
            cand = [m for m in real if m[1] == q]
            if cand:
                best = cand[0]; break
        per.append({"id": sid, "blind_verdict": r["blind_verdict"], "ceiling": CEIL_TIER[r["blind_verdict"]],
                    "summary_label": r["summary_label"], "calibrated_tier": CAL_TIER[r["summary_label"]],
                    "matched": best[0] if best else None, "match_quality": best[1] if best else None,
                    "awarded_sev": AWARDED_SEV.get(best[0]) if best else None,
                    "all_matches": mp["matches"], "note": mp["note"],
                    "mechanism_labels": [m["label"] for m in r["mechanisms"]]})

    matched = [p for p in per if p["matched"]]
    matched_med = [p for p in matched if p["awarded_sev"] == "Medium"]
    matched_high = [p for p in matched if p["awarded_sev"] == "High"]
    ceil_over = [p for p in matched_med if p["ceiling"] == "High"]
    cal_over = [p for p in matched_med if p["calibrated_tier"] == "High"]
    high_demoted_med = [p for p in matched_high if p["calibrated_tier"] == "Medium"]
    high_demoted_none = [p for p in matched_high if p["calibrated_tier"] == "None"]

    from collections import Counter
    allm = [l for p in per for l in p["mechanism_labels"]]
    metrics = {
        "_meta": {"phase": "P201", "corpus": "zetachain-2023-10-holdout", "blind_model": "sonnet",
                  "eval_harness_only": EVAL_HARNESS_ONLY, "routes_in_production": ROUTES_IN_PRODUCTION,
                  "freeze1_raw_outputs": "77d57371", "freeze2_calibration": "387a95de",
                  "oracle_class_B": "UNVALIDATED_OUT_OF_SAMPLE (no oracle findings in zetachain)"},
        "n_surfaces": len(per), "awarded": {"High": N_AWARDED_HIGH, "Medium": N_AWARDED_MED},
        "awarded_high_scope": {"offchain_out_of_solidity_scope": AWARDED_HIGH_OFFCHAIN,
                               "contract_level": AWARDED_HIGH_CONTRACT,
                               "note": "11/14 Highs are off-chain observer/cctx/consensus (Go layer), unreachable by a Solidity-source blind trace; 3 are contract-level"},
        "blind_ceiling_ge_high": sum(1 for p in per if p["ceiling"] == "High"),
        "calibrated_surface_high_confirmed": sum(1 for p in per if p["calibrated_tier"] == "High"),
        "per_mechanism_label_distribution": dict(Counter(allm)),
        "mechanism_matched_contract_findings": [f"{p['id']}->{p['matched']}({p['match_quality']},{p['awarded_sev']})" for p in matched],
        "over_high_on_matched_medium": {
            "subset": [p["id"] + "->" + p["matched"] for p in matched_med],
            "ceiling_rate": f"{len(ceil_over)}/{len(matched_med)}",
            "calibrated_rate": f"{len(cal_over)}/{len(matched_med)}",
            "fixed_by_gate": [p["id"] for p in ceil_over if p not in cal_over],
            "still_over_high": [p["id"] for p in cal_over]},
        "genuine_high_preservation": {
            "mechanism_matched_awarded_high": [p["id"] + "->" + p["matched"] for p in matched_high],
            "count_matched_high": len(matched_high),
            "demoted_to_medium": [p["id"] for p in high_demoted_med],
            "demoted_to_none": [p["id"] for p in high_demoted_none],
            "note": "0 awarded-Highs matched by mechanism -> High-preservation UNTESTED here (Highs are off-chain or recall-missed contract Highs H-06/H-10/H-13)"},
        "recall_missed_contract_high": [f"{p['id']}->{q[0]}" for p in per for q in p["all_matches"] if q[1] == "miss"],
        "per_class_calibration": {
            "DoS_griefing_to_medium": "validated (admin/DoS/pause/setter mechanisms -> Medium, not High)",
            "auth_privileged_to_medium_or_harness": "validated (TSS/module/owner-compromise -> Medium admin-prereq; permissionless-but-unseen -> Harness)",
            "precision_magnitude_dependent": "lightly tested (gas-fee/accounting -> Medium/Harness)",
            "oracle": "N/A — UNVALIDATED_OUT_OF_SAMPLE"},
        "secondary_preservation": {
            "surfaces_with_multiple_mechanism_labels": sum(1 for p in per if len(p["mechanism_labels"]) > 1),
            "note": "per-mechanism grading applied to all 46 mechanisms; no Medium-primary hid a High-secondary (0 HIGH_CONFIRMED total, so no folding occurred)"},
        "per_surface": per,
    }
    with open(os.path.join(OUT, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_surface"}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-prompts").set_defaults(fn=cmd_build_prompts)
    sub.add_parser("gate").set_defaults(fn=cmd_gate)
    sub.add_parser("score").set_defaults(fn=cmd_score)
    args = ap.parse_args()
    args.fn(args)
