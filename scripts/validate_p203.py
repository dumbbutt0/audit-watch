#!/usr/bin/env python3
"""P203 — score refined-gate v1 vs v2 over frozen decent (P202) artifacts. READ-ONLY/offline.
Reuses P202 AWARDED/SURFACE_MAP. v1 = frozen OFFLINE_REFINED_CALIBRATION.json (surface summary_label);
v2 = V2_MECHANISM_REGRADING.json (surface summary = max-severity mechanism). Scores against the P202 key."""
import json, os, sys
from collections import Counter

ROOT = "/home/dummy/clones/audit-watch/smart-contract-auditor"
P202 = os.path.join(ROOT, "documentation/research/assisted_mode/p202_decent_positive_control")
OUT = os.path.join(ROOT, "documentation/research/assisted_mode/p203_refined_gate_v2")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from validate_decent_pc import AWARDED, SURFACE_MAP  # frozen P202 mapping

SEV = {"HIGH_CONFIRMED": 4, "NEEDS_HARNESS_FOR_SEVERITY": 3, "MEDIUM_OR_LOWER_CALIBRATED": 2,
       "INSUFFICIENT_EVIDENCE": 1, "SOURCE_REFUTED": 0}
TIER = {"HIGH_CONFIRMED": "High", "NEEDS_HARNESS_FOR_SEVERITY": "Harness",
        "MEDIUM_OR_LOWER_CALIBRATED": "Medium", "INSUFFICIENT_EVIDENCE": "None", "SOURCE_REFUTED": "None"}


def best_match(sid):
    for q in ("strong", "partial", "same_surface"):
        for fid, qual in SURFACE_MAP[sid]["matches"]:
            if qual == q:
                return fid, qual, AWARDED[fid][0]
    return None, None, None


def main():
    v1 = {r["id"]: r["summary_label"] for r in json.load(open(os.path.join(P202, "OFFLINE_REFINED_CALIBRATION.json")))["calibration"]}
    v2raw = json.load(open(os.path.join(OUT, "V2_MECHANISM_REGRADING.json")))["regrading"]
    v2 = {r["id"]: max((m["v2_label"] for m in r["mechanisms"]), key=lambda l: SEV[l]) for r in v2raw}

    rows = []
    for sid in v1:
        fid, qual, sev = best_match(sid)
        rows.append({"id": sid, "v1": v1[sid], "v2": v2[sid], "v1_tier": TIER[v1[sid]], "v2_tier": TIER[v2[sid]],
                     "matched": fid, "match_q": qual, "awarded_sev": sev})

    def high(t): return [r["id"] for r in rows if r[t] == "High"]
    v1_high, v2_high = high("v1_tier"), high("v2_tier")
    # matched awarded High / Medium
    mh = [r for r in rows if r["awarded_sev"] == "High"]
    mm = [r for r in rows if r["awarded_sev"] == "Medium"]
    # H-01 surface = decent-09 ; M-03 surfaces = decent-01/02/03
    h01 = next(r for r in rows if r["id"] == "decent-09")
    m03 = [r for r in rows if r["id"] in ("decent-01", "decent-02", "decent-03")]
    # false High = calibrated High whose match is not an awarded High
    def false_high(t): return [r["id"] for r in rows if r[t] == "High" and not (r["matched"] and r["awarded_sev"] == "High")]
    # downgrade-reason tallies from v2 regrade
    dr = [m for r in v2raw for m in r["mechanisms"]]
    dg_custody = sum(1 for m in dr if m["v1_label"] == "HIGH_CONFIRMED" and m["v2_label"] != "HIGH_CONFIRMED"
                     and m.get("custody_value_flow_proof") == "NOT_PROVEN")
    dg_mag = sum(1 for m in dr if m["v1_label"] == "HIGH_CONFIRMED" and m["v2_label"] != "HIGH_CONFIRMED"
                 and m.get("magnitude_status") in ("ASSERTED_ONLY", "BOUNDED", "UNKNOWN"))
    v1hm = [m for m in dr if m["v1_label"] == "HIGH_CONFIRMED"]
    v1hm_retained = sum(1 for m in v1hm if m["v2_label"] == "HIGH_CONFIRMED")

    metrics = {
        "_meta": {"phase": "P203", "corpus": "decent-2024-01-holdout",
                  "regrade_provenance": "fresh_keyblind_firewall_subagent",
                  "freeze_v1_calibration": "90cf2a4f", "freeze_v2_regrading": "e2100588",
                  "frozen_raw_outputs": "54abf9ca"},
        "v1_vs_v2_per_mechanism": dict(Counter(m["v2_label"] for m in dr)),
        "v1_HIGH_mechanisms": len(v1hm), "v2_retained_HIGH_mechanisms": v1hm_retained,
        "v1_HIGH_surfaces": v1_high, "v2_HIGH_surfaces": v2_high,
        "v1_HIGH_surface_count": len(v1_high), "v2_HIGH_surface_count": len(v2_high),
        "H01_decent-09": {"v1": h01["v1_tier"], "v2": h01["v2_tier"], "retained_high": h01["v2_tier"] == "High"},
        "M03_decent-01_02_03": {"v1": [r["v1_tier"] for r in m03], "v2": [r["v2_tier"] for r in m03],
                                "demoted_from_high": all(r["v2_tier"] != "High" for r in m03)},
        "matched_awarded_high": [f"{r['id']}->{r['matched']}({r['match_q']})" for r in mh],
        "matched_awarded_medium": [f"{r['id']}->{r['matched']}" for r in mm],
        "over_high_on_matched_medium_v1": [r["id"] for r in mm if r["v1_tier"] == "High"],
        "over_high_on_matched_medium_v2": [r["id"] for r in mm if r["v2_tier"] == "High"],
        "genuine_high_demoted_to_medium_v2": [r["id"] for r in mh if r["v2_tier"] == "Medium"],
        "genuine_high_to_harness_v2": [r["id"] for r in mh if r["v2_tier"] == "Harness"],
        "false_high_v1": false_high("v1_tier"), "false_high_v2": false_high("v2_tier"),
        "downgrades_from_missing_custody": dg_custody, "downgrades_from_asserted_only_magnitude": dg_mag,
        "per_surface": rows,
    }
    with open(os.path.join(OUT, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_surface"}, indent=2))


if __name__ == "__main__":
    main()
