#!/usr/bin/env python3
"""
P177 validation — replay the P176 routing measurement on zaros + revert-lend under the NEW guarded-downstream
precision rule (read-only). Compares BEFORE (legacy: require_structured=False) vs AFTER (P177 default:
require_structured=True), using the production predicates (dcu.dependency_route_decision, math-estimator, F1).

Confirms: deep-pass load drops sharply; precise recoveries (math-estimator/F1) remain; the blunt re-surface
bucket → 0; no recovered finding depends only on prose/fuzzy dependency names.

Writes ONLY before_after.json next to this file.
Run: python documentation/research/assisted_mode/p177_guarded_downstream_precision/validate_p177.py
"""
from __future__ import annotations

import json
import re
import sys
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
STRONG_FIELDS = ["attacker_reachability", "guard_or_invariant", "no_impact_reason"]
STRONG_THRESHOLD = 3
TARGET_FAMILIES = {"accounting_drift", "liquidation_accounting"}
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
_CONTRACT_FN = re.compile(r"([A-Z][A-Za-z0-9]+)::([A-Za-z_][A-Za-z0-9_]*)")

CORPORA = {
    "zaros": ("zaros-2025-01-part-2-eval",
              "audits/zaros-2025-01-part-2-eval/output/eval_ready/eval_match_matrix.json"),
    "revert-lend": ("revert-lend-2024-03-strict-eval",
                    "audits/revert-lend-2024-03-strict-eval/output/eval_ready/match_matrix.json"),
}


def load(p):
    return json.loads((ROOT / p).read_text())


def synth_of(disp):
    keys = ("clear_reason", "guard_or_invariant", "no_impact_reason", "evidence", "finding_refs",
            "clear_depends_on", "dependency_clearance_status", "dependency_reason", "dependency_evidence",
            "downstream_guard_claim", "downstream_guard_type", "guard_locality", "path_dominance_evidence",
            "alternative_paths_considered", "dependency_name", "dependency_scope", "dependency_status",
            "proof_status")
    s = {k: disp.get(k) for k in keys}
    s["status"] = "cleared"
    s["manifest_id"] = disp.get("manifest_id")
    return s


def route_mechanism(disp, item, di, ni, mi, require_structured):
    """First-firing shipped mechanism (sweep order), with guarded-downstream gated by require_structured."""
    score = item.get("attack_surface_score", 0) or 0
    if score >= STRONG_THRESHOLD and any(not (disp.get(f) or "").strip() for f in STRONG_FIELDS):
        return "strong_clear_gate"
    s = synth_of(disp)
    if dcu.is_dependency_based_clear(s):
        cls = dcu.classify_clear(s, di, ni, manifest_index=mi)
        if dcu.dependency_route_decision(cls, s, locality_on=True,
                                         require_structured=require_structured) == "block":
            return "guarded_downstream"
    if me.classify_manifest_item(item).get("math_estimator_sensitive"):
        pr = disp.get("math_estimator_proof")
        if not pr or vme.validate_proof(pr)[0] != "math_proof_valid":
            return "math_estimator"
    if dwl.classify_manifest_item(item).get("lifecycle_sensitive"):
        pr = disp.get("dynamic_weight_lifecycle_proof")
        if not pr or vdwl.validate_proof(pr)[0] != "lifecycle_proof_valid":
            return "f1_lifecycle"
    return None


def map_to_items(title, note, ni, mi):
    text = f"{title or ''}  {note or ''}"
    pref = {m.group(1) for m in _CONTRACT_FN.finditer(text)}
    ids = []
    for tok in _IDENT.findall(text):
        ids.extend(ni.get(tok.lower(), []))
    ids = list(dict.fromkeys(ids))
    if pref:
        p = [i for i in ids if mi.get(i, {}).get("contract") in pref]
        if p:
            ids = p
    return ids


def targets(corpus):
    fs = json.loads(P175.read_text())
    out = {}
    for s in fs["family_scoring"]:
        if s["family"] in TARGET_FAMILIES:
            for m in s["members"]:
                c, _, fid = m.split(" ", 1)[0].partition(":")
                if c == corpus:
                    out[fid] = s["family"]
    return out


