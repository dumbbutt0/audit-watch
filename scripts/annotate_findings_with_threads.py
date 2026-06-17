#!/usr/bin/env python3
"""
annotate_findings_with_threads.py — Post-Step-2 thread-finding join.

For every output/findings_*.json produced by Step 2 specialist agents, find
promising_threads that cover the same functions or state variables and annotate
the finding in place with:
  thread_refs       — list of matching thread_ids (hard overlap: function name match)
  thread_note       — human-readable summary of why each thread matched
  soft_thread_match — score-3 invariant that covers the same state variable
                      (not traced, shown as a watch-list hint)

Called automatically at the start of cross_agent_connector.py so it always
runs before holistic synthesis. Can also be invoked standalone.

Usage:
    python scripts/annotate_findings_with_threads.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR     = audit_path("output")
THREADS_DIR    = audit_path("data/threads")
INVARIANTS_DIR = audit_path("data/invariants")

SKIP_FILES = {"findings_cross_agent.json", "findings_confirmed.json"}

VERDICT_SEVERITY = {
    "CRITICAL_THREAD": "Critical", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium",
    "CRITICAL_BACKWARD": "Critical", "HIGH_BACKWARD": "High", "MEDIUM_BACKWARD": "Medium",
    "CRITICAL_MULTITX": "Critical", "HIGH_MULTITX": "High", "MEDIUM_MULTITX": "Medium",
}

# regex to pull bare function names out of violation_path / hop_trace strings
_FN_RE = re.compile(r"\b([a-zA-Z_]\w*)\s*\(")


def _norm(name: str) -> str:
    return name.split(".")[-1].lower()


def _fns_from_text(text: str) -> set[str]:
    return {_norm(m) for m in _FN_RE.findall(text) if len(m) > 2}


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return out


def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Thread indexing
# ─────────────────────────────────────────────────────────────────────────────

def _thread_functions(thread: dict) -> set[str]:
    fns: set[str] = set()
    # Structured hop_traces (list of dicts)
    for hop in thread.get("hop_traces", []):
        fn = hop.get("function", "")
        if fn:
            fns.add(_norm(fn))
        for sv in hop.get("state_read", []) + hop.get("state_written", []):
            pass  # state vars handled separately
    # Flat hop_trace (list of strings)
    for step in thread.get("hop_trace", []):
        if isinstance(step, str):
            fns |= _fns_from_text(step)
    # violation_path (list of strings)
    for step in thread.get("violation_path", []):
        if isinstance(step, str):
            fns |= _fns_from_text(step)
    # title
    fns |= _fns_from_text(thread.get("title", ""))
    return fns


def _thread_state_vars(thread: dict) -> set[str]:
    svs: set[str] = set()
    for hop in thread.get("hop_traces", []):
        for sv in hop.get("state_read", []) + hop.get("state_written", []):
            svs.add(sv.lower())
    return svs


def _build_thread_index(threads: list[dict]) -> dict[str, list[dict]]:
    """fn_name → list of threads that touch that function."""
    idx: dict[str, list[dict]] = {}
    for t in threads:
        for fn in _thread_functions(t):
            idx.setdefault(fn, []).append(t)
    return idx


# ─────────────────────────────────────────────────────────────────────────────
# Score-3 invariant index
# ─────────────────────────────────────────────────────────────────────────────

def _build_soft_index(invariants: list[dict]) -> dict[str, list[dict]]:
    """state_var_name → list of score-3 invariants that cover it."""
    idx: dict[str, list[dict]] = {}
    for inv in invariants:
        if inv.get("suspicion_score", 0) == 3:
            for sv in inv.get("state_variables_involved", []):
                idx.setdefault(sv.lower(), []).append(inv)
    return idx


# ─────────────────────────────────────────────────────────────────────────────
# Finding analysis
# ─────────────────────────────────────────────────────────────────────────────

def _finding_functions(finding: dict) -> set[str]:
    fns: set[str] = set()
    loc = finding.get("location", {})
    fn = loc.get("function", "")
    if fn:
        fns.add(_norm(fn))
    # Also scan code_snippet for called functions
    snippet = loc.get("code_snippet", "")
    if snippet:
        fns |= _fns_from_text(snippet)
    return fns


def _finding_text(finding: dict) -> str:
    parts = [
        finding.get("description", "") or "",
        finding.get("impact", "") or "",
        finding.get("proof_of_concept", "") or "",
        (finding.get("location", {}) or {}).get("code_snippet", "") or "",
    ]
    return " ".join(parts).lower()


def _match_threads(finding: dict, thread_idx: dict[str, list[dict]]) -> list[dict]:
    """Return threads that share at least one function with this finding."""
    f_fns = _finding_functions(finding)
    matched: dict[str, dict] = {}
    for fn in f_fns:
        for t in thread_idx.get(fn, []):
            tid = t.get("thread_id", "")
            if tid and tid not in matched:
                matched[tid] = t
    return list(matched.values())


def _soft_matches(finding: dict, soft_idx: dict[str, list[dict]]) -> list[dict]:
    """Return score-3 invariants whose state_variables appear in this finding's text."""
    text = _finding_text(finding)
    matched: dict[str, dict] = {}
    for sv_lower, invs in soft_idx.items():
        if sv_lower and sv_lower in text:
            for inv in invs:
                iid = inv.get("invariant_id", "")
                if iid and iid not in matched:
                    matched[iid] = inv
    return list(matched.values())


