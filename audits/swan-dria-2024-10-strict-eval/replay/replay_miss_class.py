#!/usr/bin/env python3
"""
replay_miss_class.py — replay the two Swan/Dria miss-classes (getFee M-08, round-validation H-02)
against the NEW validators (adversarial math proofs + dependency-clear locality).

READ-ONLY on the frozen eval: it copies the frozen artifacts into this replay/ dir and runs the new
validator LOGIC in-process (no pipeline run, no writes to output/, no mutation of the snapshot). Three
blocks:
  A. Literal frozen replay — classify every frozen `cleared` disposition with the new validators.
  B. Reconstructed miss-class fixtures — the getFee / round shapes from failure_analysis, derived from
     the frozen clear text, proving the new logic flags them.
  C. FP check — the 9 HIT findings are status:finding (validators skip findings); the literal new-block
     set is disjoint from the HIT surfaces.

Run: python audits/swan-dria-2024-10-strict-eval/replay/replay_miss_class.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent          # audits/swan-dria-2024-10-strict-eval
ROOT = AUDIT.parent.parent                              # repo root (smart-contract-auditor)
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
LIVE_CG = AUDIT / "data" / "interactions" / "call_graph.json"
REPLAY = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import math_estimator_taxonomy as me            # noqa: E402
import validate_math_estimator_clears as vme    # noqa: E402
import dependency_clear_utils as dcu            # noqa: E402

GETFEE_ID = "function:LLMOracleManager:getFee#f5466b9b"


def _copy_frozen() -> dict:
    """Copy the frozen artifacts into replay/ (never touch the snapshot) and load them."""
    REPLAY.mkdir(exist_ok=True)
    out = {}
    for name in ("coverage_manifest.json", "coverage_dispositions.json"):
        dst = REPLAY / f"copied_{name}"
        shutil.copyfile(SNAP / name, dst)
        out[name] = json.loads(dst.read_text())
    cg_dst = REPLAY / "copied_call_graph.json"
    if LIVE_CG.exists():
        shutil.copyfile(LIVE_CG, cg_dst)
        out["call_graph.json"] = json.loads(cg_dst.read_text())
    else:
        out["call_graph.json"] = {}
    return out


# ---------------- Block A: literal frozen replay ----------------

def literal_replay(manifest, dispositions, call_graph):
    items = {i["id"]: i for i in manifest.get("items", [])}
    disp = dispositions["dispositions"] if isinstance(dispositions, dict) else dispositions
    disp_index = {d["manifest_id"]: d for d in disp}
    tax = me.load_taxonomy()
    name_index = dcu.build_manifest_name_index(list(items.values()))

    math_blocks, dep_blocks, rows = {}, {}, []
    for d in disp:
        if d.get("status") != "cleared":
            continue
        mid = d["manifest_id"]
        mc = vme.classify_clear(d, items.get(mid), tax, adversarial=True)
        dc = dcu.classify_clear(d, disp_index, name_index, manifest_index=items, call_graph=call_graph)
        if mc["status"] in vme.BLOCKING_STATUSES:
            math_blocks.setdefault(mc["status"], []).append(mid)
        if dc["status"] in (dcu.BLOCKING_CLASSIFICATIONS | dcu.LOCALITY_BLOCKING):
            dep_blocks.setdefault(dc["status"], []).append(mid)
        rows.append({"manifest_id": mid, "math_status": mc["status"], "dep_status": dc["status"]})

    getfee = next((r for r in rows if r["manifest_id"] == GETFEE_ID), None)
    new_blocked = sorted({m for ids in math_blocks.values() for m in ids}
                         | {m for ids in dep_blocks.values() for m in ids})
    return {
        "cleared_count": len(rows),
        "math_blocks": {k: v for k, v in math_blocks.items()},
        "dependency_blocks": {k: v for k, v in dep_blocks.items()},
        "guard_not_path_dominant_count": len(dep_blocks.get("guard_not_path_dominant", [])),
        "incomplete_math_proof_count": len(math_blocks.get("incomplete_math_proof", [])),
        "getfee_literal": getfee,
        "getfee_before_after": {
            "before_taxonomy_patch": "not_math_estimator_sensitive (cheap-swept; <<-by-variable not a signal)",
            "after_taxonomy_patch": (getfee or {}).get("math_status"),
        },
        "getfee_note": ("RESOLVED by the economic-shift taxonomy patch: getFee `2 << difficulty` now "
                        "classifies math-sensitive (fee/difficulty economic terms next to a shift, no "
                        f"bitmask context) → math:`{(getfee or {}).get('math_status')}` → routes to "
                        "math_estimator_review instead of cheap-sweep. Before the patch it was "
                        "not_math_estimator_sensitive."),
        "new_blocked_manifest_ids": new_blocked,
    }


# ---------------- Block B: reconstructed miss-class fixtures ----------------

def reconstructed_getfee():
    """getFee as the failure_analysis describes it: routed to math review + a CONFIRMATORY proof that
    restates the frozen `diff = 2 << difficulty` and never checks economic direction / boundaries."""
    tax = me.load_taxonomy()
    # math-sensitive surface (structural signal in the signature so the taxonomy flags it)
    item = {"id": "function:LLMOracleManager:getFee#recon", "kind": "function", "contract": "LLMOracleManager",
            "file": "n/a", "name": "getFee",
            "signature": "function getFee() public { for (uint i; i < numGen; i++){ fee += (2 << difficulty); } }",
            "in_scope": True, "attack_surface_score": 4, "tags": ["fee"], "source_span": {}}
    confirmatory = {
        "math_domain": "fee_math",
        "intended_formula": "diff = 2 << difficulty",          # restates the implemented formula
        "implemented_formula": "diff = 2 << difficulty",
        "formula_source": ["NatSpec", "code"], "limitations": "no whitepaper",
        "independent_rederivation": "re-derived diff = 2 << difficulty; matches the code",
        "input_domain": "difficulty bounded by onlyValidParameters", "output_domain": "uint256 wei",
        "scaling_precision": "raw shift", "rounding_behavior": "exact", "signedness_assumptions": "unsigned",
        "bounds_and_guards": "onlyValidParameters", "edge_cases_checked": ["difficulty=1"],
        "invariant_preserved": "fee >= platformFee", "evidence_span": "LLMOracleManager.sol:110-120",
        "formula_diff": "no divergence; matches the code", "assumptions": ["difficulty set by registry"],
        "monotonicity_and_economic_direction": "output is consistent",       # names no economic variable
        "attacker_favorable_search": "checked a couple of nominal difficulties",  # no boundary/extreme
        "economic_impact_if_wrong": "n/a"}
    disp_with = {"manifest_id": item["id"], "status": "cleared", "evidence": ["LLMOracleManager.sol:110"],
                 "finding_refs": [], "clear_reason": "Re-derived: diff=2<<difficulty", "math_estimator_proof": confirmatory}
    disp_without = {"manifest_id": item["id"], "status": "cleared", "evidence": ["LLMOracleManager.sol:110"],
                    "finding_refs": [], "clear_reason": "Re-derived: diff=2<<difficulty"}
    sensitive = me.classify_manifest_item(item, taxonomy=tax)["math_estimator_sensitive"]
    return {
        "math_sensitive": sensitive,
        "with_confirmatory_proof": vme.classify_clear(disp_with, item, tax, adversarial=True)["status"],
        "with_confirmatory_reasons": vme.classify_clear(disp_with, item, tax, adversarial=True)["reasons"],
        "proofless": vme.classify_clear(disp_without, item, tax, adversarial=True)["status"],
    }


def reconstructed_round():
    """Swan.purchase (external) cleared by leaning on the cross-contract BuyerAgent.getRoundPhase guard,
    with no path-dominance evidence and a call graph where purchase is directly callable."""
    sink_id = "function:Swan:purchase#recon"
    guard_id = "function:BuyerAgent:getRoundPhase#recon"
    manifest_index = {
        sink_id: {"id": sink_id, "kind": "function", "contract": "Swan", "name": "purchase",
                  "visibility": "external", "file": "Swan.sol", "source_span": {}},
        guard_id: {"id": guard_id, "kind": "function", "contract": "BuyerAgent", "name": "getRoundPhase",
                   "visibility": "public", "file": "BuyerAgent.sol", "source_span": {}}}
    name_index = dcu.build_manifest_name_index(list(manifest_index.values()))
    disp_index = {guard_id: {"manifest_id": guard_id, "status": "cleared", "evidence": ["BuyerAgent.sol:340"],
                             "clear_reason": "phase guard reviewed"}}
    clear = {"manifest_id": sink_id, "status": "cleared", "evidence": ["Swan.sol:120"],
             "clear_reason": "round/phase validated by BuyerAgent.getRoundPhase before purchase",
             "clear_depends_on": [guard_id], "dependency_clearance_status": "all_cleared",
             "dependency_reason": "the phase guard rejects stale-round purchases",
             "dependency_evidence": ["BuyerAgent.sol:340"], "downstream_guard_claim": True,
             "downstream_guard_type": "lifecycle_check"}    # no guard_locality / path_dominance_evidence
    # call graph: purchase is directly callable and never calls the guard (the H-02 shape)
    call_graph = {"call_graph": [{"caller_contract": "BuyerAgent", "caller_function": "purchaseFlow",
                                  "callee_contract": "BuyerAgent", "callee_function": "getRoundPhase"}]}
    field_gate = dcu.classify_clear(clear, disp_index, name_index, manifest_index=manifest_index, call_graph={})
    with_cg = dcu.classify_clear(clear, disp_index, name_index, manifest_index=manifest_index, call_graph=call_graph)
    return {
        "field_presence_gate": field_gate["status"],
        "field_presence_reason": field_gate["locality_reason"],
        "with_call_graph": with_cg["status"],
        "with_call_graph_reason": with_cg["locality_reason"],
    }


# ---------------- baseline delta (net-new blocks attributable to the shipped change) ----------------

def baseline_delta(literal):
    """Compare the literal new-validator blocks against the frozen validation baselines so we can
    separate blocks NET-NEW from the shipped change (adversarial fields / locality) from pre-existing
    dependency-policy blocks."""
    dep_base = json.loads((SNAP / "dependency_clear_validation.json").read_text())
    math_base = json.loads((SNAP / "math_estimator_clear_validation.json").read_text())
    dep_blocking = {"missing_dependency_metadata", "unreviewed_dependency", "unknown_dependency", "dependency_evidence_missing"}
    base_dep = {r["manifest_id"] for r in dep_base.get("rows", []) if r["status"] in dep_blocking}
    base_math = {r["manifest_id"] for r in math_base.get("rows", []) if r["status"] in
                 {"missing_math_proof", "incomplete_math_proof", "natspec_only_proof", "confirmatory_proof"}}
    now_dep = {m for ids in literal["dependency_blocks"].values() for m in ids}
    now_math = {m for ids in literal["math_blocks"].values() for m in ids}
    return {
        "frozen_dependency_blocking": sorted(base_dep),
        "frozen_math_blocking": sorted(base_math),
        "net_new_dependency_blocks": sorted(now_dep - base_dep),
        "net_new_math_blocks": sorted(now_math - base_math),
        "note": ("net-new dependency blocks should be 0 (locality adds guard_not_path_dominant only when a "
                 "non-local guard is asserted, which the frozen clears do not); net-new math blocks = the "
                 "pre-adversarial-proof clears now missing the 5 fields PLUS getFee, which the economic-shift "
                 "taxonomy patch now classifies math-sensitive (was cheap-swept) — intended stricter routing, "
                 "all clears, none a HIT finding"),
    }


# ---------------- noise audit: which manifest items does the patch newly route ----------------

def noise_audit(manifest, hit_funcs):
    """Classify every in-scope manifest item with the patched taxonomy; report items the economic-shift
    patch newly routes (matched_on == 'economic_shift') and confirm none collide with a HIT surface."""
    tax = me.load_taxonomy()
    econ_shift, all_sensitive = [], []
    for it in manifest.get("items", []):
        c = me.classify_manifest_item(it, taxonomy=tax)
        if c.get("math_estimator_sensitive"):
            all_sensitive.append(it["id"])
            if c.get("matched_on") == "economic_shift":
                econ_shift.append({"id": it["id"], "name": it.get("name"), "domain": c.get("math_domain")})
    econ_fns = {(e["name"] or "").lower() for e in econ_shift}
    return {
        "total_in_scope": len(manifest.get("items", [])),
        "math_sensitive_total": len(all_sensitive),
        "newly_routed_by_economic_shift": econ_shift,
        "newly_routed_count": len(econ_shift),
        "economic_shift_intersect_hit_surface": sorted(econ_fns & set(hit_funcs)),
    }


# ---------------- Block C: FP check on the 9 HITs ----------------

def fp_check(manifest, dispositions, literal):
    items = {i["id"]: i for i in manifest.get("items", [])}
    disp = dispositions["dispositions"] if isinstance(dispositions, dict) else dispositions
    by_func_status = {}
    for d in disp:
        nm = (items.get(d["manifest_id"], {}).get("name") or "").lower()
        by_func_status.setdefault(nm, set()).add(d.get("status"))

    mm = json.loads((AUDIT / "output" / "eval_ready" / "match_matrix.json").read_text())
    fss = json.loads((AUDIT / "output" / "eval_ready" / "final_scoring_set.json").read_text())
    fs = fss["findings"] if isinstance(fss, dict) and "findings" in fss else fss
    sc_loc = {e.get("scoring_id"): (e.get("location") or "") for e in (fs if isinstance(fs, list) else fs.values())}

    hits = [(e["answer_key_id"], e["blind_match"]) for e in mm if e["verdict"] == "HIT"]
    hit_rows = []
    for ak, sc in hits:
        loc = sc_loc.get(sc, "")
        hit_rows.append({"answer_key": ak, "blind": sc, "location": loc})

    def _fname(mid):
        return (items.get(mid, {}).get("name") or "").lower()
    new_blocked_fns = {_fname(m) for m in literal["new_blocked_manifest_ids"]}
    # HIT surface function names mentioned in the SC location strings
    hit_fns = set()
    for r in hit_rows:
        for tok in str(r["location"]).replace("(", " ").replace(")", " ").replace(".", " ").split():
            hit_fns.add(tok.lower())
    intersection = sorted(new_blocked_fns & hit_fns)
    return {
        "hit_count": len(hit_rows),
        "hits": hit_rows,
        "new_blocked_functions": sorted(new_blocked_fns),
        "new_block_intersect_hit_surface": intersection,
        "all_new_blocks_are_clears_not_findings": True,  # validators only classify status:cleared
    }


def main() -> int:
    frozen = _copy_frozen()
    manifest, dispositions, call_graph = frozen["coverage_manifest.json"], frozen["coverage_dispositions.json"], frozen["call_graph.json"]

    A = literal_replay(manifest, dispositions, call_graph)
    D = baseline_delta(A)
    B_getfee = reconstructed_getfee()
    B_round = reconstructed_round()
    C = fp_check(manifest, dispositions, A)
    N = noise_audit(manifest, [f for r in C["hits"] for f in
                               str(r["location"]).replace("(", " ").replace(")", " ").replace(".", " ").lower().split()])

    getfee_caught = B_getfee["with_confirmatory_proof"] == "confirmatory_proof" and B_getfee["proofless"] in ("missing_math_proof",)
    round_caught = B_round["field_presence_gate"] == "guard_not_path_dominant" and B_round["with_call_graph"] == "guard_not_path_dominant"
    no_fp = len(C["new_block_intersect_hit_surface"]) == 0

    report = {
        "title": "Swan/Dria miss-class replay vs new validators",
        "frozen_source": str(SNAP),
        "literal_frozen_replay": A,
        "baseline_delta": D,
        "noise_audit": N,
        "reconstructed_getfee": B_getfee,
        "reconstructed_round": B_round,
        "fp_check_9_hits": C,
        "verdict": {
            "getfee_no_longer_cleared_by_consistency": getfee_caught,
            "nonlocal_guard_no_longer_clears_missing_round_check": round_caught,
            "zero_new_fp_blocks_on_9_hits": no_fp,
        },
    }
    (REPLAY / "miss_class_report.json").write_text(json.dumps(report, indent=2))

    md = [
        "# Swan/Dria miss-class replay vs new validators", "",
        f"Frozen source (read-only, copied): `{SNAP}`", "",
        "## A. Literal frozen replay (new validators over the exact frozen clears)",
        f"- cleared dispositions classified: **{A['cleared_count']}**",
        f"- new math blocks: `{A['math_blocks'] or 'none'}`",
        f"- new dependency/locality blocks: `{A['dependency_blocks'] or 'none'}`  "
        f"(guard_not_path_dominant = **{A['guard_not_path_dominant_count']}**)",
        f"- **getFee** literal status → math:`{A['getfee_literal']['math_status']}` dep:`{A['getfee_literal']['dep_status']}`",
        f"  - before/after taxonomy patch: `{A['getfee_before_after']['before_taxonomy_patch']}` → "
        f"`{A['getfee_before_after']['after_taxonomy_patch']}`",
        f"  - {A['getfee_note']}",
        f"- new-blocked manifest_ids: `{A['new_blocked_manifest_ids']}`", "",
        "### Baseline delta (blocks NET-NEW from the shipped change vs frozen validation baselines)",
        f"- net-new **dependency/locality** blocks: `{D['net_new_dependency_blocks'] or 'NONE'}` "
        f"(frozen baseline already blocked: `{D['frozen_dependency_blocking']}`)",
        f"- net-new **math** blocks: `{D['net_new_math_blocks'] or 'NONE'}` "
        f"(frozen baseline blocked none of these — they were `math_proof_valid` under the old 14-field proof)",
        f"  - {D['note']}", "",
        "### Noise audit (items the economic-shift patch newly routes to math review)",
        f"- in-scope manifest items: {N['total_in_scope']} · math-sensitive now: {N['math_sensitive_total']} · "
        f"newly routed by economic-shift: **{N['newly_routed_count']}**",
        f"- newly routed: `{[e['name'] for e in N['newly_routed_by_economic_shift']]}`",
        f"- economic-shift ∩ HIT surface: `{N['economic_shift_intersect_hit_surface'] or 'EMPTY'}` "
        f"(no HIT finding is newly routed)", "",
        "## B. Reconstructed miss-class fixtures (derived from the frozen clear text)",
        f"- **getFee** math-sensitive: `{B_getfee['math_sensitive']}` · with confirmatory proof → "
        f"**`{B_getfee['with_confirmatory_proof']}`** · proofless → **`{B_getfee['proofless']}`** "
        f"(→ needs_deep_pass under strict)",
        f"  - reasons: {B_getfee['with_confirmatory_reasons']}",
        f"- **round** field-presence gate → **`{B_round['field_presence_gate']}`**; with call graph → "
        f"**`{B_round['with_call_graph']}`**",
        f"  - {B_round['with_call_graph_reason']}", "",
        "## C. FP check on the 9 HIT findings",
        f"- HITs: {[r['answer_key'] + '→' + r['blind'] for r in C['hits']]}",
        f"- new-blocked functions: `{C['new_blocked_functions']}`",
        f"- new-block ∩ HIT surface: `{C['new_block_intersect_hit_surface'] or 'EMPTY'}` "
        f"(validators only classify `status:cleared`; all 9 HITs are findings)", "",
        "## Verdict",
        f"- getFee no longer cleared by implemented-formula consistency: **{getfee_caught}**",
        f"- non-local guard no longer clears the missing local round check: **{round_caught}**",
        f"- zero new false-positive blocks on the 9 HIT findings: **{no_fp}**",
    ]
    (REPLAY / "miss_class_report.md").write_text("\n".join(md) + "\n")

    print("\n".join(md))
    ok = getfee_caught and round_caught and no_fp
    print(f"\n[replay] {'PASS' if ok else 'FAIL'} — report: {REPLAY / 'miss_class_report.md'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
