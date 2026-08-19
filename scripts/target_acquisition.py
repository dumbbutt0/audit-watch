#!/usr/bin/env python3
"""target_acquisition.py — 4-axis target-sourcing scorer (ADVISORY-ONLY, READ-ONLY, deterministic).

Generalizes contest_fit.py (which answers only axis 2, "can our pipeline find bugs here?") into a full
target-acquisition rubric. Given a list of candidate bounty/contest programs it hard-rejects the unpayable,
then scores the rest across four axes and emits a RANKED shortlist. The human still picks the target — this
engine RANKS, it does not SELECT, route, gate, or submit.

  Axis 1  Bug-likelihood   are real exploits likely here?      White Mage rubric (complexity/innovation/
                                                               optimization/code-quality/time/eyes-on-code)
  Axis 2  Detector-fit     can our pipeline find them?         REUSE contest_fit._class_fit
  Axis 3  Payout-EV        will we get paid fairly + worth it? cap (power-law) x platform-rep x scope/treasury
  Axis 4  Eval-cleanliness is it unseen + post-cutoff so the   HARD GATE — corpus/audits/awarded-example
          ⭐               recall number stays honest?         seen-set cross-check (ours alone)

Hard-reject pre-filter maps the White Mage "What Not to Hunt" list. Archetype constraint: AuditWatch =
Scientist + Differ + Speedrunner (breadth / cross-mechanism / fast cold passes), NOT The Digger — so the
composite down-weights mature + high-TVL + heavily-audited targets and up-weights young/uncommon/
mechanism-matched ones.

is_gate:false / advisory_only:true / never routes/gates/submits. The hard-reject de-ranks + flags a TARGET
in a shortlist; it never rejects a finding and never touches the pipeline.

Usage:
  python scripts/target_acquisition.py [--candidates config/target_candidates.json] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # so contest_fit / submission_risk_audit import

CANDIDATES = ROOT / "config" / "target_candidates.json"
CORPUS = ROOT / "evals" / "corpus.json"
MECH = ROOT / "config" / "mechanism_classes.json"

KNOWLEDGE_CUTOFF = "2026-01-31"          # anything launched after this is post-cutoff by construction
_WORD = re.compile(r"[a-z0-9]{3,}")
# generic tokens that must NOT alone trigger an already-seen match (dates, languages, common
# protocol-name suffixes). A seen-id only rejects a candidate on its DISTINCTIVE (protocol-name) tokens.
_SEEN_STOP = {
    "blind", "eval", "holdout", "solana", "sol", "move", "sui", "aptos", "ton", "evm", "svm",
    "2021", "2022", "2023", "2024", "2025", "2026",
    "protocol", "finance", "labs", "network", "app", "apps", "bounty", "bug", "audit", "contest",
    "competition", "vault", "vaults", "dao", "defi", "fi", "xyz", "core", "monorepo", "contracts",
    "contract", "program", "programs", "mainnet", "the", "and", "org", "com", "io", "v1", "v2", "v3",
    "immunefi", "cantina", "sherlock", "code4rena", "c4",
}
# platform payout-fairness priors (White Mage picks + contest platforms), 0..1
_PLATFORM_REP = {
    "immunefi": 0.9, "hackenproof": 0.8, "cantina": 0.85, "code4rena": 0.8, "c4": 0.8,
    "sherlock": 0.8, "codehawks": 0.7, "hats": 0.65, "self-hosted": 0.4, "": 0.5,
}
# White Mage "What Not to Hunt" — reject category id -> (display name, rationale). Vocabulary aligned to
# config/submission_risk_patterns.json buckets + data/fp_autopsies/rejection_rules.jsonl tags.
_REJECT_CATS = {
    "deprecated_unused":       ("deprecated / unused code", "not live surface"),
    "old_impl_behind_proxy":   ("old impl behind proxy", "not the active implementation"),
    "code_ne_deployed":        ("repo code != deployed", "audited code is not what runs"),
    "non_live_chain":          ("non-live / incompatible chain", "not exploitable in production"),
    "in_dev_unshipped":        ("in-dev, no ship proof", "may never deploy"),
    "trusted_role_gated_only": ("trusted-role-gated only", "requires_compromised_key / admin_only (OOS)"),
    "temp_dos_griefing_only":  ("temporary DoS / griefing only", "low-value, dispute-prone"),
    "third_party_gated":       ("third-party-condition gated", "impact depends on external system"),
    "offchain_mitigated":      ("offchain-mitigated", "possibly neutralized off-chain"),
    "informational_only":      ("informational / architectural", "not a payable finding"),
}


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _norm_lang(s: str) -> str:
    s = (s or "").strip().lower()
    return {"sol": "solidity", "solidity": "solidity", "rust": "rust", "solana": "rust",
            "move": "move", "sui": "move", "aptos": "move", "func": "ton", "ton": "ton"}.get(s, s)


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _months_since(date_str: str) -> float | None:
    """Whole-ish months from date_str (YYYY-MM-DD) to now, or None if unparseable."""
    try:
        d = datetime.fromisoformat(str(date_str)[:10]).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None
    return (datetime.now(timezone.utc) - d).days / 30.44


# ── seen-set (axis 4 hard gate) ───────────────────────────────────────────────
def _seen_set() -> set:
    """Every project id we've already studied — a target here is teaching-to-the-test."""
    seen = set()
    corpus = _load(CORPUS, {})
    sets = corpus.get("sets", {}) if isinstance(corpus, dict) else {}
    lists = [sets.get("training", []), sets.get("holdout", []),
             corpus.get("rust", []), corpus.get("pending_key", [])]
    for lst in lists:
        for item in (lst or []):
            pid = item.get("id") if isinstance(item, dict) else item
            if pid:
                seen.add(str(pid).lower())
    # audit workspace dir names
    adir = ROOT / "audits"
    if adir.is_dir():
        for p in adir.iterdir():
            if p.is_dir():
                seen.add(p.name.lower())
    # mechanism_classes awarded_examples: "<project-id>:<finding-id>"
    mech = _load(MECH, {}).get("classes", {})
    for c in mech.values():
        for ex in (c.get("awarded_examples") or []):
            pid = str(ex).split(":", 1)[0].strip().lower()
            if pid:
                seen.add(pid)
    return seen


