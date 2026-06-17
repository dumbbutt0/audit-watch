#!/usr/bin/env python3
"""
P182 — per-answer-key downstream recall-loss trace for quantamm (READ-ONLY).

For each of the 44 quantamm answer-key findings, walk the on-disk lifecycle (affected fn/contract -> manifest
item(s) -> disposition -> shipped-lens touch -> specialist/deep coverage -> eval -> match outcome) and assign a
FIRST loss point. For surfaced-but-cleared losses, re-run the CURRENT shipped gates (F1 re-surface +
math_estimator proof-gate) on the recorded disposition to flag whether the loss is ALREADY-ADDRESSED by the
shipped P174/P177/P178 arc vs STILL-OPEN. Function-level resolution preferred; contract-level fallback (casing-
normalized) when the answer key names only a contract. Writes ONLY loss_trace.json here. No mutation.
"""
from __future__ import annotations

import glob
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AID = ROOT / "audits" / "quantamm-2024-12-eval"
sys.path.insert(0, str(ROOT / "scripts"))

import dependency_clear_utils as dcu                       # noqa: E402
import dynamic_weight_lifecycle_taxonomy as dwl            # noqa: E402  (F1)
import validate_dynamic_weight_lifecycle_clears as vdwl    # noqa: E402
import math_estimator_taxonomy as me                       # noqa: E402
import validate_math_estimator_clears as vme               # noqa: E402

P171 = ROOT / "documentation/research/assisted_mode/p171_eval_answer_key_miss_analysis/coverage_matrix.json"
RECOVERED_CATS = ("HIT", "PARTIAL", "ADJACENT")


def jload(p):
    return json.loads(Path(p).read_text())


def _parts(affected: str):
    out = []
    for part in (affected or "").replace(",", "/").split("/"):
        part = part.strip()
        if not part or part == "*":
            continue
        c, _, f = part.partition(".")
        out.append((c.strip(), f.strip()))   # f may be ""
    return out


