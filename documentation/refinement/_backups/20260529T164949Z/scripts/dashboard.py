"""
Audit Watch — Local dashboard backend.

Launch:  python scripts/dashboard.py
Opens:   http://localhost:8765
Polling: frontend hits /api/state every 10s.

All file reads degrade gracefully — missing files return null/empty rather
than 500. Field names below are the verified-from-disk names; do not rename
without re-reading the source JSONLs.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import asyncio
import threading
import webbrowser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import html as _html

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --------------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root (if present) without requiring python-dotenv.
_dotenv = ROOT / ".env"
if _dotenv.exists():
    with _dotenv.open() as _fh:
        for _line in _fh:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
DASH_DIR = ROOT / "dashboard"
INDEX_HTML = DASH_DIR / "index.html"

# Shared project-level paths (not per-audit)
KB = ROOT / "kb"
KB_STATE = KB / "scraper_state.json"
KB_LOG   = KB / "scraper.log"
KB_CHROMA = KB / "chroma"

# Import audit context for per-audit path resolution
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import (
    audit_path as _ap,
    get_active_audit,
    get_audit_meta,
    list_audits,
    switch_audit as _switch_audit,
    create_audit_workspace as _create_workspace,
    update_registry_stats as _update_stats,
)
from decision_logic import compute_pipeline_layer, layer_label as _dl_layer_label

# Lazy path functions — re-evaluated on every /api/state call so that
# switch_audit() takes effect immediately without restarting the server.
def STATIC_JSON():            return _ap("output") / "static.json"
def MERGED_JSON():            return _ap("output") / "merged_findings.json"
def FINDINGS_DIR():           return _ap("data/findings")
def TRIAGE_SUBMIT():          return _ap("data/triage") / "submit.jsonl"
def TRIAGE_POC():             return _ap("data/triage") / "poc_required.jsonl"
def TRIAGE_DOWN():            return _ap("data/triage") / "downgraded.jsonl"
def TRIAGE_REJ():             return _ap("data/triage") / "rejected.jsonl"
def POC_QUEUE():              return _ap("data/triage") / "poc_queue.jsonl"
def EXPLOIT_JSONL():          return _ap("data/exploitability") / "models.jsonl"
def DUPS_JSONL():             return _ap("data/duplicates") / "risk.jsonl"
def SEV_JSONL():              return _ap("data/severity") / "calibrated.jsonl"
def RUNTIME_JSONL():          return _ap("data/runtime_poc") / "results.jsonl"
def JUDGE_JSONL():            return _ap("data/judge_simulation") / "results.jsonl"
def CHECKLIST_JSONL():        return _ap("data/quality_checklist") / "results.jsonl"
def POC_COMPLETE_DIR():       return _ap("output/poc_completeness")
def SUBMISSIONS_DIR():        return _ap("output/submissions")
def UPGRADE_TASK_DIR():       return _ap("output/poc_upgrade_tasks")
def POC_DIR():                return _ap("pocs/k2")
def FOUNDRY_TEST_DIR():       return _ap("pocs/foundry/test")
# Deep invariant analysis paths
def INVARIANTS_JSON():        return _ap("data/invariants") / "protocol_invariants.json"
def HIGH_SUSPICION_JSON():    return _ap("data/invariants") / "high_suspicion.json"
def CALL_GRAPH_JSON():        return _ap("data/interactions") / "call_graph.json"
def DANGEROUS_CHAINS_JSON():  return _ap("data/interactions") / "dangerous_chains.json"
def PROMISING_THREADS_JSONL(): return _ap("data/threads") / "promising_threads.jsonl"
def DEAD_ENDS_JSONL():        return _ap("data/threads") / "dead_ends.jsonl"
def DEEP_TRACE_FINDINGS_JSON(): return _ap("output") / "findings_deep_trace.json"

_VIEWER_CSS = """\
<style>
:root{--bg:#0f172a;--surface:#1e293b;--border:#334155;--text:#f1f5f9;--muted:#94a3b8;--accent:#38bdf8;--mono:"JetBrains Mono",ui-monospace,SFMono-Regular,monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:Inter,system-ui,sans-serif;font-size:14px;line-height:1.6}
.toolbar{background:var(--surface);border-bottom:1px solid var(--border);padding:10px 24px;display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:10}
.toolbar .ttl{font-weight:600;font-size:14px}
.toolbar .sub{color:var(--muted);font-size:12px;font-family:var(--mono)}
.toolbar a{color:var(--accent);text-decoration:none;font-size:12px;border:1px solid rgba(56,189,248,0.35);border-radius:4px;padding:3px 8px}
.toolbar a:hover{background:rgba(56,189,248,0.1)}
.content{max-width:960px;margin:0 auto;padding:28px 24px}
.fname{font-family:var(--mono);font-size:11px;color:var(--muted);background:var(--surface);border:1px solid var(--border);border-radius:6px 6px 0 0;padding:6px 12px;border-bottom:none}
pre{white-space:pre-wrap;word-break:break-word;font-size:12.5px;line-height:1.65;color:#e2e8f0;font-family:var(--mono);background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:20px;overflow-x:auto}
.fname+pre{border-radius:0 0 6px 6px}
</style>"""


# --------------------------------------------------------------------- SSE
_sse_clients: list[asyncio.Queue] = []
_sse_lock = threading.Lock()


def _broadcast_event(event_type: str, data: dict) -> None:
    """Push a Server-Sent Event to all connected SSE clients (thread-safe)."""
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)



def _viewer_page(title: str, subtitle: str, body_html: str) -> str:
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"/>'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f'<title>{_html.escape(title)}</title>{_VIEWER_CSS}</head><body>'
        f'<div class="toolbar">'
        f'<a href="/" title="Back to dashboard">← Dashboard</a>'
        f'<span class="ttl">{_html.escape(title)}</span>'
        f'<span class="sub">{_html.escape(subtitle)}</span>'
        f'</div>'
        f'<div class="content">{body_html}</div>'
        f'</body></html>'
    )

# ---------------------------------------------------------------- file helpers
def _read_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, OSError):
        return []
    return out


def _jsonl_by(path: Path, key: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in _read_jsonl(path):
        k = row.get(key)
        if k is not None:
            out[k] = row
    return out


def _read_dir_json(directory: Path, key: str = "finding_id") -> Dict[str, Dict[str, Any]]:
    """Load all *.json files from a directory, keyed by `key` (or filename stem)."""
    out: Dict[str, Dict[str, Any]] = {}
    if not directory.exists():
        return out
    for p in sorted(directory.glob("*.json")):
        data = _read_json(p)
        if isinstance(data, dict):
            k = data.get(key) or p.stem
            out[k] = data
    return out


def _tail(path: Path, n: int) -> List[str]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        return [ln.rstrip("\n") for ln in lines[-n:]]
    except (FileNotFoundError, OSError):
        return []


def _chroma_count() -> Optional[int]:
    """Return KB finding count via chromadb; None if unavailable."""
    if not KB_CHROMA.exists():
        return None
    try:
        import chromadb  # type: ignore
        client = chromadb.PersistentClient(path=str(KB_CHROMA))
        # Best-effort: sum counts across all collections.
        total = 0
        for col in client.list_collections():
            try:
                total += client.get_collection(col.name).count()
            except Exception:
                continue
        return total
    except Exception:
        return None


# ------------------------------------------------------------- state assembly
def _agent_palette(agents: Iterable[str]) -> Dict[str, str]:
    # Deterministic color per agent; consumed by frontend if it wants it.
    palette = [
        "#7c3aed", "#0ea5e9", "#f97316", "#10b981",
        "#f59e0b", "#ec4899", "#22d3ee", "#a3a3a3",
    ]
    return {a: palette[i % len(palette)] for i, a in enumerate(sorted(set(agents)))}


def _build_state() -> Dict[str, Any]:
    # ---------- raw sources
    static_data = _read_json(STATIC_JSON()) or {}
    merged = _read_json(MERGED_JSON()) or {}
    all_findings: List[Dict[str, Any]] = merged.get("findings") if isinstance(merged, dict) else []
    if all_findings is None:
        all_findings = merged if isinstance(merged, list) else []
    compound_notes = merged.get("compound_risk_notes", []) if isinstance(merged, dict) else []

    finding_defs = _read_dir_json(FINDINGS_DIR(), key="finding_id")

    triage_submit = _read_jsonl(TRIAGE_SUBMIT())
    triage_poc = _read_jsonl(TRIAGE_POC())
    triage_down = _read_jsonl(TRIAGE_DOWN())
    triage_rej = _read_jsonl(TRIAGE_REJ())

    triage_by_id: Dict[str, Dict[str, Any]] = {}
    triage_status_by_id: Dict[str, str] = {}
    for status, rows in (
        ("submit", triage_submit),
        ("poc_required", triage_poc),
        ("downgraded", triage_down),
        ("rejected", triage_rej),
    ):
        for r in rows:
            fid = r.get("finding_id")
            if not fid:
                continue
            triage_by_id[fid] = r
            triage_status_by_id[fid] = r.get("triage_status") or status

    exploit = _jsonl_by(EXPLOIT_JSONL(), "finding_id")
    duplicates = _jsonl_by(DUPS_JSONL(), "finding_id")
    severity = _jsonl_by(SEV_JSONL(), "finding_id")
    runtime_poc = _jsonl_by(RUNTIME_JSONL(), "finding_id")
    judge = _jsonl_by(JUDGE_JSONL(), "finding_id")
    checklist = _jsonl_by(CHECKLIST_JSONL(), "finding_id")
    completeness = _read_dir_json(POC_COMPLETE_DIR(), key="finding_id")

    submissions = sorted(p.name for p in SUBMISSIONS_DIR().glob("*.md")) if SUBMISSIONS_DIR().exists() else []
    poc_queue_rows = _read_jsonl(POC_QUEUE())

    kb_state = _read_json(KB_STATE) or {}
    kb_log_tail = _tail(KB_LOG, 5)
    kb_count = _chroma_count()

    # ---------- per-finding flattening
    severity_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    findings_out: List[Dict[str, Any]] = []
    agents_seen: List[str] = []
    findings_per_agent: Dict[str, int] = defaultdict(int)

    # Synthesize entries for findings that are in triage files but absent from merged_findings.json.
    # IMPORTANT: only synthesize if a definition file exists in data/findings/ — this prevents
    # stale findings from prior audit runs (stored in the shared triage/merged files) from
    # polluting the current audit's dashboard view.
    merged_ids = {(f.get("id") or f.get("finding_id")) for f in all_findings}
    for fid, tri_row in triage_by_id.items():
        if fid not in merged_ids and fid in finding_defs:
            all_findings.append({
                "id": fid,
                "finding_id": fid,
                "title": tri_row.get("title", fid),
                "severity": tri_row.get("recommended_severity", "").title(),
                "_source_agent": tri_row.get("agent"),
                "description": tri_row.get("impact", ""),
            })
            merged_ids.add(fid)

    # Filter all_findings to only those with an explicit definition in data/findings/
    # This scopes the dashboard to the current audit session.
    all_findings = [f for f in all_findings
                    if (f.get("id") or f.get("finding_id")) in finding_defs]

    for f in all_findings:
        fid = f.get("id") or f.get("finding_id")
        if not fid:
            continue
        defn = finding_defs.get(fid, {})
        tri = triage_by_id.get(fid, {})
        exp = exploit.get(fid, {})
        dup = duplicates.get(fid, {})
        sev = severity.get(fid, {})
        rp = runtime_poc.get(fid, {})
        jg = _normalize_judge(judge.get(fid, {})) or {}
        cl = checklist.get(fid, {})
        cg = completeness.get(fid, {})

        agent = f.get("agent") or f.get("_source_agent") or defn.get("agent") or "unknown"
        agents_seen.append(agent)
        findings_per_agent[agent] += 1

        raw_sev = f.get("severity") or defn.get("severity") or "Informational"
        cal_sev = sev.get("calibrated_severity")
        ceiling = cg.get("severity_ceiling")
        # Bucket for the distribution chart: ceiling > calibrated > raw
        bucket = (ceiling or cal_sev or raw_sev or "Informational").title()
        if bucket in severity_dist:
            severity_dist[bucket] += 1

        triage_status = triage_status_by_id.get(fid)
        triage_score = None
        score_obj = tri.get("score")
        if isinstance(score_obj, dict):
            triage_score = score_obj.get("total")

        # Derive poc_level from completeness gate first; fall back to runtime_level mapping.
        poc_level = cg.get("poc_level_achieved") or rp.get("poc_level")
        if not poc_level and rp.get("runtime_level", 0) >= 3:
            poc_level = "L3"   # generic Level-3 when no completeness detail is available
        # Promote any L3 level to L3F when a passing fork test exists.
        if poc_level and poc_level.upper().startswith("L3") and rp.get("has_fork_test"):
            poc_level = "L3F"
        upgrade_required = cg.get("upgrade_required")
        checklist_overall = cl.get("overall")

        is_chain = bool(defn.get("is_chain") or str(fid).startswith("CHAIN-"))
        chain_components = defn.get("chain_components") or []
        chain_type = defn.get("chain_type") or ""

        submission_ready = bool(
            triage_status == "submit"
            and checklist_overall != "failed"
            and upgrade_required is not True
        )

        findings_out.append({
            "id": fid,
            "title": f.get("title") or defn.get("title") or fid,
            "agent": agent,
            "raw_severity": raw_sev,
            "triage_status": triage_status,
            "triage_score": triage_score,
            "recommended_severity": tri.get("recommended_severity"),
            "calibrated_severity": cal_sev,
            "severity_ceiling": ceiling,
            "exploitability_score": exp.get("exploitability_score"),
            "duplicate_risk": dup.get("duplicate_risk"),
            "duplicate_probability": dup.get("probability"),
            "poc_status": rp.get("status"),
            "poc_level": poc_level,
            "poc_has_fork": bool(rp.get("has_fork_test")),
            "poc_runtime_level": rp.get("runtime_level"),
            "upgrade_required": upgrade_required,
            "checklist_overall": checklist_overall,
            # jg is already normalized by _normalize_judge(); use canonical names directly.
            "predicted_outcome": jg.get("predicted_outcome"),
            "predicted_severity": jg.get("predicted_severity"),
            # Derive final_action from judge first, then fall back to triage_status mapping.
            "final_action": (
                jg.get("final_action")
                or {
                    "submit": "submit",
                    "poc_required": "poc_first",
                    "downgraded": "revise",
                    "rejected": "drop",
                }.get(triage_status or "")
            ),
            "compound": bool(f.get("compound") or fid in (merged.get("compound_finding_ids") or [])),
            "is_chain": is_chain,
            "chain_components": chain_components,
            "chain_type": chain_type,
            "submission_ready": submission_ready,
            "thread_id": f.get("thread_id") or defn.get("thread_id"),
            "trace_depth": f.get("trace_depth") or defn.get("trace_depth"),
        })

    # ---------- pipeline stages
    stage1 = {
        "done": bool(static_data),
        "contract_path": static_data.get("contract_path") if static_data else None,
        "compiler": static_data.get("compiler") if static_data else None,
        "function_count": static_data.get("function_count") if static_data else None,
        "detail": (
            f"{static_data.get('contract_path')} · solc {static_data.get('compiler')} · "
            f"{static_data.get('function_count')} fns" if static_data else ""
        ),
    }

    stage2 = {
        "done": bool(all_findings),
        "agents_run": sorted(set(agents_seen)),
        "findings_per_agent": dict(findings_per_agent),
        "finding_count": len(all_findings),
        "total_raw": len(all_findings),
    }

    stage3 = {
        "done": bool(merged),
        "compound_risk_count": len(compound_notes) if isinstance(compound_notes, list) else 0,
        "detail": f"{len(all_findings)} findings · {len(compound_notes)} compound" if merged else "",
    }

    chained_ids = {fid for fid, fd in finding_defs.items() if fd.get("is_chain") or fid.startswith("CHAIN-")}
    chained_count = len(chained_ids)
    # Scope triage counts to findings that have definition files (current audit only)
    defined_submit   = [r for r in triage_submit if r.get("finding_id") in finding_defs]
    defined_poc      = [r for r in triage_poc    if r.get("finding_id") in finding_defs]
    defined_down     = [r for r in triage_down   if r.get("finding_id") in finding_defs]
    defined_rej      = [r for r in triage_rej    if r.get("finding_id") in finding_defs]
    stage4 = {
        "done": bool(defined_submit or defined_poc or defined_down or defined_rej),
        "submit": len(defined_submit),
        "poc_required": len(defined_poc),
        "downgraded": len(defined_down),
        "rejected": len(defined_rej),
        "chained": chained_count,
    }

    stage5 = {
        "done": bool(severity),
        "exploitability_done": len(exploit),
        "judge_done": len(judge),
        "severity_done": len(severity),
        "total_findings": len(all_findings),
    }

    proved = sum(1 for v in runtime_poc.values() if v.get("status") == "proved")
    failed = sum(1 for v in runtime_poc.values() if v.get("status") == "failed")
    pending = max(0, len(all_findings) - proved - failed)
    level_dist = {"L3C": 0, "L3B": 0, "L3A": 0, "L2": 0}
    for cg in completeness.values():
        lv = cg.get("poc_level_achieved")
        if lv in level_dist:
            level_dist[lv] += 1
    stage6 = {
        "done": bool(runtime_poc),
        "proved": proved,
        "failed": failed,
        "pending": pending,
        "level_dist": level_dist,
    }

    cl_passed = sum(1 for v in checklist.values() if v.get("overall") == "passed")
    cl_cond = sum(1 for v in checklist.values() if v.get("overall") == "conditional")
    cl_failed = sum(1 for v in checklist.values() if v.get("overall") in ("failed", "block"))
    stage7 = {
        "done": bool(checklist),
        "passed": cl_passed,
        "ready": cl_passed,
        "conditional": cl_cond,
        "failed": cl_failed,
        "blocked": cl_failed,
    }

    high_supported = sum(
        1 for cg in completeness.values()
        if (cg.get("severity_ceiling") or "").lower() == "high" and not cg.get("upgrade_required")
    )
    ceiling_down = sum(
        1 for cg in completeness.values()
        if (cg.get("severity_ceiling") or "").lower() == "medium"
    )
    upgrade_req = sum(1 for cg in completeness.values() if cg.get("upgrade_required"))
    stage8 = {
        "done": bool(completeness),
        "high_supported": high_supported,
        "ceiling_downgraded": ceiling_down,
        "downgraded_to_medium": ceiling_down,
        "upgrade_required": upgrade_req,
    }

    # ---------- kb block
    last_run = kb_state.get("last_run") or kb_state.get("last_sync")
    kb_block = {
        "total_findings": kb_count,
        "last_run": last_run,
        "cycles": kb_state.get("cycles"),
        "continuous_running": bool(kb_state.get("continuous_running")),
        "scraper_log_tail": kb_log_tail,
    }

    triage_funnel = {
        "total_raw": len(all_findings),  # already scoped to defined findings
        "submit": stage4["submit"],
        "poc_required": stage4["poc_required"],
        "downgraded": stage4["downgraded"],
        "rejected": stage4["rejected"],
        "chained": chained_count,
    }

    # ---------- deep invariant analysis block
    inv_list = _read_json(INVARIANTS_JSON())
    inv_list = inv_list if isinstance(inv_list, list) else []
    high_susp_list = _read_json(HIGH_SUSPICION_JSON())
    high_susp_list = high_susp_list if isinstance(high_susp_list, list) else []
    call_graph_data = _read_json(CALL_GRAPH_JSON()) or {}
    all_chains = call_graph_data.get("interaction_chains", []) if isinstance(call_graph_data, dict) else []
    dangerous_chains = _read_json(DANGEROUS_CHAINS_JSON())
    dangerous_chains = dangerous_chains if isinstance(dangerous_chains, list) else []
    promising_threads = _read_jsonl(PROMISING_THREADS_JSONL())
    dead_end_threads = _read_jsonl(DEAD_ENDS_JSONL())
    dt_findings_data = _read_json(DEEP_TRACE_FINDINGS_JSON()) or {}
    dt_findings = dt_findings_data.get("findings", []) if isinstance(dt_findings_data, dict) else []

    deep_analysis = {
        "invariants_extracted": len(inv_list),
        "high_suspicion_invariants": len(high_susp_list),
        "interaction_chains_mapped": len(all_chains),
        "dangerous_chains": len(dangerous_chains),
        "threads_traced": len(promising_threads) + len(dead_end_threads),
        "critical_threads": sum(
            1 for t in promising_threads if t.get("verdict") == "CRITICAL_THREAD"
        ),
        "high_threads": sum(
            1 for t in promising_threads if t.get("verdict") == "HIGH_THREAD"
        ),
        "dead_ends": len(dead_end_threads),
        "deep_trace_findings": len(dt_findings),
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "stage_1_static": stage1,
            "stage_2_agents": stage2,
            "stage_3_report": stage3,
            "stage_4_triage": stage4,
            "stage_5_specialist": stage5,
            "stage_6_poc": stage6,
            "stage_7_checklist": stage7,
            "stage_8_gate": stage8,
        },
        "deep_analysis": deep_analysis,
        "kb": kb_block,
        "severity_distribution": severity_dist,
        "triage_funnel": triage_funnel,
        "findings": findings_out,
        "poc_queue": [
            {
                "finding_id": r.get("finding_id"),
                "poc_priority": r.get("poc_priority"),
                "goal": r.get("goal"),
                "status": r.get("status"),
                "poc_level": r.get("poc_level"),
                "runtime_level": r.get("runtime_level"),
            }
            for r in poc_queue_rows
        ],
        "submissions": submissions,
        "compound_risks": compound_notes if isinstance(compound_notes, list) else [],
        "active_audit": _get_active_audit_block(),
    }


def _get_active_audit_block() -> Optional[Dict[str, Any]]:
    """Return active audit metadata for the state payload, or None if no audit is active."""
    try:
        active_cfg = get_active_audit()
        if not active_cfg.get("audit_id"):
            return None
        meta = get_audit_meta()
        return {
            "audit_id":      active_cfg["audit_id"],
            "name":          meta.get("name", active_cfg["audit_id"]),
            "contest":       meta.get("contest", ""),
            "platform":      meta.get("platform", ""),
            "status":        meta.get("status", ""),
            "language":      meta.get("language", ""),
            "contract_path": meta.get("contract_path", ""),
            "deadline":      meta.get("deadline", ""),
            "start_date":    meta.get("start_date", ""),
        }
    except Exception:
        return None


def _normalize_judge(jg: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Normalize judge JSONL entry to canonical field names (two vintages in the wild)."""
    if not jg:
        return jg
    out = dict(jg)
    # Old vintage: verdict + simulated_severity; new vintage: predicted_outcome + predicted_severity
    out.setdefault("predicted_outcome", jg.get("predicted_outcome") or jg.get("simulated_outcome") or jg.get("verdict"))
    out.setdefault("predicted_severity", jg.get("predicted_severity") or jg.get("simulated_severity"))
    out.setdefault("final_action", jg.get("final_action") or jg.get("final_submit_recommendation")
                   or ("submit" if out.get("predicted_outcome") == "accepted" else None))
    out.setdefault("strongest_objection", (jg.get("objections") or [""])[0] if isinstance(jg.get("objections"), list) else jg.get("strongest_objection", ""))
    out.setdefault("likely_judge_questions", jg.get("objections") if isinstance(jg.get("objections"), list) else [])
    return out


# Commands the /api/run endpoint is allowed to execute.
ALLOWED_COMMAND_PATTERNS = [
    re.compile(r"^python\s+scripts/[\w_]+\.py(\s+[\w\-=./#]+)*$"),
    re.compile(r"^python\s+tools/[\w_]+\.py(\s+[\w\-=./#]+)*$"),
]

# ------------------------------------------------------------------- FastAPI
app = FastAPI(title="Audit Watch")


@app.get("/api/state")
def get_state() -> JSONResponse:
    try:
        return JSONResponse(_build_state())
    except Exception as exc:  # noqa: BLE001
        # Never 500 on missing data; surface the error in-band.
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/audits")
def list_all_audits() -> JSONResponse:
    try:
        audits = list_audits()
        active_cfg = get_active_audit()
        return JSONResponse({
            "audits": audits,
            "active_audit_id": active_cfg.get("audit_id"),
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


class _SwitchRequest(BaseModel):
    audit_id: str


@app.post("/api/audits/switch")
def switch_audit_endpoint(body: _SwitchRequest) -> JSONResponse:
    try:
        _switch_audit(body.audit_id)
        return JSONResponse({"ok": True, "audit_id": body.audit_id})
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


class _CreateAuditRequest(BaseModel):
    audit_id: str
    name: str
    contest: str = ""
    platform: str = ""
    language: str = ""
    framework: str = ""
    contract_path: str = ""
    deadline: str = ""
    switch_to: bool = False


@app.post("/api/audits/create")
def create_audit_endpoint(body: _CreateAuditRequest) -> JSONResponse:
    try:
        meta = {
            "audit_id":      body.audit_id,
            "name":          body.name,
            "contest":       body.contest,
            "platform":      body.platform,
            "language":      body.language,
            "framework":     body.framework,
            "contract_path": body.contract_path,
            "deadline":      body.deadline,
            "status":        "active",
        }
        workspace = _create_workspace(body.audit_id, meta)
        if body.switch_to:
            _switch_audit(body.audit_id)
        return JSONResponse({"ok": True, "workspace": str(workspace)})
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=409)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


def _resolve_fork_poc_file(finding_id: str) -> Optional[str]:
    """Return the repo-relative path of a fork test file for this finding, or None."""
    triage_row = (
        _jsonl_by(TRIAGE_SUBMIT(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_POC(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_DOWN(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_REJ(), "finding_id").get(finding_id)
    )
    candidates: List[str] = []
    if triage_row:
        chain_tf = triage_row.get("chain_test_file", "") or ""
        poc_tf   = triage_row.get("poc_test_file",   "") or ""
        if chain_tf:
            candidates.append(chain_tf)
        if poc_tf and "fork" in poc_tf.lower():
            candidates.append(poc_tf)
    # Pattern-match in pocs/enzyme/test/ as fallback
    enzyme_dir = ROOT / "pocs" / "enzyme" / "test"
    if enzyme_dir.exists():
        slug = finding_id.replace("-", "").lower()
        for p in sorted(enzyme_dir.glob("*fork*.t.sol")):
            if slug in p.stem.lower():
                candidates.append(str(p.relative_to(ROOT)))
    for rel in candidates:
        if rel and (ROOT / rel).exists():
            return rel
    return None


@app.get("/api/finding/{finding_id}")
def get_finding(finding_id: str) -> JSONResponse:
    merged = _read_json(MERGED_JSON()) or {}
    findings = merged.get("findings") if isinstance(merged, dict) else merged
    raw = None
    if isinstance(findings, list):
        for f in findings:
            if (f.get("id") or f.get("finding_id")) == finding_id:
                raw = f
                break
    if raw is None:
        # Fall back to data/findings/<id>.json
        raw = _read_json(FINDINGS_DIR() / f"{finding_id}.json")
    if raw is None:
        raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found")

    # Flatten nested location object so the frontend can read f.file, f.function, f.lines, f.code.
    if isinstance(raw, dict) and isinstance(raw.get("location"), dict):
        loc = raw["location"]
        raw = {**raw}  # shallow copy to avoid mutating cached data
        raw.setdefault("file", loc.get("file"))
        raw.setdefault("function", loc.get("function"))
        lines = loc.get("line_start")
        if loc.get("line_end") and loc.get("line_end") != loc.get("line_start"):
            lines = f"{lines}–{loc['line_end']}"
        raw.setdefault("lines", str(lines) if lines else None)
        raw.setdefault("code", loc.get("code_snippet"))

    triage_row = (
        _jsonl_by(TRIAGE_SUBMIT(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_POC(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_DOWN(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_REJ(), "finding_id").get(finding_id)
    )

    return JSONResponse({
        "finding": raw,
        "definition": _read_json(FINDINGS_DIR() / f"{finding_id}.json"),
        "triage": triage_row,
        "exploitability": _jsonl_by(EXPLOIT_JSONL(), "finding_id").get(finding_id),
        "duplicates": _jsonl_by(DUPS_JSONL(), "finding_id").get(finding_id),
        "severity": _jsonl_by(SEV_JSONL(), "finding_id").get(finding_id),
        "runtime_poc": _jsonl_by(RUNTIME_JSONL(), "finding_id").get(finding_id),
        "judge": _normalize_judge(_jsonl_by(JUDGE_JSONL(), "finding_id").get(finding_id)),
        "checklist": _jsonl_by(CHECKLIST_JSONL(), "finding_id").get(finding_id),
        "completeness": _read_json(POC_COMPLETE_DIR() / f"{finding_id}.json"),
        "submission_file": next(
            (p.name for p in SUBMISSIONS_DIR().glob(f"*{finding_id}*.md")), None
        ) if SUBMISSIONS_DIR().exists() else None,
        "upgrade_task_file": next(
            (p.name for p in UPGRADE_TASK_DIR().glob(f"*{finding_id}*upgrade*.md")), None
        ) if UPGRADE_TASK_DIR().exists() else None,
        "poc_file": (lambda: (
            # 1. k2 Rust PoC (integrated_test.rs preferred, then lib.rs)
            next(
                (
                    str(p.relative_to(ROOT))
                    for p in [
                        POC_DIR() / finding_id / "src" / "integrated_test.rs",
                        POC_DIR() / finding_id / "src" / "lib.rs",
                    ]
                    if p.exists()
                ),
                None,
            )
            # 2. Foundry test from poc_result test_file field
            or (lambda tf: str((ROOT / tf).relative_to(ROOT)) if tf and (ROOT / tf).exists() else None)(
                (_read_json(_ap("data/poc_queue") / f"{finding_id}_result.json") or {}).get("test_file", "")
            )
            # 3. Triage poc_test_file (covers Foundry/Enzyme findings with no Rust PoC)
            or (lambda tf: str((ROOT / tf).relative_to(ROOT)) if tf and (ROOT / tf).exists() else None)(
                (triage_row or {}).get("poc_test_file", "")
            )
        ))(),
        "fork_poc_file": _resolve_fork_poc_file(finding_id),
        "source_file": (lambda loc: loc if isinstance(loc, str) else loc.get("file") if isinstance(loc, dict) else None)(
            (_read_json(FINDINGS_DIR() / f"{finding_id}.json") or {}).get("location", "")
        ) or None,
    })


@app.get("/api/status/summary")
def get_status_summary() -> JSONResponse:
    """Compact phone-readable status. Consumed by /status phone command and remote control."""
    try:
        state = _build_state()
        p = state.get("pipeline", {})
        t = state.get("triage_funnel", {})
        findings = state.get("findings", [])

        # current_layer + next_action via Decision Logic (mirrors /api/chat system prompt)
        s1 = p.get("stage_1_static", {})
        s3 = p.get("stage_3_report", {})
        s4 = p.get("stage_4_triage", {})
        s5 = p.get("stage_5_specialist", {})
        s6 = p.get("stage_6_poc", {})
        s7 = p.get("stage_7_checklist", {})
        s8 = p.get("stage_8_gate", {})
        total = s5.get("total_findings", 0)

        layer, last_completed, next_action, next_command = compute_pipeline_layer({
            "static_done":       s1.get("done", False),
            "findings_done":     bool(findings),
            "merged_done":       s3.get("done", False),
            "triage_submit":     t.get("submit", 0),
            "triage_poc":        t.get("poc_required", 0),
            "triage_down":       t.get("downgraded", 0),
            "triage_rej":        t.get("rejected", 0),
            "specialist_done":   max(s5.get("exploitability_done", 0), s5.get("judge_done", 0)),
            "specialist_total":  total,
            "poc_proved":        s6.get("proved", 0),
            "poc_failed":        s6.get("failed", 0),
            "poc_pending":       s6.get("pending", 0),
            "checklist_passed":  s7.get("passed", 0),
            "checklist_total":   s7.get("total", 0),
            "completeness_done": s8.get("total", 0),
            "submission_ready":  len([f for f in findings if f.get("submission_ready")]),
            "blockers":          len([f for f in findings
                                      if f.get("triage_status") == "submit"
                                      and (f.get("upgrade_required")
                                           or f.get("checklist_overall") in ("failed", "block"))]),
        })

        # Top 10 findings sorted by: submit first, then exploitability desc, then severity desc
        _sev = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0}
        def _sort(f: Dict[str, Any]):
            return (
                f.get("triage_status") == "submit",
                f.get("exploitability_score") or 0,
                _sev.get((f.get("severity_ceiling") or f.get("calibrated_severity") or "").lower(), 0),
            )
        top = sorted(findings, key=_sort, reverse=True)[:10]

        blockers = [
            {"id": f["id"], "reason": "upgrade_required" if f.get("upgrade_required") else "checklist_failed"}
            for f in findings
            if f.get("triage_status") == "submit"
            and (f.get("upgrade_required") or f.get("checklist_overall") in ("failed", "block"))
        ]

        submit_ready = [f["id"] for f in findings if f.get("submission_ready")]

        active = state.get("active_audit") or {}
        poc = s6
        return JSONResponse({
            "audit_id":            active.get("audit_id", ""),
            "audit_name":          active.get("name", ""),
            "platform":            active.get("platform", ""),
            "deadline":            active.get("deadline", ""),
            "current_layer":       layer,
            "current_layer_label": ["Not started","Static Analysis","Agent Discovery","Report Generation","Triage","Specialist Review","PoC","Quality Checklist","Completeness Gate","Final Submission"][min(layer, 9)],
            "last_completed":      last_completed,
            "next_action":         next_action,
            "next_command":        next_command,
            "triage": {
                "submit":       t.get("submit", 0),
                "poc_required": t.get("poc_required", 0),
                "downgraded":   t.get("downgraded", 0),
                "rejected":     t.get("rejected", 0),
            },
            "poc": {
                "proved":  poc.get("proved", 0),
                "failed":  poc.get("failed", 0),
                "pending": poc.get("pending", 0),
            },
            "submit_ready_count": len(submit_ready),
            "submit_ready_ids":   submit_ready,
            "blockers":           blockers,
            "top_findings": [
                {
                    "id":               f.get("id"),
                    "title":            f.get("title"),
                    "severity":         f.get("severity_ceiling") or f.get("calibrated_severity") or f.get("raw_severity"),
                    "fallback":         "High" if (f.get("severity_ceiling") or f.get("calibrated_severity") or "").lower() == "critical" else None,
                    "poc_status":       f.get("poc_status"),
                    "judge_verdict":    f.get("predicted_outcome"),
                    "submission_ready": f.get("submission_ready"),
                }
                for f in top
            ],
            "timestamp": state.get("timestamp"),
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


class _ChatRequest(BaseModel):
    messages: list[dict]


@app.post("/api/chat")
async def chat(body: _ChatRequest) -> JSONResponse:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return JSONResponse(
            {"reply": "ANTHROPIC_API_KEY is not set. Set it in your environment and restart the dashboard."},
            status_code=503,
        )
    try:
        import anthropic  # type: ignore
    except ImportError:
        return JSONResponse(
            {"reply": "anthropic package not installed. Run: pip install anthropic"},
            status_code=503,
        )

    state = _build_state()

    # Build a rich description/impact/recommendation index from individual agent output files.
    # These have full text (1000+ chars); merged_findings.json may truncate or omit fields.
    desc_by_id: Dict[str, str] = {}
    impact_by_id: Dict[str, str] = {}
    rec_by_id: Dict[str, str] = {}
    for agent_file in sorted(_ap("output").glob("findings_*.json")):
        data = _read_json(agent_file)
        if not isinstance(data, dict):
            continue
        for f in (data.get("findings") or []):
            fid = f.get("id") or f.get("finding_id")
            if not fid:
                continue
            desc_by_id.setdefault(fid, f.get("description") or "")
            impact_by_id.setdefault(fid, f.get("impact") or "")
            rec_by_id.setdefault(fid, f.get("recommendation") or "")
    # Fill any gaps from merged_findings.json
    merged = _read_json(MERGED_JSON()) or {}
    merged_list = merged.get("findings") if isinstance(merged, dict) else []
    for f in (merged_list or []):
        fid = f.get("id") or f.get("finding_id")
        if fid:
            desc_by_id.setdefault(fid, f.get("description") or "")

    # State findings (already synthesised from triage + merged)
    state_ids: set = {f.get("id") for f in state.get("findings", []) if f.get("id")}

    # Extra findings visible in agent output files but not yet in pipeline state
    extra_findings: List[Dict[str, Any]] = []
    for agent_file in sorted(_ap("output").glob("findings_*.json")):
        data = _read_json(agent_file)
        if not isinstance(data, dict):
            continue
        agent_name = data.get("agent") or agent_file.stem.replace("findings_", "")
        for f in (data.get("findings") or []):
            fid = f.get("id") or f.get("finding_id")
            if fid and fid not in state_ids:
                desc = f.get("description") or ""
                extra_findings.append({
                    "id": fid,
                    "title": f.get("title", fid),
                    "agent": agent_name,
                    "raw_severity": f.get("severity", "Unknown"),
                    "triage_status": "not_triaged",
                    "description": desc[:400] + "…" if len(desc) > 400 else desc,
                })
                state_ids.add(fid)

    # Build findings context with full descriptions
    findings_ctx: List[Dict[str, Any]] = []
    for f in state.get("findings", []):
        fid = f.get("id") or ""
        desc = desc_by_id.get(fid) or ""
        findings_ctx.append({
            "id": fid,
            "title": f.get("title"),
            "agent": f.get("agent"),
            "raw_severity": f.get("raw_severity"),
            "recommended_severity": f.get("recommended_severity"),
            "calibrated_severity": f.get("calibrated_severity"),
            "severity_ceiling": f.get("severity_ceiling"),
            "triage_status": f.get("triage_status"),
            "triage_score": f.get("triage_score"),
            "exploitability_score": f.get("exploitability_score"),
            "duplicate_risk": f.get("duplicate_risk"),
            "poc_status": f.get("poc_status"),
            "poc_level": f.get("poc_level"),
            "checklist_overall": f.get("checklist_overall"),
            "predicted_outcome": f.get("predicted_outcome"),
            "final_action": f.get("final_action"),
            "upgrade_required": f.get("upgrade_required"),
            "description": desc[:400] + "…" if len(desc) > 400 else desc,
        })
    findings_ctx.extend(extra_findings)

    poc_eligible_ids = [
        f["id"] for f in state.get("findings", [])
        if (f.get("exploitability_score") or 0) >= 3
    ]

    # Categorise findings for the prompt summary
    submit_ids  = [f["id"] for f in findings_ctx if f.get("triage_status") == "submit"]
    poc_ids     = [f["id"] for f in findings_ctx if f.get("triage_status") == "poc_required"]
    rej_ids     = [f["id"] for f in findings_ctx if f.get("triage_status") == "rejected"]
    untriaged   = [f["id"] for f in findings_ctx if not f.get("triage_status") or f.get("triage_status") == "not_triaged"]

    # Detailed pipeline state for decision logic
    p = state.get("pipeline", {})
    stage_detail = {
        "static_analysis":  {**p.get("stage_1_static",  {}), "_script": "python tools/static_analysis.py <contract>"},
        "agent_discovery":  {**p.get("stage_2_agents",  {}), "_script": "(spawn agents via Task tool or run individually)"},
        "report_gen":       {**p.get("stage_3_report",  {}), "_script": "python tools/report_generator.py"},
        "triage":           {**p.get("stage_4_triage",  {}), "_script": "python scripts/triage_findings.py  THEN  python scripts/register_pc_findings.py --apply"},
        "specialist_review":{**p.get("stage_5_specialist", {}), "_script": "python scripts/run_specialist_review.py  (or individual scripts)"},
        "poc_execution":    {**p.get("stage_6_poc",     {}), "_script": "generate_poc_plan → generate_poc_test → run_poc_tests (exploit_score>=3 only)"},
        "quality_checklist":{**p.get("stage_7_checklist", {}), "_script": "python scripts/run_quality_checklist.py --all"},
        "completeness_gate":{**p.get("stage_8_gate",    {}), "_script": "python scripts/analyze_poc_completeness.py --all"},
    }

    system = f"""You are the Audit Watch pipeline analyst — an AI assistant embedded in a smart contract security audit dashboard. You drive the audit pipeline forward, explain findings in depth, and give precise, actionable guidance.

AUDIT TARGET: Soroban/Rust DeFi protocol (contest: k2)

═══ PIPELINE STAGES & SCRIPTS ═══

Stage 1 — Static Analysis
  python tools/static_analysis.py <contract>       → output/static.json

Stage 2 — Agent Discovery (8 specialists run in parallel)
  Agents: reentrancy, access_control, arithmetic, oracle, flash_loan, logic, dos, protocol_context
  Each writes to output/findings_<agent>.json

Stage 3 — Report Generation
  python tools/report_generator.py                 → output/merged_findings.json, output/audit_report.md

Stage 4 — Triage
  python scripts/triage_findings.py                → data/triage/submit.jsonl + poc_required.jsonl + rejected.jsonl
  python scripts/register_pc_findings.py --apply   → injects PC findings (protocol_context) into the triage pipeline
  NOTE: Always run register_pc_findings.py after triage — PC findings are generated late and bypass the normal triage flow.

Stage 5 — Specialist Review (run individually or all at once)
  python scripts/run_specialist_review.py           → runs all five below
  python scripts/model_exploitability.py --all      → data/exploitability/models.jsonl  (score 1–5, attacker model, recommended_next_step)
  python scripts/estimate_duplicate_risk.py --all   → data/duplicates/risk.jsonl        (low/medium/high dup risk)
  python scripts/calibrate_severity.py --all        → data/severity/calibrated.jsonl    (conservative severity)
  python scripts/run_integrated_poc.py --all        → data/runtime_poc/results.jsonl    (integrated PoC run)
  python scripts/judge_simulate.py --all            → data/judge_simulation/results.jsonl (predicted judge verdict)

Stage 6 — PoC Generation (ONLY for findings with exploitability_score >= 3)
  python scripts/generate_poc_plan.py --finding-id ID
  python scripts/generate_poc_test.py --finding-id ID --max-repair-attempts 3
  python scripts/run_poc_tests.py --finding-id ID
  ⚠ NEVER suggest PoC commands for findings with exploit_score < 3 — those are downgraded.

Stage 7 — Quality Checklist (after PoC proved)
  python scripts/run_quality_checklist.py --all    → data/quality_checklist/results.jsonl

Stage 8 — Completeness Gate
  python scripts/analyze_poc_completeness.py --all → output/poc_completeness/<ID>.json

Stage 9 — Final Submission
  python scripts/final_submission_pack.py           → output/submission_pack.md

═══ DECISION LOGIC ═══

Use this to decide what to suggest next:

1. stage_1_static.done=False         → python tools/static_analysis.py <contract>
2. stage_3_report.done=False         → python tools/report_generator.py
3. stage_4_triage.done=False         → python scripts/triage_findings.py  THEN  python scripts/register_pc_findings.py --apply
4. exploitability_done < total       → python scripts/model_exploitability.py --all
5. judge_done < total                → python scripts/judge_simulate.py --all
6. severity_done < total             → python scripts/calibrate_severity.py --all
7. duplicate_risk missing for submit/poc findings → python scripts/estimate_duplicate_risk.py --all
8. poc_required findings w/ exploit_score >= 3 and no poc_status → run PoC pipeline per finding
9. After PoC proved                  → python scripts/run_quality_checklist.py --all
10. After checklist                  → python scripts/analyze_poc_completeness.py --all
11. All stages complete              → python scripts/final_submission_pack.py

═══ SCORE GUIDE ═══

Exploitability score (1–5):
  5 = trivially exploitable, immediate fund loss
  4 = exploitable with minimal setup, direct impact
  3 = exploitable under conditions — PoC warranted
  2 = hard to exploit, downgrade recommended — NO PoC
  1 = theoretical only — reject

Triage score (0–35): weighted sum of impact/exploitability/novelty; higher = more actionable
Duplicate risk: low/medium/high — high means another auditor likely already submitted this

═══ FINDING GROUPS ═══

Submit  ({len(submit_ids)} findings — ready to submit): {submit_ids}
PoC req ({len(poc_ids)} findings — need proof first):  {poc_ids}
Rejected ({len(rej_ids)} findings — dropped):           {rej_ids}
Not yet triaged ({len(untriaged)} findings):             {untriaged}

PoC ELIGIBLE (exploit_score >= 3): {poc_eligible_ids}

═══ PIPELINE STATE ═══
{json.dumps(stage_detail, indent=2)}

═══ ALL FINDINGS ({len(findings_ctx)} total, includes unmerged agent findings) ═══
{json.dumps(findings_ctx, indent=2)}

═══ RESPONSE RULES ═══

- Format every runnable command as a fenced code block (```python\\n...\\n```). The dashboard renders a ▶ Run button for any `python scripts/*.py` or `python tools/*.py` command.
- "What should I run next?" → use the Decision Logic above, check the pipeline state, give a prioritized numbered list with commands.
- "Summarize this output" → (1) what the command did and found, (2) warnings/errors, (3) numbered next steps with exact commands.
- "Tell me about finding X" → use the full description + all pipeline data above; explain impact, exploitability, and next steps for that specific finding.
- Never suggest PoC commands for findings not in the PoC ELIGIBLE list.
- Be direct and thorough. No filler text."""

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system,
        messages=body.messages,
    )
    return JSONResponse({"reply": resp.content[0].text})


class _RunRequest(BaseModel):
    command: str


_POC_CMDS = {"generate_poc_plan.py", "generate_poc_test.py", "run_poc_tests.py"}


@app.post("/api/run")
async def run_command(body: _RunRequest) -> JSONResponse:
    cmd = body.command.strip()
    if not any(p.match(cmd) for p in ALLOWED_COMMAND_PATTERNS):
        return JSONResponse({"error": f"Command not in allowlist: {cmd}"}, status_code=403)

    # PoC gate: skip PoC commands for downgraded findings (exploitability_score < 3).
    _fid_match = re.search(r'--finding-id\s+(\S+)', cmd)
    if _fid_match:
        _script = cmd.split()[1].split("/")[-1]
        if _script in _POC_CMDS:
            _fid = _fid_match.group(1)
            _exploit_row = next(
                (r for r in _read_jsonl(EXPLOIT_JSONL()) if r.get("finding_id") == _fid),
                None,
            )
            if _exploit_row:
                _score = _exploit_row.get("exploitability_score", 0) or 0
                _rec   = (_exploit_row.get("recommended_next_step") or "").lower()
                if _score < 3 or _rec == "downgrade":
                    msg = (
                        f"[skip] {_fid}: exploit_score={_score}/5, rec={_rec} — "
                        f"PoC not warranted. Remove this from the queue.\n"
                    )
                    return JSONResponse({"stdout": msg, "stderr": "", "returncode": 0})

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=str(ROOT), timeout=300,
        )
        return JSONResponse({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        })
    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "Timed out after 300s"}, status_code=408)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/log")
def get_log() -> JSONResponse:
    return JSONResponse({"lines": _tail(KB_LOG, 50)})



@app.get("/api/events")
async def sse_events() -> StreamingResponse:
    """Server-Sent Events stream — fires on any output file change."""
    client_q: asyncio.Queue = asyncio.Queue(maxsize=50)
    loop = asyncio.get_event_loop()
    with _sse_lock:
        _sse_clients.append(client_q)

    async def generator():
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(client_q.get(), timeout=30.0)
                    yield msg
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(client_q)
                except ValueError:
                    pass

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )



@app.get("/api/deep-findings")
def get_deep_findings() -> JSONResponse:
    """DT-* and CC-* findings with triage_status: triaged|orphaned."""
    deep = _read_json(DEEP_TRACE_FINDINGS_JSON()) or {"findings": []}
    compound_path = _ap("output") / "findings_compound_synthesis.json"
    compound = _read_json(compound_path) or {"findings": []}
    triage_ids = {
        r.get("finding_id")
        for rows in [
            _read_jsonl(TRIAGE_SUBMIT()),
            _read_jsonl(TRIAGE_POC()),
            _read_jsonl(TRIAGE_DOWN()),
            _read_jsonl(TRIAGE_REJ()),
        ]
        for r in rows
    }
    result = []
    for f in (deep.get("findings") or []) + (compound.get("findings") or []):
        fid = f.get("id") or f.get("finding_id")
        result.append({**f, "triage_status": "triaged" if fid in triage_ids else "orphaned"})
    return JSONResponse({"deep_findings": result, "total": len(result)})


@app.get("/api/chains")
def get_chains() -> JSONResponse:
    """Dangerous call chains and full call graph from interaction analysis."""
    chains = _read_json(DANGEROUS_CHAINS_JSON()) or []
    call_graph = _read_json(CALL_GRAPH_JSON()) or {}
    return JSONResponse({"dangerous_chains": chains, "call_graph": call_graph})


@app.get("/api/invariants")
def get_invariants() -> JSONResponse:
    """All protocol invariants with high_suspicion annotation."""
    inv_raw = _read_json(INVARIANTS_JSON()) or []
    inv_list = inv_raw if isinstance(inv_raw, list) else inv_raw.get("invariants", [])
    susp = _read_json(HIGH_SUSPICION_JSON()) or []
    susp_list = susp if isinstance(susp, list) else susp.get("invariants", [])
    susp_ids = {s.get("invariant_id") for s in susp_list}
    annotated = [
        {**i, "high_suspicion": i.get("invariant_id") in susp_ids}
        for i in inv_list
    ]
    return JSONResponse({"invariants": annotated, "high_suspicion_count": len(susp_ids)})


@app.get("/api/upgrade-task/{finding_id}")
def get_upgrade_task(finding_id: str) -> JSONResponse:
    """Serve the PoC upgrade task markdown for a finding."""
    upgrade_dir = UPGRADE_TASK_DIR()
    if not upgrade_dir.exists():
        raise HTTPException(status_code=404, detail="No upgrade tasks directory")
    candidate = next(upgrade_dir.glob(f"*{finding_id}*.md"), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"No upgrade task for {finding_id}")
    return JSONResponse({
        "finding_id": finding_id,
        "content": candidate.read_text(),
        "filename": candidate.name,
    })


@app.get("/api/mcp-status")
def get_mcp_status() -> JSONResponse:
    """Health check for the three registered MCP servers."""
    import importlib

    def _probe_local(script_rel: str, pkg: str) -> dict:
        path = ROOT / script_rel
        if not path.exists():
            return {"status": "missing", "detail": f"{script_rel} not found"}
        try:
            importlib.import_module(pkg)
            return {"status": "ok", "detail": f"{pkg} importable"}
        except ImportError:
            return {"status": "degraded", "detail": f"{pkg} not installed (pip install {pkg})"}

    def _probe_url(url: str) -> dict:
        try:
            import requests as _req
            r = _req.post(
                url,
                json={"jsonrpc": "2.0", "id": 0, "method": "initialize",
                      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                 "clientInfo": {"name": "dashboard-probe", "version": "1.0"}}},
                headers={"Content-Type": "application/json",
                         "Accept": "application/json, text/event-stream"},
                timeout=5,
            )
            return {"status": "ok", "detail": f"HTTP {r.status_code}"}
        except Exception as exc:
            return {"status": "unreachable", "detail": str(exc)[:120]}

    servers = {
        "onchain-context": _probe_local("tools/onchain_mcp_server.py", "mcp"),
        "kb-search": _probe_local("tools/kb_mcp_server.py", "mcp"),
        "immunefi-audit-competitions": _probe_url("https://reports.immunefi.com/~gitbook/mcp"),
    }
    return JSONResponse({
        "mcp_servers": servers,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/view/report")
def view_report() -> HTMLResponse:
    for candidate in [_ap("output") / "submission_pack.md", _ap("output") / "audit_report.md"]:
        if candidate.exists():
            try:
                text = candidate.read_text(encoding="utf-8")
                body = f"<pre>{_html.escape(text)}</pre>"
                return HTMLResponse(_viewer_page("Audit Report", candidate.name, body))
            except Exception as exc:
                return HTMLResponse(_viewer_page(
                    "Audit Report", "Error",
                    f"<pre>{_html.escape(str(exc))}</pre>",
                ))
    return HTMLResponse(_viewer_page(
        "Audit Report", "Not found",
        "<pre>No report file found.\nRun: python scripts/final_submission_pack.py</pre>",
    ))


@app.get("/view/submission/{finding_id}")
def view_submission(finding_id: str) -> HTMLResponse:
    """Serve the individual per-finding submission markdown for the detail panel Report link."""
    if not SUBMISSIONS_DIR().exists():
        raise HTTPException(status_code=404, detail="Submissions directory not found")
    candidate = next(SUBMISSIONS_DIR().glob(f"*{finding_id}*.md"), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"No submission file for {finding_id}")
    try:
        text = candidate.read_text(encoding="utf-8")
        rel = str(candidate.relative_to(ROOT))
        body = f'<div class="fname">{_html.escape(rel)}</div><pre>{_html.escape(text)}</pre>'

        # Append Foundry .t.sol file if one exists for this finding.
        # Resolution order: poc_result test_file field → pattern match in pocs/foundry/test/
        sol_path: Optional[Path] = None
        poc_result = _read_json(_ap("data/poc_queue") / f"{finding_id}_result.json") or {}
        tf = poc_result.get("test_file", "")
        first_tf = tf.split("+")[0].strip() if tf else ""
        if first_tf:
            p = ROOT / first_tf
            if p.exists() and p.suffix == ".sol":
                sol_path = p
        if sol_path is None and FOUNDRY_TEST_DIR().exists():
            # Strip hyphens from ID for filename matching (CHAIN-001 → CHAIN001)
            id_slug = finding_id.replace("-", "")
            sol_path = next(
                (p for p in FOUNDRY_TEST_DIR().glob("*.t.sol") if id_slug in p.stem),
                None,
            )
        if sol_path is not None:
            sol_text = sol_path.read_text(encoding="utf-8")
            sol_rel = str(sol_path.relative_to(ROOT))
            body += (
                f'<div class="fname" style="margin-top:24px">{_html.escape(sol_rel)}</div>'
                f'<pre>{_html.escape(sol_text)}</pre>'
            )

        return HTMLResponse(_viewer_page(f"Submission — {finding_id}", candidate.name, body))
    except Exception as exc:
        return HTMLResponse(_viewer_page(
            f"Submission — {finding_id}", "Error",
            f"<pre>{_html.escape(str(exc))}</pre>",
        ))


@app.get("/view/poc/{finding_id}")
def view_poc(finding_id: str) -> HTMLResponse:
    poc_base = POC_DIR() / finding_id
    # Build candidate list: k2 Rust first, then Foundry test from poc_result
    candidates: list[Path] = [
        poc_base / "src" / "integrated_test.rs",
        poc_base / "src" / "lib.rs",
    ]
    poc_result = _read_json(_ap("data/poc_queue") / f"{finding_id}_result.json") or {}
    tf = poc_result.get("test_file", "")
    # test_file may be a compound string like "fileA.sol + fileB.sol" — take the first
    first_tf = tf.split("+")[0].strip() if tf else ""
    if first_tf:
        candidates.append(ROOT / first_tf)
    # Fall back to triage poc_test_file (covers Foundry/Enzyme findings with no Rust PoC)
    triage_poc_tf = (
        _jsonl_by(TRIAGE_SUBMIT(), "finding_id").get(finding_id)
        or _jsonl_by(TRIAGE_POC(), "finding_id").get(finding_id)
        or {}
    ).get("poc_test_file") or ""
    if triage_poc_tf:
        candidates.append(ROOT / triage_poc_tf)

    for candidate in candidates:
        if candidate.exists():
            try:
                text = candidate.read_text(encoding="utf-8")
                rel = str(candidate.relative_to(ROOT))
                body = (
                    f'<div class="fname">{_html.escape(rel)}</div>'
                    f"<pre>{_html.escape(text)}</pre>"
                )
                return HTMLResponse(_viewer_page(f"PoC — {finding_id}", candidate.name, body))
            except Exception as exc:
                return HTMLResponse(_viewer_page(
                    f"PoC — {finding_id}", "Error",
                    f"<pre>{_html.escape(str(exc))}</pre>",
                ))
    return HTMLResponse(_viewer_page(
        f"PoC — {finding_id}", "Not found",
        f"<pre>No PoC file found for {_html.escape(finding_id)}.\n"
        f"Run generate_poc_plan.py and generate_poc_test.py first.</pre>",
    ))


@app.get("/view/fork-poc/{finding_id}")
def view_fork_poc(finding_id: str) -> HTMLResponse:
    """Serve the Foundry fork test (.t.sol) linked to this finding."""
    rel = _resolve_fork_poc_file(finding_id)
    if rel is None:
        return HTMLResponse(_viewer_page(
            f"Fork PoC — {finding_id}", "Not found",
            f"<pre>No fork test file found for {_html.escape(finding_id)}.\n"
            f"Check chain_test_file / poc_test_file in data/triage/submit.jsonl.</pre>",
        ))
    candidate = ROOT / rel
    try:
        text = candidate.read_text(encoding="utf-8")
        body = (
            f'<div class="fname">{_html.escape(rel)}</div>'
            f"<pre>{_html.escape(text)}</pre>"
        )
        return HTMLResponse(_viewer_page(f"Fork PoC — {finding_id}", candidate.name, body))
    except Exception as exc:
        return HTMLResponse(_viewer_page(
            f"Fork PoC — {finding_id}", "Error",
            f"<pre>{_html.escape(str(exc))}</pre>",
        ))


@app.get("/view/source/{finding_id}")
def view_source(finding_id: str) -> HTMLResponse:
    """Serve the vulnerable contract source file linked to this finding."""
    defn = _read_json(FINDINGS_DIR() / f"{finding_id}.json") or {}
    loc = defn.get("location", "")
    # location may be "path/to/File.sol", "path/to/File.sol:123", or a dict with "file" key
    if isinstance(loc, dict):
        loc = loc.get("file", "")
    # Strip trailing :line or :line-range
    file_path_str = loc.split(":")[0].strip() if loc else ""
    if not file_path_str:
        raise HTTPException(status_code=404, detail=f"No source file location for {finding_id}")
    candidate = ROOT / file_path_str
    if not candidate.exists():
        raise HTTPException(status_code=404, detail=f"Source file not found: {file_path_str}")
    try:
        text = candidate.read_text(encoding="utf-8")
        body = f'<div class="fname">{_html.escape(file_path_str)}</div><pre>{_html.escape(text)}</pre>'
        return HTMLResponse(_viewer_page(f"Source — {candidate.name}", candidate.name, body))
    except Exception as exc:
        return HTMLResponse(_viewer_page(
            f"Source — {finding_id}", "Error",
            f"<pre>{_html.escape(str(exc))}</pre>",
        ))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(INDEX_HTML), headers={"Cache-Control": "no-store"})


if DASH_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASH_DIR)), name="static")


# --------------------------------------------------------------------- launch
if __name__ == "__main__":
    import uvicorn

    URL = "http://localhost:8765"

    def _open() -> None:
        time.sleep(1.5)
        # WSL2: use cmd.exe to open in Windows browser; fall back to webbrowser.
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", "start", URL],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        try:
            webbrowser.open(URL)
        except Exception:
            pass

    print(f"Audit Watch dashboard — {URL}", file=sys.stderr)
    threading.Thread(target=_open, daemon=True).start()

    def _start_file_watcher() -> None:
        """Watch output directories; broadcast SSE state_changed event on any change."""
        try:
            from watchfiles import watch
        except ImportError:
            return

        def _watch_loop():
            watch_dirs = []
            for sub in [
                "output", "data/triage", "data/exploitability",
                "data/severity", "data/runtime_poc",
                "data/judge_simulation", "data/quality_checklist",
            ]:
                p = _ap(sub)
                try:
                    p.mkdir(parents=True, exist_ok=True)
                    watch_dirs.append(str(p))
                except Exception:
                    pass
            if not watch_dirs:
                return
            try:
                for changes in watch(*watch_dirs):
                    _broadcast_event("state_changed", {
                        "files": [str(c[1]) for c in changes],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception:
                pass

        threading.Thread(target=_watch_loop, daemon=True, name="sse-watcher").start()

    _start_file_watcher()
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="warning")
