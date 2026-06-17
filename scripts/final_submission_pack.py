#!/usr/bin/env python3
"""
final_submission_pack.py — Generates contest-ready submission files.

Reads:
  data/triage/submit.jsonl          — findings ready to submit
  data/triage/poc_required.jsonl    — findings needing proof (included with caveat)
  output/merged_findings.json       — full finding details

Writes:
  output/submission_pack.md         — formatted for contest submission
  output/submission_pack.json       — machine-readable with triage metadata

Usage:
    python scripts/final_submission_pack.py
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

TRIAGE_DIR  = audit_path("data/triage")
OUTPUT_DIR  = audit_path("output")
EXPLOIT_DIR = audit_path("data/exploitability")
JUDGE_DIR   = audit_path("data/judge_simulation")
DUP_DIR     = audit_path("data/duplicates")
SEV_DIR     = audit_path("data/severity")
POC_DIR     = audit_path("data/runtime_poc")

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5}
SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium",
             "low": "Low", "qa": "QA", "invalid": "Invalid"}

# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  [warn] Skipping malformed line in {path.name}")
    return items


def load_merged_findings() -> dict[str, dict]:
    path = OUTPUT_DIR / "merged_findings.json"
    if not path.exists():
        print("  [warn] output/merged_findings.json not found — using triage data only")
        return {}
    data = json.loads(path.read_text())
    return {f["id"]: f for f in data.get("findings", [])}


def load_downgraded() -> list[dict]:
    return load_jsonl(TRIAGE_DIR / "downgraded.jsonl")


def load_specialist_outputs() -> dict:
    """Load all specialist review outputs (optional — degrade gracefully if absent)."""
    def _map(path: Path) -> dict[str, dict]:
        return {r["finding_id"]: r for r in load_jsonl(path) if "finding_id" in r}

    return {
        "exploitability": _map(EXPLOIT_DIR / "models.jsonl"),
        "judge":          _map(JUDGE_DIR / "results.jsonl"),
        "duplicates":     _map(DUP_DIR / "risk.jsonl"),
        "severity":       _map(SEV_DIR / "calibrated.jsonl"),
        "poc":            _map(POC_DIR / "results.jsonl"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Finding enrichment
# ─────────────────────────────────────────────────────────────────────────────

def enrich(triage: dict, merged: dict[str, dict],
           specialist: dict | None = None) -> dict:
    fid      = triage.get("finding_id", "")
    original = merged.get(fid, {})
    spec     = specialist or {}

    # Prefer calibrated severity over triage severity
    sev_rec    = spec.get("severity", {}).get(fid, {})
    cal_sev    = sev_rec.get("calibrated_severity", "")
    final_sev  = cal_sev or triage.get("recommended_severity", "low")

    # Pull exploitability execution_sequence for PoC narrative
    exploit = spec.get("exploitability", {}).get(fid, {})
    exec_seq = exploit.get("execution_sequence", [])

    # Pull judge rewrite suggestions
    judge = spec.get("judge", {}).get(fid, {})

    # Pull duplicate info
    dup = spec.get("duplicates", {}).get(fid, {})

    return {
        "triage":           triage,
        "original":         original,
        "title":            triage.get("title") or original.get("title", fid),
        "severity":         final_sev,
        "triage_severity":  triage.get("recommended_severity", "low"),
        "calibrated":       bool(cal_sev),
        "location":         original.get("location", {}),
        "description":      original.get("description", ""),
        "poc":              original.get("proof_of_concept", ""),
        "recommendation":   original.get("recommendation", ""),
        "compound_bonus":   triage.get("_compound_bonus", False),
        "execution_sequence": exec_seq,
        "rewrite_suggestions": judge.get("rewrite_suggestions", []),
        "judge_objections": judge.get("likely_judge_questions", []),
        "duplicate_risk":   dup.get("duplicate_risk", ""),
        "compound_split_recommended": dup.get("compound_split_recommended", False),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ─────────────────────────────────────────────────────────────────────────────

def format_location(loc) -> str:
    if not loc:
        return "Unknown"
    if isinstance(loc, str):
        return loc
    parts = [loc.get("file", "")]
    fn = loc.get("function", "")
    if fn:
        parts.append(f"`{fn}()`")
    lines = ""
    ls, le = loc.get("line_start"), loc.get("line_end")
    if ls and le and ls != le:
        lines = f" L{ls}-{le}"
    elif ls:
        lines = f" L{ls}"
    return " → ".join(p for p in parts if p) + lines


def render_finding_section(item: dict, idx: int, needs_poc: bool = False) -> str:
    triage = item["triage"]
    fid = triage.get("finding_id", "?")
    title = item["title"]
    sev = SEV_LABEL.get(item["severity"], item["severity"].title())
    loc = format_location(item["location"])
    desc = item["description"] or triage.get("impact", {}).get("severity_reason", "")
    poc = item["poc"] or triage.get("exploitability", {}).get("profit_or_damage", "")
    rec = item["recommendation"]
    score = triage.get("score", {}).get("total", "?")
    confidence = triage.get("confidence", "?")
    compound = item["compound_bonus"]

    cal_flag   = " *(calibrated)*" if item.get("calibrated") else ""
    dup_flag   = f" | **Dup Risk:** {item.get('duplicate_risk','').upper()}" if item.get("duplicate_risk") else ""

    lines = [
        f"## [{idx}] {fid} — {title}",
        "",
        f"**Severity:** {sev}{cal_flag}{dup_flag}  ",
        f"**Score:** {score}/35  |  **Confidence:** {confidence}/5",
    ]
    if compound:
        lines.append("**Note:** Part of a compound risk — combined severity may be higher")
    if item.get("compound_split_recommended"):
        lines.append("**Note:** Compound split recommended — submit root causes separately")
    if needs_poc:
        lines.append("**Status:** PoC required before submission")
    lines += [
        "",
        f"**Location:** {loc}",
        "",
        "### Description",
        "",
        desc or "_No description available_",
        "",
    ]
    if poc:
        lines += [
            "### Proof of Concept",
            "",
            poc,
            "",
        ]
    if rec:
        lines += [
            "### Recommendation",
            "",
            rec,
            "",
        ]

    exec_seq = item.get("execution_sequence", [])
    if exec_seq:
        lines += [
            "### Attack Sequence",
            "",
        ]
        for i, step in enumerate(exec_seq, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    rewrite = item.get("rewrite_suggestions", [])
    if rewrite:
        lines += [
            "### Suggested Improvements Before Submission",
            "",
        ]
        for s in rewrite[:3]:
            lines.append(f"- {s}")
        lines.append("")

    objections = item.get("judge_objections", [])
    if objections:
        lines += [
            "### Anticipated Judge Questions",
            "",
        ]
        for q in objections[:3]:
            lines.append(f"- {q}")
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def render_specialist_summary(items: list[dict], specialist: dict) -> str:
    """Render the decision matrix table from specialist review outputs."""
    exploit_map = specialist.get("exploitability", {})
    dup_map     = specialist.get("duplicates", {})
    sev_map     = specialist.get("severity", {})
    poc_map     = specialist.get("poc", {})
    judge_map   = specialist.get("judge", {})

    if not any([exploit_map, dup_map, sev_map, poc_map, judge_map]):
        return ""

    _triage_action_map = {
        "submit":       "SUBMIT",
        "poc_required": "POC_FIRST",
        "downgraded":   "REVISE",
        "rejected":     "DROP",
    }

    rows = []
    for item in items:
        fid           = item["triage"].get("finding_id", "?")
        triage_status = item["triage"].get("triage_status", "")
        e   = exploit_map.get(fid, {})
        d   = dup_map.get(fid, {})
        s   = sev_map.get(fid, {})
        p   = poc_map.get(fid, {})
        j   = judge_map.get(fid, {})
        rows.append({
            "fid":      fid,
            "exploit":  e.get("exploitability_score", "—"),
            "dup":      d.get("duplicate_risk", "—"),
            "sev":      s.get("calibrated_severity", "—"),
            "poc_lvl":  p.get("runtime_level", "—"),
            "judge":    j.get("predicted_outcome", "—"),
            "action":   _triage_action_map.get(triage_status, "REVISE"),
        })

    lines = [
        "",
        "## Specialist Review Summary",
        "",
        "| Finding | Exploit | Dup Risk | Sev Calibrated | PoC Lvl | Judge Outcome | Action |",
        "|---------|---------|----------|----------------|---------|---------------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['fid']} | {r['exploit']} | {r['dup']} | {r['sev']} "
            f"| {r['poc_lvl']} | {r['judge']} | **{r['action']}** |"
        )
    lines.append("")
    return "\n".join(lines)


def render_markdown(submit_items: list[dict], poc_items: list[dict],
                    downgraded: list[dict], compound_notes: list[str],
                    specialist: dict | None = None) -> str:
    all_submit = sorted(submit_items, key=lambda x: SEV_ORDER.get(x["severity"], 99))
    all_poc = sorted(poc_items, key=lambda x: SEV_ORDER.get(x["severity"], 99))

    by_sev: dict[str, int] = defaultdict(int)
    for item in all_submit + all_poc:
        by_sev[item["severity"]] += 1

    high_count = by_sev.get("critical", 0) + by_sev.get("high", 0)
    med_count = by_sev.get("medium", 0)
    compound_count = sum(1 for item in all_submit + all_poc if item["compound_bonus"])

    lines = [
        "# Audit Submission Pack",
        "",
        "## Executive Summary",
        "",
        f"- **{high_count}** High/Critical findings",
        f"- **{med_count}** Medium findings",
        f"- **{by_sev.get('low', 0)}** Low findings",
        f"- **{compound_count}** compound risk pairs identified",
        f"- **{len(all_poc)}** findings require PoC before submission",
        "",
    ]

    if compound_notes:
        lines += ["## Compound Risks", ""]
        for note in compound_notes:
            lines.append(f"- {note}")
        lines.append("")

    lines += ["## Submit-Ready Findings", ""]
    idx = 1
    for item in all_submit:
        lines.append(render_finding_section(item, idx, needs_poc=False))
        idx += 1

    if all_poc:
        lines += ["", "## Findings Requiring PoC", ""]
        for item in all_poc:
            lines.append(render_finding_section(item, idx, needs_poc=True))
            idx += 1

    if downgraded:
        lines += ["", "## Appendix — Downgraded Findings", ""]
        lines.append("These findings were downgraded during triage and are not recommended for submission.\n")
        for triage in downgraded:
            fid = triage.get("finding_id", "?")
            title = triage.get("title", "")
            reason = triage.get("decision_reason", "")
            sev = triage.get("recommended_severity", "?")
            lines.append(f"- **{fid}** ({sev}): {title}")
            if reason:
                lines.append(f"  - Reason: {reason}")
        lines.append("")

    if specialist:
        summary = render_specialist_summary(all_submit + all_poc, specialist)
        if summary:
            lines.append(summary)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# JSON output
# ─────────────────────────────────────────────────────────────────────────────

ID_PATTERN = re.compile(r'\b([A-Z]{2,3}-\d{3})\b')


def build_json_output(submit_items: list[dict], poc_items: list[dict],
                      compound_notes: list[str]) -> dict:
    all_items = submit_items + poc_items
    submission_ready = []

    for item in all_items:
        triage = item["triage"]
        original = item["original"]
        submission_ready.append({
            "finding_id": triage.get("finding_id"),
            "title": item["title"],
            "recommended_severity": triage.get("recommended_severity"),
            "triage_status": triage.get("triage_status"),
            "score": triage.get("score"),
            "confidence": triage.get("confidence"),
            "needs_poc": triage.get("exploitability", {}).get("needs_poc", False),
            "compound": triage.get("_compound_bonus", False),
            "location": original.get("location"),
            "vuln_type": original.get("vuln_type"),
            "decision_reason": triage.get("decision_reason"),
            "required_next_steps": triage.get("required_next_steps", []),
            "attacker_model": triage.get("attacker_model"),
            "impact": triage.get("impact"),
            "quality_gate": triage.get("quality_gate"),
        })

    # Link compound pairs by ID
    compound_pairs = []
    for note in compound_notes:
        ids = ID_PATTERN.findall(note)
        if len(ids) >= 2:
            compound_pairs.append({"ids": ids, "note": note})

    return {
        "generated_at": _now(),
        "summary": {
            "total_submit_ready": len(submit_items),
            "total_poc_required": len(poc_items),
        },
        "compound_pairs": compound_pairs,
        "findings": submission_ready,
    }


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# ROI summary
# ─────────────────────────────────────────────────────────────────────────────

def print_roi_summary(submit_items: list[dict], poc_items: list[dict]) -> None:
    all_items = submit_items + poc_items
    if not all_items:
        return

    high_unique, high_dupe = [], []
    for item in all_items:
        sev = item["severity"]
        dup_risk = item["triage"].get("score", {}).get("duplicate_risk", 3)
        quality = item["triage"].get("quality_gate", {})
        if sev in ("critical", "high"):
            if dup_risk >= 4 and not quality.get("likely_duplicate"):
                high_unique.append(item)
            else:
                high_dupe.append(item)

    print("\n" + "=" * 60)
    print("Contest ROI Summary")
    print("=" * 60)
    print(f"  High/Critical unique (low dupe risk):  {len(high_unique)}")
    print(f"  High/Critical likely duplicate:        {len(high_dupe)}")

    # Recommended submission order: uniqueness × severity weight
    def roi_score(item: dict) -> float:
        sev_w = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}.get(item["severity"], 0.5)
        dup_risk = item["triage"].get("score", {}).get("duplicate_risk", 3)
        return sev_w * dup_risk

    ordered = sorted(all_items, key=roi_score, reverse=True)
    print("\n  Recommended submission order:")
    print(f"  {'Rank':<5} {'ID':<12} {'Severity':<10} {'Dup-Risk':<9} {'ROI Score'}")
    print("  " + "-" * 50)
    for rank, item in enumerate(ordered[:10], 1):
        fid = item["triage"].get("finding_id", "?")
        sev = item["severity"]
        dup = item["triage"].get("score", {}).get("duplicate_risk", "?")
        roi = roi_score(item)
        print(f"  {rank:<5} {fid:<12} {sev:<10} {str(dup):<9} {roi:.1f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def _check_gate_results(triage_dir: Path, force: bool = False) -> None:
    """Block submission if gate_results.jsonl is missing. Use --bypass-gate to override."""
    gate_path = triage_dir / "gate_results.jsonl"
    if not gate_path.exists():
        msg = (
            "\n  *** BLOCKED: data/triage/gate_results.jsonl not found ***\n"
            "  The 8-gate pre-submission filter (pre_submission_gate.py) has not run.\n"
            "  Run:  python scripts/pre_submission_gate.py --all\n"
            "  Then re-run this script.\n"
            "  Override (not recommended): add --bypass-gate flag.\n"
        )
        if force:
            print(msg.replace("BLOCKED", "WARNING (bypassed)"))
        else:
            print(msg)
            sys.exit(1)
    else:
        gate_entries = load_jsonl(gate_path)
        reject_count = sum(1 for g in gate_entries if g.get("overall_verdict") == "REJECT")
        if reject_count:
            print(f"  [gate] {reject_count} findings have REJECT verdicts — run triage_findings.py before packing.\n")


def _check_poc_completeness(output_dir: Path, force: bool = False) -> bool:
    """Invoke analyze_poc_completeness --all, then block if any High claim lacks L3B support."""
    import subprocess
    completeness_script = Path(__file__).resolve().parent / "analyze_poc_completeness.py"
    if completeness_script.exists():
        subprocess.run(
            [sys.executable, str(completeness_script), "--all"],
            check=False, capture_output=True,
        )

    completeness_dir = output_dir / "poc_completeness"
    if not completeness_dir.exists():
        return True  # No PoC data yet — allow pack to proceed

    high_unsupported = []
    for f in completeness_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        fid = data.get("finding_id", f.stem)
        claimed_sev = (data.get("claimed_severity") or "").lower()
        poc_level = data.get("poc_level_achieved", "")
        upgrade_req = data.get("upgrade_required", False)
        if claimed_sev in ("high", "critical") and upgrade_req:
            high_unsupported.append(f"  {fid}: {claimed_sev} claim requires PoC upgrade (level={poc_level})")

    if high_unsupported:
        print("\n  *** BLOCKED: High/Critical findings with unsupported PoC claims ***")
        for msg in high_unsupported:
            print(msg)
        print("  Fix upgrade tasks in output/poc_upgrade_tasks/ before submitting.")
        print("  Override: add --bypass-poc flag.\n")
        if not force:
            return False
    return True


def _validate_severity(submit_triage: list[dict]) -> list[str]:
    """Return list of finding IDs where severity is missing or unknown."""
    bad = []
    for t in submit_triage:
        sev = (t.get("recommended_severity") or t.get("severity") or "").strip().lower()
        if not sev or sev in ("unknown", ""):
            bad.append(t.get("finding_id", "?"))
    return bad


def main():
    import argparse as _argparse
    parser = _argparse.ArgumentParser(description="Generate contest-ready submission pack")
    parser.add_argument("--bypass-gate", action="store_true",
                        help="Skip gate_results.jsonl check (not recommended)")
    parser.add_argument("--bypass-poc", action="store_true",
                        help="Skip PoC completeness enforcement (not recommended)")
    args, _ = parser.parse_known_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    print("Smart Contract Auditor — Final Submission Pack\n")

    # ── Pre-flight checks ──────────────────────────────────────────────────────
    _check_gate_results(TRIAGE_DIR, force=args.bypass_gate)
    ok = _check_poc_completeness(OUTPUT_DIR, force=args.bypass_poc)
    if not ok:
        sys.exit(1)

    submit_triage = load_jsonl(TRIAGE_DIR / "submit.jsonl")
    poc_triage = load_jsonl(TRIAGE_DIR / "poc_required.jsonl")
    downgraded = load_downgraded()
    merged = load_merged_findings()

    # ── Severity validation ────────────────────────────────────────────────────
    missing_sev = _validate_severity(submit_triage)
    if missing_sev:
        print(f"\n  [warn] {len(missing_sev)} submit.jsonl entry(ies) have no severity field:")
        for fid in missing_sev:
            print(f"    {fid}: severity=unknown — run validate_triage_output.py to repair")
        print()

    print(f"  submit.jsonl:       {len(submit_triage)} findings")
    print(f"  poc_required.jsonl: {len(poc_triage)} findings")
    print(f"  merged_findings:    {len(merged)} full details available")

    # Load compound notes from merged_findings
    compound_notes: list[str] = []
    mf_path = OUTPUT_DIR / "merged_findings.json"
    if mf_path.exists():
        mf = json.loads(mf_path.read_text())
        notes = mf.get("compound_risk_notes", [])
        compound_notes = notes if isinstance(notes, list) else [str(notes)]

    specialist = load_specialist_outputs()
    spec_counts = {k: len(v) for k, v in specialist.items() if v}
    if spec_counts:
        print(f"  Specialist outputs: {spec_counts}")

    submit_items = [enrich(t, merged, specialist) for t in submit_triage]
    poc_items    = [enrich(t, merged, specialist) for t in poc_triage]

    # Markdown
    md = render_markdown(submit_items, poc_items, downgraded, compound_notes, specialist)
    md_path = OUTPUT_DIR / "submission_pack.md"
    md_path.write_text(md)
    print(f"\n  Written: {md_path}")

    # JSON
    json_out = build_json_output(submit_items, poc_items, compound_notes)
    json_path = OUTPUT_DIR / "submission_pack.json"
    json_path.write_text(json.dumps(json_out, indent=2))
    print(f"  Written: {json_path}")

    print_roi_summary(submit_items, poc_items)
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