def _seen_hit(cand: dict, seen: set) -> str | None:
    """Return the matched seen-set id if this candidate is already studied, else None."""
    toks = set()
    for field in ("name", "repo", "id"):
        v = str(cand.get(field) or "").lower()
        toks |= set(_WORD.findall(v))
    if not toks:
        return None
    for s in seen:
        stoks = set(_WORD.findall(s))
        if not stoks:
            continue
        # match only on DISTINCTIVE tokens — drop dates, languages, and generic protocol-name noise
        # ("protocol", "finance", "labs", ...). A single generic token like "protocol" must NOT trigger a
        # seen-hit (it collided "Light Protocol" with "yo-protocol"). Over-stopwording only reduces false
        # rejects (never weakens a real match): every real seen-id keeps a distinctive protocol token.
        distinctive = {t for t in stoks if t not in _SEEN_STOP}
        if distinctive and distinctive <= toks:
            return s
    return None


# ── axis 4: eval-cleanliness (HARD GATE) ──────────────────────────────────────
def _axis4_cleanliness(cand: dict, seen: set, allow_pre_cutoff: bool = False) -> dict:
    hit = _seen_hit(cand, seen)
    launch = cand.get("launch_date")
    post_cutoff = None
    if launch:
        post_cutoff = str(launch)[:10] > KNOWLEDGE_CUTOFF
    # soft "have we studied this" KB hint (reuse #5(a) helpers; degrade gracefully)
    kb_hint = None
    try:
        from submission_risk_audit import _kb_max_similarity
        sim, title, proto = _kb_max_similarity("", str(cand.get("name") or ""))
        if sim is not None:
            kb_hint = {"kb_max_similarity": round(sim, 3), "closest": title}
    except Exception:
        kb_hint = None
    # seen-set membership ALWAYS hard-rejects (teaching-to-the-test). pre-cutoff hard-rejects in the
    # default eval-clean mode (Option-2 honest recall); --allow-pre-cutoff relaxes it to a soft penalty
    # for real (get-paid) hunts where prior knowledge doesn't disqualify.
    pre_cutoff_reject = (post_cutoff is False) and not allow_pre_cutoff
    clean = hit is None and not pre_cutoff_reject
    return {"clean": clean, "seen_hit": hit,
            "post_cutoff": post_cutoff, "pre_cutoff_penalized": (post_cutoff is False and allow_pre_cutoff),
            "kb_hint": kb_hint,
            "rationale": (f"already studied (seen-set: {hit}) — teaching-to-the-test" if hit else
                          ("launched pre-cutoff — likely in prior knowledge (eval-clean reject; "
                           "use --allow-pre-cutoff for real hunts)" if pre_cutoff_reject else
                           ("launched pre-cutoff — soft-penalized (real-hunt mode)" if post_cutoff is False
                            else "unseen + post-cutoff (or undated) — honest eval target")))}


