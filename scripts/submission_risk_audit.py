#!/usr/bin/env python3
"""submission_risk_audit.py — pre-READY submission-risk scorer (ADVISORY-ONLY, READ-ONLY, deterministic).

The first batch of real-world bounty outcomes showed the PoCs were technically valid in nearly every case;
rejections clustered on three axes that have NOTHING to do with PoC validity (documentation/real_world_results.json
calibration_lessons):
  1. deployment_reachability — vulnerable code present in source but NOT wired in the live deployment
  2. duplicate / novelty       — already reported / known prior
  3. design_accepted / known   — excluded by program rules

This flags each finding on those axes so effort isn't spent submitting a finding likely to bounce. It is
**advisory-only**: it writes output/submission_risk.json and a human-readable advisory string per finding; it
NEVER changes a finding's state, NEVER auto-rejects, and NEVER writes rejection_rules.jsonl. Where the wiring
cannot be known from the finding text (the common case for reachability/novelty), it emits `checklist_required`
rather than a confident score — the human/agent answers via agents/submission_risk_review.md.

Distinct from confirm_reachability.py (that checks CODE-PATH reachability inside the audited contracts; this
checks LIVE-DEPLOYMENT wiring + novelty + design-acceptance, the bounty-rejection axes).

Usage:  python scripts/submission_risk_audit.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "config" / "submission_risk_patterns.json"


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _finding_text(f: dict) -> str:
    parts = [f.get("title", ""), f.get("description", ""), f.get("recommendation", ""),
             f.get("vuln_type") or ""]
    return " ".join(str(p) for p in parts).lower()


def _finding_path(f: dict) -> str:
    """The finding's CODE LOCATION only (file / function / contract). Module & handler manifest terms are matched
    against THIS, not the prose — so a generic crate name like 'token' matches contracts/token/... but NOT a
    finding that merely says 'token amount' in its description."""
    loc = f.get("location")
    bits = []
    if isinstance(loc, dict):
        bits = [loc.get("file") or "", loc.get("function") or "", loc.get("contract") or ""]
    elif isinstance(loc, str):
        bits = [loc]
    bits.append(f.get("_contract") or "")
    return " ".join(str(b) for b in bits).lower()


def _finding_locus(f: dict) -> str:
    """Finding text PLUS its path — what the text-anchored terms (profiles, no-op fallbacks) match against."""
    return (_finding_text(f) + " " + _finding_path(f)).lower()


_MANIFEST_TEMPLATE = {
    "schema": "deployment_manifest/v1",
    "_note": "Human-authored LIVE-deployment facts for this audit. submission_risk_audit.py matches these terms "
             "(token-boundary) against each finding's file/function/contract/title to AUTO-decide deployment "
             "reachability (not_wired => likely OUT OF SCOPE) instead of asking. Leave a list empty if unknown. "
             "Advisory-only: it never changes a finding's state.",
    "active_profiles": [], "inactive_profiles": [],
    "active_modules": [], "inactive_modules": [],
    "unregistered_handlers": [], "noop_fallbacks": [],
    "onchain": {
        "_note": "OPTIONAL live-deployment coordinates for scripts/live_reachability_check.py. With a QuickNode "
                 "endpoint set it verifies each target's selector is in the deployed (proxy-resolved) bytecode "
                 "and that gating storage is active; a live not_wired verdict overrides the heuristics below.",
        "address": "", "chain": "ethereum",
        "targets": [],            # [{"finding_id": "F-1", "signature": "withdraw(uint256)"}]
        "storage_assertions": [],  # [{"finding_id": "F-1", "slot": 3, "expect_nonzero": true}]
    },
    "notes": "",
}


def _deployment_manifest() -> dict | None:
    p = audit_path("deployment_manifest.json")
    if not p.exists():
        return None
    m = _load(p, None)
    return m if isinstance(m, dict) else None


def _has(text: str, kw: str) -> bool:
    """Token-boundary match (not substring): 'nav' must not match 'navigation'/'Aerodrome'. The keyword may be
    a phrase or contain non-alnum chars (request-time, acc_reward_per_share, 1%) — bordered by non-alnum/edges."""
    return re.search(r"(?<![a-z0-9])" + re.escape(kw.lower()) + r"(?![a-z0-9])", text) is not None


def _matches(text: str, pat: dict) -> bool:
    """all-of `all`, at-least-one-of `any`, none-of `none` (all optional), token-boundary matched."""
    if any(not _has(text, k) for k in pat.get("all", [])):
        return False
    anyset = pat.get("any", [])
    if anyset and not any(_has(text, k) for k in anyset):
        return False
    if any(_has(text, k) for k in pat.get("none", [])):
        return False
    return True


def _design_axis(text: str, cfg: dict) -> dict:
    for pat in cfg.get("design_acceptance", []):
        if (pat.get("all") or pat.get("any")) and _matches(text, pat):
            return {"level": "match", "pattern": pat["id"], "name": pat["name"],
                    "outcome_provenance": pat.get("outcome_provenance", ""),
                    "rationale": pat.get("rationale", "")}
    return {"level": "low", "rationale": "no known design-accepted/known-pattern shape matched"}


# Module + handler names are CODE IDENTIFIERS -> match the path only (avoids generic-name prose FPs like
# 'token' matching "token amount"). Profiles + no-op-fallback type names are described in prose -> match the locus.
_PATH_INACTIVE = ("inactive_modules", "unregistered_handlers")
_TEXT_INACTIVE = ("inactive_profiles", "noop_fallbacks")
_PATH_ACTIVE = ("active_modules",)
_TEXT_ACTIVE = ("active_profiles",)


def _first_hit(s: str, manifest: dict, keys) -> tuple[str, str] | None:
    """Return (key, term) for the first manifest term (token-boundary) found in string `s`."""
    for k in keys:
        for term in manifest.get(k, []) or []:
            if _has(s, term):
                return k, term
    return None


def _reachability_axis(path: str, locus: str, cfg: dict, manifest: dict | None,
                       live: dict | None = None) -> dict:
    # 0) Live on-chain evidence (live_reachability_check.py) wins over manifest/heuristic/checklist — it is a
    #    direct read of the deployed contract, not a guess.
    if live and live.get("level") in ("not_wired", "wired"):
        lvl = live["level"]
        return {"level": lvl, "source": "onchain",
                "rationale": live.get("rationale", f"on-chain: {lvl}")}
    # 1) Deployment manifest (human-supplied live-deployment facts) — auto-decides where it can.
    #    Module/handler terms match the PATH; profile/fallback terms match the prose LOCUS.
    if manifest:
        inactive = _first_hit(path, manifest, _PATH_INACTIVE) or _first_hit(locus, manifest, _TEXT_INACTIVE)
        if inactive:
            return {"level": "not_wired", "matched": {"field": inactive[0], "term": inactive[1]},
                    "rationale": f"deployment manifest marks '{inactive[1]}' ({inactive[0]}) as NOT live — the "
                                 f"vulnerable path is likely UNREACHABLE in the deployment (probable OUT OF SCOPE); "
                                 f"verify against the deployed config before submitting"}
        active = _first_hit(path, manifest, _PATH_ACTIVE) or _first_hit(locus, manifest, _TEXT_ACTIVE)
        if active:
            return {"level": "wired", "matched": {"field": active[0], "term": active[1]},
                    "rationale": f"deployment manifest confirms '{active[1]}' ({active[0]}) is live — reachable"}
        # manifest present but silent on this finding -> fall through to signals/checklist
    # 2) Text signals (heuristic hint).
    sig = cfg.get("deployment_reachability_signals", {})
    hits = [label for label in ("null_or_noop_fallback", "profile_or_feature_gated")
            if any(_has(locus, k) for k in sig.get(label, []))]
    if hits:
        return {"level": "flag", "signals": sorted(set(hits)),
                "rationale": "finding text hints the path may be feature/profile-gated or behind a no-op "
                             "fallback — verify it is wired in the LIVE deployment before submitting"}
    # 3) Cannot decide — wiring is deployment knowledge, not source. Ask (fill the manifest or the checklist).
    return {"level": "checklist_required",
            "rationale": "confirm the vulnerable path is WIRED in the live deployment (not feature-flagged off / "
                         "Null-fallback / unregistered handler) — fill audits/<id>/deployment_manifest.json "
                         "(run_pipeline submission-risk --init-manifest) or see agents/submission_risk_review.md"}


_DUP_REGISTRY = ROOT / "data" / "duplicate_registry.jsonl"
_WORD = re.compile(r"[a-z0-9]{3,}")

# advisory thresholds (mirror existing conventions: retriever emits KB_MATCH >0.75;
# Hermes treats KB similarity <0.4 as novel)
_KB_DUP = 0.75   # >= => likely the same known bug
_KB_NEAR = 0.40  # >= => close enough to verify by hand
_REG_OVERLAP = 0.30  # token-Jaccard vs one of OUR prior submitted root-cause signatures


def _kb_max_similarity(vuln_type: str, text: str) -> tuple:
    """Best KB similarity for this finding, or (None, ...) if the KB can't be read.
    Returns (max_similarity_score | None, closest_title, closest_protocol)."""
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from tools.retriever import query_kb
    except Exception:
        return (None, "", "")
    try:
        results = query_kb(vuln_type or "", text[:800], top_k=5)
    except Exception:
        return (None, "", "")
    if not isinstance(results, list) or not results or results[0].get("error"):
        return (None, "", "")
    scored = [r for r in results if isinstance(r, dict) and isinstance(r.get("similarity_score"), (int, float))]
    if not scored:
        return (None, "", "")
    top = max(scored, key=lambda r: r["similarity_score"])
    return (float(top["similarity_score"]), top.get("title", ""), top.get("protocol", ""))


def _registry_overlap(text: str) -> tuple:
    """Token-Jaccard of the finding against OUR previously-submitted findings' root-cause signatures.
    A high hit means we (or the dedup registry) already reported this shape. Returns (overlap, registry_id, title)."""
    ftok = set(_WORD.findall(text))
    if not ftok:
        return (0.0, "", "")
    best = (0.0, "", "")
    for line in _load_jsonl(_DUP_REGISTRY):
        sig = str(line.get("root_cause_signature") or line.get("title") or "").lower()
        stok = set(_WORD.findall(sig))
        if not stok:
            continue
        j = len(ftok & stok) / len(ftok | stok)
        if j > best[0]:
            best = (round(j, 3), line.get("registry_id", ""), line.get("title", ""))
    return best


def _load_jsonl(p: Path) -> list:
    out = []
    try:
        for ln in p.read_text().splitlines():
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return out


def _novelty_axis(text: str, vuln_type: str, kb_present: bool) -> dict:
    """Advisory novelty read. novelty_score = 1 - max(KB similarity, registry overlap); higher = more novel.
    Falls back to the prior checklist_required prompt when the KB can't be read (fully additive)."""
    reg_j, reg_id, reg_title = _registry_overlap(text)
    kb_sim, kb_title, kb_proto = _kb_max_similarity(vuln_type, text)

    if kb_sim is None:
        # KB unreadable (no Chroma / empty / error) — preserve prior behavior, but fold in a registry hit.
        base_rat = ("no KB/solodit crossref on disk — manually check for a prior/duplicate public report "
                    "before submitting") if not kb_present else \
                   ("KB present but not queryable (run the scraper / index) — verify the closest known finding "
                    "is not the same bug before submitting")
        out = {"level": "checklist_required", "novelty_score": None, "kb_max_similarity": None,
               "registry_overlap": reg_j, "rationale": base_rat}
        if reg_j >= _REG_OVERLAP:
            out["level"] = "likely_duplicate"
            out["rationale"] = (f"overlaps our prior finding {reg_id} ('{reg_title}', Jaccard {reg_j}) — "
                                f"likely a re-report of a shape we already submitted")
        return out

    max_sim = max(kb_sim, reg_j)
    novelty = round(1.0 - max_sim, 3)
    src = f"KB '{kb_title}'" + (f" [{kb_proto}]" if kb_proto else "") if kb_sim >= reg_j else \
          f"our prior {reg_id} ('{reg_title}')"

    if kb_sim >= _KB_DUP or reg_j >= _REG_OVERLAP:
        level, rat = "likely_duplicate", (f"closest prior = {src} at similarity {round(max_sim,3)} "
                                          f"(novelty {novelty}) — verify this is not the SAME bug before submitting")
    elif kb_sim >= _KB_NEAR:
        level, rat = "checklist_required", (f"near-match to {src} at similarity {round(kb_sim,3)} "
                                            f"(novelty {novelty}) — confirm it's a distinct root cause")
    else:
        level, rat = "novel", (f"no close prior (best {src} at {round(max_sim,3)}, novelty {novelty}) — "
                               f"looks original")
    return {"level": level, "novelty_score": novelty, "kb_max_similarity": round(kb_sim, 3),
            "registry_overlap": reg_j, "closest_known": kb_title, "closest_protocol": kb_proto,
            "rationale": rat}


