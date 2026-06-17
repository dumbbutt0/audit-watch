#!/usr/bin/env python3
"""
calibrate_severity.py — Severity Calibration Agent.

Reads all specialist outputs and picks the severity most likely to survive
contest judging, using the historical severity rules YAML and any ingested
contest outcome history.

Usage:
    python scripts/calibrate_severity.py --all
    python scripts/calibrate_severity.py --finding-id LG-005
    python scripts/calibrate_severity.py --all --force
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
DUP_DIR     = audit_path("data/duplicates")
LEARN_DIR   = audit_path("data/learning")
SEV_DIR     = audit_path("data/severity")
PROMPTS     = Path(__file__).resolve().parent.parent / "prompts"
OUTPUT_DIR  = audit_path("output")


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


def load_severity_rules() -> str:
    path = LEARN_DIR / "severity_rules.yaml"
    return path.read_text() if path.exists() else ""


def load_severity_history() -> list[dict]:
    return load_jsonl(LEARN_DIR / "severity_history.jsonl")


# ─────────────────────────────────────────────────────────────────────────────
# API call
# ─────────────────────────────────────────────────────────────────────────────

def call_calibrator(triage: dict, original: dict, exploit_model: dict,
                    judge_result: dict, poc_result: dict,
                    dup_result: dict, severity_rules: str,
                    history: list[dict]) -> dict:
    system = (PROMPTS / "severity_calibrator.md").read_text()

    user = json.dumps({
        "finding_id":          triage.get("finding_id", ""),
        "title":               triage.get("title") or original.get("title", ""),
        "original_severity":   original.get("severity", "?"),
        "triage_severity":     triage.get("recommended_severity", "?"),
        "triage":              triage,
        "original":            original,
        "exploitability_model": exploit_model,
        "judge_simulation":    judge_result,
        "runtime_poc":         poc_result,
        "duplicate_risk":      dup_result,
        "severity_rules_yaml": severity_rules,
        "recent_history":      history[-20:] if history else [],
    }, indent=2)

    import uuid as _uuid
    from datetime import datetime as _dt, timezone as _tz
    messages = [{"role": "user", "content": user}]
    client = require_llm(skill="calibrate_severity")
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    try:
        from viz.intercept.cassette import CassetteRecorder
        CassetteRecorder(os.environ.get("VIZ_SESSION_ID", "")).record_llm_call(
            call_id=str(_uuid.uuid4()), agent="calibrate_severity", model=MODEL,
            messages=messages, response=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            timestamp=_dt.now(_tz.utc).isoformat(),
        )
    except Exception:
        pass

    raw = strip_fences(response.content[0].text)
    result = json.loads(raw)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Per-finding processor
# ─────────────────────────────────────────────────────────────────────────────

def process_finding(triage: dict, original: dict, exploit_model: dict,
                    judge_result: dict, poc_result: dict, dup_result: dict,
                    severity_rules: str, history: list[dict],
                    existing: dict[str, dict], force: bool) -> dict:
    fid = triage.get("finding_id", "")
    ts  = datetime.now(timezone.utc).isoformat()

    if fid in existing and not force:
        print(f"  {fid}: already processed — skip")
        return existing[fid]

    orig_sev   = original.get("severity", "?")
    triage_sev = triage.get("recommended_severity", "?")
    print(f"  {fid}: calibrating severity ({orig_sev} → triage:{triage_sev})...", end=" ", flush=True)

    try:
        raw = call_calibrator(triage, original, exploit_model,
                              judge_result, poc_result, dup_result,
                              severity_rules, history)
        result = normalize_calibration(raw, fid, orig_sev, triage_sev)
        result["analyzed_at"] = ts
        cal = result.get("calibrated_severity", "?")
        src = result.get("calibration_source", "?")
        flag = " ⚠ DOWNGRADE" if (triage_sev != "?" and cal != "?" and
                                   _sev_order(cal) > _sev_order(triage_sev)) else ""
        print(f"→ {cal} ({src}){flag}")
        return result
    except Exception as exc:
        print(f"ERROR: {exc}")
        return {
            "finding_id":        fid,
            "status":            "error",
            "error":             str(exc),
            "original_severity": orig_sev,
            "triage_severity":   triage_sev,
            "calibrated_severity": triage_sev,
            "analyzed_at":       ts,
        }


_SEV_MAP = {
    "critical": "critical", "high": "high", "medium": "medium",
    "low": "low", "qa": "qa", "invalid": "invalid",
    "informational": "low", "info": "low",
}

_CAL_SRC_MAP = {
    "rules_only": "rules_only", "rules": "rules_only",
    "historical": "historical", "history": "historical",
    "judge_informed": "judge_informed", "judge": "judge_informed",
    "poc_informed": "poc_informed", "poc": "poc_informed",
}


def normalize_calibration(raw: dict, fid: str,
                           orig_sev: str, triage_sev: str) -> dict:
    """Map Claude's calibration output to canonical severity_calibration schema."""
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
        return default

    sev_raw = _str(raw, "calibrated_severity", "recommended_severity",
                   "severity", "final_severity")
    sev = _SEV_MAP.get(sev_raw.lower().strip(), "") or triage_sev or "medium"

    src_raw = _str(raw, "calibration_source", "source")
    src = _CAL_SRC_MAP.get(src_raw.lower().strip(), "rules_only")
    # Better source if we have judge + poc data
    if not src or src == "rules_only":
        src = "judge_informed"

    return {
        "finding_id":          fid,
        "original_severity":   orig_sev or "?",
        "triage_severity":     triage_sev or "?",
        "calibrated_severity": sev,
        "confidence":          _int(raw, "confidence"),
        "severity_drivers":    _list(raw, "severity_drivers", "drivers", "supporting_factors"),
        "downgrade_triggers":  _list(raw, "downgrade_triggers", "downgrade_reasons", "reasons_to_downgrade"),
        "upgrade_triggers":    _list(raw, "upgrade_triggers", "upgrade_reasons"),
        "rules_applied":       _list(raw, "rules_applied", "rules", "calibration_rules"),
        "similar_historical_cases": _list(raw, "similar_historical_cases", "historical_cases"),
        "recommended_report_wording": _str(raw, "recommended_report_wording",
                                           "report_wording", "wording", "reasoning"),
        "calibration_source":  src,
    }


