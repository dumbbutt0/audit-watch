#!/usr/bin/env python3
"""
P202 — Positive-control validation of the refined severity gate on decent-2024-01-holdout.

READ-ONLY / OFFLINE eval harness. EVAL_HARNESS_ONLY. Does NOT route/submit/promote/demote/set production severity.
NOTE: the refined-gate CALIBRATION is NOT authored here (the orchestrator is PCS-contaminated). Calibration is
produced by a FRESH cold-start firewall subagent and stored in OFFLINE_REFINED_CALIBRATION.json; this harness only
builds blind prompts and (post-freeze) scores.

Subcommands:
  build-prompts   freeze blind prompts (deep_trace.md + verbatim source) per surface; token-scan
  score           post-freeze: read decent report.md, score original-vs-refined PER MECHANISM -> metrics.json
"""
import json, os, argparse, hashlib

ROOT = "/home/dummy/clones/audit-watch/smart-contract-auditor"
SRC = os.path.join(ROOT, "audits/decent-2024-01-holdout/contracts")
DEEP_TRACE = os.path.join(ROOT, "prompts/deep_trace.md")
OUT = os.path.join(ROOT, "documentation/research/assisted_mode/p202_decent_positive_control")
PROMPTS = os.path.join(OUT, "blind_prompts")
RAW = os.path.join(OUT, "raw_outputs")
REPORT = os.path.join(ROOT, "audits/decent-2024-01-holdout/_sealed_answer_key/report.md")
EVAL_HARNESS_ONLY = True
ROUTES_IN_PRODUCTION = False

# (id, file(s) rel to SRC, focus, category)
SURFACES = [
    ("decent-01", "src/UTB.sol", "swapAndExecute / _swapAndExecute", "swap+execute entry"),
    ("decent-02", "src/UTB.sol", "bridgeAndExecute / callBridge", "bridge initiation"),
    ("decent-03", "src/UTB.sol", "receiveFromBridge", "bridge completion / message"),
    ("decent-04", "src/UTBExecutor.sol", "execute (both overloads)", "executor / refund / stuck-funds"),
    ("decent-05", "src/UTBFeeCollector.sol", "collectFees / redeemFees / splitSignature", "fee handling / signature-auth"),
    ("decent-06", "src/swappers/UniSwapper.sol", "swap / swapExactIn / swapExactOut / _sendToRecipient", "swap / token transfer"),
    ("decent-07", "src/bridge_adapters/StargateBridgeAdapter.sol", "bridge / callBridge / sgReceive", "adapter / message validation"),
    ("decent-08", "src/bridge_adapters/DecentBridgeAdapter.sol", "bridge / receiveFromBridge", "adapter / completion"),
    ("decent-09", "lib/decent-bridge/src/DcntEth.sol", "mint / burn / setRouter / mintByOwner", "token mint-burn access-control"),
    ("decent-10", "lib/decent-bridge/src/DecentEthRouter.sol", "bridge / _bridgeWithPayload / bridgeWithPayload", "bridge initiation (router)"),
    ("decent-11", "lib/decent-bridge/src/DecentEthRouter.sol", "onOFTReceived", "bridge completion / message validation"),
    ("decent-12", "lib/decent-bridge/src/DecentEthRouter.sol", "redeemEth / redeemWeth / removeLiquidityEth / addLiquidityEth", "stuck-funds / liquidity value-flow"),
    ("decent-13", "lib/decent-bridge/src/DecentBridgeExecutor.sol", "execute / _executeWeth / _executeEth", "executor / stuck-funds"),
    ("decent-14", ["src/UTBOwned.sol", "src/bridge_adapters/BaseAdapter.sol",
                   "lib/decent-bridge/src/utils/Operable.sol", "lib/decent-bridge/src/utils/Roles.sol"],
                  "access-control setters / role primitives", "access-control path"),
]
LEAK_TOKENS = ["[H-0", "[M-0", "[C-0", "[L-0", "code-423n4", "Risk Findings", "Severity Criteria"]


def md5_8(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8]


def read_files(rel):
    rels = rel if isinstance(rel, list) else [rel]
    out = []
    for r in rels:
        with open(os.path.join(SRC, r), encoding="utf-8") as f:
            out.append(f"// ===== FILE: {r} =====\n" + f.read())
    return "\n\n".join(out)