# ── hard-reject pre-filter ────────────────────────────────────────────────────
def _hard_rejects(cand: dict) -> list:
    reasons = []
    for flag in (cand.get("reject_flags") or []):
        f = str(flag).strip().lower()
        if f in _REJECT_CATS:
            reasons.append({"id": f, "name": _REJECT_CATS[f][0], "rationale": _REJECT_CATS[f][1]})
    # a couple of inferable rejects from structured booleans
    if cand.get("active_bounty") is False and cand.get("self_hosted") is False and cand.get("platform") is None:
        pass  # no reliable inference; explicit flags are the source of truth
    if cand.get("live") is False or cand.get("deployed") is False:
        reasons.append({"id": "non_live_chain", "name": _REJECT_CATS["non_live_chain"][0],
                        "rationale": "candidate marked not live/deployed"})
    return reasons


# ── axis 1: bug-likelihood ────────────────────────────────────────────────────
def _axis1_bug_likelihood(cand: dict) -> dict:
    signals = {}
    absent = []

    # complexity
    loc = cand.get("loc")
    comp = 0.0
    parts = 0
    if isinstance(loc, (int, float)):
        comp += _clamp((loc - 500) / 8000); parts += 1      # ~8.5k loc saturates
    else:
        absent.append("loc")
    comp += 0.25 * min(4, cand.get("components") or 0) / 4 if cand.get("components") else 0
    comp += 0.2 if cand.get("cross_chain") else 0
    comp += 0.2 if cand.get("math_heavy") else 0
    complexity = _clamp(comp / max(1, 1)) if parts or cand.get("components") or cand.get("cross_chain") \
        or cand.get("math_heavy") else 0.4
    signals["complexity"] = round(_clamp(complexity), 3)

    # innovation
    tags = {str(t).lower() for t in (cand.get("innovation_tags") or [])}
    innov_keys = {"new_lang", "new_vm", "port", "young_ecosystem", "rwa", "zk", "ai", "novel_design",
                  "new_yield", "consensus"}
    innovation = _clamp(0.3 + 0.18 * len(tags & innov_keys))
    if not tags:
        innovation = 0.45; absent.append("innovation_tags")
    signals["innovation"] = round(innovation, 3)

    # optimization
    optimization = _clamp((0.6 if cand.get("assembly_unsafe") else 0.3)
                          + (0.3 if cand.get("perf_refactor") else 0.0))
    signals["optimization"] = round(optimization, 3)

    # code-quality / audit signal: MORE prior criticals / basic-issue density => MORE bugs likely
    crit = cand.get("prior_criticals")
    dens = cand.get("basic_issue_density")
    cq = 0.4
    if isinstance(crit, (int, float)) or isinstance(dens, (int, float)):
        cq = _clamp(0.3 + 0.15 * min(4, crit or 0) + 0.4 * _clamp(dens or 0))
    else:
        absent.append("prior_criticals/basic_issue_density")
    signals["code_quality_audit"] = round(cq, 3)

    # time-since-launch: favor the post-audit weeks-to-months window
    m = _months_since(cand.get("launch_date"))
    if m is None:
        tsl = 0.5; absent.append("launch_date")
    elif m < 0.5:
        tsl = 0.35           # red-hot day-one: intense competition
    elif m <= 6:
        tsl = 1.0            # sweet spot
    elif m <= 18:
        tsl = 0.6
    else:
        tsl = 0.35           # old & picked-over
    signals["time_since_launch"] = round(tsl, 3)

    # eyes-on-code: uncommon lang / obscure chain / no active bounty => more findable
    eyes = 0.4
    lang = _norm_lang(cand.get("lang", ""))
    eyes += 0.25 if lang in ("rust", "move", "ton") else 0.0
    eyes += 0.2 if cand.get("obscure_chain") else 0.0
    eyes += 0.15 if cand.get("active_bounty") is False else 0.0
    signals["eyes_on_code"] = round(_clamp(eyes), 3)

    raw = sum(signals.values()) / len(signals)
    return {"score": round(_clamp(raw), 3), "signals": signals, "absent_signals": absent}


