#!/usr/bin/env python3
"""
judge_simulate.py — Judge Simulation Agent.

Evaluates each finding through five adversarial judge personas and predicts
whether it will be accepted, downgraded, or rejected in a contest.

Usage:
    python scripts/judge_simulate.py --all
    python scripts/judge_simulate.py --finding-id LG-005
    python scripts/judge_simulate.py --all --force
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

MODEL       = "claude-sonnet-4-6"
TRIAGE_DIR  = audit_path("data/triage")
EXPLOIT_DIR = audit_path("data/exploitability")
POC_DIR     = audit_path("data/runtime_poc")
JUDGE_DIR   = audit_path("data/judge_simulation")
PROMPTS     = Path(__file__).resolve().parent.parent / "prompts"
OUTPUT_DIR  = audit_path("output")

ACTION_MAP = {
    "accepted":            "submit",
    "accepted_downgraded": "revise_severity",
    "duplicate_risk":      "merge_or_reframe",
    "needs_poc":           "poc_first",
    "rejected":            "drop",
}

_OUTCOME_MAP = {
    "accepted":            "accepted",
    "accept":              "accepted",
    "valid":               "accepted",
    "accepted_downgraded": "accepted_downgraded",
    "accepted downgraded": "accepted_downgraded",
    "downgraded":          "accepted_downgraded",
    "downgrade":           "accepted_downgraded",
    "duplicate":           "duplicate_risk",
    "duplicate_risk":      "duplicate_risk",
    "needs_poc":           "needs_poc",
    "needs poc":           "needs_poc",
    "poc required":        "needs_poc",
    "rejected":            "rejected",
    "reject":              "rejected",
    "invalid":             "rejected",
}

_SEV_MAP = {
    "critical": "critical", "high": "high", "medium": "medium",
    "low": "low", "qa": "qa", "invalid": "invalid",
    "informational": "low", "info": "low",
}

_REC_MAP = {
    "submit": "submit", "revise": "revise",
    "poc_first": "poc_first", "poc first": "poc_first",
    "drop": "drop",
}


def normalize_judge(raw: dict, fid: str) -> dict:
    """Map Claude's natural judge output to canonical judge_simulation schema."""
    def _str(d: dict, *keys, default: str = "") -> str:
        for k in keys:
            v = d.get(k)
            if isinstance(v, str) and v:
                return v
        return default

    def _list(d: dict, *keys) -> list:
        for k in keys:
            v = d.get(k)
            if isinstance(v, list):
                return v
            if isinstance(v, str) and v:
                return [v]
        return []

    def _int(d: dict, *keys, default: int = 3) -> int:
        for k in keys:
            v = d.get(k)
            if isinstance(v, (int, float)):
                return int(v)
            if isinstance(v, str):
                try:
                    return int(v)
                except ValueError:
                    pass
        return default

    # Try to extract from nested final_judgment / verdict / judgment structures
    final = raw.get("final_judgment") or raw.get("verdict") or raw.get("judgment") or {}
    if isinstance(final, str):
        final = {"outcome": final}

    # Predicted outcome
    outcome_raw = (
        _str(raw, "predicted_outcome", "outcome") or
        _str(final, "outcome", "predicted_outcome", "decision") or ""
    )
    outcome = _OUTCOME_MAP.get(outcome_raw.lower().strip(), "")
    if not outcome:
        # Try to infer from recommendation
        rec_raw = _str(raw, "final_submit_recommendation", "recommendation") or _str(final, "recommendation")
        if "submit" in rec_raw.lower():
            outcome = "accepted"
        elif "revise" in rec_raw.lower():
            outcome = "accepted_downgraded"
        elif "drop" in rec_raw.lower() or "reject" in rec_raw.lower():
            outcome = "rejected"
        elif "poc" in rec_raw.lower():
            outcome = "needs_poc"
        else:
            outcome = "accepted"  # safe default

    # Predicted severity
    sev_raw = (
        _str(raw, "predicted_severity", "severity") or
        _str(final, "severity", "predicted_severity") or ""
    )
    sev = _SEV_MAP.get(sev_raw.lower().strip(), "")
    if not sev:
        sev = "medium"  # safe default

    # Confidence
    conf = _int(raw, "confidence") or _int(final, "confidence")
    conf = max(1, min(5, conf))

    # Strongest objection
    objection = (
        _str(raw, "strongest_objection", "main_objection", "objection") or
        _str(final, "strongest_objection", "objection") or ""
    )

    # Personas
    personas_raw = raw.get("personas", raw.get("persona_verdicts", {}))
    if isinstance(personas_raw, dict):
        persona_verdicts = {
            "strict_judge":    _str(personas_raw, "strict_judge", "judge", "strict_contest_judge"),
            "protocol_sponsor": _str(personas_raw, "protocol_sponsor", "sponsor"),
            "duplicate_hunter": _str(personas_raw, "duplicate_hunter", "duplicate"),
            "downgrade_judge":  _str(personas_raw, "downgrade_judge", "severity_downgrade_judge", "downgrade"),
            "exploit_skeptic":  _str(personas_raw, "exploit_skeptic", "skeptic", "practical_exploit_skeptic"),
        }
        # Try numbered keys like "persona_1", "persona_2" etc.
        if not any(persona_verdicts.values()):
            keys = list(personas_raw.keys())
            labels = ["strict_judge", "protocol_sponsor", "duplicate_hunter",
                      "downgrade_judge", "exploit_skeptic"]
            for i, label in enumerate(labels):
                if i < len(keys):
                    persona_verdicts[label] = str(personas_raw.get(keys[i], ""))
    else:
        persona_verdicts = {k: "" for k in
                            ["strict_judge", "protocol_sponsor", "duplicate_hunter",
                             "downgrade_judge", "exploit_skeptic"]}

    # Final recommendation
    rec_raw = (
        _str(raw, "final_submit_recommendation", "recommendation") or
        _str(final, "recommendation", "final_submit_recommendation") or ""
    )
    rec = _REC_MAP.get(rec_raw.lower().strip(), "")
    if not rec:
        rec = {"accepted": "submit", "accepted_downgraded": "revise",
               "duplicate_risk": "drop", "needs_poc": "poc_first",
               "rejected": "drop"}.get(outcome, "revise")

    return {
        "finding_id":               fid,
        "predicted_outcome":        outcome,
        "predicted_severity":       sev,
        "confidence":               conf,
        "strongest_objection":      objection,
        "likely_judge_questions":   _list(raw, "likely_judge_questions", "judge_questions"),
        "severity_downgrade_reasons": _list(raw, "severity_downgrade_reasons", "downgrade_reasons"),
        "duplicate_risk_reasons":   _list(raw, "duplicate_risk_reasons", "duplicate_reasons"),
        "missing_evidence":         _list(raw, "missing_evidence", "missing_proof"),
        "rewrite_suggestions":      _list(raw, "rewrite_suggestions", "suggestions"),
        "persona_verdicts":         persona_verdicts,
        "final_submit_recommendation": rec,
    }


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
                pass
    return items


