#!/usr/bin/env python3
"""P106 — Rank-signal probe (research-only, UN-WIRED). "Ranker: prioritize, don't promote."

P105 proved coverage generalizes but ranking is alphabetical: the existing ranker (_rank_score/_RANK_W in
auto_validate_invariants.py) is EVIDENCE-GATED, so before the validation layer every candidate scores ~0. This probe
MEASURES whether a set of EVIDENCE-FREE, source-derivable features would discriminate the awarded function from the
surrounding surface — the precursor to the P107 ranking prototype.

It does NOT combine features into a score, reorder candidates, set a threshold, or wire anything. For each subject it
computes per-function feature vectors over the FULL public/external surface, then reports each awarded function's
value + PERCENTILE/RANK within that surface per feature, plus per-feature discrimination stats. A feature only helps
ranking if the awarded function lands HIGH within its surface (the P105 lesson: firing everywhere discriminates
nothing).

Two deliberate departures from run_subject, both part of the rank-signal design:
  1. features are computed on the FUNCTION BODY, not the whole file -> de-saturates the keyword signals;
  2. features map onto the existing _RANK_W vocabulary (defense_gap / actor_clarity / consequence / exploitability)
     so P107 can wire the same names into _rank_score.

It REUSES the frozen pipeline read-only (inventory + enumerate + map_defenses); it edits nothing.

Usage:
    python scripts/assisted/rank_signal_probe.py --self-test
    python scripts/assisted/rank_signal_probe.py --run     # over the P105 corpus -> p106/rank_signal_probe.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))

import inventory_public_external_functions as INV   # noqa: E402  (frozen — read-only reuse)
import enumerate_candidate_invariants as ENUM       # noqa: E402
import map_invariant_defenses as DEF                # noqa: E402
import benchmark_replay as BENCH                    # noqa: E402  (reuse _resolve_sol_files)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p106"

_CORE = set(ENUM._CORE)  # categories enumerate always emits -> "core-only" is the weak signal

# Feature names align with the existing _RANK_W vocabulary where they correspond (see module docstring).
FEATURES = [
    "category_specificity",          # new: # of NON-core invariant categories fired on the body
    "defense_gap",                   # <- _RANK_W.defense_gap: # of fired categories with DOES_NOT_COVER (+.5 partial)
    "actor_clarity",                 # <- _RANK_W.actor_clarity: permissionless public/external (no role guard)
    "consequence_value_movement",    # <- _RANK_W.consequence: moves tokens/value
    "consequence_fund_reachability", # <- _RANK_W.consequence: withdraw/claim/redeem/collect/rescue
    "exploitability_external_call",  # <- _RANK_W.exploitability: cross-contract boundary (the P105 blind class)
    "state_write_breadth",           # new: # of state writes (stateful-complexity proxy)
    "missing_update_asymmetry",      # new: sets/updates without a matching reset/clear (negative_space proxy)
]

_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_CONTAINER_RE = re.compile(r"\b(contract|library|interface|abstract\s+contract)\s+([A-Za-z_]\w*)")
_FUNC_SIG_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")

_VALUE_MOVE_RE = re.compile(r"\btransfer\b|\btransferfrom\b|safetransfer|\bmint\b|\b_mint\b|\bburn\b|\b_burn\b|\.call\{|call\{value")
_FUND_REACH_RE = re.compile(r"withdraw|claim|redeem|release|collect|rescue|unlock|payout")
_EXT_CALL_RE = re.compile(r"staticcall|\.call\(|\binterface\b|factory|oracle|hooks?\.|getpair|\.delegatecall")
_ROLE_GUARD_RE = DEF._PRIMS["role_auth_modifier"]
_STATE_WRITE_RE = re.compile(r"[A-Za-z_]\w*(\[[^\]]*\])?\s*(=|\+=|-=)\s")
_RESET_RE = re.compile(r"delete\s|=\s*0\b|=\s*false\b|\.reset\(|clear\(")
_SET_RE = re.compile(r"(\+=|=\s*true\b|=\s*1\b)|[A-Za-z_]\w*\s*=")


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    """No external config; returned for advisory-helper-pattern parity. Centralises the top-quartile threshold."""
    return {"top_quartile": 0.75, "features": list(FEATURES)}


def _strip_comments(text: str) -> str:
    return _COMMENT_RE.sub(" ", text)


def _container_at(containers: List[Tuple[int, str]], pos: int) -> Optional[str]:
    name = None
    for start, nm in containers:
        if start <= pos:
            name = nm
        else:
            break
    return name


def _function_bodies(file_text: str) -> Dict[Tuple[str, str], str]:
    """Extract {(container, function): body_text} by brace-matching from each signature. Comment-stripped so braces
    in comments don't corrupt the match. Interface/abstract decls (';' before '{') yield an empty body."""
    text = _strip_comments(file_text)
    containers = sorted(((m.start(), m.group(2)) for m in _CONTAINER_RE.finditer(text)), key=lambda x: x[0])
    out: Dict[Tuple[str, str], str] = {}
    for m in _FUNC_SIG_RE.finditer(text):
        name = m.group(1)
        container = _container_at(containers, m.start()) or "?"
        # find the body: first '{' after the signature, unless a ';' terminates it first (no body)
        i = m.end()
        depth = 0
        brace_start = None
        n = len(text)
        while i < n:
            ch = text[i]
            if ch == ";" and brace_start is None:
                break
            if ch == "{":
                if brace_start is None:
                    brace_start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and brace_start is not None:
                    out[(container, name)] = text[brace_start:i + 1]
                    break
            i += 1
        out.setdefault((container, name), "")
    return out


# P115: access-control modifiers that do not start with "only" (only* is caught by DEF role_auth_modifier).
_SIG_AUTH_RE = re.compile(r"\b(requiresauth|restricted|authorized|onlyrole|onlygovernance)\b")

# P119: caller-equality admin-role gates the DEF body regex misses. role_auth_modifier matches only
# `require(msg.sender == ...` (caller-first); it does NOT see the operand-reversed / OR-clause / cast forms,
# e.g. `<role> == msg.sender`, `msg.sender == s2Admin()`,
# `require(listing.seller == msg.sender || msg.sender == IMarketplaceSetting(x).s2Admin())` (secondswap
# unlistVesting, P118). Role-TARGETED (word-boundary role names) so resource-ownership checks are NOT demoted:
# `\bowner\b` matches `owner()` but NOT `ownerOf(` (no word boundary inside "ownerof"), so attacker-reachable
# functions like EntityForging.forgeWithListed (`require(ownerOf(id) == msg.sender)`) stay permissionless.
# Under-detection (e.g. `msg.sender == address(entityForgingContract)` contract-address gates) is accepted as
# safer than false demotion of attack surface.
_CALLER_EQ = r"(?:msg\.sender|_msgsender\(\))"
_ROLE_NAME = (r"\b(?:owner|admin|s2admin|governor|governance|authority|manager|controller"
              r"|guardian|operator|treasury|deployer|issuer)\b")
_CALLER_ROLE_EQ_RE = re.compile(
    _CALLER_EQ + r"\s*==\s*[^;\n]*?" + _ROLE_NAME
    + r"|" + _ROLE_NAME + r"[^;\n]*?==\s*" + _CALLER_EQ, re.I)


def _function_signatures(file_text: str) -> Dict[Tuple[str, str], str]:
    """P115: extract {(container, function): signature_text} — the declaration from the `function` keyword up to the
    body's opening '{' (or terminating ';'). Mirrors _function_bodies' comment-stripped brace scan; this is where
    access MODIFIERS (onlyBorrower, onlyPhiFactory, ...) live, which the body-only scan misses. Kept SEPARATE from
    _function_bodies so that function's return contract (used by self_kill_validation) is unchanged."""
    text = _strip_comments(file_text)
    containers = sorted(((m.start(), m.group(2)) for m in _CONTAINER_RE.finditer(text)), key=lambda x: x[0])
    out: Dict[Tuple[str, str], str] = {}
    for m in _FUNC_SIG_RE.finditer(text):
        name = m.group(1)
        container = _container_at(containers, m.start()) or "?"
        i = m.end()
        n = len(text)
        end = n
        while i < n:
            ch = text[i]
            if ch == "{" or ch == ";":
                end = i
                break
            i += 1
        out.setdefault((container, name), text[m.start():end])
    return out


def _features_for(body: str, fn_name: str, visibility: str, signature: str = "") -> Dict[str, float]:
    """Compute the evidence-free feature vector for one function. All purely source-derived. `signature` (P115) is the
    declaration text incl. modifiers; actor_clarity reads BOTH body and signature so access modifiers are not missed."""
    b = (body or "").lower()
    sig = (signature or "").lower()
    name = (fn_name or "").lower()

    # category_specificity + defense_gap come from enumerate/map_defenses on the BODY (de-saturated vs whole-file).
    gen = ENUM.enumerate_invariants({"function": fn_name, "source_text": body})
    fired = [c["invariant_type"] for c in gen["candidate_invariants"]]
    non_core = [c for c in fired if c not in _CORE]
    category_specificity = float(len(non_core))

    defense_gap = 0.0
    for cat in fired:
        cov = DEF.map_defenses({"invariant_type": cat}, body)["coverage"]
        if cov == DEF.DOES_NOT_COVER:
            defense_gap += 1.0
        elif cov == DEF.PARTIALLY_COVERS:
            defense_gap += 0.5

    # P115: role-guarded if a guard appears in the BODY or in the SIGNATURE (modifiers live in the signature).
    # P119: also catch caller-equality admin-role gates in the BODY (operand-reversed / OR-clause / cast forms).
    role_guarded = bool(_ROLE_GUARD_RE.search(b) or _ROLE_GUARD_RE.search(sig)
                        or _SIG_AUTH_RE.search(sig) or _CALLER_ROLE_EQ_RE.search(b))
    permissionless = visibility in ("public", "external") and not role_guarded
    value_move = bool(_VALUE_MOVE_RE.search(b))
    fund_reach = bool(_FUND_REACH_RE.search(b) or _FUND_REACH_RE.search(name))
    ext_call = bool(_EXT_CALL_RE.search(b))
    state_writes = float(len(_STATE_WRITE_RE.findall(b)))
    missing_update = bool(_SET_RE.search(b)) and not bool(_RESET_RE.search(b))

    return {
        "category_specificity": category_specificity,
        "defense_gap": defense_gap,
        "actor_clarity": 1.0 if permissionless else 0.0,
        "consequence_value_movement": 1.0 if value_move else 0.0,
        "consequence_fund_reachability": 1.0 if fund_reach else 0.0,
        "exploitability_external_call": 1.0 if ext_call else 0.0,
        "state_write_breadth": state_writes,
        "missing_update_asymmetry": 1.0 if missing_update else 0.0,
    }


def _percentile(values: List[float], v: float) -> float:
    """Fraction of surface values <= v (1.0 == awarded fn is at/above the whole surface on this feature)."""
    if not values:
        return 0.0
    return round(sum(1 for x in values if x <= v) / len(values), 4)


def _rank(values_desc_sorted: List[float], v: float) -> int:
    """1-based rank of v among values (1 = highest); ties share the best rank."""
    higher = sum(1 for x in values_desc_sorted if x > v)
    return higher + 1


def build_surface(spec: Dict[str, Any], excludes: List[str]) -> Dict[str, Any]:
    """Inventory the subject's public/external surface and compute every function's feature vector."""
    files = BENCH._resolve_sol_files(spec.get("source_roots", []), excludes)
    bodies: Dict[Tuple[str, str], str] = {}
    signatures: Dict[Tuple[str, str], str] = {}
    for f in files:
        try:
            txt = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        bodies.update(_function_bodies(txt))
        signatures.update(_function_signatures(txt))   # P115: capture modifiers in the signature
    inv = INV.inventory(files)
    surface: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for fnrec in inv["public_external"]:
        key = (fnrec["contract"], fnrec["function"])
        body = bodies.get(key, "")
        surface[key] = {
            "contract": fnrec["contract"], "function": fnrec["function"],
            "visibility": fnrec["visibility"], "has_body": bool(body.strip()),
            "features": _features_for(body, fnrec["function"], fnrec["visibility"],
                                      signature=signatures.get(key, "")),
        }
    return {"files": len(files), "surface": surface}


def score_finding(surface: Dict[Tuple[str, str], Dict[str, Any]], finding: Dict[str, Any]) -> Dict[str, Any]:
    key = (finding.get("contract"), finding.get("function"))
    rec = surface.get(key)
    feats = (rec or {}).get("features", {})
    per_feature = {}
    for feat in FEATURES:
        col = [s["features"][feat] for s in surface.values()]
        v = feats.get(feat, 0.0)
        per_feature[feat] = {
            "value": v,
            "percentile": _percentile(col, v) if rec else None,
            "rank": _rank(sorted(col, reverse=True), v) if rec else None,
        }
    elevating = [f for f, d in per_feature.items()
                 if d["percentile"] is not None and d["percentile"] >= _cfg()["top_quartile"] and d["value"] > 0]
    return {
        "finding_id": finding.get("finding_id"),
        "contract": finding.get("contract"),
        "function": finding.get("function"),
        "invariant_category": finding.get("invariant_category"),
        "severity": finding.get("severity"),
        "grounding": finding.get("grounding"),
        "found_in_surface": rec is not None,
        "has_body": (rec or {}).get("has_body", False),
        "surface_size": len(surface),
        "per_feature": per_feature,
        "elevating_features": elevating,
    }


def run_corpus(corpus: Dict[str, Any]) -> Dict[str, Any]:
    excludes = corpus.get("exclude_substrings", [])
    subjects = []
    all_rows: List[Dict[str, Any]] = []
    surface_cols: Dict[str, List[float]] = {f: [] for f in FEATURES}
    for spec in corpus.get("subjects", []):
        built = build_surface(spec, excludes)
        surface = built["surface"]
        for s in surface.values():
            for f in FEATURES:
                surface_cols[f].append(s["features"][f])
        rows = [score_finding(surface, f) for f in spec.get("awarded_findings", []) if f.get("surfaceable")]
        all_rows.extend(rows)
        subjects.append({
            "id": spec.get("id"), "phase": spec.get("phase"),
            "surface_size": len(surface), "files": built["files"],
            "scored_findings": rows,
        })
    return {
        **FLAGS,
        "schema": "p106_rank_signal_probe_v1",
        "invariant": "Ranker: prioritize, don't promote.",
        "note": ("Evidence-free, source-derived feature discrimination over the FULL public/external surface. "
                 "Features are computed on FUNCTION BODIES (de-saturated vs run_subject's whole-file). NO combined "
                 "score, NO ordering, NO threshold, NO wiring — that is P107."),
        "subjects": subjects,
        "discrimination": _discrimination(all_rows, surface_cols),
    }


def _discrimination(rows: List[Dict[str, Any]], surface_cols: Dict[str, List[float]]) -> Dict[str, Any]:
    """Per-feature: does the awarded function land HIGH within its surface, AND is the signal selective?
    mean_awarded_percentile / top-quartile / rank1 measure elevation; surface_base_rate measures selectivity.
    HONESTY: a binary feature's percentile is ~1.0 whenever the awarded fn has the trait, so a HIGH mean percentile
    with a HIGH base_rate (e.g. actor_clarity) is BLUNT (necessary, not discriminating); a high mean percentile with
    a LOW base_rate is a SHARP discriminator. 'lift' = mean_awarded_percentile - base_rate makes this explicit."""
    tq = _cfg()["top_quartile"]
    out = {}
    n = len(rows)
    for feat in FEATURES:
        pcts = [r["per_feature"][feat]["percentile"] for r in rows
                if r["per_feature"][feat]["percentile"] is not None]
        present = [r for r in rows if r["per_feature"][feat]["value"] > 0]
        top_q = [r for r in rows if (r["per_feature"][feat]["percentile"] or 0) >= tq
                 and r["per_feature"][feat]["value"] > 0]
        rank1 = [r for r in rows if r["per_feature"][feat]["rank"] == 1 and r["per_feature"][feat]["value"] > 0]
        col = surface_cols.get(feat, [])
        base_rate = round(sum(1 for x in col if x > 0) / len(col), 4) if col else None
        mean_pct = round(sum(pcts) / len(pcts), 4) if pcts else None
        out[feat] = {
            "mean_awarded_percentile": mean_pct,
            "surface_base_rate": base_rate,
            "lift": (round(mean_pct - base_rate, 4) if (mean_pct is not None and base_rate is not None) else None),
            "awarded_with_signal_present": len(present),
            "awarded_in_top_quartile": len(top_q),
            "awarded_ranked_first": len(rank1),
            "n": n,
        }
    return out


# ---------------------------------------------------------------------------- self-test

_FIXTURE = {
    "Fix.sol": (
        "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
        "contract Fix {\n"
        "  mapping(address=>uint256) public balance; uint256 public total; address owner;\n"
        "  // permissionless, moves value, reachable, external call, no reset -> should score HIGH\n"
        "  function drain(uint256 amount) external {\n"
        "     balance[msg.sender] += amount; total += amount;\n"
        "     IERC20(token).transfer(msg.sender, amount); pool.staticcall(data);\n"
        "  }\n"
        "  // guarded admin setter (BODY guard), pure-ish, no value -> should score LOW\n"
        "  function setOwner(address o) external { require(msg.sender == owner); owner = o; }\n"
        "  // P115: guard is ONLY a SIGNATURE modifier (no body guard) -> must be detected as privileged\n"
        "  function adminPoke(uint256 v) external onlyOwner { total = v; }\n"
        "  function ping() external view returns (uint256) { return total; }\n"
        "}\n"
    )
}


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    bodies = _function_bodies(_FIXTURE["Fix.sol"])
    chk(("Fix", "drain") in bodies and "transfer" in bodies[("Fix", "drain")].lower(), "extracts function body")
    chk(("Fix", "setOwner") in bodies, "extracts guarded setter body")

    sigs = _function_signatures(_FIXTURE["Fix.sol"])
    fdrain = _features_for(bodies[("Fix", "drain")], "drain", "external", signature=sigs.get(("Fix", "drain"), ""))
    fset = _features_for(bodies[("Fix", "setOwner")], "setOwner", "external", signature=sigs.get(("Fix", "setOwner"), ""))
    fping = _features_for(bodies[("Fix", "ping")], "ping", "external", signature=sigs.get(("Fix", "ping"), ""))
    # P115: a function whose ONLY guard is a signature modifier (onlyOwner) must be non-permissionless
    fadmin_sig = _features_for(bodies[("Fix", "adminPoke")], "adminPoke", "external",
                              signature=sigs.get(("Fix", "adminPoke"), ""))
    fadmin_nosig = _features_for(bodies[("Fix", "adminPoke")], "adminPoke", "external")  # body-only (old behavior)

    chk(fdrain["actor_clarity"] == 1.0, "permissionless fn -> actor_clarity high")
    chk(fset["actor_clarity"] == 0.0, "role-guarded setter (body) -> actor_clarity 0")
    chk("onlyowner" in sigs.get(("Fix", "adminPoke"), "").lower(), "signature captures the onlyOwner modifier")
    chk(fadmin_sig["actor_clarity"] == 0.0, "P115: signature-modifier-only fn -> actor_clarity 0 (privileged)")
    chk(fadmin_nosig["actor_clarity"] == 1.0, "without signature, the modifier is missed (the old bug) -> 1.0")

    # P119: caller-equality admin-role gates (operand-reversed / OR-clause / cast) must demote, while
    # resource-ownership (`ownerOf(id) == msg.sender`) must NOT demote (preserves forgeWithListed-class surface).
    eq_or = "{ require(listing.seller == msg.sender || msg.sender == IMarketplaceSetting(s).s2Admin()); x = 1; }"
    eq_rev = "{ require(owner == msg.sender); x = 1; }"
    eq_res = "{ require(nftContract.ownerOf(id) == msg.sender); x = 1; }"  # resource-ownership, NOT a role gate
    eq_none = "{ x = 1; }"
    chk(_features_for(eq_or, "unlistVesting", "external")["actor_clarity"] == 0.0,
        "P119: seller==msg.sender || msg.sender==s2Admin() -> demoted (privileged)")
    chk(_features_for(eq_rev, "f", "external")["actor_clarity"] == 0.0,
        "P119: reversed role==msg.sender -> demoted (privileged)")
    chk(_features_for(eq_res, "forgeWithListed", "external")["actor_clarity"] == 1.0,
        "P119: ownerOf(id)==msg.sender (resource-ownership) -> NOT demoted (permissionless)")
    chk(_features_for(eq_none, "f", "external")["actor_clarity"] == 1.0,
        "P119: no guard -> permissionless")

    chk(fdrain["consequence_value_movement"] == 1.0, "value-moving fn detected")
    chk(fset["consequence_value_movement"] == 0.0, "non-value setter not flagged for value movement")
    chk(fdrain["exploitability_external_call"] == 1.0, "external call detected")
    chk(fdrain["state_write_breadth"] >= fping["state_write_breadth"], "stateful fn writes more than a view")
    chk(fdrain["missing_update_asymmetry"] == 1.0, "set-without-reset asymmetry flagged")

    # percentile/rank math
    chk(_percentile([0, 1, 2, 3], 3) == 1.0, "max value -> percentile 1.0")
    chk(_percentile([0, 1, 2, 3], 0) == 0.25, "min value -> low percentile")
    chk(_rank(sorted([0, 1, 2, 3], reverse=True), 3) == 1, "max value -> rank 1")

    # end-to-end on a fixture corpus: the HIGH fn must out-rank the guarded setter on the right features
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="p106_selftest_"))
    (tmp / "Fix.sol").write_text(_FIXTURE["Fix.sol"], encoding="utf-8")
    corpus = {
        "exclude_substrings": [],
        "subjects": [{
            "id": "fx", "phase": "self-test", "source_roots": [str(tmp)],
            "awarded_findings": [
                {"finding_id": "F-HIGH", "contract": "Fix", "function": "drain",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "grounding": "high"},
                {"finding_id": "F-LOW", "contract": "Fix", "function": "setOwner",
                 "invariant_category": "role_access", "severity": "Low",
                 "surfaceable": True, "grounding": "high"},
            ],
        }],
    }
    res = run_corpus(corpus)
    res2 = run_corpus(corpus)
    for p in tmp.glob("*"):
        p.unlink()
    tmp.rmdir()

    rows = {r["finding_id"]: r for r in res["subjects"][0]["scored_findings"]}
    chk(rows["F-HIGH"]["found_in_surface"] and rows["F-HIGH"]["has_body"], "awarded HIGH fn found with body")
    chk(rows["F-HIGH"]["per_feature"]["actor_clarity"]["percentile"]
        >= rows["F-LOW"]["per_feature"]["actor_clarity"]["percentile"], "HIGH fn >= LOW fn on actor_clarity")
    chk(len(rows["F-HIGH"]["elevating_features"]) > len(rows["F-LOW"]["elevating_features"]),
        "HIGH fn has more elevating features than the guarded setter")
    chk("discrimination" in res and all(f in res["discrimination"] for f in FEATURES),
        "discrimination summary computed for every feature")
    chk(json.dumps(res, sort_keys=True) == json.dumps(res2, sort_keys=True), "deterministic on re-run")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def write_outputs(results: Dict[str, Any], out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "rank_signal_probe.json"
    p.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true", help="run over the P105 corpus -> p106/rank_signal_probe.json")
    ap.add_argument("--corpus", help="path to benchmark_corpus.json (default: p105/benchmark_corpus.json)")
    ap.add_argument("--out-dir", help="output dir (default: documentation/research/assisted_mode/p106)")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()
    if args.run:
        corpus = json.loads(Path(args.corpus or DEFAULT_CORPUS).read_text(encoding="utf-8"))
        results = run_corpus(corpus)
        out = write_outputs(results, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        disc = results["discrimination"]
        print("rank-signal probe complete. lift = mean_awarded_percentile - surface_base_rate "
              "(high lift = SHARP discriminator; high percentile + high base_rate = BLUNT/necessary):")
        for feat in sorted(FEATURES, key=lambda f: -(disc[f]["lift"] or 0)):
            d = disc[feat]
            print(f"  {feat:32} lift={d['lift']}  mean_pct={d['mean_awarded_percentile']}  "
                  f"base_rate={d['surface_base_rate']}  topQ={d['awarded_in_top_quartile']}/{d['n']}  "
                  f"rank1={d['awarded_ranked_first']}")
        print(f"  -> {out}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
