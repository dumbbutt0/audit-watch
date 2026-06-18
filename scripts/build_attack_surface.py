#!/usr/bin/env python3
"""
build_attack_surface.py — Derive output/attack_surface.json from the coverage manifest (no LLM).

WHY: The /ite-audit specialist skill and cross_agent_connector.py read output/attack_surface.json
(`functions[]` ranked by `attack_surface_score`) to decide where to spend DEPTH first. In API mode
that file is produced by the agents/attacker_mindset.md LLM agent. In the api-free path
(`run_pipeline.sh analyze-resume`), Step 0.25 only writes step0_brief.md, so attack_surface.json was
NEVER produced for ANY language — every api-free fleet run lacked it and had to bridge it by hand.

The manifest (built in Step 1.6) already carries a deterministic per-item `attack_surface_score` plus
visibility/signature/tags/external_calls/sink flags, so this script just projects the function-like
items into the schema the consumers expect. Deterministic, idempotent, language-agnostic.

SAFETY: never clobbers an LLM/agent-authored attack_surface.json. It only writes when the file is
absent or was itself produced by this script (marked `_derived_from`). So if the API attacker_mindset
agent later writes the richer file, this won't overwrite it.

Usage:
    python scripts/build_attack_surface.py            # write if missing/derived
    python scripts/build_attack_surface.py --force     # always (re)derive from the manifest
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

# manifest item kinds that represent a callable attack surface (functions ranked for DEPTH)
_FUNCTION_KINDS = {"function", "constructor", "initializer"}
_DERIVED_MARKER = "coverage_manifest.json"


def _project(item: dict) -> dict:
    """Project a manifest function-item into the attack_surface.json function schema consumers read."""
    return {
        "name": item.get("name", ""),
        "contract": item.get("contract", ""),
        "file": item.get("file", ""),
        "signature": item.get("signature", ""),
        "visibility": item.get("visibility", ""),
        "mutability": item.get("mutability", ""),
        "attack_surface_score": item.get("attack_surface_score", 0),
        "tags": item.get("tags", []),
        "external_calls": item.get("external_calls", False),
        "in_tainted_sink": item.get("in_tainted_sink", False),
        "source_span": item.get("source_span", {}),
    }


def main(argv: list[str] | None = None) -> int:
    force = "--force" in (argv if argv is not None else sys.argv[1:])

    out_path = audit_path("output") / "attack_surface.json"
    if out_path.exists() and not force:
        try:
            existing = json.loads(out_path.read_text())
        except (json.JSONDecodeError, OSError):
            existing = {}
        # Preserve an LLM/agent-authored file (it has no _derived_from marker). Only this script's own
        # output is safe to refresh.
        if isinstance(existing, dict) and existing.get("_derived_from") != _DERIVED_MARKER:
            print(f"[build_attack_surface] attack_surface.json present and not manifest-derived "
                  f"(agent-authored) — leaving it untouched. Use --force to override.")
            return 0

    man_path = audit_path("output") / "coverage_manifest.json"
    if not man_path.exists():
        raise SystemExit("[build_attack_surface] coverage_manifest.json missing — "
                         "run scripts/build_coverage_manifest.py first.")
    manifest = json.loads(man_path.read_text())
    items = manifest.get("items", [])

    functions = [_project(it) for it in items if it.get("kind") in _FUNCTION_KINDS]
    functions.sort(key=lambda f: f.get("attack_surface_score", 0), reverse=True)

    doc = {
        "_derived_from": _DERIVED_MARKER,
        "_note": "Deterministic api-free attack surface projected from coverage_manifest.json "
                 "(no LLM). In API mode agents/attacker_mindset.md writes a richer version; this "
                 "file is the api-free equivalent so /ite-audit + cross_agent_connector always have it.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "function_count": len(functions),
        "high_surface_count": sum(1 for f in functions if f.get("attack_surface_score", 0) >= 3),
        "functions": functions,
    }
    out_path.write_text(json.dumps(doc, indent=2))
    top = [(f["name"], f["attack_surface_score"]) for f in functions[:5]]
    print(f"[build_attack_surface] attack_surface.json → {out_path}")
    print(f"     functions: {len(functions)} · high-surface (score>=3): {doc['high_surface_count']}")
    print(f"     top: {top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