def load_existing(output_path: Path) -> dict[str, dict]:
    return {r["finding_id"]: r for r in load_jsonl(output_path) if "finding_id" in r}


def write_jsonl(records: dict[str, dict], path: Path) -> None:
    with path.open("w") as fh:
        for r in records.values():
            fh.write(json.dumps(r) + "\n")


def strip_fences(raw: str) -> str:
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
    return raw.strip()


def load_merged_findings() -> dict[str, dict]:
    path = OUTPUT_DIR / "merged_findings.json"
    if not path.exists():
        return {}
    return {f["id"]: f for f in json.loads(path.read_text()).get("findings", [])}


def load_all_triage_findings(finding_id: str | None = None) -> list[dict]:
    items = (
        load_jsonl(TRIAGE_DIR / "submit.jsonl") +
        load_jsonl(TRIAGE_DIR / "poc_required.jsonl")
    )
    if finding_id:
        items = [i for i in items if i.get("finding_id") == finding_id]
    return items


# ─────────────────────────────────────────────────────────────────────────────
# API call
# ─────────────────────────────────────────────────────────────────────────────

def call_judge(triage: dict, original: dict, exploit_model: dict,
               poc_result: dict, all_findings_summary: list[dict]) -> dict:
    system = (PROMPTS / "judge_simulator.md").read_text()

    user = json.dumps({
        "finding_id":           triage.get("finding_id", ""),
        "title":                triage.get("title") or original.get("title", ""),
        "triage":               triage,
        "original":             original,
        "exploitability_model": exploit_model,
        "runtime_poc_result":   poc_result,
        "batch_context":        all_findings_summary,
    }, indent=2)

    client = require_llm(skill="judge_simulate")
    response = client.messages.create(
        model=MODEL,
        max_tokens=3072,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = strip_fences(response.content[0].text)
    result = json.loads(raw)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Per-finding processor
# ─────────────────────────────────────────────────────────────────────────────

def process_finding(triage: dict, original: dict, exploit_model: dict,
                    poc_result: dict, all_findings_summary: list[dict],
                    existing: dict[str, dict], force: bool) -> dict:
    fid = triage.get("finding_id", "")
    ts  = datetime.now(timezone.utc).isoformat()

    if fid in existing and not force:
        print(f"  {fid}: already processed — skip")
        return existing[fid]

    exploit_score = exploit_model.get("exploitability_score", 0)
    if exploit_score < 3:
        print(f"  {fid}: exploit_score={exploit_score} < 3 — skip")
        return {
            "finding_id":    fid,
            "status":        "skipped",
            "reason":        "low_exploitability",
            "analyzed_at":   ts,
        }

    print(f"  {fid}: simulating judge review...", end=" ", flush=True)
    try:
        raw = call_judge(triage, original, exploit_model,
                         poc_result, all_findings_summary)
        result = normalize_judge(raw, fid)
        outcome = result.get("predicted_outcome", "?")
        result["final_action"] = ACTION_MAP.get(outcome, "review")
        result["analyzed_at"]  = ts

        sev  = result.get("predicted_severity", "?")
        conf = result.get("confidence", "?")
        print(f"{outcome} → {sev} (conf={conf})")
        return result
    except Exception as exc:
        print(f"ERROR: {exc}")
        return {
            "finding_id":  fid,
            "status":      "error",
            "error":       str(exc),
            "final_action": "review",
            "analyzed_at": ts,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Judge Simulation Agent")
    parser.add_argument("--finding-id", default=None)
    parser.add_argument("--all",   action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.finding_id and not args.all:
        parser.print_help()
        return 1

    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = JUDGE_DIR / "results.jsonl"

    merged      = load_merged_findings()
    exploit_map = {r["finding_id"]: r
                   for r in load_jsonl(EXPLOIT_DIR / "models.jsonl") if "finding_id" in r}
    poc_map     = {r["finding_id"]: r
                   for r in load_jsonl(POC_DIR / "results.jsonl") if "finding_id" in r}
    existing    = load_existing(output_path)
    findings    = load_all_triage_findings(args.finding_id)

    if not findings:
        print(f"[error] No findings found{f' for {args.finding_id}' if args.finding_id else ''}")
        return 1

    # Build batch summary for duplicate detection context
    all_findings_summary = [
        {
            "finding_id": t.get("finding_id"),
            "title":      t.get("title") or merged.get(t.get("finding_id", ""), {}).get("title", ""),
            "severity":   t.get("recommended_severity"),
            "vuln_type":  merged.get(t.get("finding_id", ""), {}).get("vuln_type", ""),
            "location":   merged.get(t.get("finding_id", ""), {}).get("location", {}),
            "description_excerpt":
                (merged.get(t.get("finding_id", ""), {}).get("description", "") or "")[:300],
        }
        for t in load_all_triage_findings()  # always all findings for context
    ]

    print(f"Judge Simulation — {len(findings)} finding(s)\n")

    results: dict[str, dict] = {**existing}
    new_results = []

    for triage in findings:
        fid          = triage.get("finding_id", "")
        original     = merged.get(fid, {})
        exploit_model = exploit_map.get(fid, {"exploitability_score": 0})
        poc_result   = poc_map.get(fid, {})
        result = process_finding(
            triage, original, exploit_model, poc_result,
            all_findings_summary, existing, args.force,
        )
        results[fid] = result
        new_results.append(result)

    write_jsonl(results, output_path)

    # Summary table
    print(f"\n{'='*90}")
    print(f"  {'Finding':<12} {'Outcome':<22} {'Severity':<10} {'Conf':<6} {'Objection'}")
    print(f"  {'-'*85}")
    for r in new_results:
        if r.get("status") in ("skipped", "error"):
            print(f"  {r['finding_id']:<12} {r.get('status','?'):<22} {'—':<10} {'—':<6}")
            continue
        objection = (r.get("strongest_objection", "") or "")[:60]
        print(f"  {r['finding_id']:<12} {r.get('predicted_outcome','?'):<22} "
              f"{r.get('predicted_severity','?'):<10} {str(r.get('confidence','?')):<6} {objection}")

    print(f"\n  Written → {output_path}")
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