# ── axis 2: detector-fit (REUSE contest_fit) ──────────────────────────────────
def _axis2_detector_fit(cand: dict) -> dict:
    lang = _norm_lang(cand.get("lang", ""))
    try:
        from contest_fit import _class_fit
        cf = _class_fit(lang) if lang else {}
    except Exception as e:
        return {"score": None, "fit_score": None, "note": f"contest_fit unavailable: {e}"}
    fs = cf.get("fit_score")
    return {"score": fs, "fit_score": fs, "language": lang,
            "n_strong": len(cf.get("strong", [])), "n_weak": len(cf.get("weak", [])),
            "n_classes": cf.get("n_classes", 0)}


# ── axis 3: payout-EV ─────────────────────────────────────────────────────────
def _axis3_payout_ev(cand: dict) -> dict:
    import math
    cap = cand.get("cap")
    absent = []
    if isinstance(cap, (int, float)) and cap > 0:
        # power-law: log-scale, $10k -> ~0.4, $100k -> ~0.6, $1M -> ~0.8, $10M -> ~1.0
        cap_score = _clamp((math.log10(cap) - 3) / 4)
    else:
        cap_score = 0.4; absent.append("cap")
    plat = str(cand.get("platform") or "").strip().lower()
    plat_rep = _PLATFORM_REP.get(plat, 0.6)
    fairness = plat_rep
    if cand.get("scope_clear") is True:
        fairness = _clamp(fairness + 0.05)
    elif cand.get("scope_clear") is False:
        fairness = _clamp(fairness - 0.15)
    if cand.get("prior_disputes"):
        fairness = _clamp(fairness - 0.2)
    treasury_ok = 1.0 if cand.get("treasury") in (None, "", 0) else \
        _clamp((math.log10(cand["treasury"]) - 4) / 4) if isinstance(cand.get("treasury"), (int, float)) else 1.0
    ev = round(_clamp(cap_score * 0.6 + fairness * 0.3 + treasury_ok * 0.1), 3)
    driver = "cap" if cap_score >= fairness else "payout-fairness"
    return {"score": ev, "cap_score": round(cap_score, 3), "platform_rep": plat_rep,
            "fairness": round(fairness, 3), "dominant_driver": driver, "absent_signals": absent}