def _sev_order(sev: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5}.get(
        sev.lower(), 9
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Severity Calibration Agent")
    parser.add_argument("--finding-id", default=None)
    parser.add_argument("--all",   action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.finding_id and not args.all:
        parser.print_help()
        return 1

    SEV_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SEV_DIR / "calibrated.jsonl"

    merged       = load_merged_findings()
    exploit_map  = {r["finding_id"]: r for r in load_jsonl(EXPLOIT_DIR / "models.jsonl")
                    if "finding_id" in r}
    judge_map    = {r["finding_id"]: r for r in load_jsonl(JUDGE_DIR / "results.jsonl")
                    if "finding_id" in r}
    poc_map      = {r["finding_id"]: r for r in load_jsonl(POC_DIR / "results.jsonl")
                    if "finding_id" in r}
    dup_map      = {r["finding_id"]: r for r in load_jsonl(DUP_DIR / "risk.jsonl")
                    if "finding_id" in r}
    existing     = load_existing(output_path)
    findings     = load_all_triage_findings(args.finding_id)
    sev_rules    = load_severity_rules()
    history      = load_severity_history()

    if not findings:
        print(f"[error] No findings found{f' for {args.finding_id}' if args.finding_id else ''}")
        return 1

    print(f"Severity Calibration — {len(findings)} finding(s)\n")

    results: dict[str, dict] = {**existing}
    new_results = []

    for triage in findings:
        fid          = triage.get("finding_id", "")
        original     = merged.get(fid, {})
        result = process_finding(
            triage, original,
            exploit_map.get(fid, {}),
            judge_map.get(fid, {}),
            poc_map.get(fid, {}),
            dup_map.get(fid, {}),
            sev_rules, history,
            existing, args.force,
        )
        results[fid] = result
        new_results.append(result)

    write_jsonl(results, output_path)

    # ── viz: emit CONFIDENCE_SHIFT for each calibrated finding ───────────────
    try:
        from viz.event_emitter import emit as _viz_emit
        _sev_conf = {"Critical": 0.95, "High": 0.80, "Medium": 0.60, "Low": 0.35, "Informational": 0.15}
        for _r in new_results:
            _fid = _r.get("finding_id", "")
            _orig_sev = _r.get("original_severity", "Medium")
            _cal_sev  = _r.get("calibrated_severity", "Medium")
            _old_conf = _sev_conf.get(_orig_sev, 0.5)
            _new_conf = _sev_conf.get(_cal_sev, 0.5)
            if _fid:
                _viz_emit("CONFIDENCE_SHIFT", source_agent="severity_calibration",
                          target_node_id=_fid, payload={
                              "old_confidence": _old_conf,
                              "new_confidence": _new_conf,
                              "reason": f"Severity calibrated: {_orig_sev} → {_cal_sev}",
                              "calibrated_severity": _cal_sev,
                          })
    except Exception:
        pass

    # ── Hermes: emit severity_calibrated ─────────────────────────────────────
    try:
        from scripts.emit_hermes_event import emit_hermes as _h_emit
        from audit_context import get_audit_meta as _get_meta
        _cal_audit_id = _get_meta().get("audit_id", "")
        for _r in new_results:
            _fid = _r.get("finding_id", "")
            if _fid:
                _h_emit("severity_calibrated", {
                    "finding_id": _fid,
                    "original_severity": _r.get("original_severity", ""),
                    "calibrated_severity": _r.get("calibrated_severity", ""),
                    "audit_id": _cal_audit_id,
                })
    except Exception:
        pass

    # Print table
    downgrades = [r for r in new_results
                  if _sev_order(r.get("calibrated_severity", "?")) >
                     _sev_order(r.get("triage_severity", "?"))]

    print(f"\n{'='*70}")
    print(f"  {'Finding':<12} {'Orig':<10} {'Triage':<10} {'Calibrated':<12} {'Source'}")
    print(f"  {'-'*65}")
    for r in new_results:
        flag = " ⚠" if r in downgrades else ""
        print(f"  {r['finding_id']:<12} "
              f"{r.get('original_severity','?'):<10} "
              f"{r.get('triage_severity','?'):<10} "
              f"{r.get('calibrated_severity','?'):<12} "
              f"{r.get('calibration_source','?')}{flag}")

    if downgrades:
        print(f"\n  ⚠  {len(downgrades)} finding(s) calibrated lower than triage severity")
    print(f"  Written → {output_path}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
