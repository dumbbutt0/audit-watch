#!/usr/bin/env python3
"""P278 — expanded validation queue + evidence-package extraction (RESEARCH-ONLY, ADVISORY, UN-WIRED).

Consumes a p277/p278 replay out-dir (shadow harness candidates + coverage_decisions + triage_decisions) and builds the
validation queue (<= validation_queue_budget) with class-coverage reporting + anti-monoculture(40%) check, then
auto-extracts an evidence package per queue candidate from the harness mechanism bodies. Any evidence field that is
empty OR equals an 'operator-to-derive' placeholder is recorded MISSING (the honest completeness signal). Never sets
severity/reportability/submission/confirmed.

Usage:
  python scripts/research/expanded_validation_queue.py --replay-dir <dir> --out-dir <dir> [--inject <handpkgs.json>] [--quiet]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_expanded_validation_queue.json").read_text())
LABEL = "SUPERVISED_EVAL"
PLACEHOLDERS = {str(x).strip().lower() for x in CFG["placeholder_markers"]}


def _load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def _present(v) -> bool:
    """A value is 'present' if it is non-empty and not a placeholder ('operator-to-derive' etc.)."""
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (list, dict)):
        return len(v) > 0
    s = str(v).strip().lower()
    if s in PLACEHOLDERS:
        return False
    # treat a field that merely echoes the operator-to-derive prompt as missing
    return "operator-to-derive" not in s and "operator to derive" not in s and len(s) > 0


def _evidence_from_mechanism(cid, award_class, contract, function, cand, why) -> dict:
    """Map populated harness mechanism fields -> evidence package; placeholders -> MISSING."""
    mechs = cand.get("generated_mechanisms") or []
    m = mechs[0] if mechs else {}
    rf = (m.get("ranking_features_for_profile_C") or {})
    pkg = {
        "candidate_id": cid, "award_class": award_class, "contract_function": f"{contract}.{function}",
        "source_refs": m.get("source_backed_trigger") or cand.get("locus"),
        "mechanism_hypothesis": m.get("mechanism_summary"),
        "root_cause": m.get("source_backed_trigger"),
        "affected_state_vars": m.get("affected_state_assets_permissions"),
        "attacker_model": m.get("attacker_action"),
        "attacker_controlled_inputs": m.get("attacker_action"),
        "victim_gainer": m.get("victim_gainer_hypothesis"),
        "state_value_liveness_delta": m.get("expected_value_delta"),
        "invariant_expected": None,
        "invariant_broken": None,
        "tx_sequence": None,
        "terminality_or_amplification": m.get("terminality_hypothesis") or m.get("amplification_hypothesis"),
        "runner_up_mechanism": "candidate_for_runner_up_overtake" if rf.get("candidate_for_runner_up_overtake") else None,
        "why_selected": why,
        "falsification_questions": m.get("falsification_question"),
        "refutation_result": None,
        "poc_feasibility_tier": None,
        "poc_assertion": None,
        "unresolved_assumptions": m.get("assumptions"),
        "evidence_source": "auto_extracted_from_harness",
    }
    pkg["missing_fields"] = sorted([f for f in CFG["readiness_required_dimensions"] if not _present(pkg.get(f))])
    return pkg


def build(replay_dir: Path, out_dir: Path, inject: Path | None, quiet: bool) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    shadow = _load(replay_dir / "shadow" / "recall_advisory_candidates.json") or {}
    cands = {c.get("candidate_id"): c for c in shadow.get("advisory_candidates", [])}
    cov = _load(replay_dir / "coverage_decisions.json") or {}
    tri = _load(replay_dir / "triage_decisions.json") or {}
    cls_by_id = {d["id"]: d["award_class"] for d in cov.get("decisions", [])}
    handoff = cov.get("handoff_queue_to_p269", [])
    tri_sel = {d["id"] for d in tri.get("decisions", []) if d.get("outcome", "").startswith("SELECT_FOR")}

    budget = CFG["validation_queue_budget"]
    queue_ids = handoff[:budget]  # handoff is already coverage-balanced + budget-capped
    queue, packages = [], []
    for cid in queue_ids:
        c = cands.get(cid, {})
        award_class = cls_by_id.get(cid, "UNKNOWN_OTHER")
        why = "coverage-routed" + ("; triage-selected" if cid in tri_sel else "")
        pkg = _evidence_from_mechanism(cid, award_class, c.get("contract"), c.get("function"), c, why)
        packages.append(pkg)
        queue.append({"candidate_id": cid, "award_class": award_class, "locus": c.get("locus"),
                      "in_triage_select": cid in tri_sel, "missing_fields": pkg["missing_fields"]})

    # ---- P292: internal-locus duplicate-class admission exception ----
    # Default dedup is preserved (handoff already applied COVERAGE_DEFER_DUPLICATE_CLASS). Here we ADMIT distinct internal
    # reward/accounting/share/index loci that coverage deferred as duplicate-class, as a SEPARATE bounded pool appended
    # on top of the base queue (no eviction). Narrow: never re-admits a non-internal duplicate.
    dup_decisions = []
    icfg = CFG.get("internal_locus_admission") or {}
    if icfg.get("enabled"):
        elig = set(icfg.get("eligible_classes", []))
        sig = [s.lower() for s in icfg.get("signal_terms", [])]
        same_cap = int(icfg.get("max_same_class_admissions", 2))
        total_cap = int(icfg.get("max_total_admissions", 5))
        admitted_fns = {(q.get("award_class"), str(q.get("locus") or "").split(":")[-1]) for q in queue}
        # rank deferred internal-locus candidates deterministically (class-relevance + reached-from-queued)
        deferred = [d for d in cov.get("decisions", []) if d.get("label") == "COVERAGE_DEFER_DUPLICATE_CLASS"]
        queued_loci = {str(q.get("locus") or "") for q in queue}

        def _rank(d):
            c = cands.get(d["id"], {})
            nm = str(c.get("function", "")).lower()
            reached = str(c.get("reached_from_public_entry", ""))
            relevance = sum(1 for t in sig if t in nm)
            reached_queued = any(reached.split(".")[-1] and reached.split(".")[-1] in ql for ql in queued_loci)
            return (-relevance, 0 if reached_queued else 1, d["id"])
        same_class_count: Counter = Counter()
        total_adm = 0
        for d in sorted(deferred, key=_rank):
            cid = d["id"]; c = cands.get(cid, {}); cls = cls_by_id.get(cid, d.get("award_class", "UNKNOWN_OTHER"))
            competing = next((q["candidate_id"] for q in queue if q.get("award_class") == cls), None)
            dec = {"candidate_id": cid, "award_class": cls,
                   "reached_from_public_entry": c.get("reached_from_public_entry"),
                   "call_path": c.get("call_path"), "competing_same_class_candidate": competing}
            # eligibility (all must hold)
            nm = str(c.get("function", "")).lower()
            ok = (bool(c.get("internal_locus")) and bool(c.get("reached_from_public_entry"))
                  and bool(c.get("source_span")) and cls in elig and any(t in nm for t in sig)
                  and (cls, c.get("function")) not in admitted_fns)
            if not ok:
                dec["duplicate_class_decision"] = "DEFERRED_DUPLICATE_CLASS"
                dec["internal_locus_admission_reason"] = "not an eligible distinct internal-locus exception"
                dec["admission_cap_status"] = "n/a"
                dup_decisions.append(dec); continue
            # caps
            if total_adm >= total_cap or same_class_count[cls] >= same_cap:
                dec["duplicate_class_decision"] = "DEFERRED_INTERNAL_LOCUS_CAP"
                dec["internal_locus_admission_reason"] = "internal-locus admission cap reached"
                dec["admission_cap_status"] = f"total={total_adm}/{total_cap} class={same_class_count[cls]}/{same_cap}"
                dup_decisions.append(dec); continue
            # anti-monoculture on the COMBINED queue (tentative)
            tentative = Counter(q["award_class"] for q in queue); tentative[cls] += 1
            nn = sum(tentative.values()) or 1
            mf = max(tentative.values()) / nn
            if (mf > CFG["anti_monoculture_max_class_fraction"] and nn >= 5
                    and len(tentative) >= CFG["anti_monoculture_min_plausible_classes"]):
                dec["duplicate_class_decision"] = "DEFERRED_MONOCULTURE_GUARD"
                dec["internal_locus_admission_reason"] = f"would push {cls} class fraction to {mf:.2f} (>40%)"
                dec["admission_cap_status"] = f"total={total_adm}/{total_cap}"
                dup_decisions.append(dec); continue
            # ADMIT
            why = f"internal-locus exception (distinct {cls} reached from {c.get('reached_from_public_entry')})"
            pkg = _evidence_from_mechanism(cid, cls, c.get("contract"), c.get("function"), c, why)
            pkg["internal_locus"] = True
            packages.append(pkg)
            queue.append({"candidate_id": cid, "award_class": cls, "locus": c.get("locus"),
                          "internal_locus": True, "reached_from_public_entry": c.get("reached_from_public_entry"),
                          "in_triage_select": False, "missing_fields": pkg["missing_fields"]})
            admitted_fns.add((cls, c.get("function")))
            same_class_count[cls] += 1; total_adm += 1
            dec["duplicate_class_decision"] = "ADMITTED_INTERNAL_LOCUS_EXCEPTION"
            dec["internal_locus_admission_reason"] = why
            dec["admission_cap_status"] = f"total={total_adm}/{total_cap} class={same_class_count[cls]}/{same_cap}"
            dup_decisions.append(dec)
    # base-queue candidates get an ADMITTED_PRIMARY_CLASS marker for the decisions report
    for q in queue:
        if not q.get("internal_locus") and not any(dd["candidate_id"] == q["candidate_id"] for dd in dup_decisions):
            dup_decisions.append({"candidate_id": q["candidate_id"], "award_class": q.get("award_class"),
                                  "duplicate_class_decision": "ADMITTED_PRIMARY_CLASS"})

    # optional hand-authored evidence packages (corpus source-derived) merged in
    injected = []
    if inject and inject.exists():
        for pkg in json.loads(inject.read_text()).get("packages", []):
            pkg.setdefault("evidence_source", "hand_authored_corpus_sample")
            pkg["missing_fields"] = sorted([f for f in CFG["readiness_required_dimensions"] if not _present(pkg.get(f))])
            packages.append(pkg)
            queue.append({"candidate_id": pkg["candidate_id"], "award_class": pkg.get("award_class"),
                          "locus": pkg.get("contract_function"), "in_triage_select": True,
                          "missing_fields": pkg["missing_fields"]})
            injected.append(pkg["candidate_id"])

    # coverage compliance + anti-monoculture(40%)
    class_counts = Counter(q["award_class"] for q in queue)
    n = len(queue) or 1
    max_frac = max(class_counts.values()) / n if class_counts else 0.0
    plausible_classes = len(class_counts)
    monoculture_ok = (max_frac <= CFG["anti_monoculture_max_class_fraction"]) or \
                     (plausible_classes < CFG["anti_monoculture_min_plausible_classes"])
    coverage_met = {cls: class_counts.get(cls, 0) for cls in CFG["class_coverage_minimums"]}

    result = {"label": LABEL, "mode": "SUPERVISED_EVAL_VALIDATION_QUEUE", "replay_dir": str(replay_dir.name),
              "is_gate": False, "research_only": True, "emits_findings": False,
              "validation_queue_budget": budget, "queue_size": len(queue),
              "class_distribution": dict(class_counts), "max_class_fraction": round(max_frac, 3),
              "anti_monoculture_ok": monoculture_ok, "coverage_counts": coverage_met,
              "internal_locus_admitted": [q["candidate_id"] for q in queue if q.get("internal_locus")],
              "duplicate_class_decisions": dup_decisions,
              "hand_injected": injected, "queue": queue}
    (out_dir / "validation_queue.json").write_text(json.dumps(result, indent=2))
    (out_dir / "evidence_packages.json").write_text(json.dumps(
        {"label": LABEL, "is_gate": False, "emits_findings": False, "packages": packages}, indent=2))
    if not quiet:
        print(f"[p278:queue] {replay_dir.name}: queue={len(queue)} classes={plausible_classes} "
              f"maxfrac={max_frac:.2f} monoculture_ok={monoculture_ok} injected={len(injected)}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--inject")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    build(Path(a.replay_dir), Path(a.out_dir), Path(a.inject) if a.inject else None, a.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
