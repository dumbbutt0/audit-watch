#!/usr/bin/env python3
"""
escalate_threads.py — Thread escalation layer.

Reads data/threads/promising_threads.jsonl and converts each thread with
escalate=true into a structured finding that enters the existing pipeline.

For each thread:
  1. Selects the appropriate specialist agent prompt based on invariant category
  2. Calls Claude to convert the thread into a full finding
  3. Spawns additional Claude calls for each escalation_angle in the thread
  4. Picks the strongest finding output
  5. Writes to output/findings_deep_trace.json

Usage:
    python scripts/escalate_threads.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import anthropic
import subprocess as _primitives_sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT = Path(__file__).resolve().parent.parent
THREADS_DIR      = audit_path("data/threads")
INVARIANTS_DIR   = audit_path("data/invariants")
INTERACTIONS_DIR = audit_path("data/interactions")
AGENTS_DIR       = ROOT / "agents"
PROMPTS_DIR      = ROOT / "prompts"
STATIC_JSON      = audit_path("output") / "static.json"
PROMISING_THREADS = audit_path("data/threads") / "promising_threads.jsonl"
OUT_FILE          = audit_path("output") / "findings_deep_trace.json"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}

# Map invariant category → specialist agent file
CATEGORY_TO_AGENT = {
    "ACCOUNTING": "agents/logic.md",
    "SOLVENCY": "agents/flash_loan.md",
    "STATE_MACHINE": "agents/multi_tx_agent.md",
    "ACCESS": "agents/access_control.md",
    "ARITHMETIC": "agents/arithmetic.md",
    "CROSS_CONTRACT": "agents/reentrancy.md",
    # Thread-ID-prefix-based routing for backward and multi-tx threads
    "_BT": "agents/logic.md",
    "_MT": "agents/multi_tx_agent.md",
}

VERDICT_TO_SEVERITY = {
    "CRITICAL_THREAD": "Critical",
    "HIGH_THREAD": "High",
    "MEDIUM_THREAD": "Medium",
    # Backward trace verdicts
    "CRITICAL_BACKWARD": "Critical",
    "HIGH_BACKWARD": "High",
    "MEDIUM_BACKWARD": "Medium",
    # Multi-transaction verdicts
    "CRITICAL_MULTITX": "Critical",
    "HIGH_MULTITX": "High",
    "MEDIUM_MULTITX": "Medium",
}

VERDICT_TO_CONFIDENCE = {
    "CRITICAL_THREAD": "High",
    "HIGH_THREAD": "High",
    "MEDIUM_THREAD": "Medium",
    "CRITICAL_BACKWARD": "High",
    "HIGH_BACKWARD": "High",
    "MEDIUM_BACKWARD": "Medium",
    "CRITICAL_MULTITX": "High",
    "HIGH_MULTITX": "High",
    "MEDIUM_MULTITX": "Medium",
}

ESCALATION_SYSTEM = """\
You are a smart contract security auditor. You receive a deep trace thread result
showing a potential invariant violation path. Your job is to convert it into a
complete finding conforming to the project's findings schema.

Return valid JSON with these fields:
{
  "title": "One-line summary (max 80 chars)",
  "severity": "Critical|High|Medium|Low|Informational",
  "vuln_type": "reentrancy|access-control|arithmetic|oracle-manipulation|flash-loan|logic-error|gas-griefing|dos|front-running|price-manipulation|other",
  "description": "Full explanation: what it is, why it exists, what an attacker can do",
  "location": {
    "file": "contract file path",
    "function": "vulnerable function name",
    "line_start": null,
    "code_snippet": "the exact vulnerable lines"
  },
  "impact": "Concrete worst-case outcome",
  "proof_of_concept": "Attack scenario or test skeleton demonstrating exploitability",
  "recommendation": "Specific actionable fix",
  "confidence": "High|Medium|Low"
}

