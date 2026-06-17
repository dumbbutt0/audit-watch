#!/usr/bin/env python3
"""
backfill_outcomes.py — Deterministic, evidence-gated outcome backfill across past audits.

Encodes the backfill discipline as an ARTIFACT (not human judgment): it scans each audit's
in-repo evidence and AUTO-RECORDS a ground-truth outcome ONLY when a hard evidence rule matches.
Everything with partial evidence (submitted / proved-L3 / pipeline-downgraded / failed PoC) is
routed to that audit's needs_human_review.jsonl with a disposition question — never guessed.

Hard auto-record rules:
  R1 duplicate  — a duplicate_registry.jsonl entry for this audit → outcome=duplicate,
                  evidence_class=platform_confirmed.
  R2 neg-ctrl FP — a runtime_poc record with status == "rejected_negative_poc" → outcome=invalid,
                  evidence_class=fork_confirmed. ("failed" alone is NOT auto-recorded — ambiguous.)

Never auto-records accepted/paid (no in-repo evidence of platform disposition). Excludes the
Beanstalk benchmark. Idempotent: skips ids already in ground_truth or needs_human_review.

Usage:
    python scripts/backfill_outcomes.py            # dry-run (default): report only, writes nothing
    python scripts/backfill_outcomes.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_ground_truth as gt
from audit_context import _AUDITS_DIR, _PROJECT_ROOT, list_audits, load_jsonl

EXCLUDE_AUDITS = {"beanstalk-2024-05"}   # benchmark, not a live human-established outcome
DUP_REGISTRY = _PROJECT_ROOT / "data" / "duplicate_registry.jsonl"
REPORT = _PROJECT_ROOT / "documentation" / "metrics" / "backfill_report.md"
ID_RE = re.compile(r"([A-Z][A-Z_]*[-_]?\d{2,3})")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ids_in(path: Path) -> set[str]:
    return {r.get("finding_id") for r in load_jsonl(path) if r.get("finding_id")}


def _merged_index(root: Path) -> dict[str, dict]:
    p = root / "output" / "merged_findings.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}
    out = {}
    for f in (data.get("findings", data if isinstance(data, list) else []) or []):
        fid = f.get("id") or f.get("finding_id")
        if fid:
            out[fid] = f
    return out


def _submission_ids(root: Path) -> set[str]:
    d = root / "output" / "submissions"
    ids: set[str] = set()
    if d.is_dir():
        for p in d.glob("*.md"):
            m = ID_RE.search(p.stem)
            if m:
                ids.add(m.group(1).replace("_", "-") if m.group(1)[:3].isalpha() is False else m.group(1))
    return ids


def scan_audit(audit_id: str) -> dict:
    root = _AUDITS_DIR / audit_id
    eval_dir = root / "data" / "evaluation"
    existing_gt = _ids_in(eval_dir / "ground_truth.jsonl")
    existing_nhr = _ids_in(eval_dir / "needs_human_review.jsonl")
    seen = existing_gt | existing_nhr

    merged = _merged_index(root)
    rejected = _ids_in(root / "data" / "triage" / "rejected.jsonl")
    downgraded = _ids_in(root / "data" / "triage" / "downgraded.jsonl")
    submissions = _submission_ids(root)
    runtime = load_jsonl(root / "data" / "runtime_poc" / "results.jsonl")

    dup_rows = [r for r in load_jsonl(DUP_REGISTRY) if r.get("our_audit") == audit_id]

    auto: list[dict] = []   # (record, rule)
    nhr: list[dict] = []
    skipped: list[str] = []

    def ctx(fid):
        f = merged.get(fid, {})
        return {"title": f.get("title", ""), "vuln_type": f.get("vuln_type", ""),
                "agent": f.get("agent") or f.get("_source_agent", "")}

    # R1 — duplicates
    for d in dup_rows:
        fid = d.get("our_finding_id")
        if not fid or fid in existing_gt:
            if fid in existing_gt:
                skipped.append(f"{fid} (R1 dup: already in ground truth)")
            continue
        c = ctx(fid)
        auto.append(({
            "finding_id": fid, "source_audit": audit_id, **c,
            "claimed_severity": "", "ground_truth_outcome": "duplicate",
            "ground_truth_severity": "invalid",
            "evidence_class": "platform_confirmed",
            "source_file": "data/duplicate_registry.jsonl",
            "evidence_summary": f"duplicate of {d.get('duplicate_of_report','?')} "
                                f"({d.get('platform','')}) per registry {d.get('registry_id','')}",
            "duplicate_of_report": d.get("duplicate_of_report", ""),
            "recorded_by": "human", "recorded_at": _now(),
        }, "R1"))
        seen.add(fid)

    # R2 — negative-control FP (explicit marker only)
    for r in runtime:
        fid = r.get("finding_id")
        if not fid or r.get("status") != "rejected_negative_poc":
            continue
        if fid in existing_gt:
            skipped.append(f"{fid} (R2 neg-ctrl: already in ground truth)")
            continue
        c = ctx(fid)
        auto.append(({
            "finding_id": fid, "source_audit": audit_id, **c,
            "claimed_severity": (merged.get(fid, {}) or {}).get("severity", ""),
            "ground_truth_outcome": "invalid", "ground_truth_severity": "invalid",
            "evidence_class": "fork_confirmed",
            "source_file": f"audits/{audit_id}/data/runtime_poc/results.jsonl",
            "evidence_summary": "negative-control PoC (status=rejected_negative_poc) confirms not exploitable",
            "recorded_by": "human", "recorded_at": _now(),
        }, "R2"))
        seen.add(fid)

    # R4 — partial evidence → needs_human_review (no outcome guessed)
    proved_l3 = {r.get("finding_id") for r in runtime
                 if r.get("status") == "proved" and (
                     str(r.get("poc_level", "")).upper().startswith("L3")
                     or str(r.get("runtime_level", "")).startswith("3"))}
    failed_poc = {r.get("finding_id") for r in runtime
                  if r.get("status") in ("failed", "inconclusive")}

    candidates: dict[str, list[str]] = {}
    for fid in submissions:
        candidates.setdefault(fid, []).append("submitted (submission file present)")
    for fid in proved_l3:
        if fid:
            candidates.setdefault(fid, []).append("proved L3 PoC (technical validity, disposition unknown)")
    for fid in downgraded:
        candidates.setdefault(fid, []).append("pipeline-downgraded (confirm if human agrees)")
    for fid in failed_poc:
        if fid:
            candidates.setdefault(fid, []).append("PoC failed/inconclusive (confirm invalid vs needs work)")

    for fid, evidence in candidates.items():
        if fid in seen:
            continue
        nhr.append({
            "finding_id": fid, "source_audit": audit_id, **ctx(fid),
            "candidate_evidence": evidence,
            "disposition_question": "What was the real outcome? (accepted/duplicate/invalid/"
                                    "downgraded/escalated/paid/closed) — record via record_outcome.py "
                                    "with evidence.",
            "_routed_at": _now(), "_routed_by": "backfill_outcomes",
        })
        seen.add(fid)

    return {"audit_id": audit_id, "eval_dir": eval_dir, "auto": auto, "nhr": nhr,
            "skipped": skipped}


def main() -> int:
    ap = argparse.ArgumentParser(description="Evidence-gated cross-audit outcome backfill")
    ap.add_argument("--apply", action="store_true", help="Write (default: dry-run)")
    args = ap.parse_args()
    apply = args.apply

    audits = [a["audit_id"] for a in list_audits() if a["audit_id"] not in EXCLUDE_AUDITS]
    results = [scan_audit(a) for a in audits]

    total_auto = total_nhr = 0
    lines = [f"# Backfill Report ({'APPLY' if apply else 'DRY-RUN'})\n",
             f"_Generated {_now()} · {len(audits)} audits (beanstalk excluded)._\n",
             "Auto-records only on hard evidence (R1 duplicate, R2 negative-control FP). "
             "No outcome inferred; partial evidence → needs_human_review.\n"]

    for r in results:
        aid = r["audit_id"]
        if not (r["auto"] or r["nhr"] or r["skipped"]):
            continue
        lines.append(f"## {aid}")
        for rec, rule in r["auto"]:
            total_auto += 1
            lines.append(f"- **RECORD [{rule}]** {rec['finding_id']}: {rec['ground_truth_outcome']} "
                         f"[{rec['evidence_class']}] — {rec['evidence_summary']}")
            if apply:
                written, dest = gt.write_outcome(rec, eval_dir=r["eval_dir"])
                lines.append(f"    → {'written' if written else 'ROUTED(nhr)'}: {dest}")
        for n in r["nhr"]:
            total_nhr += 1
            lines.append(f"- needs_human_review: {n['finding_id']} — {', '.join(n['candidate_evidence'])}")
            if apply:
                nh = r["eval_dir"] / "needs_human_review.jsonl"
                nh.parent.mkdir(parents=True, exist_ok=True)
                with nh.open("a") as fh:
                    fh.write(json.dumps(n) + "\n")
        for s in r["skipped"]:
            lines.append(f"- skipped: {s}")
        lines.append("")

    lines.append(f"## Totals\n- auto-recorded: {total_auto}\n- needs_human_review: {total_nhr}\n"
                 "- learning candidates: NOT staged during cross-audit backfill (by design — run "
                 "`derive_learning.py` within an audit to stage into its `_proposed/`).")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")

    print(f"{'APPLIED' if apply else 'DRY-RUN'} — auto-recorded {total_auto}, "
          f"needs_human_review {total_nhr}. Report: {REPORT}")
    if not apply:
        print("Review the report, then re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
