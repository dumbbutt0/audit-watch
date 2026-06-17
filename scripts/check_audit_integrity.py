#!/usr/bin/env python3
"""check_audit_integrity.py — workspace-integrity preflight (READ-ONLY).

An audit workspace can be silently overwritten by a LATER audit's run (k2-kinetic-2026-04 carried a K2
Soroban/Rust meta.json but Origin ARM *Solidity* findings — scoring it would have measured the wrong target).
This detects that class before a workspace is trusted/scored:

  1. lang_mismatch (CONTAMINATED): meta.language disagrees with the dominant file-extension of the findings in
     output/merged_findings.json (meta=rust but findings are .sol, etc.).
  2. empty_sources_with_findings (WARN): contracts/_sources has no source files yet merged_findings is non-empty
     (findings with nothing to re-derive them from — stale/orphaned).

It NEVER edits the workspace. Exit 0 = ok/warn, exit 2 = contaminated (so an eval/scoring preflight can block;
override with AUDITWATCH_INTEGRITY_OVERRIDE=1).

Usage:
    python scripts/check_audit_integrity.py [<audit-id>] [--all] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import _AUDITS_DIR  # noqa: E402

EXT_LANG = {".sol": "solidity", ".rs": "rust", ".move": "move"}
_SRC_EXTS = (".sol", ".rs", ".move")


def _meta_languages(meta: dict) -> set[str]:
    """meta.language may be 'solidity', 'solidity+rust', 'rust, move', etc. Return the normalized set."""
    raw = (meta.get("language") or "").lower()
    return {t for t in re.split(r"[+,/\s]+", raw) if t}


def _findings_ext(findings: list[dict]) -> tuple[str | None, Counter]:
    exts: Counter = Counter()
    for f in findings:
        loc = f.get("location")
        s = loc if isinstance(loc, str) else (loc.get("file", "") if isinstance(loc, dict) else "")
        s = (s or str(f.get("_contract", ""))).lower()
        for e in _SRC_EXTS:
            if e in s:
                exts[e] += 1
                break
    dom = exts.most_common(1)[0][0] if exts else None
    return dom, exts


def _has_source(audit_dir: Path) -> bool:
    src = audit_dir / "contracts" / "_sources"
    roots = [src] if src.exists() else [audit_dir / "contracts"]
    for r in roots:
        if r.exists():
            for _ in (p for p in r.rglob("*") if p.suffix in _SRC_EXTS):
                return True
    return False


def check_audit(aid: str) -> dict:
    adir = _AUDITS_DIR / aid
    meta = {}
    try:
        meta = json.loads((adir / "meta.json").read_text())
    except (OSError, json.JSONDecodeError):
        pass
    mf = adir / "output" / "merged_findings.json"
    findings = []
    if mf.exists():
        try:
            findings = json.loads(mf.read_text()).get("findings", [])
        except (OSError, json.JSONDecodeError):
            findings = []

    langs = _meta_languages(meta)
    dom_ext, ext_counts = _findings_ext(findings)
    issues: list[str] = []
    status = "ok"

    if findings and dom_ext and langs:
        ext_lang = EXT_LANG.get(dom_ext)
        if ext_lang and ext_lang not in langs:
            status = "contaminated"
            issues.append(
                f"lang_mismatch: meta.language={sorted(langs)} but findings are predominantly {dom_ext} "
                f"({ext_lang}) [{dict(ext_counts)}] — workspace likely overwritten by a different audit")

    if findings and not _has_source(adir):
        if status != "contaminated":
            status = "warn"
        issues.append("empty_sources_with_findings: contracts/_sources has no .sol/.rs/.move but "
                      "merged_findings is non-empty — findings are stale/orphaned (nothing to re-derive them)")

    return {"audit_id": aid, "status": status,
            "meta_language": meta.get("language"), "framework": meta.get("framework"),
            "findings_count": len(findings), "dominant_findings_ext": dom_ext,
            "ext_counts": dict(ext_counts), "issues": issues}


def _all_audit_ids() -> list[str]:
    if not _AUDITS_DIR.exists():
        return []
    return [p.name for p in sorted(_AUDITS_DIR.iterdir())
            if p.is_dir() and not p.name.startswith("_") and (p / "meta.json").exists()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audit_id", nargs="?", help="audit id (default: active audit)")
    ap.add_argument("--all", action="store_true", help="check every audit workspace")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.all:
        ids = _all_audit_ids()
    elif args.audit_id:
        ids = [args.audit_id]
    else:
        from audit_context import get_active_audit
        ids = [get_active_audit().get("audit_id")]
        ids = [i for i in ids if i]

    results = [check_audit(aid) for aid in ids if aid]
    contaminated = [r for r in results if r["status"] == "contaminated"]
    warned = [r for r in results if r["status"] == "warn"]

    # Per-audit report next to the (single) audit; for --all also a combined report under the active output.
    for r in results:
        out = _AUDITS_DIR / r["audit_id"] / "output"
        if out.exists():
            (out / "audit_integrity.json").write_text(json.dumps(r, indent=2) + "\n")

    if not args.quiet:
        for r in results:
            if r["status"] != "ok":
                tag = "CONTAMINATED" if r["status"] == "contaminated" else "WARN"
                print(f"[{tag}] {r['audit_id']}: " + " | ".join(r["issues"]))
        ok = len(results) - len(contaminated) - len(warned)
        print(f"audit-integrity: {len(results)} checked · ok {ok} · warn {len(warned)} · "
              f"contaminated {len(contaminated)}")

    override = os.environ.get("AUDITWATCH_INTEGRITY_OVERRIDE", "").strip() in ("1", "true", "yes", "on")
    if contaminated and not override:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
