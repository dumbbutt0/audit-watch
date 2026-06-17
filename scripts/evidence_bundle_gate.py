#!/usr/bin/env python3
"""
evidence_bundle_gate.py — READ-ONLY Evidence Bundle Gate (research-only).

Consumes the normalization-layer output (research_findings_normalized.json) and, for each normalized record,
assembles a concrete EVIDENCE BUNDLE (code location + snippet + detector evidence + rationale) and answers ONE
narrow question:

    "Is this candidate evidence-complete enough for a human/judge to INVESTIGATE?"

It is a COMPLETENESS check — NOT "is this a bug", NOT severity, NOT exploitability. Invariant: ASSEMBLE, DON'T
ADJUDICATE.

STRICTLY RESEARCH-ONLY:
  * Every bundle carries routing_allowed:false and research_only:true.
  * confidence and declared_severity_potential are carried VERBATIM from the normalized record — never changed.
  * It emits NO bug/severity/exploitability verdict (no poc/submit/downgrade/reject). Its only recommendation is
    a completeness one: ready_for_review | needs_more_evidence.
  * Defensive guard: if the input's top-level routing_allowed is not false → refuse.
  * Read-only: reads the normalized file + source snippets; never writes to a workspace; never calls the
    production exploitability/submission/gate engine.

Usage:
  python scripts/evidence_bundle_gate.py --normalized <research_findings_normalized.json> \
      --out evidence_bundles.json [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "evidence_bundle_gate.json"
SCHEMA_VERSION = "1.0"
_FILE_CACHE: dict[str, list[str]] = {}


def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {"required_elements": ["location_resolvable", "code_snippet", "candidate_surface", "signal_type",
                                      "confidence", "evidence_payload", "rationale", "traceability"],
                "rationale_fields": ["missing_binding_explanation", "reason", "missing_context"],
                "snippet_max_lines": 40}


def _parse_ref(file_line_refs: str) -> tuple[str, int | None]:
    if not file_line_refs or ":" not in file_line_refs:
        return file_line_refs or "", None
    f, _, ln = file_line_refs.rpartition(":")
    try:
        return f, int(ln)
    except ValueError:
        return file_line_refs, None


def _snippet(file_rel: str, start: int | None, max_lines: int) -> str | None:
    """Read a bounded, brace-aware source snippet (read-only). None if unresolvable."""
    if not file_rel or not start:
        return None
    p = ROOT / file_rel
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines or start > len(lines):
        return None
    i = start - 1
    # brace-aware window: from the signature line until depth returns to 0, capped at max_lines
    depth, started, out = 0, False, []
    for k in range(i, min(len(lines), i + max_lines)):
        ln = lines[k]
        out.append(ln)
        depth += ln.count("{") - ln.count("}")
        if "{" in ln:
            started = True
        if started and depth <= 0:
            break
    text = "\n".join(out).strip()
    return text or None


def assemble_bundle(rec: dict, cfg: dict) -> dict:
    file_rel, start = _parse_ref(rec.get("file_line_refs", ""))
    snippet = _snippet(file_rel, start, cfg.get("snippet_max_lines", 40))
    evidence = rec.get("evidence", {}) or {}
    rationale = next((evidence[k] for k in cfg.get("rationale_fields", []) if evidence.get(k)), None)
    surface = rec.get("candidate_surface", "")

    # presence-based completeness (NO adjudication)
    checks = {
        "location_resolvable": bool(file_rel and start),
        "code_snippet": bool(snippet),
        "candidate_surface": bool(surface and "." in surface),
        "signal_type": bool(rec.get("signal_type")),
        "confidence": bool(rec.get("confidence")),
        "evidence_payload": bool(evidence),
        "rationale": bool(rationale),
        "traceability": bool(rec.get("candidate_id") and rec.get("source_audit_path")),
    }
    required = cfg.get("required_elements", list(checks))
    present = [k for k in required if checks.get(k)]
    missing = [k for k in required if not checks.get(k)]
    complete = not missing
    return {
        "candidate_id": rec.get("candidate_id", ""), "detector": rec.get("detector", ""),
        "detector_version": rec.get("detector_version", ""), "signal_type": rec.get("signal_type", ""),
        "candidate_surface": surface,
        "confidence": rec.get("confidence", ""),                              # VERBATIM
        "declared_severity_potential": rec.get("declared_severity_potential", ""),  # VERBATIM
        "source_audit_path": rec.get("source_audit_path", ""),
        "location": {"file": file_rel, "start_line": start, "resolvable": bool(file_rel and start)},
        "code_snippet": snippet,
        "evidence_signals": evidence,
        "rationale": rationale,
        "evidence_completeness": {"status": "COMPLETE" if complete else "INCOMPLETE",
                                  "present": present, "missing": missing},
        "bundle_status": "READY_FOR_REVIEW" if complete else "INSUFFICIENT_EVIDENCE",
        "investigate_recommendation": "ready_for_review" if complete else "needs_more_evidence",
        "routing_allowed": False, "research_only": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only evidence bundle gate (completeness, not verdict).")
    ap.add_argument("--normalized", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    np = Path(args.normalized)
    if not np.is_absolute() and not np.exists():
        np = ROOT / args.normalized
    norm = json.loads(np.read_text())
    # defensive guard: only ever consume a research-only normalized file
    if norm.get("routing_allowed", True) is not False:
        raise SystemExit("[evidence_bundle_gate] refused: input routing_allowed is not false (research-only only)")

    cfg = _cfg()
    bundles = [assemble_bundle(r, cfg) for r in norm.get("records", [])]
    out = {
        "schema_version": SCHEMA_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(),
        "routing_allowed": False, "source_normalized": str(np),
        "bundles": bundles,
        "summary": {
            "total_bundles": len(bundles),
            "by_status": dict(Counter(b["bundle_status"] for b in bundles)),
            "by_detector": dict(Counter(b["detector"] for b in bundles)),
        },
    }
    Path(args.out).write_text(json.dumps(out, indent=2))
    if not args.quiet:
        print(f"[evidence_bundle_gate] RESEARCH-ONLY (completeness, not verdict) · bundles {len(bundles)} · "
              f"by_status {out['summary']['by_status']} · wrote {args.out}")
        for b in bundles:
            miss = "" if not b["evidence_completeness"]["missing"] else f" missing={b['evidence_completeness']['missing']}"
            print(f"   • {b['candidate_surface']:40} {b['bundle_status']}{miss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