def _make_thread_note(threads: list[dict]) -> str:
    parts = []
    for t in threads:
        tid = t.get("thread_id", "?")
        verdict = t.get("verdict", "")
        score = t.get("suspicion_score", "?")
        title = t.get("title", "")[:60]
        sev = VERDICT_SEVERITY.get(verdict, verdict)
        soft = " [soft]" if t.get("soft_flag") else ""
        parts.append(f"{tid}{soft}: {sev} (score={score}) — {title}")
    return "; ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Annotation pass
# ─────────────────────────────────────────────────────────────────────────────

def annotate(dry_run: bool = False) -> dict:
    threads = _load_jsonl(THREADS_DIR / "promising_threads.jsonl")
    # Include soft-flag threads but keep them separate in the index
    hard_threads = [t for t in threads if not t.get("soft_flag")]
    soft_threads  = [t for t in threads if t.get("soft_flag")]

    thread_idx = _build_thread_index(hard_threads + soft_threads)

    all_invariants = _load_json(INVARIANTS_DIR / "protocol_invariants.json") or []
    soft_inv_idx = _build_soft_index(all_invariants)

    stats = {"files": 0, "findings": 0, "thread_annotations": 0, "soft_annotations": 0}

    for findings_path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        if findings_path.name in SKIP_FILES:
            continue
        try:
            data = json.loads(findings_path.read_text())
        except json.JSONDecodeError:
            continue

        modified = False
        for finding in data.get("findings", []):
            # Hard thread match (function overlap)
            matches = _match_threads(finding, thread_idx)
            # Separate hard vs soft threads
            hard_matches = [t for t in matches if not t.get("soft_flag")]
            soft_t_matches = [t for t in matches if t.get("soft_flag")]

            if hard_matches:
                existing_refs = set(finding.get("thread_refs", []))
                new_refs = [t.get("thread_id") for t in hard_matches
                            if t.get("thread_id") not in existing_refs]
                if new_refs:
                    finding["thread_refs"] = list(existing_refs) + new_refs
                    finding["thread_note"] = _make_thread_note(hard_matches)
                    modified = True
                    stats["thread_annotations"] += 1

            # Soft thread matches (score-3, same function)
            if soft_t_matches:
                existing_soft = set(
                    s.get("thread_id") for s in finding.get("soft_thread_matches", [])
                )
                new_soft = [
                    {"thread_id": t.get("thread_id"), "verdict": t.get("verdict"),
                     "note": f"soft-flag thread (score-3 pass) — {t.get('title', '')[:60]}"}
                    for t in soft_t_matches
                    if t.get("thread_id") not in existing_soft
                ]
                if new_soft:
                    finding.setdefault("soft_thread_matches", []).extend(new_soft)
                    modified = True

            # Score-3 invariant match (state variable overlap in finding text)
            soft_inv_matches = _soft_matches(finding, soft_inv_idx)
            if soft_inv_matches:
                existing_inv = {
                    s.get("invariant_id")
                    for s in finding.get("soft_thread_match", [])
                }
                new_inv = [
                    {
                        "invariant_id": inv.get("invariant_id"),
                        "note": (
                            f"score-3 invariant covers same state vars "
                            f"({', '.join(inv.get('state_variables_involved', [])[:3])}); "
                            "not traced — consider manual review"
                        ),
                    }
                    for inv in soft_inv_matches
                    if inv.get("invariant_id") not in existing_inv
                ]
                if new_inv:
                    finding.setdefault("soft_thread_match", []).extend(new_inv)
                    modified = True
                    stats["soft_annotations"] += 1

            stats["findings"] += 1

        if modified:
            stats["files"] += 1
            if not dry_run:
                findings_path.write_text(json.dumps(data, indent=2))
                print(f"  Annotated {findings_path.name}")

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotate Step 2 findings with thread cross-refs")
    parser.add_argument("--dry-run", action="store_true", help="Print stats but do not write files")
    args = parser.parse_args()

    print("Thread-Finding Join — annotating Step 2 findings with promising thread refs")

    if not (THREADS_DIR / "promising_threads.jsonl").exists():
        print("  No promising_threads.jsonl found — skipping annotation")
        return 0

    stats = annotate(dry_run=args.dry_run)

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"  {prefix}Files annotated:        {stats['files']}")
    print(f"  {prefix}Findings scanned:       {stats['findings']}")
    print(f"  {prefix}Thread annotations:     {stats['thread_annotations']}")
    print(f"  {prefix}Soft-inv annotations:   {stats['soft_annotations']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