def measure(corpus, audit_id, mm_path, require_structured):
    disp = load(f"audits/{audit_id}/output/coverage_dispositions.json")["dispositions"]
    man = load(f"audits/{audit_id}/output/coverage_manifest.json")["items"]
    mi = {i["id"]: i for i in man}
    di = {d["manifest_id"]: d for d in disp}
    ni = dcu.build_manifest_name_index(man)
    cleared = [d for d in disp if d.get("status") == "cleared"]

    routed = {}
    for d in cleared:
        it = mi.get(d["manifest_id"])
        if not it:
            continue
        m = route_mechanism(d, it, di, ni, mi, require_structured)
        if m:
            routed[d["manifest_id"]] = m

    tgt = targets(corpus)
    rows = load(mm_path)["rows"] if "rows" in load(mm_path) else load(mm_path).get("match_matrix", [])
    rowmap = {str(r.get("answer_key_id", r.get("id"))): r for r in rows}
    precise = blunt = 0
    recovered_mechs = []
    for fid in tgt:
        r = rowmap.get(fid, {})
        ids = [i for i in map_to_items(r.get("ak_title", r.get("title", "")), r.get("note", ""), ni, mi)
               if di.get(i, {}).get("status") == "cleared"]
        hit = next((routed[i] for i in ids if i in routed), None)
        if hit:
            recovered_mechs.append((fid, hit))
            if hit == "guarded_downstream":
                blunt += 1          # guarded-downstream recovery on these old (prose/incomplete) clears
            else:
                precise += 1        # math_estimator / f1 / strong_clear_gate
    from collections import Counter
    return {"deep_pass_load": len(routed), "deep_pass_pct": round(100 * len(routed) / max(1, len(cleared)), 1),
            "mechanism_counts": dict(Counter(routed.values())),
            "target_precise_recovered": precise, "target_guarded_recovered": blunt,
            "recovered": recovered_mechs}


def main():
    out = {"phase": "P177", "type": "guarded_downstream_precision_validation", "read_only": True,
           "before": "require_structured=False (legacy)", "after": "require_structured=True (P177 default)",
           "corpora": {}}
    for corpus, (aid, mm) in CORPORA.items():
        before = measure(corpus, aid, mm, require_structured=False)
        after = measure(corpus, aid, mm, require_structured=True)
        out["corpora"][corpus] = {"before": before, "after": after}
    (HERE / "before_after.json").write_text(json.dumps(out, indent=2))

    for corpus, r in out["corpora"].items():
        b, a = r["before"], r["after"]
        print(f"\n===== {corpus} =====")
        print(f"deep-pass load:  before {b['deep_pass_load']} ({b['deep_pass_pct']}%)  ->  "
              f"after {a['deep_pass_load']} ({a['deep_pass_pct']}%)")
        print(f"  before mechanisms: {b['mechanism_counts']}")
        print(f"  after  mechanisms: {a['mechanism_counts']}")
        print(f"target accounting/liquidation recovery (precise / guarded-downstream):")
        print(f"  before: precise={b['target_precise_recovered']}  guarded={b['target_guarded_recovered']}")
        print(f"  after : precise={a['target_precise_recovered']}  guarded={a['target_guarded_recovered']}")
        # invariant: after-precise must equal before-precise (precise lenses untouched);
        # after-guarded recovery on these metadata-poor corpora must be 0 (no prose-only hard-route).
        assert a["target_precise_recovered"] == b["target_precise_recovered"], "precise recovery changed!"
        assert a["target_guarded_recovered"] == 0, "prose/incomplete guarded-downstream still recovering!"
        assert a["deep_pass_load"] <= b["deep_pass_load"], "deep-pass load did not drop!"
        # no recovered finding may rely on a prose/fuzzy guarded-downstream route under the new rule
        assert all(m != "guarded_downstream" for _, m in a["recovered"]), "a recovery still via guarded prose!"
    print("\n[OK] read-only; wrote before_after.json; all P177 invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
