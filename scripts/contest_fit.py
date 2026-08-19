#!/usr/bin/env python3
"""contest_fit.py — detector-market-fit scorer for a candidate contest (ADVISORY-ONLY, READ-ONLY).

Answers, before committing a fleet to a contest: "how well does our detector portfolio fit THIS
target's language + surface?" It joins three read-only sources:

  1. config/mechanism_classes.json  — the expert-bug FAMILIES we teach, filtered by the contest language,
     weighted by status (caught > reincorporated > seeded).
  2. evals/<lang>_scoreboard.json    — per-class PROVEN recall (by_mechanism_class.recall_of_surfaced).
     A class we *teach* but the scoreboard still misses is taught-but-unproven, discounted accordingly.
  3. documentation/architecture/detector_registry.md — research-detector "Supported architectures",
     keyword-matched against the in-scope filenames as an advisory hint (research detectors are un-wired).

There are NO contest-side mechanism tags today (tags live only on awarded findings), so fit is INFERRED
from language + surface and is explicitly advisory. This NEVER selects, routes, or gates — it writes
output/contest_fit.json (is_gate:false) + a human summary. It is not part of any pipeline gate.

Usage:
  python scripts/contest_fit.py --audit <audit_id>
  python scripts/contest_fit.py --scope <scope.json> --language <solidity|rust|move|ton>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

MECH = ROOT / "config" / "mechanism_classes.json"
REGISTRY = ROOT / "documentation" / "architecture" / "detector_registry.md"

# solidity's scoreboard is the un-prefixed default; other languages are <lang>_scoreboard.json
_SCOREBOARD = {
    "solidity": "scoreboard.json",
    "rust": "rust_scoreboard.json",
    "move": "move_scoreboard.json",
    "ton": "ton_scoreboard.json",
}
# taught-but-unmeasured strength when the scoreboard has no proven recall for a class
_STATUS_WEIGHT = {"caught": 1.0, "reincorporated": 0.7, "seeded": 0.35, "design": 0.2}
_WORD = re.compile(r"[a-z0-9]{4,}")


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _norm_lang(s: str) -> str:
    s = (s or "").strip().lower()
    return {"sol": "solidity", "solidity": "solidity", "rust": "rust", "solana": "rust",
            "move": "move", "sui": "move", "aptos": "move", "func": "ton", "ton": "ton"}.get(s, s)


def _resolve_inputs(args) -> tuple:
    """Return (audit_id, language, in_scope_files:list[str], scope_source)."""
    if args.audit:
        # resolve the NAMED audit directly — NOT audit_context.audit_path (that is scoped to the
        # currently-active audit, which is usually a different workspace).
        base = ROOT / "audits" / args.audit
        scope = _load(base / "scope.json", {})
        meta = _load(base / "meta.json", {})
        lang = _norm_lang(args.language or meta.get("language", ""))
        files = [f.get("file", "") if isinstance(f, dict) else str(f)
                 for f in scope.get("in_scope_files", [])]
        return (args.audit, lang, [f for f in files if f], str(base / "scope.json"))
    scope = _load(Path(args.scope), {}) if args.scope else {}
    lang = _norm_lang(args.language or scope.get("language", ""))
    files = [f.get("file", "") if isinstance(f, dict) else str(f)
             for f in scope.get("in_scope_files", [])]
    return (scope.get("audit_id", ""), lang, [f for f in files if f], args.scope or "")


def _class_fit(lang: str) -> dict:
    classes = (_load(MECH, {}) or {}).get("classes", {})
    board = _load(ROOT / "evals" / _SCOREBOARD.get(lang, f"{lang}_scoreboard.json"), {})
    by_class = board.get("by_mechanism_class", {}) if isinstance(board, dict) else {}

    strong, weak, taught = [], [], []
    eff_scores = []
    for name, c in classes.items():
        if _norm_lang(c.get("language", "")) != lang:
            continue
        status = c.get("status", "")
        sb = by_class.get(name)
        proven_recall = sb.get("recall_of_surfaced") if isinstance(sb, dict) else None
        # effective strength: proven scoreboard recall dominates; else the status weight (discounted, unproven)
        if proven_recall is not None:
            eff = float(proven_recall)
            basis = "proven"
        else:
            eff = _STATUS_WEIGHT.get(status, 0.3)
            basis = "taught_unmeasured"
        eff_scores.append(eff)
        row = {"class": name, "status": status, "effective_strength": round(eff, 3),
               "basis": basis, "proven_recall": proven_recall,
               "prompt_section": c.get("prompt_section", ""), "agent": c.get("agent", "")}
        if basis == "proven" and eff >= 0.6:
            strong.append(row)
        elif (basis == "proven" and eff <= 0.34) or (basis == "taught_unmeasured" and eff <= 0.35):
            weak.append(row)
        else:
            taught.append(row)

    fit = round(sum(eff_scores) / len(eff_scores), 3) if eff_scores else None
    strong.sort(key=lambda r: -r["effective_strength"])
    weak.sort(key=lambda r: r["effective_strength"])
    return {"language": lang, "fit_score": fit, "n_classes": len(eff_scores),
            "n_proven": sum(1 for e in eff_scores if e is not None) - eff_scores.count(None),
            "strong": strong, "weak": weak, "taught_unmeasured": taught}


def _detector_hints(files: list) -> list:
    """Keyword-overlap research detectors' Supported-architecture text against the in-scope filenames.
    Advisory ONLY — research detectors are un-wired (is_gate:false)."""
    if not REGISTRY.exists():
        return []
    fname_tokens = set()
    for f in files:
        fname_tokens |= set(_WORD.findall(f.lower()))
    hints = []
    cur = None
    for ln in REGISTRY.read_text().splitlines():
        m = re.match(r"^##\s+`([^`]+)`", ln)
        if m:
            cur = m.group(1)
            continue
        if cur and "**Supported architectures**" in ln:
            arch = ln.split("|")[2] if ln.count("|") >= 3 else ln
            arch = arch.strip()
            arch_tokens = set(_WORD.findall(arch.lower()))
            overlap = sorted(fname_tokens & arch_tokens)
            if overlap:
                hints.append({"detector": cur, "matched_terms": overlap[:8],
                              "supported_architectures": arch[:200],
                              "note": "research-only, un-wired (is_gate:false) — advisory surface hint"})
            cur = None
    return hints


def build(args) -> dict:
    audit_id, lang, files, scope_src = _resolve_inputs(args)
    cf = _class_fit(lang) if lang else {"language": lang, "fit_score": None, "n_classes": 0,
                                        "strong": [], "weak": [], "taught_unmeasured": []}
    hints = _detector_hints(files) if lang == "solidity" else []  # research detectors are Solidity-only today
    doc = {
        "schema": "contest_fit/v1", "is_gate": False, "advisory_only": True, "research_only": True,
        "routes_in_production": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_id": audit_id, "language": lang, "scope_source": scope_src,
        "in_scope_file_count": len(files),
        "note": ("ADVISORY fit inferred from LANGUAGE + SURFACE only — there are no contest-side mechanism "
                 "tags. fit_score = mean effective per-class strength (proven scoreboard recall where known, "
                 "else discounted status weight). Never selects/routes/gates a contest."),
        "class_fit": cf,
        "research_detector_hints": hints,
    }
    return doc


def _print(doc: dict) -> None:
    cf = doc["class_fit"]
    fs = cf.get("fit_score")
    print(f"=== contest-fit (ADVISORY) — {doc['audit_id'] or doc['scope_source']} ===")
    print(f"language: {doc['language'] or '?'} · in-scope files: {doc['in_scope_file_count']} · "
          f"mechanism classes for language: {cf.get('n_classes', 0)}")
    print(f"FIT SCORE: {fs if fs is not None else 'n/a'}  "
          f"(1.0 = every language class proven-recalled; discounted where only taught)")
    if cf.get("strong"):
        print(f"\nSTRONG ({len(cf['strong'])}) — proven recall ≥0.6:")
        for r in cf["strong"][:8]:
            print(f"  ✓ {r['class']}  (recall {r['proven_recall']}, {r['prompt_section']})")
    if cf.get("weak"):
        print(f"\nWEAK ({len(cf['weak'])}) — systematically missed / seeded-unproven:")
        for r in cf["weak"][:8]:
            pr = r['proven_recall']
            tag = f"recall {pr}" if pr is not None else f"{r['status']} (unmeasured)"
            print(f"  ✗ {r['class']}  ({tag}, {r['prompt_section']})")
    if doc["research_detector_hints"]:
        print(f"\nRESEARCH-DETECTOR SURFACE HINTS (un-wired, advisory):")
        for h in doc["research_detector_hints"]:
            print(f"  ~ {h['detector']}  (surface terms: {', '.join(h['matched_terms'])})")
    print("\nCaveat: fit is inferred from language+surface (no contest mechanism tags). "
          "Coverage-vs-reasoning: a taught-but-unproven class may still miss at runtime.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", help="audit_id under audits/ (reads its scope.json + meta language)")
    ap.add_argument("--scope", help="path to a scope.json (in_scope_files) when not using --audit")
    ap.add_argument("--language", help="override language (solidity|rust|move|ton)")
    ap.add_argument("--out", help="write the JSON doc to this path (default: output/contest_fit.json "
                                  "for --audit, else stdout only)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if not args.audit and not args.scope:
        ap.error("provide --audit <id> or --scope <scope.json>")

    doc = build(args)

    out_path = None
    if args.out:
        out_path = Path(args.out)
    elif args.audit:
        out_path = ROOT / "audits" / args.audit / "output" / "contest_fit.json"
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(doc, indent=2) + "\n")

    if not args.quiet:
        _print(doc)
        if out_path:
            print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