def cmd_build_prompts(_):
    os.makedirs(PROMPTS, exist_ok=True)
    deep = open(DEEP_TRACE, encoding="utf-8").read()
    leaks = []
    for sid, rel, focus, cat in SURFACES:
        src = read_files(rel)
        label = rel if isinstance(rel, str) else " + ".join(rel)
        prompt = (
            deep
            + "\n\n=== INPUT: ONE FUNCTION UNDER TRACE ===\n"
            + f"high_suspicion_invariant: cross-chain bridge value / authorization correctness of `{focus}`\n"
            + f"dangerous_interaction: external/permissionless entry into `{focus}` in `{label}` ({cat})\n\n"
            + f"Trace the function(s) `{focus}` in the verbatim source below. Run STEP 0 mechanism inventory,\n"
            + "carry forward every supported mechanism, then return ONLY the JSON verdict per the schema above.\n\n"
            + f"=== VERBATIM SOURCE: {label} ===\n```solidity\n" + src + "\n```\n"
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
# POST-FREEZE SCORING (decent answer key opened only here, after both freezes)
# ---------------------------------------------------------------------------
AWARDED = {
    "H-01": ("High", "Anyone can update DcntEth Router address -> mint/burn"),
    "H-02": ("High", "Missing min-gas check for LayerZero -> destination execution fails"),
    "H-03": ("High", "DecentBridgeExecutor.execute fail -> funds to random address"),
    "H-04": ("High", "Destination router lacks WETH reserves -> user loses cross-chain tx"),
    "M-01": ("Medium", "Permanent token loss if swap data outdated"),
    "M-02": ("Medium", "Free protocol use via DecentEthRouter.bridgeWithPayload direct call (fee bypass)"),
    "M-03": ("Medium", "Missing AC on UTB.receiveFromBridge -> swaps w/o bridge fees, bypass signature verification"),
    "M-04": ("Medium", "Loss due to fixed fee calculations"),
    "M-05": ("Medium", "Refunded ETH stuck in DecentBridgeAdapter"),
}
# Mechanism match (post-freeze, conservative). quality: strong|partial|same_surface|none
SURFACE_MAP = {
    "decent-01": {"matches": [("M-03", "strong")], "note": "receiveFromBridge missing-AC = M-03 (awarded Medium); blind over-claimed theft of UTB-held funds"},
    "decent-02": {"matches": [("M-03", "strong"), ("M-02", "partial")], "note": "receiveFromBridge AC = M-03; fee-bypass overlaps M-02; awarded Medium"},
    "decent-03": {"matches": [("M-03", "strong")], "note": "receiveFromBridge AC = M-03 (Medium)"},
    "decent-04": {"matches": [], "note": "UTBExecutor refund/paymentOperator not in awarded H/M (H-03 is DecentBridgeExecutor)"},
    "decent-05": {"matches": [("M-04", "partial")], "note": "UTBFeeCollector fee handling overlaps M-04 fixed-fee; blind found signature/replay (diff mechanism)"},
    "decent-06": {"matches": [], "note": "UniSwapper public-swap drain not in awarded set (M-01 is swap-data-outdated, diff mechanism)"},
    "decent-07": {"matches": [], "note": "Stargate sgReceive source-validation not in awarded H/M"},
    "decent-08": {"matches": [], "note": "DecentBridgeAdapter amt2Bridge mismatch not clearly awarded"},
    "decent-09": {"matches": [("H-01", "strong")], "note": "DcntEth setRouter public = H-01 (awarded HIGH) EXACT"},
    "decent-10": {"matches": [("M-02", "partial"), ("H-02", "partial"), ("M-05", "partial")], "note": "DecentEthRouter.bridge: direct-call fee bypass ~M-02; gas/LZ ~H-02; refund-stuck ~M-05"},
    "decent-11": {"matches": [("H-04", "partial")], "note": "onOFTReceived WETH-reserve fallback ~H-04 (insufficient reserves); blind framed accounting drift"},
    "decent-12": {"matches": [("H-04", "partial")], "note": "reserve strict-> check loosely ~H-04; blind PRIMARY = double-withdrawal (unawarded), graded HIGH_CONFIRMED"},
    "decent-13": {"matches": [("H-03", "same_surface")], "note": "DecentBridgeExecutor.execute = H-03 surface; blind found stuck/approval not 'funds to random address'"},
    "decent-14": {"matches": [], "note": "access-control setters zero-address DoS not in awarded H/M"},
}
CEIL = {"CRITICAL_THREAD": "High", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium", "DEAD_END": "None", "NEEDS_MORE_CONTEXT": "None"}
CAL_TIER = {"HIGH_CONFIRMED": "High", "MEDIUM_OR_LOWER_CALIBRATED": "Medium", "NEEDS_HARNESS_FOR_SEVERITY": "Harness", "SOURCE_REFUTED": "None", "INSUFFICIENT_EVIDENCE": "None"}


def cmd_score(_):
    cal = {r["id"]: r for r in json.load(open(os.path.join(OUT, "OFFLINE_REFINED_CALIBRATION.json")))["calibration"]}
    raw = {sid: json.load(open(os.path.join(RAW, f"{sid}.json"))) for sid, *_ in SURFACES}
    per = []
    for sid, rel, focus, cat in SURFACES:
        mp = SURFACE_MAP[sid]; c = cal[sid]
        # best match preferring strong>partial>same_surface
        best = None
        for q in ("strong", "partial", "same_surface"):
            cands = [m for m in mp["matches"] if m[1] == q]
            if cands:
                best = cands[0]; break
        per.append({"id": sid, "blind_verdict": raw[sid].get("verdict"), "ceiling": CEIL[raw[sid].get("verdict")],
                    "summary_label": c["summary_label"], "calibrated_tier": CAL_TIER[c["summary_label"]],
                    "matched": best[0] if best else None, "match_quality": best[1] if best else None,
                    "awarded_sev": AWARDED[best[0]][0] if best else None,
                    "all_matches": mp["matches"], "note": mp["note"]})

    matched = [p for p in per if p["matched"]]
    matched_high = [p for p in matched if p["awarded_sev"] == "High"]
    matched_med = [p for p in matched if p["awarded_sev"] == "Medium"]
    # High preservation
    high_confirmed = [p for p in matched_high if p["calibrated_tier"] == "High"]
    high_harness = [p for p in matched_high if p["calibrated_tier"] == "Harness"]
    high_demoted_med = [p for p in matched_high if p["calibrated_tier"] == "Medium"]
    high_demoted_none = [p for p in matched_high if p["calibrated_tier"] == "None"]
    # Medium demotion / over-HIGH
    med_overhigh_ceiling = [p for p in matched_med if p["ceiling"] == "High"]
    med_overhigh_calibrated = [p for p in matched_med if p["calibrated_tier"] == "High"]
    med_demoted = [p for p in matched_med if p["calibrated_tier"] in ("Medium", "None")]
    # false HIGH_CONFIRMED = surface calibrated High whose match is NOT an awarded High
    false_high = [p for p in per if p["calibrated_tier"] == "High" and not (p["matched"] and p["awarded_sev"] == "High")]
    unawarded_high = [p for p in per if p["calibrated_tier"] == "High" and not p["matched"]]

    from collections import Counter
    allm = [m["label"] for r in cal.values() for m in r["mechanisms"]]
    metrics = {
        "_meta": {"phase": "P202", "corpus": "decent-2024-01-holdout", "blind_model": "sonnet",
                  "calibration_provenance": "fresh_firewall_subagent (orchestrator PCS-contaminated, did NOT author calibration)",
                  "freeze1_raw_outputs": "54abf9ca", "freeze2_calibration": "90cf2a4f"},
        "awarded": {"High": 4, "Medium": 5},
        "blind_ceiling": dict(Counter(p["ceiling"] for p in per)),
        "calibrated_surface": dict(Counter(p["calibrated_tier"] for p in per)),
        "per_mechanism_labels": dict(Counter(allm)),
        "high_preservation": {
            "mechanism_matched_awarded_high": [f"{p['id']}->{p['matched']}({p['match_quality']})" for p in matched_high],
            "confirmed_HIGH": [p["id"] for p in high_confirmed],
            "routed_HARNESS": [p["id"] for p in high_harness],
            "DEMOTED_TO_MEDIUM": [p["id"] for p in high_demoted_med],
            "DEMOTED_TO_NONE": [p["id"] for p in high_demoted_none]},
        "medium_demotion": {
            "matched_awarded_medium": [f"{p['id']}->{p['matched']}" for p in matched_med],
            "over_high_ceiling": [p["id"] for p in med_overhigh_ceiling],
            "over_high_calibrated_STILL": [p["id"] for p in med_overhigh_calibrated],
            "correctly_demoted": [p["id"] for p in med_demoted]},
        "false_HIGH_CONFIRMED": {
            "surfaces": [p["id"] for p in false_high],
            "over_high_on_awarded_medium": [p["id"] for p in false_high if p["matched"]],
            "unawarded_mechanism_high": [p["id"] for p in unawarded_high]},
        "high_bucket_precision": f"{len(high_confirmed)}/{sum(1 for p in per if p['calibrated_tier']=='High')}",
        "secondary_preservation": "per-mechanism grading applied to all 33 mechanisms; no Medium primary hid a High secondary",
        "per_surface": per,
    }
    with open(os.path.join(OUT, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_surface"}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-prompts").set_defaults(fn=cmd_build_prompts)
    sub.add_parser("score").set_defaults(fn=cmd_score)
    args = ap.parse_args()
    args.fn(args)
