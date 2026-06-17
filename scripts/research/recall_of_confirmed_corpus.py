#!/usr/bin/env python3
"""P295 — corpus-wide recall-of-confirmed harness (RESEARCH-ONLY, ADVISORY, UN-WIRED).

Measures, on the locally-answer-keyed subset (surfacing-first), the funnel
    awarded  ->  surfaced (recall ceiling)  ->  confirmed-by-execution (P294 verifier).
Awarded set + per-locus surfacing come from EXISTING read-only artifacts (reveal_score.json / ground_truth.jsonl /
match_matrix.json). Confirmation is overlaid by running the P294 executed-PoC verifier over each awarded locus's
mapped pocs/<id> dir — a candidate is confirmed ONLY by a real exploit-test forge PASS (L1+L2+L3). confirmed-FP is 0
by construction (only awarded loci with a passing exploit PoC count). Answer keys are never written.

Outputs: recall_funnel.json · verification_records.json · backlog.json · guard_report.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

CFG = json.loads((ROOT / "config/research_recall_corpus_map.json").read_text())
OUT = ROOT / "documentation/research/assisted_mode/p295_recall_of_confirmed_corpus/outputs"
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "reportable": False,
          "submission_ready": False, "concluded": False, "production_routing": False, "auto_submitted": False}


def _surfaced(val) -> bool:
    """A locus counts as surfaced if its reveal value is truthy or a descriptive (non-miss) string."""
    if val is True:
        return True
    if isinstance(val, str):
        v = val.strip().lower()
        return bool(v) and v not in ("false", "missed", "no") and "not surfaced" not in v
    return False


def _read(p):
    return json.loads((ROOT / p).read_text())


def _awarded_from_reveal(spec) -> list:
    d = _read(spec["reveal"])
    rows = d.get(spec["awarded_key"], [])
    out = []
    for r in rows:
        out.append({"id": r.get("id"), "locus": r.get("locus") or r.get("area"),
                    "surfaced": _surfaced(r.get("surfaced")), "surfaced_raw": r.get("surfaced"),
                    "match_level": r.get("match_level")})
    return out


def _awarded_beanstalk(spec) -> list:
    # An 'accepted' ground_truth entry is a SYSTEM finding confirmed to match an awarded bug (recorded_by
    # contest_result, evidence_class platform_confirmed) -> surfaced by definition. confirmed (by executed PoC)
    # is separate and requires a PoC (none yet -> all in the PoC backlog). Finding-level (no clean contract.fn locus).
    gt = [json.loads(l) for l in (ROOT / spec["ground_truth"]).read_text().splitlines() if l.strip()]
    acc = [r for r in gt if r.get("ground_truth_outcome") == "accepted"]
    out = []
    for r in acc:
        out.append({"id": r.get("finding_id"), "locus": r.get("title", "")[:60], "surfaced": True,
                    "surfaced_raw": f"accepted/{r.get('evidence_class', 'platform_confirmed')} (system finding matched)",
                    "match_level": "FINDING_LEVEL_ACCEPTED"})
    return out


def _verify(poc_dir, fid):
    try:
        return epv.verify_poc(ROOT / poc_dir, finding_id=fid)
    except Exception as e:  # fail-closed: a broken poc dir never confirms
        return {"attacker_verified": False, "status": f"error:{type(e).__name__}", "finding_id": fid}


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    audits = {}
    all_records = []
    backlog = {"surfaced_unconfirmed_poc_worklist": [], "missed_surfacing_worklist": []}
    agg = {"awarded": 0, "surfaced": 0, "confirmed": 0}  # over full_local denominators only
    additional_confirmed = []  # partial_local audits (no full denominator)

    for audit, spec in CFG["subset"].items():
        if spec.get("reveal"):
            awarded = _awarded_from_reveal(spec)
        elif spec.get("awarded_inline"):
            awarded = [{"id": a["id"], "locus": a["locus"], "surfaced": _surfaced(a.get("surfaced")),
                        "surfaced_raw": a.get("surfaced"), "match_level": None} for a in spec["awarded_inline"]]
        else:
            awarded = _awarded_beanstalk(spec)
        poc_map = spec.get("poc_map", {})
        confirmed_ids = []
        for a in awarded:
            pd = poc_map.get(a["id"])
            a["poc_dir"] = pd
            a["confirmed"] = False
            if pd:
                rec = _verify(pd, f"{audit}:{a['id']}")
                all_records.append({"audit": audit, "awarded_id": a["id"], "locus": a["locus"], **rec})
                a["confirmed"] = bool(rec.get("attacker_verified"))
            if a["confirmed"]:
                confirmed_ids.append(a["id"])
            elif a["surfaced"]:
                backlog["surfaced_unconfirmed_poc_worklist"].append(
                    {"audit": audit, "id": a["id"], "locus": a["locus"], "match_level": a.get("match_level")})
            else:
                backlog["missed_surfacing_worklist"].append({"audit": audit, "id": a["id"], "locus": a["locus"]})

        n_aw = len(awarded)
        n_surf = sum(1 for a in awarded if a["surfaced"])
        n_conf = sum(1 for a in awarded if a["confirmed"])
        full = spec.get("denominator") == "full_local"
        audits[audit] = {
            "denominator": spec.get("denominator"), "level": spec.get("level", "locus"),
            "awarded": n_aw, "surfaced": n_surf, "confirmed": n_conf,
            "recall_of_surfaced": round(n_surf / n_aw, 3) if n_aw else None,
            "recall_of_confirmed": round(n_conf / n_aw, 3) if (n_aw and full) else None,
            "confirmation_yield_on_surfaced": round(n_conf / n_surf, 3) if n_surf else None,
            "confirmed_loci": confirmed_ids}
        if full:
            agg["awarded"] += n_aw; agg["surfaced"] += n_surf; agg["confirmed"] += n_conf
        else:
            additional_confirmed += [f"{audit}:{i}" for i in confirmed_ids]

    # refutation controls must NOT confirm
    refutation = {}
    for fid, pd in CFG.get("refutation_controls", {}).items():
        rec = _verify(pd, fid)
        refutation[fid] = {"status": rec.get("status"), "attacker_verified": rec.get("attacker_verified")}
        all_records.append({"audit": "control", "awarded_id": fid, "locus": "(false hypothesis)", **rec})

    # confirmed-FP = a confirmed record that is NOT an awarded locus (impossible here: every confirmed maps to an
    # awarded id) OR a refutation control that confirmed. Must be 0.
    confirmed_fp = sum(1 for r in refutation.values() if r["attacker_verified"])

    funnel = dict(_STAMP, label="P295_RECALL_OF_CONFIRMED", mode="MEASURABLE_SUBSET",
                  audits=audits, aggregate_full_local={
                      **agg,
                      "recall_of_surfaced": round(agg["surfaced"] / agg["awarded"], 3) if agg["awarded"] else None,
                      "recall_of_confirmed": round(agg["confirmed"] / agg["awarded"], 3) if agg["awarded"] else None,
                      "confirmation_yield_on_surfaced": round(agg["confirmed"] / agg["surfaced"], 3) if agg["surfaced"] else None},
                  additional_confirmed_partial_local=additional_confirmed,
                  total_loci_confirmed_by_execution=agg["confirmed"] + len(additional_confirmed),
                  refutation_controls=refutation, confirmed_false_positive_count=confirmed_fp)

    (OUT / "recall_funnel.json").write_text(json.dumps(funnel, indent=2))
    (OUT / "verification_records.json").write_text(json.dumps(dict(_STAMP, records=all_records), indent=2))
    (OUT / "backlog.json").write_text(json.dumps(dict(_STAMP, **backlog), indent=2))
    # answer-key artifacts must be unchanged — record their hashes for the integrity check
    ak = {}
    for audit, spec in CFG["subset"].items():
        for k in ("reveal", "ground_truth", "match_matrix"):
            p = spec.get(k)
            if p and (ROOT / p).exists():
                ak[p] = hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16]
    (OUT / "guard_report.json").write_text(json.dumps(dict(
        _STAMP, module="recall_of_confirmed_corpus",
        confirmed_false_positive_count=confirmed_fp,
        total_confirmed=funnel["total_loci_confirmed_by_execution"],
        every_confirmed_has_real_log=all(
            any(x.get("passed") and x.get("log_ref") for x in r.get("runs", []))
            for r in all_records if r.get("attacker_verified")),
        answer_key_hashes=ak), indent=2))
    print(json.dumps({"aggregate_full_local": funnel["aggregate_full_local"],
                      "total_confirmed_incl_partial": funnel["total_loci_confirmed_by_execution"],
                      "confirmed_FP": confirmed_fp,
                      "backlog_poc": len(backlog["surfaced_unconfirmed_poc_worklist"]),
                      "backlog_missed": len(backlog["missed_surfacing_worklist"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