def main():
    akd = jload(AID / "output/answer_key/normalized_answer_key.json")
    ak = akd["distinct_findings"] if isinstance(akd, dict) else akd
    mm = {r["answer_key_id"]: r for r in jload(AID / "output/eval_ready/match_matrix.json")["rows"]}
    man = jload(AID / "output/coverage_manifest.json")["items"]
    mi = {i["id"]: i for i in man}
    ni = dcu.build_manifest_name_index(man)
    by_contract = {}
    for i in man:
        by_contract.setdefault((i.get("contract") or "").lower(), []).append(i["id"])
    di = {d["manifest_id"]: d for d in jload(AID / "output/coverage_dispositions.json")["dispositions"]}
    p171 = {r["finding_id"]: r for r in jload(P171)["rows"] if r.get("track") == "recall_quantamm"}

    # functions + contracts covered by any PRODUCED finding (specialist/deep/merged/ice)
    produced_fns, produced_contracts = set(), set()
    for f in glob.glob(str(AID / "output/findings_*.json")) + [str(AID / "output/merged_findings.json")]:
        try:
            d = jload(f)
        except Exception:
            continue
        fl = d if isinstance(d, list) else d.get("findings") or next((v for v in d.values()
                                                                       if isinstance(v, list)), [])
        for x in fl:
            loc = x.get("location") or {}
            if isinstance(loc, dict):
                if loc.get("function"):
                    produced_fns.add(loc["function"].lower())
                if loc.get("file"):
                    produced_contracts.add(Path(loc["file"]).stem.lower())
    eval_fns = set()
    ef = jload(AID / "output/eval_ready/eval_findings.json")
    efl = ef if isinstance(ef, list) else ef.get("findings") or next((v for v in ef.values()
                                                                       if isinstance(v, list)), [])
    for x in efl:
        for fn in (x.get("affected_functions") or []):
            eval_fns.add(str(fn).lower())

    def resolve(affected):
        """Return (items, resolution_level, fn_names, contract_names)."""
        items, fns, contracts, level = [], [], [], "unresolved"
        for c, f in _parts(affected):
            contracts.append(c)
            ids = [i for i in ni.get(f.lower(), []) if not c or mi.get(i, {}).get("contract") == c] if f else []
            if ids:
                items += ids; fns.append(f); level = "function"
        if level != "function":  # contract-level fallback (casing-normalized)
            for c, _f in _parts(affected):
                cids = by_contract.get(c.lower(), [])
                if cids:
                    items += cids; level = "contract"
        return list(dict.fromkeys(items)), level, fns, contracts

    rows, funnel = [], Counter()
    for a in ak:
        fid = a["answer_key_id"]
        cat = mm.get(fid, {}).get("category", "?")
        note = mm.get(fid, {}).get("note", "")
        fam = p171.get(fid, {}).get("root_cause_family")
        miss_class = p171.get(fid, {}).get("miss_class")
        items, level, fns, contracts = resolve(a.get("affected", ""))

        f1_hit = any(dwl.classify_manifest_item(mi[i]).get("lifecycle_sensitive") for i in items)
        me_hit = any(me.classify_manifest_item(mi[i]).get("math_estimator_sensitive") for i in items)
        dlist = [di.get(i) for i in items if di.get(i)]
        dstatuses = sorted({d.get("status") for d in dlist})
        dep_prose = any(dcu.is_dependency_based_clear(d) for d in dlist)
        clear_reason = next((d.get("clear_reason") for d in dlist if d.get("clear_reason")), None)
        covered = (any(f.lower() in produced_fns for f in fns) if level == "function"
                   else any(c.lower() in produced_contracts for c in contracts))
        in_eval = any(f.lower() in eval_fns for f in fns)

        # already-addressed by shipped gates? (re-run F1 + math_estimator proof-gates on a CLEARED site)
        already_fixed, gate = False, None
        for i in items:
            d = di.get(i, {})
            if d.get("status") != "cleared":
                continue
            if me.classify_manifest_item(mi[i]).get("math_estimator_sensitive"):
                pr = d.get("math_estimator_proof")
                if not pr or vme.validate_proof(pr)[0] != "math_proof_valid":
                    already_fixed, gate = True, "math_estimator_proof_gate"; break
            if dwl.classify_manifest_item(mi[i]).get("lifecycle_sensitive"):
                pr = d.get("dynamic_weight_lifecycle_proof")
                if not pr or vdwl.validate_proof(pr)[0] != "lifecycle_proof_valid":
                    already_fixed, gate = True, "f1_lifecycle_resurface"; break

        # ---- first loss point ----
        if not items:
            loss = "AFFECTED_UNRESOLVED"
        elif cat in RECOVERED_CATS:
            loss = "REPORTABLE_OR_HIT"
        elif "deferred_out_of_scope" in dstatuses or miss_class == "OUT_OF_SCOPE_FOR_CURRENT_PIPELINE":
            loss = "TRUE_OUT_OF_SCOPE"
        elif covered or in_eval:
            loss = "DEEP_RUN_BUT_WRONG_MECHANISM"   # surface deep-read / finding produced there, awarded bug not the one reported
        elif "cleared" in dstatuses and (f1_hit or me_hit or dep_prose or miss_class == "MISSED_SHOULD_HAVE_FOUND"):
            loss = "SURFACED_BUT_CLEARED"
        elif "assigned" in dstatuses:
            loss = "ROUTED_TO_DEEP_BUT_NOT_RUN"
        else:
            loss = "NOT_SURFACED"

        if loss == "REPORTABLE_OR_HIT":
            bucket = "reportable"
        elif loss == "AFFECTED_UNRESOLVED":
            bucket = "unmappable"
        elif loss in ("TRUE_OUT_OF_SCOPE", "NOT_SURFACED"):
            bucket = "true_discovery_gap"
        elif loss == "SURFACED_BUT_CLEARED" and already_fixed:
            bucket = "already_fixed_by_shipped"
        else:
            bucket = "still_open_downstream"

        funnel[loss] += 1
        rows.append({"finding": fid, "severity": a.get("severity"), "family": fam, "miss_class": miss_class,
                     "affected": a.get("affected"), "resolution": level, "match_category": cat,
                     "disposition": dstatuses, "clear_reason": (clear_reason or "")[:150],
                     "surfaced_by_F1": f1_hit, "surfaced_by_math_estimator": me_hit,
                     "dependency_prose_clear": dep_prose,
                     "specialist_deep_covered": covered, "in_eval_findings": in_eval,
                     "first_loss_point": loss, "already_addressed_by_shipped_gates": already_fixed, "gate": gate,
                     "recommendation_bucket": bucket, "match_note": note[:140]})

    buckets = Counter(r["recommendation_bucket"] for r in rows)
    sev_w = {"High": 3, "Medium": 2, "Low": 1}
    out = {"phase": "P182", "corpus": "quantamm-2024-12-eval", "read_only": True, "n": len(rows),
           "first_loss_point_funnel": dict(funnel), "recommendation_buckets": dict(buckets),
           "recommendation_buckets_sev_weighted": {
               b: sum(sev_w.get(r["severity"], 1) for r in rows if r["recommendation_bucket"] == b)
               for b in buckets},
           "resolution_levels": dict(Counter(r["resolution"] for r in rows)),
           "rows": rows}
    (HERE / "loss_trace.json").write_text(json.dumps(out, indent=2))

    assert len(rows) == 44
    assert funnel["REPORTABLE_OR_HIT"] == sum(1 for a in ak if mm.get(a["answer_key_id"], {}).get("category")
                                              in RECOVERED_CATS)
    assert sum(buckets.values()) == 44

    print("=== P182 downstream recall-loss trace (quantamm, 44) ===")
    print(f"resolution levels: {out['resolution_levels']}")
    print(f"first-loss-point funnel: {dict(funnel)}")
    print(f"\nrecommendation buckets: {dict(buckets)}")
    print(f"sev-weighted:           {out['recommendation_buckets_sev_weighted']}")
    print(f"surfaced by current lenses (F1 or math_estimator): "
          f"{sum(1 for r in rows if r['surfaced_by_F1'] or r['surfaced_by_math_estimator'])}/44")
    for label in ("still_open_downstream", "already_fixed_by_shipped", "true_discovery_gap", "unmappable"):
        print(f"\n{label}:")
        for r in rows:
            if r["recommendation_bucket"] == label:
                g = f" via {r['gate']}" if r["gate"] else ""
                print(f"  {r['finding']:5} {str(r['severity'])[:4]:4} {r['first_loss_point']:28} "
                      f"{r['family']}{g}")
    print("\n[OK] read-only; wrote loss_trace.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
