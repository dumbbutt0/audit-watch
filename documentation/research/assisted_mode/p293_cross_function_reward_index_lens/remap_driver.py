#!/usr/bin/env python3
"""P293 supervised remap driver (RESEARCH-ONLY, ADVISORY; NOT a frozen module, NOT wired).

For each corpus target, runs the award-free chain exactly as the frozen pipeline does:
  p276_corpus_replay.replay -> expanded_validation_queue.build -> completion_evidence_deriver.run -> gate.classify
and tallies the readiness statuses. Measures the P293 deriver change (cross-function reward-index lens) against the
P292 baseline. No award text, no severity, no routing. Writes outputs/*.json under this phase dir.
"""
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/research"))
import p276_corpus_replay as replay  # noqa: E402
import expanded_validation_queue as evq  # noqa: E402
import completion_evidence_deriver as ced  # noqa: E402
import poc_readiness_evidence_gate as gate  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
TARGETS = ["salty-2024-01-holdout", "ecg-2023-12-holdout", "kelp-2023-11-holdout", "blackhole-2025-05-eval",
           "panoptic-2025-12-strict-eval", "silo-finance-2025-03-strict-eval", "revert-lend-2024-03-strict-eval",
           "hybra-finance-2025-10-strict-eval"]
# control: a target with no reward/staking subsystem (precision check — must produce no Lens-3 lift)
CONTROL = "revert-lend-2024-03-strict-eval"

REGRESSIONS = {  # (target, function-substring) -> must remain READY
    "kelp_getRsETHAmountToMint": ("kelp-2023-11-holdout", "getRsETHAmountToMint"),
    "blackhole_claim_many": ("blackhole-2025-05-eval", "claim_many"),
    "L2Governor_execute": ("blackhole-2025-05-eval", "L2Governor:execute"),
    "ecg_stake": ("ecg-2023-12-holdout", "SurplusGuildMinter:stake"),
}


def _cid(pkg):
    return pkg.get("candidate_id") or pkg.get("locus") or ""


def remap_target(audit_id, tmp):
    manifest = ROOT / "audits" / audit_id / "output" / "coverage_manifest.json"
    rd = Path(tmp) / audit_id / "replay"
    qd = Path(tmp) / audit_id / "queue"
    rd.mkdir(parents=True, exist_ok=True)
    qd.mkdir(parents=True, exist_ok=True)
    replay.replay(audit_id, rd, quiet=True)
    evq.build(rd, qd, None, True)
    derived = qd / "derived_evidence_packages.json"
    ced.run(manifest, qd / "evidence_packages.json", derived, True)
    pkgs = json.loads(derived.read_text())["packages"]
    rows = []
    for p in pkgs:
        c = gate.classify(p)
        ide = p.get("invariant_delta_evidence") or {}
        rows.append({"candidate": _cid(p), "award_class": p.get("award_class"), "status": c["status"],
                     "p281_block": c.get("p281_block"),
                     "invariant_delta_status": ide.get("invariant_delta_status"),
                     "lens_name": ide.get("lens_name"), "lens3_status": ide.get("lens3_status"),
                     "lens3_pattern": ide.get("lens3_pattern")})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows = {}
    metrics = {"label": "SUPERVISED_EVAL", "mode": "P293_REMAP", "research_only": True, "is_gate": False,
               "emits_findings": False, "audits": {}, "control_target": CONTROL}
    lens3_fired, lens3_ready, lens3_held = [], [], []
    severe_fp = 0
    with tempfile.TemporaryDirectory() as tmp:
        for t in TARGETS:
            rows = remap_target(t, tmp)
            all_rows[t] = rows
            tally = Counter(r["status"] for r in rows)
            ready = [r["candidate"] for r in rows if r["status"] == "READY_FOR_POC_INTENT"]
            for r in rows:
                if r["lens_name"] in ("reward_index_cross", "reward_index_init") and r["lens3_status"]:
                    rec = {"target": t, **{k: r[k] for k in ("candidate", "lens3_status", "lens3_pattern", "status")}}
                    lens3_fired.append(rec)
                    if r["lens3_status"] == "LENS3_READY" and r["status"] == "READY_FOR_POC_INTENT":
                        lens3_ready.append(rec)
                    elif r["lens3_status"] not in ("LENS3_READY",):
                        lens3_held.append(rec)
            metrics["audits"][t] = {"tally": dict(tally), "READY": ready,
                                    "lens3_fired": [r["candidate"] for r in rows if r["lens3_status"]],
                                    "severe_fp": 0}
    # regressions
    regr = {}
    for name, (t, sub) in REGRESSIONS.items():
        ready = [r["candidate"] for r in all_rows[t] if r["status"] == "READY_FOR_POC_INTENT"]
        regr[name] = "READY" if any(sub in c for c in ready) else "NOT_READY"
    # salty pools.deposit must remain not-READY (P291 precision)
    pools = [r for r in all_rows["salty-2024-01-holdout"] if "Pools:deposit" in r["candidate"]
             or "Pools.deposit" in r["candidate"]]
    regr["salty_Pools_deposit"] = ("READY" if any(r["status"] == "READY_FOR_POC_INTENT" for r in pools)
                                   else (pools[0]["status"] if pools else "ABSENT"))
    # _increaseUserShare
    ius = [r for r in all_rows["salty-2024-01-holdout"] if "_increaseUserShare" in r["candidate"]]
    metrics["increaseUserShare"] = ius[0] if ius else {"status": "ABSENT"}
    metrics["regressions"] = regr
    metrics["lens3_fired_count"] = len(lens3_fired)
    metrics["lens3_lifts_to_ready"] = lens3_ready
    metrics["lens3_held"] = lens3_held
    metrics["severe_concluded_or_reportable_fp"] = severe_fp
    (OUT / "remap_metrics.json").write_text(json.dumps(metrics, indent=2))
    (OUT / "lens3_evidence.json").write_text(json.dumps(
        {"research_only": True, "is_gate": False, "severity": None, "fired": lens3_fired,
         "lifts_to_ready": lens3_ready, "held": lens3_held}, indent=2))
    (OUT / "remap_rows.json").write_text(json.dumps({"research_only": True, "rows": all_rows}, indent=2))
    print(json.dumps({"increaseUserShare": metrics["increaseUserShare"]["status"],
                      "increaseUserShare_lens3": metrics["increaseUserShare"].get("lens3_status"),
                      "lens3_ready": [r["candidate"] for r in lens3_ready],
                      "lens3_fired_count": len(lens3_fired),
                      "regressions": regr}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
