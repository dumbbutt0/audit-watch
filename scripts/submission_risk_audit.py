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


def _reachability_axis(path: str, locus: str, cfg: dict, manifest: dict | None) -> dict:
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


def _novelty_axis(text: str, kb_present: bool) -> dict:
    if not kb_present:
        return {"level": "checklist_required",
                "rationale": "no KB/solodit crossref on disk — manually check for a prior/duplicate public "
                             "report before submitting"}
    # KB crossref present: a real similarity read would go here; conservatively prompt verification.
    return {"level": "checklist_required",
            "rationale": "KB crossref present — verify the closest known finding is not the same bug "
                         "(duplicate/known) before submitting"}


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
    if nov["level"] == "checklist_required":
        out.append(f"submission_risk[novelty]: {nov['rationale']}")
    return out


def build() -> dict:
    out_dir = audit_path("output")
    merged = _load(out_dir / "merged_findings.json", {})
    findings = merged.get("findings", []) if isinstance(merged, dict) else (merged or [])
    cfg = _load(PATTERNS, {})
    manifest = _deployment_manifest()
    kb_present = (out_dir / "kb_crossref.md").exists()

    records = []
    for f in findings:
        fid = f.get("id")
        if not fid:
            continue
        text = _finding_text(f)
        design = _design_axis(text, cfg)
        reach = _reachability_axis(_finding_path(f), _finding_locus(f), cfg, manifest)
        nov = _novelty_axis(text, kb_present)
        advisories = _advisories(fid, design, reach, nov)
        # overall: high if a design/known shape matched OR reachability is not_wired/flagged; review if anything
        # needs a human checklist; low otherwise. (Advisory severity only — never a gate verdict.)
        if design["level"] == "match" or reach["level"] in ("not_wired", "flag"):
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
