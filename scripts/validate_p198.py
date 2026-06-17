#!/usr/bin/env python3
"""validate_p198.py — READ-ONLY scorer for the P198 Centrifuge blind adjudication campaign.

Encodes the answer-aware (post-freeze) mapping of the 8 awarded Medium findings to the 12 frozen blind outputs,
and emits metrics.json. The blind run was performed by Sonnet subagents on deep_trace.md + verbatim source
(blind_prompts/ + raw_outputs/). This scorer does not run any model; it records the human-audited scoring with
artifact citations. fabrication_rate=0.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter

PD = Path("documentation/research/assisted_mode/p198_centrifuge_campaign")

# 8 awarded Mediums (from report.md, read post-freeze). in_sample = covered by the 12-surface bounded sample.
AWARDED = [
 {"id":"M-01","title":"onlyCentrifugeChainOrigin can't require msg.sender==axelarGateway","surface":"Gateway/axelar Router","in_sample":False,"score":"OUT_OF_SAMPLE","blind":None,
  "note":"axelar Router auth not in bounded invariant-core sample"},
 {"id":"M-02","title":"requestRedeemWithPermit front-run with different liquidity pool","surface":"LiquidityPool.requestRedeemWithPermit","in_sample":False,"score":"OUT_OF_SAMPLE","blind":None,
  "note":"permit entrypoint not sampled (sampled LP.withdraw)"},
 {"id":"M-03","title":"Cached DOMAIN_SEPARATOR incorrect for tranche tokens","surface":"ERC20/Tranche permit DOMAIN_SEPARATOR","in_sample":False,"score":"OUT_OF_SAMPLE","blind":None,
  "note":"permit/domain-separator not sampled (sampled Tranche.transfer)"},
 {"id":"M-04","title":"Deposit small amount for other users to DoS them","surface":"LiquidityPool.deposit/mint (-> processDeposit)","in_sample":True,"score":"MISS_WRONG_MECHANISM","blind":"IM-04",
  "note":"IM-04 traced the auth-gated callee processDeposit and REJECTED the access-control angle (auth-gated), missing that the PUBLIC LiquidityPool.deposit wrapper has no access control -> the awarded front-run griefing. wrong-layer / non-responsive-rejection class"},
 {"id":"M-05","title":"Claiming maxDeposit via deposit() starves Escrow shares for other claimers","surface":"LiquidityPool.deposit -> Escrow shares / processDeposit","in_sample":True,"score":"PARTIAL","blind":"IM-04",
  "note":"IM-04 selected 'maxDeposit not decremented -> drains Escrow tranche tokens beyond earned, affecting other holders' = same Escrow-share-conservation family, related but not the exact epoch-accumulation framing"},
 {"id":"M-06","title":"DelayedAdmin cannot PauseAdmin.removePauser","surface":"PauseAdmin/DelayedAdmin","in_sample":False,"score":"OUT_OF_SAMPLE","blind":None,
  "note":"admin module not sampled"},
 {"id":"M-07","title":"trancheTokenAmount should be rounded UP on withdrawal (currently DOWN)","surface":"InvestmentManager._calculateTrancheTokenAmount (L591) via processWithdraw","in_sample":True,"score":"HIT","blind":"IM-06",
  "note":"IM-06 selected EXACTLY _calculateTrancheTokenAmount rounding-DOWN as a precision/conservation defect (exact function L591 + rounding-direction mechanism)"},
 {"id":"M-08","title":"RestrictionManager incomplete ERC1404: only checks receiver, not sender","surface":"RestrictionManager.detectTransferRestriction","in_sample":True,"score":"HIT","blind":"RM-12",
  "note":"RM-12 selected EXACTLY 'checks hasMember(to) but NOT hasMember(from)' -> revoked sender can transfer; exact function + exact mechanism. TR-11 also flagged the restriction gap"},
]

# blind-run verdicts (from frozen raw_outputs) — precision/calibration lens
BLIND_VERDICTS = {"IM-01":"HIGH","IM-02":"HIGH","IM-03":"HIGH","IM-04":"HIGH","IM-05":"HIGH","IM-06":"MEDIUM",
                  "IM-07":"HIGH","ESC-08":"HIGH","ESC-09":"HIGH","LP-10":"HIGH","TR-11":"HIGH","RM-12":"HIGH"}

def main():
    sc = Counter(a["score"] for a in AWARDED)
    in_sample = [a for a in AWARDED if a["in_sample"]]
    in_sc = Counter(a["score"] for a in in_sample)
    hits = sum(1 for a in in_sample if a["score"]=="HIT")
    partials = sum(1 for a in in_sample if a["score"]=="PARTIAL")
    misses = sum(1 for a in in_sample if a["score"].startswith("MISS"))
    high_verdicts = sum(1 for v in BLIND_VERDICTS.values() if v=="HIGH")
    metrics = {
      "phase":"P198","corpus":"centrifuge-2023-09-holdout","read_only":True,"blind_model":"sonnet",
      "awarded_total":len(AWARDED),"awarded_severity":"8 Medium / 0 High",
      "bounded_sample_surfaces":12,
      "awarded_in_bounded_sample":len(in_sample),
      "awarded_out_of_sample":len(AWARDED)-len(in_sample),
      "in_sample_scoring":dict(in_sc),
      "in_sample_hits":hits,"in_sample_partials":partials,"in_sample_miss_wrong_mechanism":misses,
      "exact_hits":["M-07 (IM-06 _calculateTrancheTokenAmount rounding-direction)","M-08 (RM-12 sender-not-checked restriction)"],
      "partial":["M-05 (IM-04 Escrow-share conservation, related framing)"],
      "miss_wrong_mechanism":["M-04 (IM-04 rejected access-control on auth-gated callee, missed public deposit wrapper)"],
      "out_of_sample_awarded":["M-01 axelar gateway auth","M-02 requestRedeemWithPermit","M-03 DOMAIN_SEPARATOR","M-06 admin removePauser"],
      "precision_calibration":{
        "blind_HIGH_verdicts":high_verdicts,"of_surfaces":len(BLIND_VERDICTS),
        "awarded_reality":"0 High / 8 Medium",
        "selected_mechanisms_per_surface":"~2 (24+ selected across 12) + many NEEDS_HARNESS",
        "verdict":"severity OVER-calibrated (11/12 HIGH on an all-Medium/0-High codebase); high enumeration volume / low precision on a clean corpus"},
      "decision":"PARTIAL_GENERALIZATION",
      "decision_basis":("Adjudication RECALL generalizes to the RWA tranche/escrow/ERC4626 invariant core: on the "
        "4 awarded findings the bounded sample actually covered, the stack scored 2 EXACT hits (M-07 rounding "
        "direction, M-08 restriction sender-check) + 1 PARTIAL (M-05 escrow-share conservation) + 1 wrong-mechanism "
        "(M-04). BUT precision/severity-calibration does NOT generalize cleanly (11/12 HIGH verdicts vs 8-Medium/"
        "0-High reality; over-enumeration), and M-04 shows a non-responsive-rejection on the wrong layer. 4/8 "
        "awarded were outside the bounded sample (coverage/sampling, not adjudication)."),
      "caveats":["bounded sample (12 surfaces) -> generalization signal on the invariant core, not full recall",
                 "Sonnet same-vendor (as P186); n small",
                 "awarded loci built from official report.md (read post-freeze); scoring is human-audited mapping",
                 "blind verdicts skew HIGH partly because deep_trace.md asks for worst-case threat framing"]}
    PD.mkdir(parents=True,exist_ok=True)
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    (PD/"_scoring_table.json").write_text(json.dumps({"awarded":AWARDED,"blind_verdicts":BLIND_VERDICTS},indent=2)+"\n")
    print(json.dumps({k:metrics[k] for k in ("awarded_in_bounded_sample","in_sample_hits","in_sample_partials",
        "in_sample_miss_wrong_mechanism","awarded_out_of_sample","precision_calibration","decision")},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