# ── archetype multiplier (Scientist+Differ+Speedrunner, NOT The Digger) ───────
def _archetype_multiplier(cand: dict) -> dict:
    """Down-weight Digger-shaped targets (mature + high-TVL + heavily-audited); up-weight young/uncommon."""
    mult = 1.0
    notes = []
    ac = cand.get("audit_count")
    if isinstance(ac, (int, float)):
        if ac >= 5:
            mult *= 0.8; notes.append("heavily-audited (-)")
        elif ac <= 1:
            mult *= 1.1; notes.append("thinly-audited (+)")
    tvl = cand.get("tvl")
    if isinstance(tvl, (int, float)) and tvl >= 5e8:
        mult *= 0.85; notes.append("very-high-TVL Digger target (-)")
    m = _months_since(cand.get("launch_date"))
    if m is not None and m <= 6:
        mult *= 1.1; notes.append("young (+)")
    elif m is not None and m >= 24:
        mult *= 0.85; notes.append("mature (-)")
    if _norm_lang(cand.get("lang", "")) in ("rust", "move", "ton"):
        mult *= 1.1; notes.append("uncommon-lang mechanism-match (+)")
    return {"multiplier": round(max(0.5, min(1.3, mult)), 3), "notes": notes}


# ── per-candidate composite ───────────────────────────────────────────────────
def score_candidate(cand: dict, seen: set, allow_pre_cutoff: bool = False) -> dict:
    rejects = _hard_rejects(cand)
    a4 = _axis4_cleanliness(cand, seen, allow_pre_cutoff)
    a1 = _axis1_bug_likelihood(cand)
    a2 = _axis2_detector_fit(cand)
    a3 = _axis3_payout_ev(cand)
    arche = _archetype_multiplier(cand)

    gated = bool(rejects) or (not a4["clean"])
    reject_reasons = [r["name"] for r in rejects]
    if not a4["clean"]:
        reject_reasons.append("already-seen / pre-cutoff (eval-cleanliness)" if a4["seen_hit"]
                              else "pre-cutoff (eval-cleanliness)")

    # composite: blend axes 1-3 (axis 2 may be None -> drop it), apply archetype mult to axis 1's weight.
    a2s = a2.get("score")
    a1_eff = _clamp(a1["score"] * arche["multiplier"])
    parts = [("bug_likelihood", a1_eff, 0.45), ("payout_ev", a3["score"], 0.30)]
    if isinstance(a2s, (int, float)):
        parts.append(("detector_fit", a2s, 0.25))
    wsum = sum(w for _, v, w in parts if isinstance(v, (int, float)))
    composite = round(sum(v * w for _, v, w in parts if isinstance(v, (int, float))) / wsum, 3) if wsum else 0.0
    if a4.get("pre_cutoff_penalized"):
        composite = round(composite * 0.7, 3)  # real-hunt mode: prior-knowledge risk discount

    return {
        "name": cand.get("name", "?"), "platform": cand.get("platform", ""),
        "lang": _norm_lang(cand.get("lang", "")), "cap": cand.get("cap"),
        "reject": gated, "reject_reasons": reject_reasons,
        "composite": 0.0 if gated else composite,
        "archetype": arche,
        "axis1_bug_likelihood": a1, "axis2_detector_fit": a2,
        "axis3_payout_ev": a3, "axis4_eval_cleanliness": a4,
    }


def build(candidates_path: Path, allow_pre_cutoff: bool = False) -> dict:
    raw = _load(candidates_path, None)
    if raw is None:
        cands = []
        note = f"no candidate file at {candidates_path} — seed it (see config schema in the header)"
    else:
        cands = raw.get("candidates", raw) if isinstance(raw, dict) else raw
        cands = [c for c in cands if isinstance(c, dict)]
        note = None
    seen = _seen_set()
    scored = [score_candidate(c, seen, allow_pre_cutoff) for c in cands]
    # rank: eligible (not reject) by composite desc, then rejected rows last
    scored.sort(key=lambda r: (not r["reject"], r["composite"]), reverse=True)
    doc = {
        "schema": "target_acquisition/v1", "is_gate": False, "advisory_only": True,
        "routes_in_production": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidates_path": str(candidates_path), "seen_set_size": len(seen),
        "knowledge_cutoff": KNOWLEDGE_CUTOFF,
        "note": ("ADVISORY target sourcing. RANKS candidate programs across 4 axes; the human SELECTS. "
                 "Hard-reject de-ranks + flags a TARGET (never a finding); axis-4 REJECTS already-seen / "
                 "pre-cutoff targets to keep the recall number honest. Never routes/gates/submits."),
        "counts": {"total": len(scored), "eligible": sum(1 for r in scored if not r["reject"]),
                   "rejected": sum(1 for r in scored if r["reject"])},
        "candidates": scored,
    }
    if note:
        doc["input_note"] = note
    return doc


