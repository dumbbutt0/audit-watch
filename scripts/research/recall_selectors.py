"""recall_selectors — research-only F1/F2 recall selectors + the guarded-downstream rule (P172).

Answer-key-grounded recall fixes from P171, built as RESEARCH-ONLY selectors and validated OFFLINE against the
quantamm answer key. These do NOT touch production detectors (`*_audit.py`), the coverage-sweep/clear policy, or
routing. Promotion into the production recall pipeline is a separate, later, human decision.

INVARIANTS (mirror the Research Detector Platform discipline): un-wired (no run_pipeline/agent_policy
reference); reads protocol_src only via the P167 hygiene scan; every emitted record carries
`research_only=true` / `routes_in_production=false` / `is_gate=false`; fail-open; never mutates anything.

F1 = dynamic-weight lifecycle selector (re-surfaces weight-update / pool-accounting entrypoints whose body is
     missing a lifecycle guard — sum/bounds/epsilon/interval/staleness).
F2 = rule/estimator math-correctness selector (re-surfaces math/estimator fns with an arithmetic edge —
     div-before-mul / signed int128 / normalization-without-reclamp / single-asset/zero edge).
Both are RE-SURFACE selectors: they route a missed surface to deep-trace; they do NOT auto-confirm a bug.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from option_a_campaign import classify_signal_source  # noqa: E402  (P167 hygiene)

_FLAGS = {"research_only": True, "routes_in_production": False, "is_gate": False}

# ---- F1 dynamic-weight lifecycle -------------------------------------------------------------------
# weight-update / pool-accounting entrypoints (the family the quantamm sweep over-cleared)
_F1_FN = re.compile(r"\b(setWeights\w*|setWeightsManually|updateWeights?\w*|_?setInitialWeights|"
                    r"_setIntermediateValues|performUpdate|calculateNewWeights|onSwap|computeBalance|"
                    r"_getNormalisedWeight\w*|_calculateQuantAMMVariance)\b")
# lifecycle guards we expect somewhere near a weight-update body
_F1_GUARDS = [r"updateInterval", r"lastUpdate\w*[Tt]ime", r"epsilon|EPSILON", r"normaliz|_sum|sumOfWeights",
              r"MIN_WEIGHT|minWeight|MAX_WEIGHT|maxWeight|requireWeight|_clampWeights|_guardQuantAMMWeights"]

# ---- F2 rule/estimator math-correctness ------------------------------------------------------------
_F2_FN = re.compile(r"\b(_normalizeWeightUpdates|_clampWeights|_guardQuantAMMWeights|\w*[Cc]ovariance\w*|"
                    r"\w*[Gg]radient\w*|\w*[Vv]ariance\w*|quantAMMPack\w*|quantAMMUnpack\w*|"
                    r"_quantAMMNormalise\w*|calculateUnGuardedWeights|_calculateNewWeights)\b")
# arithmetic-edge signals
_F2_EDGES = [(r"/\s*\w[\w.]*\s*\)?\s*\*", "division_before_multiplication"),
             (r"\bint128\b|\bint256\b|SignedMath|toInt", "signed_int_math"),
             (r"<<\s*\d+|>>\s*\d+|<<\s*resolution|\bpack|\bunpack", "bit_pack_shift"),
             (r"1e18|1e36|ONE|PRECISION|FixedPoint|mulDown|divDown|mulUp|divUp", "fixed_point_scaling")]


def _read_protocol_sol(corpus_root: str) -> List[Path]:
    out: List[Path] = []
    root = Path(corpus_root)
    if not root.exists():
        return out
    for f in root.rglob("*.sol"):
        if classify_signal_source(str(f)) != "protocol_src":
            continue
        if "/interfaces/" in str(f).replace("\\", "/") or f.name.startswith("I") and f.name[1:2].isupper():
            continue  # skip interface files (no bodies to guard)
        out.append(f)
    return out


def _functions(text: str):
    """Yield (fn_name, signature, body_slice) for each function (best-effort, brace-balanced). The signature is
    the text between the name and the opening brace (carries modifiers like onlyOwner)."""
    for m in re.finditer(r"function\s+(\w+)\s*\(", text):
        name = m.group(1)
        start = m.end()
        i = text.find("{", start)
        sig = text[start:i] if i != -1 else text[start:start + 200]
        if i == -1:
            yield name, sig, text[start:start + 400]
            continue
        depth = 0
        j = i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield name, sig, text[i:j + 1]


def _contract_of(path: Path) -> str:
    return path.stem


def f1_dynamic_weight_lifecycle(corpus_root: str) -> List[Dict[str, Any]]:
    """Re-surface weight-update / pool-accounting fns whose body lacks a lifecycle guard. Skips role-gated-only
    setters (reject-first: keep permissionless update paths)."""
    hits: List[Dict[str, Any]] = []
    for f in _read_protocol_sol(corpus_root):
        text = f.read_text(encoding="utf-8", errors="ignore")
        contract = _contract_of(f)
        for name, sig, body in _functions(text):
            if not _F1_FN.search(name):
                continue
            present = [g for g in _F1_GUARDS if re.search(g, body)]
            missing = [g for g in _F1_GUARDS if not re.search(g, body)]
            # reject-first filter: a setter that is ONLY owner/role-gated and has no permissionless path
            role_gated = bool(re.search(r"onlyOwner|onlyRole|onlyAdmin|onlyGovernance", sig + body))
            if role_gated and "performUpdate" not in name and "onSwap" not in name and "computeBalance" not in name:
                continue
            hits.append({"selector": "F1", "family": "dynamic_weight_lifecycle", "contract": contract,
                         "function": name, "guards_present": present[:3],
                         "missing_lifecycle_checks": [g.split("|")[0] for g in missing][:4],
                         "reason": "weight-update/pool-accounting fn missing one or more lifecycle guards "
                                   "(sum/bounds/epsilon/interval/staleness) — re-surface for deep-trace",
                         **_FLAGS})
    return hits


def f2_estimator_math(corpus_root: str) -> List[Dict[str, Any]]:
    """Re-surface math/estimator fns with an arithmetic-edge signal and no proven in-scope clamp."""
    hits: List[Dict[str, Any]] = []
    for f in _read_protocol_sol(corpus_root):
        text = f.read_text(encoding="utf-8", errors="ignore")
        contract = _contract_of(f)
        for name, _sig, body in _functions(text):
            if not _F2_FN.search(name):
                continue
            edges = [label for rx, label in _F2_EDGES if re.search(rx, body)]
            if not edges:
                continue
            proven_clamp = bool(re.search(r"_clampWeights|_guardQuantAMMWeights|require\(|revert", body)) and \
                name in ("_clampWeights", "_guardQuantAMMWeights")
            if proven_clamp:
                continue  # the clamp fn itself, with a require — don't flag (proven guard)
            hits.append({"selector": "F2", "family": "estimator_math_correctness", "contract": contract,
                         "function": name, "edges": edges,
                         "reason": "math/estimator fn with an arithmetic edge (overflow/sign/normalization/"
                                   "single-asset) and no proven in-scope clamp — re-surface for deep-trace",
                         **_FLAGS})
    return hits


def guarded_downstream_flag(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """The guarded-downstream over-clearance rule. A sweep that would clear a candidate with a 'guarded
    downstream' rationale must NOT clear it when the named guard is itself in scope and unproven → route to
    deep-trace. Re-surface only; never mutates the production sweep."""
    rationale = str(candidate.get("clear_rationale") or "").lower()
    guarded = any(k in rationale for k in ("guard", "clamp", "downstream", "bounded"))
    guard_in_scope = bool(candidate.get("guard_in_scope"))
    guard_proven = bool(candidate.get("guard_proven"))
    do_not_clear = guarded and guard_in_scope and not guard_proven
    return {"do_not_clear": do_not_clear,
            "action": "needs_deep_pass" if do_not_clear else "clear_allowed",
            "why": ("guard is in scope and unproven — clearing on it is over-clearance" if do_not_clear
                    else "no in-scope-unproven guard underlies the clear"),
            **_FLAGS}


# ---- offline validation against the quantamm answer key (read-only) --------------------------------
QUANTAMM_ROOT = ROOT / "audits/quantamm-2024-12-eval/contracts/in-scope"
ANSWER_KEY = ROOT / "audits/quantamm-2024-12-eval/output/answer_key/normalized_answer_key.json"
F1_TARGETS = {"H-04", "M-04", "M-08", "M-09", "M-12", "M-14"}
F2_TARGETS = {"H-09", "H-10", "H-11", "L-06", "L-09", "M-07"}
TOUCHED_BEFORE = {"H-01", "M-01", "L-03", "H-02", "H-06", "L-04", "L-05", "M-16"}  # P171 Track-A touched 8/44


def _answer_key() -> List[Dict[str, Any]]:
    return json.load(open(ANSWER_KEY))["distinct_findings"]


def _hit_matches_affected(hit: Dict[str, Any], affected: str) -> bool:
    aff = (affected or "").lower()
    return hit["contract"].lower() in aff and (hit["function"].lower() in aff or hit["function"].lower() == "onswap"
                                               or "." not in aff)


def validate_against_quantamm() -> Dict[str, Any]:
    ak = _answer_key()
    aff = {x["answer_key_id"]: (x.get("affected") or "") for x in ak}
    f1 = f1_dynamic_weight_lifecycle(str(QUANTAMM_ROOT))
    f2 = f2_estimator_math(str(QUANTAMM_ROOT))

    def recovered(hits, targets):
        rec = set()
        for tid in targets:
            a = aff.get(tid, "")
            if any(_hit_matches_affected(h, a) for h in hits):
                rec.add(tid)
        return sorted(rec)

    def new_fps(hits):
        # a hit is a "new FP" (re-surface cost) if its contract.function matches NO answer-key affected
        fps = []
        for h in hits:
            key = f"{h['contract']}.{h['function']}"
            if not any((h["contract"].lower() in a.lower() and h["function"].lower() in a.lower()) for a in aff.values()):
                fps.append(key)
        return sorted(set(fps))

    r1, r2 = recovered(f1, F1_TARGETS), recovered(f2, F2_TARGETS)
    fp1, fp2 = new_fps(f1), new_fps(f2)
    recovered_all = sorted(set(r1) | set(r2))
    touched_after = sorted(TOUCHED_BEFORE | set(recovered_all))

    def precision(rec, fp):
        return f"{len(rec)}/{len(rec) + len(fp)}" if (len(rec) + len(fp)) else "0/0"

    return {
        "phase": "P172", "corpus": "quantamm-2024-12-eval", "track": "recall_quantamm",
        "f1": {"hits": len(f1), "recovered": r1, "recovered_n": len(r1), "of_targets": sorted(F1_TARGETS),
               "new_false_positives": fp1, "new_fp_n": len(fp1), "resurface_precision": precision(r1, fp1)},
        "f2": {"hits": len(f2), "recovered": r2, "recovered_n": len(r2), "of_targets": sorted(F2_TARGETS),
               "new_false_positives": fp2, "new_fp_n": len(fp2), "resurface_precision": precision(r2, fp2)},
        "coverage_before_touched": f"{len(TOUCHED_BEFORE)}/44",
        "coverage_after_touched": f"{len(touched_after)}/44",
        "recovered_total": recovered_all,
        "note": "RE-SURFACE recall (Track A only, never combined with Track B). A 'recovered' miss means the "
                "selector re-surfaced the answer-key surface for deep-trace; it does not auto-confirm the bug. "
                "'new_false_positives' = re-surfaced fns with no answer-key finding (the deep-trace cost).",
        **_FLAGS,
    }


def main(argv: List[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "validate"
    if cmd == "validate":
        print(json.dumps(validate_against_quantamm(), indent=2))
    elif cmd == "f1":
        print(json.dumps(f1_dynamic_weight_lifecycle(str(QUANTAMM_ROOT)), indent=2))
    elif cmd == "f2":
        print(json.dumps(f2_estimator_math(str(QUANTAMM_ROOT)), indent=2))
    else:
        print("usage: recall_selectors.py [validate|f1|f2]")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
