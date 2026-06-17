#!/usr/bin/env python3
"""confirm_prepare.py — stage multi-pass confirmation bundles for the credit-free /confirm skill.

Mirrors triage_prepare.py but for Step 3.5 (multi-pass confirmation). `multi_pass_confirm.py` SKIPS when there is
no ANTHROPIC_API_KEY (the api-free default), which silently left High/Critical findings unconfirmed. This stages
one bundle per High/Critical finding (claim + source slice + required pass count) so the /confirm skill can run
the N independent passes IN-SESSION (no credits), then confirm_write.py persists the result. The canonical record
(build_candidate_records.py) routes any still-unconfirmed High/Critical to human_pending, so this is the mechanism
that lets them be confirmed rather than parked.

Writes output/confirm/_bundles/<id>.json + index.json. Read-only over source; deterministic.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HIGH = {"high", "critical"}


def _cfg() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text())
    except Exception:
        return {}


def _resolve_source(file_field: str) -> Path | None:
    if not file_field:
        return None
    for base in (ROOT, audit_path()):
        p = (base / file_field)
        if p.exists():
            return p
    name = Path(file_field).name
    hits = list(audit_path("contracts").rglob(name)) if audit_path("contracts").exists() else []
    return hits[0] if hits else None


def _source_slice(loc: dict, ctx: int = 40) -> str:
    p = _resolve_source(loc.get("file", ""))
    if not p:
        return loc.get("code_snippet", "") or "(source not resolvable; using finding snippet)"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return loc.get("code_snippet", "")
    start = max(0, (loc.get("line_start") or 1) - 1 - ctx)
    end = min(len(lines), (loc.get("line_end") or loc.get("line_start") or 1) + ctx)
    return "\n".join(f"{i+1}: {lines[i]}" for i in range(start, end))


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage multi-pass confirmation bundles for the /confirm skill")
    ap.add_argument("--context-lines", type=int, default=40)
    args = ap.parse_args()

    cfg = _cfg()
    if cfg.get("active_mode") == "fast":
        print("[confirm_prepare] fast mode — confirmation skipped by policy.")
        return 0
    mp = cfg.get("multi_pass", {})
    if not mp.get("enabled", True):
        print("[confirm_prepare] multi_pass disabled in config — nothing to stage.")
        return 0
    passes_high = mp.get("passes_high", 3)
    passes_critical = mp.get("passes_critical", 5)
    threshold = mp.get("confirmation_threshold", 0.6)

    merged = audit_path("output", "merged_findings.json")
    if not merged.exists():
        print("[confirm_prepare] no merged_findings.json — run synthesis first.", file=sys.stderr)
        return 1
    findings = json.loads(merged.read_text()).get("findings", [])

    bundle_dir = audit_path("output", "confirm", "_bundles")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for old in bundle_dir.glob("*.json"):
        old.unlink()

    index = []
    for f in findings:
        sev = ((f.get("ice_chain") or {}).get("severity_ceiling") or f.get("severity") or "").strip().lower()
        if sev not in HIGH:
            continue
        fid = f.get("id")
        n = passes_critical if sev == "critical" else passes_high
        loc = f.get("location") or {}
        bundle = {
            "finding_id": fid, "title": f.get("title", ""), "severity": f.get("severity"),
            "vuln_type": f.get("vuln_type"), "passes_required": n, "threshold": threshold,
            "claim": {"description": f.get("description", ""), "impact": f.get("impact", ""),
                      "ice_chain": f.get("ice_chain") or {}, "location": loc},
            "source_slice": _source_slice(loc, args.context_lines),
            "instructions": (f"Run {n} INDEPENDENT yes/no judgments: is this finding's vulnerable code path "
                             "reachable from an unprivileged entry AND is the logic flaw real? Reset reasoning "
                             "each pass. Record passes_yes/passes_run; human_review_required if score < threshold."),
        }
        (bundle_dir / f"{fid}.json").write_text(json.dumps(bundle, indent=2))
        index.append({"finding_id": fid, "severity": f.get("severity"), "passes_required": n})

    (bundle_dir / "index.json").write_text(json.dumps(index, indent=2))
    if not index:
        print("[confirm_prepare] no High/Critical findings to confirm — nothing to do.")
    else:
        print(f"[confirm_prepare] staged {len(index)} confirmation bundle(s) → {bundle_dir}")
        print("  Next: run the /confirm skill (in-session, credit-free), then: python scripts/confirm_write.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