def _fmt_pct(x):
    return f"{x:.3f}" if isinstance(x, (int, float)) else "n/a"


def render_md(doc: dict) -> str:
    L = ["# Target Acquisition — ranked shortlist (ADVISORY, is_gate:false)", "",
         f"_generated {doc['generated_at']} · seen-set {doc['seen_set_size']} · "
         f"{doc['counts']['eligible']} eligible / {doc['counts']['rejected']} rejected of "
         f"{doc['counts']['total']}_", "",
         "> " + doc["note"], "",
         "| # | target | lang | composite | bug-lik | det-fit | EV | arche× | verdict |",
         "|--:|--------|------|:--:|:--:|:--:|:--:|:--:|---------|"]
    rank = 0
    for r in doc["candidates"]:
        if r["reject"]:
            verdict = "❌ " + "; ".join(r["reject_reasons"][:2])
            n = "—"
        else:
            rank += 1; n = str(rank); verdict = "✓ eligible"
        L.append(f"| {n} | {r['name']} | {r['lang'] or '?'} | {_fmt_pct(r['composite'])} | "
                 f"{_fmt_pct(r['axis1_bug_likelihood']['score'])} | "
                 f"{_fmt_pct(r['axis2_detector_fit'].get('score'))} | "
                 f"{_fmt_pct(r['axis3_payout_ev']['score'])} | "
                 f"{r['archetype']['multiplier']} | {verdict} |")
    L += ["", "Caveat: axes 1 & 3 are inferred from candidate metadata (advisory). Axis 2 reuses the "
          "per-language detector scoreboard. Axis 4 is a hard eval-cleanliness gate, not a weight. "
          "The human picks the target from the eligible rows."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=str(CANDIDATES),
                    help="path to config/target_candidates.json")
    ap.add_argument("--out-json", default=str(ROOT / "evals" / "target_shortlist.json"))
    ap.add_argument("--out-md", default=str(ROOT / "evals" / "target_shortlist.md"))
    ap.add_argument("--allow-pre-cutoff", action="store_true",
                    help="relax the eval-clean pre-cutoff HARD reject to a soft penalty (real get-paid "
                         "hunts, where prior knowledge doesn't disqualify); seen-set still hard-rejects")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    doc = build(Path(args.candidates), allow_pre_cutoff=args.allow_pre_cutoff)
    Path(args.out_json).write_text(json.dumps(doc, indent=2) + "\n")
    Path(args.out_md).write_text(render_md(doc))

    if not args.quiet:
        c = doc["counts"]
        print(f"=== target acquisition (ADVISORY) — {c['eligible']} eligible / {c['rejected']} rejected "
              f"of {c['total']} · seen-set {doc['seen_set_size']} ===")
        if doc.get("input_note"):
            print(f"  ! {doc['input_note']}")
        rank = 0
        for r in doc["candidates"]:
            if r["reject"]:
                print(f"  ❌ {r['name']:28s} [{r['lang'] or '?':7s}] REJECT: {'; '.join(r['reject_reasons'][:2])}")
            else:
                rank += 1
                a2 = _fmt_pct(r['axis2_detector_fit'].get('score'))
                print(f"  {rank:>2}. {r['name']:28s} [{r['lang'] or '?':7s}] composite={r['composite']} "
                      f"(bug={r['axis1_bug_likelihood']['score']} fit={a2} "
                      f"EV={r['axis3_payout_ev']['score']} arche×{r['archetype']['multiplier']})")
        print(f"\nwrote {args.out_json} + {args.out_md}")
        print("The engine ranks; you pick the target from the eligible rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