If you cannot construct a valid finding (the thread is inconclusive or missing data),
return {"error": "reason why"}.
"""


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


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _load_source_for_functions(funcs: list[str]) -> dict[str, str]:
    """Load source excerpts for the named functions by scanning contracts/."""
    excerpts: dict[str, str] = {}
    func_names = {f.split(".")[-1] for f in funcs if f}

    candidates = []
    for candidate in ["contracts", "src"]:
        p = ROOT / candidate
        if p.is_dir():
            for ext in CONTRACT_EXTENSIONS:
                candidates.extend(p.rglob(f"*{ext}"))

    static = _load_json(STATIC_JSON)
    if isinstance(static, dict):
        cp = static.get("contract_path")
        if cp:
            p = ROOT / cp
            if p.is_file() and p.suffix in CONTRACT_EXTENSIONS:
                candidates.append(p)

    for p in candidates:
        try:
            source = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = source.splitlines()
        for fn in func_names:
            for i, line in enumerate(lines):
                if fn in line and ("fn " in line or "function " in line):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 40)
                    key = f"{p.name}::{fn}"
                    excerpts[key] = "\n".join(lines[start:end])
    return excerpts


def _agent_prompt_for_category(category: str, thread_id: str = "") -> str:
    # Route by thread ID prefix first (MT-* and BT-* override category)
    if thread_id.startswith("MT-"):
        agent_rel = CATEGORY_TO_AGENT.get("_MT", "agents/multi_tx_agent.md")
    elif thread_id.startswith("BT-"):
        agent_rel = CATEGORY_TO_AGENT.get("_BT", "agents/logic.md")
    else:
        agent_rel = CATEGORY_TO_AGENT.get(category, "agents/logic.md")
    agent_path = ROOT / agent_rel
    if agent_path.exists():
        return agent_path.read_text(encoding="utf-8")
    return ESCALATION_SYSTEM


def _call_claude(system_prompt: str, user_content: str) -> str:
    import uuid as _uuid
    from datetime import datetime as _dt, timezone as _tz
    messages = [{"role": "user", "content": user_content}]
    client = require_llm(skill="deep_analysis")
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=messages,
    )
    try:
        from viz.intercept.cassette import CassetteRecorder
        CassetteRecorder(os.environ.get("VIZ_SESSION_ID", "")).record_llm_call(
            call_id=str(_uuid.uuid4()), agent="escalate_threads", model=MODEL,
            messages=messages, response=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            timestamp=_dt.now(_tz.utc).isoformat(),
        )
    except Exception:
        pass
    return response.content[0].text


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        return {}
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def _finding_completeness(finding: dict) -> int:
    """Score a finding by how concrete/complete it is (higher = better)."""
    score = 0
    if finding.get("title"):
        score += 1
    if finding.get("description") and len(finding["description"]) > 50:
        score += 2
    if finding.get("proof_of_concept") and len(finding.get("proof_of_concept", "")) > 30:
        score += 3
    if finding.get("location", {}).get("function"):
        score += 1
    if finding.get("recommendation") and len(finding.get("recommendation", "")) > 20:
        score += 1
    return score


def _escalate_thread(thread: dict, thread_idx: int) -> dict | None:
    thread_id = thread.get("thread_id", f"DT-{thread_idx:03d}")
    inv_id = thread.get("invariant_id", "")
    chain_id = thread.get("chain_id", "")
    verdict = thread.get("verdict", "")

    # Determine category from invariant_id prefix
    inv_prefix = inv_id.split("-")[0] if inv_id else ""
    prefix_to_cat = {
        "ACC": "ACCOUNTING", "SOL": "SOLVENCY", "STATE": "STATE_MACHINE",
        "ACCESS": "ACCESS", "ARITH": "ARITHMETIC", "CROSS": "CROSS_CONTRACT",
    }
    category = prefix_to_cat.get(inv_prefix, "ACCOUNTING")

    # Load invariant for category info
    invariants = _load_json(INVARIANTS_DIR / "protocol_invariants.json") or []
    for inv in invariants:
        if inv.get("invariant_id") == inv_id:
            category = inv.get("category", category)
            break

    # Load source excerpts for violation path functions
    violation_funcs = thread.get("violation_path", []) + [
        hop.get("function", "") for hop in thread.get("hop_traces", [])
    ]
    excerpts = _load_source_for_functions(violation_funcs)

    agent_system = _agent_prompt_for_category(category, thread_id)

    # Fetch relevant attack primitives for extra context
    _prim_cat = {
        "ACCOUNTING": "logic-error", "SOLVENCY": "flash-loan",
        "ACCESS": "access-control", "ARITHMETIC": "arithmetic",
        "CROSS_CONTRACT": "reentrancy", "STATE_MACHINE": "logic-error",
    }.get(category, "")
    _primitives_ctx = "[]"
    if _prim_cat:
        try:
            _pr = _primitives_sp.run(
                [sys.executable, str(ROOT / "tools" / "primitives_retriever.py"), _prim_cat],
                capture_output=True, text=True, timeout=10,
            )
            if _pr.returncode == 0 and _pr.stdout.strip():
                _primitives_ctx = _pr.stdout.strip()
        except Exception:
            pass

    user_task = (
        "Convert this deep trace thread into a full security finding. "
        "Write the title, description, impact, proof_of_concept (as a numbered attack sequence), "
        "and recommendation. If you cannot construct a valid PoC, explain exactly why.\n\n"
        f"Thread JSON:\n{json.dumps(thread, indent=2, ensure_ascii=False)}\n\n"
        f"Relevant source excerpts:\n{json.dumps(excerpts, indent=2, ensure_ascii=False)}\n\n"
        f"Attack primitives for this category ({_prim_cat}):\n{_primitives_ctx}"
    )

    candidates: list[dict] = []

    # Main escalation call
    print(f"    Escalating {thread_id} ({verdict}) …", end="", flush=True)
    try:
        raw = _call_claude(ESCALATION_SYSTEM, user_task)
        finding = _extract_json_object(raw)
        if finding and not finding.get("error"):
            candidates.append(finding)
            print(f" got finding", end="")
        else:
            print(f" no finding", end="")
    except Exception as e:
        print(f" ERROR: {e}", end="")

    # Escalation angle calls
    angles = thread.get("escalation_angles", [])
    angle_count = 0
    for angle in angles[:3]:  # Limit to 3 angles per thread
        angle_task = (
            f"Explore this specific angle for the deep trace thread below:\n\n"
            f"ANGLE: {angle}\n\n"
            f"Thread JSON:\n{json.dumps(thread, indent=2, ensure_ascii=False)}\n\n"
            f"Source excerpts:\n{json.dumps(excerpts, indent=2, ensure_ascii=False)}\n\n"
            "Return a full finding JSON or {\"error\": \"reason\"} if inconclusive."
        )
        try:
            raw = _call_claude(ESCALATION_SYSTEM, angle_task)
            af = _extract_json_object(raw)
            if af and not af.get("error"):
                candidates.append(af)
                angle_count += 1
        except Exception:
            pass

    print(f" ({angle_count} angle(s))")

    if not candidates:
        return None

    # Pick strongest candidate by completeness score
    best = max(candidates, key=_finding_completeness)

    # Determine depth from hop_traces
    trace_depth = len(thread.get("hop_traces", []))

    # Build the final finding
    finding_id = thread_id  # DT-001, DT-002, …
    severity = best.get("severity") or VERDICT_TO_SEVERITY.get(verdict, "Medium")
    confidence = best.get("confidence") or VERDICT_TO_CONFIDENCE.get(verdict, "Medium")

    final = {
        "id": finding_id,
        "title": (best.get("title") or f"Deep trace: {inv_id} × {chain_id}")[:80],
        "severity": severity,
        "vuln_type": best.get("vuln_type") or "logic-error",
        "description": best.get("description") or thread.get("entry_conditions") or "",
        "location": best.get("location") or {"file": "unknown", "function": "unknown"},
        "impact": best.get("impact") or thread.get("profit_or_damage") or "",
        "proof_of_concept": best.get("proof_of_concept") or "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(thread.get("violation_path", []))
        ),
        "recommendation": best.get("recommendation") or "",
        "confidence": confidence,
        # Deep trace extension fields
        "invariant_violated": inv_id,
        "thread_id": thread_id,
        "interaction_chain_id": chain_id,
        "trace_depth": trace_depth,
    }

    return final


def main() -> int:
    import argparse as _ap
    _parser = _ap.ArgumentParser(description="Escalate promising threads to findings")
    _parser.add_argument("--include-soft", action="store_true",
                         help="Also escalate soft-flag (score-3 pass) threads")
    _args = _parser.parse_args()

    OUT_FILE.parent.mkdir(exist_ok=True)

    print("Thread Escalation — Converting promising threads to findings")

    threads = _load_jsonl(PROMISING_THREADS)
    if not threads:
        print("  No promising threads found. Run deep_trace.py first.")
        # Write empty findings file so report_generator.py still works
        out = {
            "agent": "deep_trace",
            "contract": "various",
            "findings": [],
        }
        OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    # Soft-flag threads are not escalated by default; use --include-soft to override
    soft_count = sum(1 for t in threads if t.get("soft_flag"))
    if not _args.include_soft and soft_count:
        threads = [t for t in threads if not t.get("soft_flag")]
        print(f"  Skipped {soft_count} soft-flag thread(s) (use --include-soft to escalate)")

    to_escalate = [t for t in threads if t.get("escalate", False)]
    print(f"  Threads to escalate: {len(to_escalate)} of {len(threads)} promising")

    findings = []
    angles_explored = 0

    for idx, thread in enumerate(to_escalate, 1):
        print(f"\n  [{idx}/{len(to_escalate)}]", end=" ")
        # ── viz: emit AGENT_SPAWNED before Claude call ────────────────────────
        try:
            from viz.event_emitter import emit as _viz_emit
            _viz_emit("AGENT_SPAWNED", source_agent="escalate_threads",
                      target_node_id=thread.get("thread_id"), payload={
                          "thread_id": thread.get("thread_id", ""),
                          "invariant_id": thread.get("invariant_id", ""),
                          "branch_trigger": thread.get("verdict", "promising_thread"),
                          "spawned_agent": CATEGORY_TO_AGENT.get(
                              thread.get("category", ""), "agents/logic.md"),
                      })
        except Exception:
            pass
        finding = _escalate_thread(thread, idx)
        if finding:
            findings.append(finding)
            angles_explored += len(thread.get("escalation_angles", []))

    # Write output in standard agent output shape
    out = {
        "agent": "deep_trace",
        "contract": "various",
        "findings": findings,
    }
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"\n  Results:")
    print(f"    Threads escalated: {len(to_escalate)}")
    print(f"    Findings generated: {len(findings)}")
    print(f"    Escalation angles explored: {angles_explored}")
    print(f"\n  Output: {OUT_FILE}")
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