def _advisories(fid: str, design: dict, reach: dict, nov: dict) -> list[str]:
    out = []
    if design["level"] == "match":
        out.append(f"submission_risk[design_acceptance]: matches '{design['name']}' "
                   f"(program-excluded/known shape; provenance: {design['outcome_provenance']}). "
                   f"{design['rationale']}")
    if reach["level"] == "not_wired":
        out.append(f"submission_risk[deployment_reachability]: LIKELY OUT OF SCOPE — {reach['rationale']}")
    elif reach["level"] == "flag":
        out.append(f"submission_risk[deployment_reachability]: {reach['rationale']} "
                   f"(signals: {', '.join(reach['signals'])})")
    elif reach["level"] == "checklist_required":
        out.append(f"submission_risk[deployment_reachability]: {reach['rationale']}")
    if nov["level"] == "likely_duplicate":
        out.append(f"submission_risk[novelty]: LIKELY DUPLICATE/KNOWN — {nov['rationale']}")
    elif nov["level"] == "checklist_required":
        out.append(f"submission_risk[novelty]: {nov['rationale']}")
    return out


def build() -> dict:
    out_dir = audit_path("output")
    merged = _load(out_dir / "merged_findings.json", {})
    findings = merged.get("findings", []) if isinstance(merged, dict) else (merged or [])
    cfg = _load(PATTERNS, {})
    manifest = _deployment_manifest()
    kb_present = (out_dir / "kb_crossref.md").exists()
    live_doc = _load(out_dir / "live_reachability.json", {})
    live_by_id = live_doc.get("findings", {}) if isinstance(live_doc, dict) else {}

    records = []
    for f in findings:
        fid = f.get("id")
        if not fid:
            continue
        text = _finding_text(f)
        design = _design_axis(text, cfg)
        reach = _reachability_axis(_finding_path(f), _finding_locus(f), cfg, manifest, live_by_id.get(fid))
        nov = _novelty_axis(text, f.get("vuln_type") or "", kb_present)
        advisories = _advisories(fid, design, reach, nov)
        # overall: high if a design/known shape matched OR reachability is not_wired/flagged OR novelty flags a
        # likely duplicate; review if anything needs a human checklist; low otherwise. (Advisory only — never a gate.)
        if design["level"] == "match" or reach["level"] in ("not_wired", "flag") or nov["level"] == "likely_duplicate":
            overall = "high"
        elif any(x["level"] == "checklist_required" for x in (reach, nov)):
            overall = "review"
        else:
            overall = "low"
        records.append({"finding_id": fid, "overall": overall,
                        "deployment_reachability_risk": reach, "novelty_risk": nov,
                        "design_acceptance_risk": design, "advisories": advisories})

    doc = {
        "schema": "submission_risk/v1", "is_gate": False, "advisory_only": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "ADVISORY-ONLY pre-READY flags on bounty-rejection axes (reachability/novelty/design). Never "
                "changes finding state, never auto-rejects. checklist_required => answer via "
                "agents/submission_risk_review.md.",
        "kb_crossref_present": kb_present,
        "deployment_manifest_present": manifest is not None,
        "counts": {lvl: sum(1 for r in records if r["overall"] == lvl) for lvl in ("high", "review", "low")},
        "findings": records,
    }
    (out_dir / "submission_risk.json").write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--init-manifest", action="store_true",
                    help="write a deployment_manifest.json template for the auditor to fill (won't overwrite)")
    args = ap.parse_args()
    if args.init_manifest:
        p = audit_path("deployment_manifest.json")
        if p.exists():
            print(f"deployment_manifest.json already exists: {p} (left untouched)")
            return 0
        p.write_text(json.dumps(_MANIFEST_TEMPLATE, indent=2) + "\n")
        print(f"Wrote deployment-manifest template: {p}\n  Fill active_/inactive_ profiles+modules, "
              f"unregistered_handlers, noop_fallbacks — then re-run submission-risk.")
        return 0
    d = build()
    if not args.quiet:
        c = d["counts"]
        print(f"Submission-risk (ADVISORY): {len(d['findings'])} finding(s) — "
              f"high {c['high']} · review {c['review']} · low {c['low']}")
        for r in d["findings"]:
            if r["overall"] != "low":
                for a in r["advisories"]:
                    print(f"   {r['finding_id']}: {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
