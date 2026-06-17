#!/usr/bin/env python3
"""P298 — beanstalk eval validity judge (RESEARCH-ONLY, ADVISORY).

For each awarded-matched validity target: build_mode=poc -> the P294 executed_poc_verifier JUDGES the Tier-C PoC
under pocs/p298/beanstalk__<id>/ (sole confirmer; builder self-report advisory; confirmed = executed exploit PASS +
L1+L2+L3 + assertion_map). build_mode=bundle -> assemble an evidence-bundle from the existing merged finding
(call path / source / invariant / expected assertion) and mark `needs_execution` (NOT confirmed). The p290 refutation
control is re-judged (must stay refuted). Emits loop_results.json + evidence_bundles.json. confirmed-FP = 0 by const.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

CFG = json.loads((ROOT / "config/research_beanstalk_eval.json").read_text())
OUT = ROOT / "documentation/research/assisted_mode/p298_beanstalk_eval/outputs"
REFUTATION_CONTROL = ("salty-Pools-deposit-callback", "pocs/p290/salty-2024-01-holdout/Pools_deposit")
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "reportable": False,
          "submission_ready": False, "concluded": False, "production_routing": False, "auto_submitted": False}


def _merged():
    mf = json.loads((ROOT / CFG["merged_findings"]).read_text())
    return {x["id"]: x for x in (mf if isinstance(mf, list) else mf.get("findings", []))}


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    merged = _merged()
    results, bundles = [], []
    for t in CFG["validity_targets"]:
        fid = t["id"]
        if t["build_mode"] == "poc":
            d = ROOT / "pocs/p298" / f"beanstalk__{fid}"
            man = d / "poc_manifest.json"
            agent_claimed = None
            ar = d / "agent_report.json"
            if ar.exists():
                try:
                    agent_claimed = json.loads(ar.read_text()).get("agent_claimed")
                except Exception:
                    pass
            if not man.exists():
                results.append({"awarded_id": fid, "locus": t["locus"], "build_mode": "poc",
                                "verifier_verdict": "not_built", "attacker_verified": False,
                                "has_assertion_map": False, "clean_confirmation": False, "agent_claimed": agent_claimed})
                continue
            rec = epv.verify_poc(d, audit_id="beanstalk-2024-05", finding_id=f"beanstalk-{fid}")
            has_map = bool(json.loads(man.read_text()).get("assertion_map"))
            verified = bool(rec.get("attacker_verified"))
            results.append({"awarded_id": fid, "locus": t["locus"], "build_mode": "poc",
                            "verifier_verdict": rec.get("status"), "attacker_verified": verified,
                            "l1": rec.get("l1"), "l2": rec.get("l2"), "l3": rec.get("l3"),
                            "has_assertion_map": has_map, "clean_confirmation": verified and has_map,
                            "confirmed_but_unmapped": verified and not has_map, "agent_claimed": agent_claimed,
                            "runs": [{k: r.get(k) for k in ("test", "passed", "log_ref")} for r in rec.get("runs", [])]})
        else:  # bundle -> evidence-bundle + needs_execution (NEVER confirmed)
            f = merged.get(fid, {})
            loc = f.get("location", {})
            bundle = {"awarded_id": fid, "locus": t["locus"], "status": "needs_execution",
                      "call_path_entry": loc.get("function") or t["locus"],
                      "source_file": loc.get("file"), "lines": loc.get("lines"),
                      "mechanism": t["mechanism"],
                      "invariant_or_expected": (f.get("impact") or "")[:300],
                      "expected_assertion": (f.get("proof_of_concept") or f.get("description") or "")[:400],
                      "why_bundle_not_poc": "too entangled with the full reseed/migration/AMM system to mock faithfully "
                      "(Tier-C would not be source-faithful); recorded as needs_execution, NOT confirmed"}
            bundles.append(bundle)
            results.append({"awarded_id": fid, "locus": t["locus"], "build_mode": "bundle",
                            "verifier_verdict": "needs_execution", "attacker_verified": False,
                            "has_assertion_map": False, "clean_confirmation": False})

    # negative control
    cr = epv.verify_poc(ROOT / REFUTATION_CONTROL[1], finding_id=REFUTATION_CONTROL[0])
    refutation = {"finding_id": REFUTATION_CONTROL[0], "verifier_verdict": cr.get("status"),
                  "attacker_verified": cr.get("attacker_verified")}

    clean = [r for r in results if r.get("clean_confirmation")]
    confirmed_fp = (1 if refutation["attacker_verified"] else 0) + sum(1 for r in results if r.get("confirmed_but_unmapped"))
    summary = dict(_STAMP, label="P298_BEANSTALK_VALIDITY",
                   poc_targets=sum(1 for t in CFG["validity_targets"] if t["build_mode"] == "poc"),
                   bundle_targets=sum(1 for t in CFG["validity_targets"] if t["build_mode"] == "bundle"),
                   confirmed_by_execution=len(clean),
                   confirmed_loci=[r["awarded_id"] for r in clean],
                   needs_execution=[r["awarded_id"] for r in results if r["verifier_verdict"] == "needs_execution"],
                   refuted=[r["awarded_id"] for r in results if r["verifier_verdict"] in ("refuted_by_execution", "no_exploit_test")],
                   refutation_control=refutation, confirmed_false_positive_count=confirmed_fp,
                   results=results)
    (OUT / "loop_results.json").write_text(json.dumps(summary, indent=2))
    (OUT / "evidence_bundles.json").write_text(json.dumps(dict(_STAMP, bundles=bundles), indent=2))
    print(json.dumps({"confirmed_by_execution": summary["confirmed_by_execution"],
                      "confirmed_loci": summary["confirmed_loci"],
                      "needs_execution": summary["needs_execution"], "refuted": summary["refuted"],
                      "confirmed_FP": confirmed_fp}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
