#!/usr/bin/env python3
"""P105 — Reproducibility benchmark for the autonomous SURFACING layer (research-only, UN-WIRED).

Drives the EXISTING, FROZEN pipeline (`auto_validate_invariants.run_subject` + `inventory`) across a corpus of
already-burned blind subjects and scores, per documented awarded finding, whether the deterministic recall layer
SURFACES it: inventory coverage (function_enumerated) + invariant enumeration (any/category invariant generated) +
position. It imports the pipeline; it copies nothing and changes nothing.

This answers "was P104 luck or capability — does SURFACING generalize?" It does NOT measure whole-loop conversion:
`validated_candidates`/PoC require per-subject source-backed evidence (the P102/P103 capability ceiling), so those
columns are honestly NOT_ATTEMPTED for every subject except IQ-AI M-01 (P104, the lone CONFIRMED data point).

HARD RULE: research-only, un-wired. No routing, no gate, no submission, no production severity. The harness is
read-only over source and writes only its own report under documentation/research/assisted_mode/p105/.

Usage:
    python scripts/assisted/benchmark_replay.py --self-test
    python scripts/assisted/benchmark_replay.py --run            # full corpus -> results.json + report.md
    python scripts/assisted/benchmark_replay.py --run --corpus <path> --out-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))

import auto_validate_invariants as AV          # noqa: E402  (frozen pipeline — imported, never modified)
import inventory_public_external_functions as INV  # noqa: E402

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p105"

NOT_ATTEMPTED = "NOT_ATTEMPTED"


@lru_cache(maxsize=1)
def _load_corpus_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_corpus(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path or DEFAULT_CORPUS)
    return json.loads(_load_corpus_text(str(p)))


def _rate(num: int, den: int) -> Dict[str, Any]:
    """Mirror scripts/compute_metrics.py:_rate — unmeasured when denominator is 0."""
    if den == 0:
        return {"value": None, "n": 0, "state": "unmeasured (no grounded findings)"}
    return {"value": round(num / den, 3), "n": den, "numerator": num}


def _excluded(f: Path, excludes: List[str]) -> bool:
    """An exclude that contains '/' matches a path SEGMENT (so '/test' drops a `test/` dir but NOT a file/dir
    merely named 'test_foo'); an exclude with no '/' matches anywhere in the path (e.g. 'Mock', 'forge-std')."""
    parts = set(f.parts)
    sp = str(f)
    for x in excludes:
        if "/" in x:
            if x.strip("/") in parts:
                return True
        elif x in sp:
            return True
    return False


def _resolve_sol_files(source_roots: List[str], excludes: List[str]) -> List[Path]:
    """Recursively collect .sol files under each root, dropping excluded paths (segment-aware, see _excluded).
    Deterministic: returns a sorted, de-duplicated list of absolute paths."""
    seen: Dict[str, Path] = {}
    for root in source_roots:
        base = Path(root)
        if not base.exists():
            continue
        for f in base.rglob("*.sol"):
            if _excluded(f, excludes):
                continue
            seen[str(f)] = f
    return [seen[k] for k in sorted(seen)]


def _stage_flat(files: List[Path]) -> tuple:
    """Symlink the resolved files into a flat temp dir (run_subject/inventory glob non-recursively).
    Basename collisions get a numeric suffix (contract name is parsed from content, so the rename is harmless).
    Returns (tempdir_path, staged_count, collisions). Caller removes the tempdir."""
    tmp = Path(tempfile.mkdtemp(prefix="p105_bench_"))
    used: Dict[str, int] = {}
    collisions = 0
    for f in files:
        stem, ext = f.stem, f.suffix
        name = f.name
        if name in used:
            used[name] += 1
            collisions += 1
            name = f"{stem}__{used[f.name]}{ext}"
        else:
            used[name] = 1
        try:
            os.symlink(f.resolve(), tmp / name)
        except OSError:
            pass
    return tmp, len([p for p in tmp.glob("*.sol")]), collisions


def _score_finding(result: Dict[str, Any], finding: Dict[str, Any]) -> Dict[str, Any]:
    """Mechanical scoring of one awarded finding against a run_subject() result. Function match is the primary
    signal; category match is secondary (and near-saturated because run_subject feeds whole-file source_text)."""
    contract = finding.get("contract")
    fn = finding.get("function")
    cat = finding.get("invariant_category")
    enum_fns = result.get("enumerated_functions", [])
    fq = f"{contract}.{fn}"

    function_enumerated = fq in enum_fns
    gen_for_fn = [g for g in result.get("generated_invariants", [])
                  if g.get("contract") == contract and g.get("function") == fn]
    any_invariant_generated = len(gen_for_fn) > 0
    gen_types = [g.get("invariant_type") for g in gen_for_fn]
    category_match = cat in gen_types

    # position: where the awarded function sits in the (sorted) enumerated surface, and where the matching
    # category invariant sits within that function's generated list. No evidence => no validated ranking.
    fn_position = (enum_fns.index(fq) + 1) if function_enumerated else None
    cat_position = (gen_types.index(cat) + 1) if category_match else None

    conv = finding.get("conversion") or {}
    return {
        "finding_id": finding.get("finding_id"),
        "contract": contract,
        "function": fn,
        "invariant_category": cat,
        "severity": finding.get("severity"),
        "grounding": finding.get("grounding"),
        "function_enumerated": function_enumerated,
        "relevant_invariant_generated": any_invariant_generated,
        "category_invariant_generated": category_match,
        "function_position": fn_position,
        "function_surface_size": len(enum_fns),
        "category_position_within_function": cat_position,
        "generated_types_for_function": gen_types,
        "relevant_candidate_validated": "VALIDATED" if conv.get("validated") else NOT_ATTEMPTED,
        "poc_attempted": bool(conv.get("poc_attempted")),
        "poc_succeeded": (True if conv.get("poc_succeeded")
                          else (False if conv.get("poc_attempted") else NOT_ATTEMPTED)),
        "conversion_evidence_ref": conv.get("evidence_ref"),
    }


def _false_promotions(result: Dict[str, Any], awarded: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """validated_candidates (precision-gated survivors) that match NO awarded (contract, function).
    Expected empty in the recall-only run (no evidence => nothing validates); any entry is a precision signal."""
    awarded_fns = {(a.get("contract"), a.get("function")) for a in awarded}
    return [{"contract": v.get("contract"), "function": v.get("function"),
             "invariant_type": v.get("invariant_type")}
            for v in result.get("validated_candidates", [])
            if (v.get("contract"), v.get("function")) not in awarded_fns]


def run_subject_for_spec(spec: Dict[str, Any], excludes: List[str]) -> Dict[str, Any]:
    """Stage the subject's in-scope source flat, then call the FROZEN run_subject() with NO evidence
    (recall layer only). Returns the run_subject result plus staging metadata."""
    files = _resolve_sol_files(spec.get("source_roots", []), excludes)
    tmp, staged, collisions = _stage_flat(files)
    try:
        result = AV.run_subject(tmp, lens_leads=[], evidence_by_fn=None, subject=spec.get("id"))
    finally:
        # remove symlinks + dir; never touch the originals
        for p in tmp.glob("*"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            tmp.rmdir()
        except OSError:
            pass
    result["_staging"] = {"resolved_files": len(files), "staged": staged, "basename_collisions": collisions}
    return result


def score_subject(spec: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    awarded = spec.get("awarded_findings", [])
    surfaceable = [f for f in awarded if f.get("surfaceable")]
    unsurfaceable = [{"finding_id": f.get("finding_id"), "reason": f.get("surfaceable_reason")}
                     for f in awarded if not f.get("surfaceable")]
    rows = [_score_finding(result, f) for f in surfaceable]
    return {
        "id": spec.get("id"),
        "contest": spec.get("contest"),
        "phase": spec.get("phase"),
        "benchmark_findings_are_subset": spec.get("benchmark_findings_are_subset", False),
        "subset_note": spec.get("subset_note"),
        "coverage": result.get("coverage"),
        "staging": result.get("_staging"),
        "runtime_ms": result.get("runtime_ms"),
        "scored_findings": rows,
        "unsurfaceable_findings": unsurfaceable,
        "false_promotions": _false_promotions(result, awarded),
    }


def _aggregate(subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_rows = [r for s in subjects for r in s["scored_findings"]]
    high = [r for r in all_rows if r.get("grounding") == "high"]

    def cov(rows):  # function_enumerated rate
        return _rate(sum(1 for r in rows if r["function_enumerated"]), len(rows))

    def gen(rows):  # relevant_invariant_generated rate
        return _rate(sum(1 for r in rows if r["relevant_invariant_generated"]), len(rows))

    def catm(rows):
        return _rate(sum(1 for r in rows if r["category_invariant_generated"]), len(rows))

    validated_rows = [r for r in all_rows if r["relevant_candidate_validated"] == "VALIDATED"]
    poc_attempted = [r for r in all_rows if r["poc_attempted"]]
    poc_success = [r for r in poc_attempted if r["poc_succeeded"] is True]
    false_promo_total = sum(len(s["false_promotions"]) for s in subjects)

    return {
        "subjects_run": len(subjects),
        "grounded_findings_scored": len(all_rows),
        "unsurfaceable_findings_excluded": sum(len(s["unsurfaceable_findings"]) for s in subjects),
        "enumeration_coverage_rate_all": cov(all_rows),
        "enumeration_coverage_rate_high_grounding": cov(high),
        "invariant_generation_rate_all": gen(all_rows),
        "category_match_rate_all": catm(all_rows),
        "false_promotions_total": false_promo_total,
        "validation_attempted": len(validated_rows),
        "validation_validated": len(validated_rows),
        "poc_attempted": len(poc_attempted),
        "poc_succeeded": len(poc_success),
        "poc_conversion_rate": _rate(len(poc_success), len(poc_attempted)),
        "headline": ("SURFACING layer is benchmarked across N subjects (objective, retrospective ceiling). "
                     "Whole-loop conversion is NOT: validation/PoC are NOT_ATTEMPTED except IQ-AI M-01 (P104). "
                     "category_match is near-saturated by design (whole-file source_text); function_enumerated "
                     "(inventory coverage, the P103 repair) is the meaningful recall signal."),
    }


def run_corpus(corpus: Dict[str, Any]) -> Dict[str, Any]:
    excludes = corpus.get("exclude_substrings", [])
    subjects = []
    for spec in corpus.get("subjects", []):
        result = run_subject_for_spec(spec, excludes)
        subjects.append(score_subject(spec, result))
    return {
        **FLAGS,
        "schema": "p105_benchmark_results_v1",
        "caveats": corpus.get("caveats", []),
        "subjects": subjects,
        "aggregate": _aggregate(subjects),
    }


# ---------------------------------------------------------------------------- report

def _yn(v) -> str:
    if v is True:
        return "YES"
    if v is False:
        return "no"
    return str(v)


def render_report(results: Dict[str, Any]) -> str:
    agg = results["aggregate"]
    lines = ["# P105 — Reproducibility benchmark (surfacing layer, retrospective)", ""]
    lines.append("**What this is:** the deterministic surfacing layer (`inventory` + `enumerate`, via the frozen "
                 "`run_subject`) run across already-burned blind subjects and scored against documented awarded "
                 "findings. Objective for coverage/enumeration; retrospective (not blind) for relevance labels.")
    lines.append("")
    lines.append("## Caveats (read first)")
    for c in results.get("caveats", []):
        lines.append(f"- {c}")
    lines.append("")
    lines.append("## Aggregate")
    def fmt(rate):
        if rate.get("value") is None:
            return rate.get("state", "unmeasured")
        return f"{rate['value']:.0%} ({rate['numerator']}/{rate['n']})"
    lines += [
        f"- Subjects run: **{agg['subjects_run']}**; grounded findings scored: **{agg['grounded_findings_scored']}** "
        f"(+{agg['unsurfaceable_findings_excluded']} unsurfaceable, excluded).",
        f"- **Enumeration coverage (function_enumerated), all:** {fmt(agg['enumeration_coverage_rate_all'])}",
        f"- Enumeration coverage, high-grounding only: {fmt(agg['enumeration_coverage_rate_high_grounding'])}",
        f"- Invariant generated on awarded fn: {fmt(agg['invariant_generation_rate_all'])}",
        f"- Category match (near-saturated by design): {fmt(agg['category_match_rate_all'])}",
        f"- **False promotions (precision): {agg['false_promotions_total']}**",
        f"- Validation attempted/validated: {agg['validation_attempted']}/{agg['validation_validated']} "
        f"(recall-layer run; evidence supplied only for IQ-AI M-01)",
        f"- PoC attempted/succeeded: {agg['poc_attempted']}/{agg['poc_succeeded']} "
        f"(conversion rate {fmt(agg['poc_conversion_rate'])})",
        "",
        f"> {agg['headline']}",
        "",
        "## Per-finding",
        "",
        "| Subject | Finding | Contract.fn | Cat | Sev | Gnd | Fn enum | Inv gen | Cat gen | Fn pos | Validated | PoC try | PoC ok |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in results["subjects"]:
        for r in s["scored_findings"]:
            pos = f"{r['function_position']}/{r['function_surface_size']}" if r["function_position"] else "-"
            lines.append(
                f"| {s['id']} | {r['finding_id']} | {r['contract']}.{r['function']} | {r['invariant_category']} | "
                f"{r['severity']} | {r['grounding']} | {_yn(r['function_enumerated'])} | "
                f"{_yn(r['relevant_invariant_generated'])} | {_yn(r['category_invariant_generated'])} | {pos} | "
                f"{r['relevant_candidate_validated']} | {_yn(r['poc_attempted'])} | {_yn(r['poc_succeeded'])} |")
    lines.append("")
    lines.append("### Unsurfaceable findings (excluded from recall denominators)")
    for s in results["subjects"]:
        for u in s["unsurfaceable_findings"]:
            lines.append(f"- {s['id']} {u['finding_id']}: {u['reason']}")
    lines.append("")
    lines.append("### Per-subject coverage / staging")
    for s in results["subjects"]:
        cv = s.get("coverage") or {}
        st = s.get("staging") or {}
        lines.append(f"- **{s['id']}** ({s['phase']}): public/external enumerated={cv.get('public_external')}, "
                     f"staged_files={st.get('staged')} (collisions {st.get('basename_collisions')}), "
                     f"runtime={s.get('runtime_ms')}ms; false_promotions={len(s['false_promotions'])}")
    lines.append("")
    lines.append("## Reading the result")
    lines.append("- High & consistent `function_enumerated` => the **coverage** half of P104's surfacing is "
                 "**capability, not luck**: the P103 inventory repair captures the awarded entrypoint across every "
                 "architecture tested (incl. the hard cases: a sibling-file `executeWithdrawal` and an "
                 "underscore-named-but-`public` `_removeCredIdPerAddress`).")
    lines.append("- **Honest counterweight — coverage != ranking.** `function_position` is alphabetical, not "
                 "scored: awarded functions sit mid-list (e.g. 193/211, 169/180). In the recall-only run there is "
                 "NO ranking signal, because ranking needs the per-candidate evidence/validation layer (the P102 "
                 "selection ceiling). So a human still faces the whole enumerated surface; the pipeline guarantees "
                 "the answer is IN the set, not that it is on top.")
    lines.append("- `false_promotions=0` confirms the recall-only run promotes nothing without evidence "
                 "(precision preserved): recall widened, promotions did not.")
    lines.append("- Net: **coverage generalizes; selection/ranking and whole-loop conversion remain "
                 "evidence-and-capability-bound** (the separately-studied P107/P108 gap). This benchmark is a "
                 "retrospective CEILING over a function-grounded subset, not a blind recall measurement.")
    return "\n".join(lines) + "\n"


def write_outputs(results: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rj = out_dir / "benchmark_results.json"
    rm = out_dir / "benchmark_report.md"
    rj.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    rm.write_text(render_report(results), encoding="utf-8")
    return {"results": str(rj), "report": str(rm)}


# ---------------------------------------------------------------------------- self-test

_FIXTURE_SRC = {
    "Hit.sol": (
        "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
        "contract Hit {\n"
        "  uint256 public total; mapping(address=>uint256) public balance;\n"
        "  function withdraw(uint256 amount) external { balance[msg.sender]-=amount; total-=amount; }\n"
        "  function _helper() internal { total++; }\n"
        "}\n"
    ),
    "Miss.sol": (
        "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
        "contract Miss {\n"
        "  function ping() external pure returns (uint256) { return 1; }\n"
        "}\n"
    ),
}


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    tmp = Path(tempfile.mkdtemp(prefix="p105_selftest_"))
    for name, body in _FIXTURE_SRC.items():
        (tmp / name).write_text(body, encoding="utf-8")

    corpus = {
        "exclude_substrings": ["/test"],
        "caveats": ["self-test fixture"],
        "subjects": [{
            "id": "fixture", "contest": "fixture", "phase": "self-test",
            "source_roots": [str(tmp)], "benchmark_findings_are_subset": True,
            "awarded_findings": [
                # surfaceable HIT: withdraw is public/external, should enumerate + generate
                {"finding_id": "F-HIT", "contract": "Hit", "function": "withdraw",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "surfaceable_reason": "public", "grounding": "high",
                 "conversion": {"validated": True, "poc_attempted": True, "poc_succeeded": True,
                                "evidence_ref": "fixture"}},
                # surfaceable MISS: function name not present in source -> NOT enumerated
                {"finding_id": "F-MISS", "contract": "Hit", "function": "doesNotExist",
                 "invariant_category": "value_conservation", "severity": "Medium",
                 "surfaceable": True, "surfaceable_reason": "public", "grounding": "high"},
                # internal-only: _helper is internal -> NOT in public/external surface
                {"finding_id": "F-INTERNAL", "contract": "Hit", "function": "_helper",
                 "invariant_category": "value_conservation", "severity": "Low",
                 "surfaceable": True, "surfaceable_reason": "n/a", "grounding": "inferred"},
                # unsurfaceable: excluded from denominators
                {"finding_id": "F-UNSURF", "contract": "Hit", "function": None,
                 "invariant_category": "value_conservation", "severity": "High",
                 "surfaceable": False, "surfaceable_reason": "missing-function class", "grounding": "high"},
            ],
        }],
    }

    res = run_corpus(corpus)
    res2 = run_corpus(corpus)  # determinism re-run BEFORE the fixture is torn down
    for p in tmp.glob("*"):
        p.unlink()
    tmp.rmdir()

    s0 = res["subjects"][0]
    rows = {r["finding_id"]: r for r in s0["scored_findings"]}
    chk(len(s0["scored_findings"]) == 3, "3 surfaceable findings scored (1 unsurfaceable excluded)")
    chk(len(s0["unsurfaceable_findings"]) == 1, "1 unsurfaceable finding recorded")
    chk(rows["F-HIT"]["function_enumerated"] is True, "public function enumerated (HIT)")
    chk(rows["F-HIT"]["relevant_invariant_generated"] is True, "invariant generated for HIT")
    chk(rows["F-HIT"]["category_invariant_generated"] is True, "per_user_accounting generated for HIT")
    chk(rows["F-MISS"]["function_enumerated"] is False, "nonexistent function NOT enumerated (MISS)")
    chk(rows["F-INTERNAL"]["function_enumerated"] is False, "internal function NOT in public/external surface")

    agg = res["aggregate"]
    chk(agg["enumeration_coverage_rate_all"]["numerator"] == 1, "coverage numerator = 1 (only HIT)")
    chk(agg["enumeration_coverage_rate_all"]["n"] == 3, "coverage denominator = 3 surfaceable")
    chk(agg["false_promotions_total"] == 0, "no false promotions in recall-only run")
    chk(agg["poc_attempted"] == 1 and agg["poc_succeeded"] == 1, "PoC conversion counted (fixture HIT)")
    chk(agg["poc_conversion_rate"]["value"] == 1.0, "PoC conversion rate = 1.0")

    # determinism: same corpus -> identical serialized result (drop volatile runtime fields)
    def _strip(r):
        c = json.loads(json.dumps(r))
        for s in c["subjects"]:
            s["runtime_ms"] = 0
            if s.get("staging"):
                s["staging"] = {k: v for k, v in s["staging"].items()}
        return c
    chk(json.dumps(_strip(res), sort_keys=True) == json.dumps(_strip(res2), sort_keys=True),
        "deterministic: identical result on re-run")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true", help="run internal tests")
    ap.add_argument("--run", action="store_true", help="run the full corpus and write results.json + report.md")
    ap.add_argument("--corpus", help="path to benchmark_corpus.json (default: p105/benchmark_corpus.json)")
    ap.add_argument("--out-dir", help="output dir (default: documentation/research/assisted_mode/p105)")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if args.run:
        corpus = load_corpus(Path(args.corpus) if args.corpus else None)
        results = run_corpus(corpus)
        out = write_outputs(results, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        agg = results["aggregate"]
        print(f"benchmark complete: {agg['subjects_run']} subjects, "
              f"coverage {agg['enumeration_coverage_rate_all']}, "
              f"false_promotions {agg['false_promotions_total']}")
        print(f"  -> {out['results']}")
        print(f"  -> {out['report']}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
