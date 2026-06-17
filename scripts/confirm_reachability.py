#!/usr/bin/env python3
"""
confirm_reachability.py — Reachability-truth analyzer (deterministic, no LLM).

Reads the confirm inventory + manifest + dispositions + taxonomy and answers, per candidate, the precision
question: "can an UNPRIVILEGED attacker drive the claimed path to the claimed impact in the relevant deployed
lifecycle state?" — via the manifest's visibility/modifiers/kind/file and the dispositions.

Honesty rule (critical): deterministic checks only DOWNGRADE/FLAG. `mark_false_positive` is reserved for a
clear deterministic kill (dead_path). A speculative finding (a public entrypoint exists but the precondition/
impact is unproven) routes to `uncertain` + `needs_runtime_poc` — NEVER auto-FP and NEVER auto-confirm. We do
not overclaim in either direction. READ-ONLY on findings; writes only output/confirm/reachability_analysis.json.

Usage: python scripts/confirm_reachability.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "confirm_reachability_patterns.json"


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _speculative(c: dict) -> bool:
    """A finding is speculative if its impact wording is conditional / its precondition is a state that must
    be 'driven' / 'forced' without a shown path (scans title + impact + technique)."""
    blob = " ".join([str(c.get("title", "")), str(c.get("claimed_impact", "")),
                     str((c.get("source_evidence") or {}).get("technique", ""))]).lower()
    return any(w in blob for w in ("drive ", "force ", "if ", "could ", "may ", "potential", "assuming",
                                   "unproven", "below ", "exceeds", "overflow", "underflow", "divide by zero",
                                   "div-by", "div by", "division by", "revert", "underflows", "/ 0", "by zero",
                                   "could be", "theoretically"))


def main() -> int:
    tax = _load(CONFIG, None)
    inv = _load(audit_path("output") / "confirm" / "confirm_inventory.json", "candidates")
    if not inv:
        raise SystemExit("[confirm_reachability] no inventory — run confirm_inventory.py first.")
    man = _load(audit_path("output") / "coverage_manifest.json", "items")
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    # index manifest functions by name (prefer in-scope production defs)
    by_name = defaultdict(list)
    for it in man:
        if it.get("kind") in ("function", "constructor", "initializer") and it.get("name"):
            by_name[it["name"].lower()].append(it)

    priv_terms = [t.lower() for t in tax.get("privileged_modifier_terms", [])]
    lc_files = [t.lower() for t in tax.get("lifecycle_file_terms", [])]
    lc_names = [t.lower() for t in tax.get("lifecycle_name_terms", [])]

    def _resolve(name):
        cands = by_name.get((name or "").lower(), [])
        ins = [c for c in cands if c.get("in_scope", True)]
        return (ins or cands)

    results = []
    for c in inv:
        fns = c.get("affected_functions") or ([c.get("claimed_sink")] if c.get("claimed_sink") else [])
        resolved = [m for n in fns for m in _resolve(n)]
        sink_file = (c.get("claimed_sink_file") or "").lower()
        blockers, warnings, evidence = [], [], []

        # gather manifest signals across resolved + the claimed entrypoint
        ep_resolved = _resolve(c.get("claimed_entrypoint"))
        all_res = resolved + ep_resolved
        # privileged ONLY if every resolved fn actually carries a privileged modifier (all() over an empty
        # filtered set would be vacuously true — so check each fn directly, no 'if modifiers' filter).
        def _has_priv(m):
            return any(p in (mod or "").lower() for mod in (m.get("modifiers") or []) for p in priv_terms)
        # an UNPRIVILEGED attacker entrypoint = external/public + state-changing + NOT privileged-gated.
        # A privileged external fn (onlyOwner/onlyGovernance) is NOT an attacker entrypoint.
        has_external = any(m.get("visibility") in ("external", "public") and m.get("mutability") not in ("view", "pure")
                           and not _has_priv(m) for m in all_res)
        is_initializer = any(m.get("kind") == "initializer" for m in resolved) or \
            any(t in (c.get("claimed_sink") or "").lower() for t in lc_names) and any(t in sink_file for t in lc_files)
        in_lifecycle_file = any(t in sink_file for t in lc_files) or \
            any(t in (m.get("file") or "").lower() for m in resolved for t in lc_files)
        privileged = bool(resolved) and all(_has_priv(m) for m in resolved)
        any_priv = any(_has_priv(m) for m in resolved)
        internal_only = bool(resolved) and all(m.get("visibility") in ("internal", "private") for m in resolved)
        dispositions = {disp.get(r["id"], {}).get("status") for r in resolved}
        deferred = bool(resolved) and dispositions == {"deferred_out_of_scope"}
        missing_refs = not c.get("manifest_refs")
        is_dup = bool(c.get("duplicate_relationships")) or c.get("classification") == "duplicate_of_existing"

        # ── classify (most-specific / most-blocking first) ──
        status, action = "uncertain", "needs_manual_review"
        if is_dup:
            status, action = "duplicate", "merge_duplicate"
            warnings.append("duplicate_root_cause: " + ", ".join(str(x) for x in c["duplicate_relationships"][:3]))
        elif missing_refs:
            status, action = "insufficient_evidence", "needs_manual_review"
            blockers.append("no manifest_refs — affected code not pinned")
        elif deferred:
            status, action = "dead_path", "mark_false_positive"
            blockers.append("all resolved functions are deferred_out_of_scope (dead/out-of-scope path)")
        elif is_initializer or (in_lifecycle_file and not has_external):
            status, action = "lifecycle_only", "downgrade"
            warnings.append("only reachable via initializer/reseed/migration (owner-gated diamondCut) — not steady-state permissionless")
        elif privileged and not has_external:
            status, action = "privileged_only", "downgrade"
            warnings.append("all resolved functions carry a privileged modifier — not unprivileged-attacker reachable")
        elif internal_only and not has_external and not c.get("consumer_found"):
            status, action = "uncertain", "needs_manual_review"
            blockers.append("internal/private sink with no public caller surfaced (no_call_chain_to_sink)")
        elif has_external or c.get("consumer_found"):
            if _speculative(c):
                status, action = "uncertain", "needs_runtime_poc"
                warnings.append("public entrypoint exists but precondition/impact is conditional/unproven — fork PoC required to confirm")
            else:
                status, action = "likely_reachable", "keep"
                evidence.append("external/public entrypoint reaches the sink; no privileged/lifecycle blocker found")
        else:
            status, action = "uncertain", "needs_manual_review"
            warnings.append("could not resolve a clear entrypoint in the manifest")

        if any_priv and status not in ("privileged_only", "duplicate"):
            warnings.append("note: at least one resolved function is privileged-gated")
        if (c.get("severity") or "").lower() in ("low", "info") and status == "likely_reachable":
            warnings.append("severity_overclaim check: low/info impact — confirm a concrete higher-severity path")

        results.append({
            "finding_id": c.get("finding_id"), "title": c.get("title"), "severity": c.get("severity"),
            "layer": c.get("layer"), "reachability_status": status, "suggested_action": action,
            "blockers": blockers, "warnings": warnings,
            "resolved_functions": [{"name": m.get("name"), "visibility": m.get("visibility"),
                                    "kind": m.get("kind"), "modifiers": m.get("modifiers"),
                                    "file": (m.get("file") or "").split("/")[-1]} for m in resolved[:6]],
            "has_external_entrypoint": has_external, "evidence": evidence,
        })

    ts = datetime.now(timezone.utc).isoformat()
    by_status = Counter(r["reachability_status"] for r in results)
    by_action = Counter(r["suggested_action"] for r in results)
    payload = {"generated_at": ts, "count": len(results), "by_status": dict(by_status.most_common()),
               "by_action": dict(by_action.most_common()), "results": results}
    out = audit_path("output") / "confirm" / "reachability_analysis.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"[ok] confirm_reachability → {out}")
    print(f"     by_status: {dict(by_status.most_common())}")
    print(f"     by_action: {dict(by_action.most_common())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
