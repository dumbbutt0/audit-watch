#!/usr/bin/env python3
"""
P176 — Shipped-routing recovery measurement on zaros + revert-lend (READ-ONLY).

Replays the EXACT production clear-routing predicates over the EXISTING cleared dispositions of each corpus
(no sweep run, no disposition mutation) and measures how much of the awarded accounting/liquidation miss tail
the already-shipped routing would re-surface to deep-pass. Imports the same modules coverage_sweep_write.py
uses, so this IS the production logic minus the write.

Mechanisms simulated, in the sweep's first-match order (full-audit strict assumed — when routing is active):
  1. strong_clear_gate     score>=threshold AND a strong-clear field is empty            (coverage_sweep_write:154)
  2. guarded_downstream     dcu.is_dependency_based_clear + classify_clear blocking       (…:175)
  3. math_estimator         me sensitive AND no valid math proof                          (…:215)
  4. f1_lifecycle           dwl sensitive AND no valid lifecycle proof                    (…:240)
(Other shipped routers — special-focus / gate-DoS / spec-checklist — are NOT simulated; deep-pass load is
therefore a LOWER BOUND and recovery via measured mechanisms is conservative.)

Three-bucket outcome for each MAPPED awarded miss (so a missing audit trail is never miscounted as a
selector/discovery failure):
  recovered                       -> a measured predicate fires on its cleared item
  discovery_gap                   -> NOT routed AND the clear is evidence-complete (full strong-clear triplet)
  unrecoverable_missing_evidence  -> NOT routed AND the clear is evidence-incomplete (no triplet)
(unmappable = a 4th status, distinct from the three buckets: no manifest function could be resolved.)

Writes ONLY recovery_by_finding.json next to this file. Touches no disposition/manifest/answer-key/production
file.

Run: python documentation/research/assisted_mode/p176_shipped_routing_recovery/routing_recovery.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import dependency_clear_utils as dcu                       # noqa: E402
import math_estimator_taxonomy as me                       # noqa: E402
import validate_math_estimator_clears as vme               # noqa: E402
import dynamic_weight_lifecycle_taxonomy as dwl            # noqa: E402
import validate_dynamic_weight_lifecycle_clears as vdwl    # noqa: E402

P175 = ROOT / "documentation/research/assisted_mode/p175_remaining_miss_family_roadmap/family_scoring.json"

# policy (mirrors config/agent_policy.json coverage_policy under full-audit strict)
STRONG_FIELDS = ["attacker_reachability", "guard_or_invariant", "no_impact_reason"]
STRONG_THRESHOLD = 3
DEP_REQUIRE = True
DEP_BLOCKING = dcu.BLOCKING_CLASSIFICATIONS | dcu.LOCALITY_BLOCKING   # full-audit: locality strict on too
TARGET_FAMILIES = {"accounting_drift", "liquidation_accounting"}
RECOVERED_VERDICTS = ("HIT", "PARTIAL", "ADJACENT", "FOUND")

CORPORA = {
    "zaros": {
        "id": "zaros-2025-01-part-2-eval",
        "mm": "audits/zaros-2025-01-part-2-eval/output/eval_ready/eval_match_matrix.json",
        "mm_key": "rows", "id_k": "answer_key_id", "sev_k": "severity", "title_k": "ak_title",
        "note_k": "note", "verdict_k": "category",
    },
    "revert-lend": {
        "id": "revert-lend-2024-03-strict-eval",
        "mm": "audits/revert-lend-2024-03-strict-eval/output/eval_ready/match_matrix.json",
        "mm_key": "rows", "id_k": "answer_key_id", "sev_k": "severity", "title_k": "ak_title",
        "note_k": "note", "verdict_k": "category",
    },
}

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
_CONTRACT_FN = re.compile(r"([A-Z][A-Za-z0-9]+)::([A-Za-z_][A-Za-z0-9_]*)")


def load(p):
    return json.loads((ROOT / p).read_text())


def p175_target_ids(corpus):
    """{finding_id: family} for accounting/liquidation misses of this corpus, from P175."""
    fs = json.loads(P175.read_text())
    out = {}
    for s in fs["family_scoring"]:
        if s["family"] not in TARGET_FAMILIES:
            continue
        for m in s["members"]:                       # "corpus:id SEV | title"
            cid = m.split(" ", 1)[0]
            c, _, fid = cid.partition(":")
            if c == corpus:
                out[fid] = s["family"]
    return out


def evidence_complete(disp):
    return all((disp.get(f) or "").strip() for f in STRONG_FIELDS)


def build_synth(disp):
    """Mirror coverage_sweep_write.py:162-173 — build the dict the dependency predicate reads."""
    return {"status": "cleared", "manifest_id": disp.get("manifest_id"),
            "clear_reason": disp.get("clear_reason"),
            "guard_or_invariant": disp.get("guard_or_invariant"),
            "no_impact_reason": disp.get("no_impact_reason"),
            "evidence": disp.get("evidence"),
            "finding_refs": disp.get("finding_refs"),
            "clear_depends_on": disp.get("clear_depends_on"),
            "dependency_clearance_status": disp.get("dependency_clearance_status"),
            "dependency_reason": disp.get("dependency_reason"),
            "dependency_evidence": disp.get("dependency_evidence"),
            "downstream_guard_claim": disp.get("downstream_guard_claim"),
            "downstream_guard_type": disp.get("downstream_guard_type"),
            "guard_locality": disp.get("guard_locality"),
            "path_dominance_evidence": disp.get("path_dominance_evidence"),
            "alternative_paths_considered": disp.get("alternative_paths_considered")}


def route_mechanism(disp, item, disp_index, name_index, man_idx, call_graph):
    """Return the first-firing shipped mechanism for a CLEARED item, or None. Mirrors the sweep order."""
    score = item.get("attack_surface_score", 0) or 0
    # 1) strong-clear gate
    if score >= STRONG_THRESHOLD and any(not (disp.get(f) or "").strip() for f in STRONG_FIELDS):
        return "strong_clear_gate", f"high-surface (score {score}) clear missing strong-clear field"
    # 2) guarded-downstream. Distinguish GENUINE (structured metadata present and adjudicated blocking) from
    # BLUNT (prose-only -> missing_dependency_metadata fallback that fires on incidental tokens like
    # "invariant"/"guard"/"oracle"). The blunt fallback is high-recall/low-precision on older clears that
    # predate the structured dependency fields, so it is reported separately and NOT counted as precise.
    synth = build_synth(disp)
    if dcu.is_dependency_based_clear(synth):
        cls = dcu.classify_clear(synth, disp_index, name_index, manifest_index=man_idx, call_graph=call_graph)
        st = cls["status"]
        blocking = st in DEP_BLOCKING
        if st == "missing_dependency_metadata" and not DEP_REQUIRE:
            blocking = False
        if blocking:
            structured = bool(disp.get("downstream_guard_claim") or disp.get("clear_depends_on"))
            mech = "guarded_downstream_genuine" if (structured and st != "missing_dependency_metadata") \
                else "guarded_downstream_blunt"
            return mech, f"{st}: {cls.get('locality_reason') or (cls['names'][:3])}"
    # 3) math-estimator
    mcls = me.classify_manifest_item(item)
    if mcls.get("math_estimator_sensitive"):
        proof = disp.get("math_estimator_proof")
        if not proof or vme.validate_proof(proof)[0] != "math_proof_valid":
            return "math_estimator", f"math_estimator_sensitive ({mcls.get('math_domain')}), no valid proof"
    # 4) F1 lifecycle
    lcls = dwl.classify_manifest_item(item)
    if lcls.get("lifecycle_sensitive"):
        proof = disp.get("dynamic_weight_lifecycle_proof")
        if not proof or vdwl.validate_proof(proof)[0] != "lifecycle_proof_valid":
            return "f1_lifecycle", "lifecycle_sensitive, no valid proof"
    return None, None


def map_finding_to_items(title, note, name_index, man_idx):
    """Resolve a finding's named function(s) to manifest items. Only identifiers that ARE manifest function
    names map (strong filter against prose). Prefer items in a Contract:: prefix when present."""
    text = f"{title or ''}  {note or ''}"
    pref_contracts = {m.group(1) for m in _CONTRACT_FN.finditer(text)}
    ids = []
    for tok in _IDENT.findall(text):
        hit = name_index.get(tok.lower())
        if hit:
            ids.extend(hit)
    ids = list(dict.fromkeys(ids))
    if pref_contracts:
        pref = [i for i in ids if man_idx.get(i, {}).get("contract") in pref_contracts]
        if pref:
            ids = pref
    return ids


def run_corpus(corpus, cfg):
    disp_all = load(f"audits/{cfg['id']}/output/coverage_dispositions.json")["dispositions"]
    man_items = load(f"audits/{cfg['id']}/output/coverage_manifest.json")["items"]
    man_idx = {i["id"]: i for i in man_items}
    disp_index = {d["manifest_id"]: d for d in disp_all}
    name_index = dcu.build_manifest_name_index(man_items)
    cg_path = ROOT / "audits" / cfg["id"] / "data" / "interactions" / "call_graph.json"
    call_graph = json.loads(cg_path.read_text()) if cg_path.exists() else {}
    cleared = [d for d in disp_all if d.get("status") == "cleared"]

    # ---- population-level routing simulation over ALL cleared items ----
    routed_ids, mech_count = {}, defaultdict(int)
    for d in cleared:
        it = man_idx.get(d["manifest_id"])
        if not it:
            continue
        mech, why = route_mechanism(d, it, disp_index, name_index, man_idx, call_graph)
        if mech:
            routed_ids[d["manifest_id"]] = (mech, why)
            mech_count[mech] += 1

    # ---- per-finding recovery for accounting/liquidation misses ----
    targets = p175_target_ids(corpus)
    mm = load(cfg["mm"])[cfg["mm_key"]]
    rows = {str(r[cfg["id_k"]]): r for r in mm}
    by_finding, bucket = [], defaultdict(int)
    routed_target_ids = set()
    for fid, fam in sorted(targets.items()):
        r = rows.get(fid, {})
        title, note = r.get(cfg["title_k"], ""), r.get(cfg["note_k"], "")
        item_ids = map_finding_to_items(title, note, name_index, man_idx)
        # restrict to items that are currently CLEARED (only a clear can be "recovered" by re-routing)
        cleared_items = [i for i in item_ids if disp_index.get(i, {}).get("status") == "cleared"]
        rec = {"finding": fid, "family": fam, "severity": r.get(cfg["sev_k"]), "title": title[:90],
               "mapped_item_ids": item_ids, "cleared_item_ids": cleared_items}
        if not item_ids:
            rec["bucket"] = "unmappable"; rec["mechanism"] = None
        elif not cleared_items:
            # mapped but the item isn't a clear (finding/assigned/deferred) → not in the over-clear population
            rec["bucket"] = "unmappable"; rec["mechanism"] = None
            rec["note"] = "mapped item(s) not in cleared state"
        else:
            hit = next(((i, *routed_ids[i]) for i in cleared_items if i in routed_ids), None)
            if hit:
                mech = hit[1]
                rec["mechanism"] = mech; rec["routed_item"] = hit[0]; rec["reason"] = hit[2]
                routed_target_ids.update(cleared_items)
                # blunt guarded-downstream (prose-only missing-metadata) is NOT a precise recovery; it is the
                # instrumentation-gap fallback that re-surfaces ~half of all clears. Bucket it separately.
                rec["bucket"] = "recovered_blunt_resurface" if mech == "guarded_downstream_blunt" else "recovered"
            else:
                comp = any(evidence_complete(disp_index[i]) for i in cleared_items)
                rec["bucket"] = "discovery_gap" if comp else "unrecoverable_missing_evidence"
                rec["mechanism"] = None
                rec["evidence_complete"] = comp
        bucket[rec["bucket"]] += 1
        by_finding.append(rec)

    # FP surface proxy: routed items that map to NO awarded finding (any family) ÷ total routed.
    all_target_item_ids = set()
    for fid in targets:
        r = rows.get(fid, {})
        all_target_item_ids.update(map_finding_to_items(r.get(cfg["title_k"], ""), r.get(cfg["note_k"], ""),
                                                        name_index, man_idx))
    off_target = sum(1 for mid in routed_ids if mid not in all_target_item_ids)

    return {
        "corpus": corpus, "audit_id": cfg["id"],
        "cleared_total": len(cleared),
        "deep_pass_load_routed": len(routed_ids),
        "deep_pass_load_pct": round(100 * len(routed_ids) / max(1, len(cleared)), 1),
        "mechanism_counts_population": dict(sorted(mech_count.items(), key=lambda x: -x[1])),
        "fp_surface_off_target_routed": off_target,
        "fp_surface_pct": round(100 * off_target / max(1, len(routed_ids)), 1),
        "target_findings": len(targets),
        "buckets": dict(bucket),
        "by_finding": by_finding,
    }


def main():
    out = {"phase": "P176", "type": "shipped_routing_recovery_measurement", "read_only": True,
           "assumed": "full-audit strict; mechanisms simulated = strong_clear_gate, guarded_downstream, "
                      "math_estimator, f1_lifecycle (special-focus/gate-DoS/spec-checklist NOT simulated -> "
                      "deep-pass load is a lower bound)",
           "corpora": {}}
    for corpus, cfg in CORPORA.items():
        out["corpora"][corpus] = run_corpus(corpus, cfg)
    (HERE / "recovery_by_finding.json").write_text(json.dumps(out, indent=2))

    # ---- self-checks + summary ----
    for corpus, r in out["corpora"].items():
        b = r["buckets"]
        mapped = (b.get("recovered", 0) + b.get("recovered_blunt_resurface", 0)
                  + b.get("discovery_gap", 0) + b.get("unrecoverable_missing_evidence", 0))
        total = sum(b.values())
        assert mapped + b.get("unmappable", 0) == total == r["target_findings"], (corpus, b, r["target_findings"])
        print(f"\n===== {corpus} ({r['audit_id']}) =====")
        print(f"cleared={r['cleared_total']}  deep-pass load (routed)={r['deep_pass_load_routed']} "
              f"({r['deep_pass_load_pct']}%)  FP-surface off-target={r['fp_surface_off_target_routed']} "
              f"({r['fp_surface_pct']}%)")
        print(f"population mechanism counts: {r['mechanism_counts_population']}")
        print(f"accounting/liquidation misses = {r['target_findings']}  buckets: {dict(sorted(b.items()))}")
        for rec in r["by_finding"]:
            mech = f" via {rec['mechanism']}" if rec.get("mechanism") else ""
            print(f"   {rec['finding']:5} {str(rec['severity'])[:4]:4} {rec['bucket']:30}{mech}  "
                  f"| {rec['title'][:60]}")
    print("\n[OK] read-only; wrote recovery_by_finding.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
