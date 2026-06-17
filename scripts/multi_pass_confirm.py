#!/usr/bin/env python3
"""
multi_pass_confirm.py — Multi-pass confirmation for High/Critical findings.

Reads output/findings_*.json, identifies High and Critical findings,
re-runs the relevant specialist agent's reasoning via Claude API N times
(3 for High, 5 for Critical per config), computes confirmation_score,
and routes findings below threshold to human review.

Adds to each confirmed finding:
  confirmation_passes     — number of YES confirmations
  confirmation_score      — float 0.0–1.0
  human_review_required   — true if score < threshold
  human_review_reason     — explanation string

Writes: output/findings_confirmed.json
Does NOT modify original output/findings_*.json files.

Usage:
    python scripts/multi_pass_confirm.py
    python scripts/multi_pass_confirm.py --finding-id RE-001
    python scripts/multi_pass_confirm.py --force   # ignore cached results
"""

import argparse
import glob
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from audit_context import audit_path

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

MODEL = "claude-sonnet-4-6"
TARGET_SEVERITIES = {"High", "Critical"}

# ─────────────────────────────────────────────────────────────────────────────
# Tool-use setup (KB precedent lookup before confirmation passes)
# ─────────────────────────────────────────────────────────────────────────────

_TOOLS_DIR = REPO_ROOT / "tools"

RETRIEVER_TOOLS = [
    {
        "name": "search_kb",
        "description": (
            "Search the Solodit/Code4rena/Sherlock knowledge base for audit findings "
            "similar to the finding being confirmed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vuln_type": {
                    "type": "string",
                    "enum": [
                        "reentrancy", "access-control", "arithmetic",
                        "oracle-manipulation", "flash-loan", "logic-error",
                        "dos", "other",
                    ],
                },
                "query": {"type": "string"},
            },
            "required": ["vuln_type", "query"],
        },
    },
    {
        "name": "search_immunefi",
        "description": (
            "Search the Immunefi bug-bounty report database for precedents matching "
            "the vulnerability pattern being confirmed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vuln_type": {"type": "string"},
                "query": {"type": "string"},
            },
            "required": ["vuln_type", "query"],
        },
    },
]


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_kb":
        cmd = [
            sys.executable,
            str(_TOOLS_DIR / "retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    else:  # search_immunefi
        cmd = [
            sys.executable,
            str(_TOOLS_DIR / "immunefi_retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else "[]"
    except Exception as e:
        return f"[]  # tool error: {e}"


def _fetch_kb_precedents(client, finding: dict) -> str:
    """Run a single tool-use call to gather KB precedents before confirmation passes."""
    vuln_type = finding.get("vuln_type", "other")
    title = finding.get("title", "")
    desc = (finding.get("description", "") or "")[:200]

    pre_prompt = (
        f"I need to confirm a smart contract finding. Before answering, search for "
        f"precedents using search_kb and search_immunefi. Then summarize what you found "
        f"in 2-3 sentences — are there known examples of this pattern?\n\n"
        f"Finding title: {title}\n"
        f"vuln_type: {vuln_type}\n"
        f"Description: {desc}\n\n"
        f"After searching, reply with only your 2-3 sentence precedent summary."
    )

    messages: list[dict] = [{"role": "user", "content": pre_prompt}]
    for _ in range(4):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=512,
                tools=RETRIEVER_TOOLS,
                messages=messages,
            )
        except Exception:
            return ""

        if resp.stop_reason == "end_turn":
            for block in resp.content:
                if hasattr(block, "text"):
                    return block.text.strip()
            return ""

        if resp.stop_reason == "tool_use":
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    kb_result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": kb_result,
                    })
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return ""


def load_config() -> dict:
    policy_path = REPO_ROOT / "config" / "agent_policy.json"
    if policy_path.exists():
        cfg = json.loads(policy_path.read_text())
        return cfg
    return {}


def load_agent_spec(agent_name: str) -> str:
    spec_path = REPO_ROOT / "agents" / f"{agent_name}.md"
    if spec_path.exists():
        return spec_path.read_text()
    return f"You are a smart contract security specialist focused on {agent_name} vulnerabilities."


def load_code_snippet(finding: dict) -> str:
    code = finding.get("location", {}).get("code_snippet", "")
    if code:
        return code
    static_path = audit_path("output") / "static.json"
    if not static_path.exists():
        return ""
    try:
        static = json.loads(static_path.read_text())
        func_name = finding.get("location", {}).get("function", "")
        for fn in static.get("functions", []):
            if fn.get("name") == func_name:
                return fn.get("source", "")[:1500]
    except Exception:
        pass
    return ""


def confirm_finding(client, finding: dict, agent_spec: str, n_passes: int, threshold: float) -> dict:
    finding_id = finding.get("id", "unknown")
    severity = finding.get("severity", "")
    code_snippet = load_code_snippet(finding)

    finding_context = json.dumps({
        "id": finding_id,
        "title": finding.get("title", ""),
        "severity": severity,
        "description": finding.get("description", ""),
        "location": finding.get("location", {}),
        "impact": finding.get("impact", ""),
        "ite": finding.get("ite", {}),
    }, indent=2)

    # Fetch KB precedents once before running confirmation passes
    kb_context = _fetch_kb_precedents(client, finding)

    prompt = (
        f"You are a smart contract security expert performing an independent review.\n\n"
        f"Re-examine the following finding independently. Given the code context and finding details, "
        f"is this vulnerability real and exploitable as described?\n\n"
        f"Answer YES with a one-line justification, or NO with the specific reason it is a false positive.\n\n"
        f"Finding:\n{finding_context}\n"
    )
    if code_snippet:
        prompt += f"\nCode context:\n```solidity\n{code_snippet}\n```\n"
    if kb_context:
        prompt += f"\nKnowledge base precedents:\n{kb_context}\n"

    yes_count = 0
    total_passes = n_passes

    for pass_num in range(n_passes):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.content[0].text.strip()
            first_word = answer[:150].upper()
            if first_word.startswith("YES"):
                yes_count += 1
        except Exception as e:
            print(f"  Pass {pass_num + 1}/{n_passes}: API error — {e}", file=sys.stderr)
            return {
                **finding,
                "confirmation_passes": 0,
                "confirmation_score": 0.0,
                "human_review_required": True,
                "human_review_reason": f"confirmation_api_error: {e}",
            }

        # Brief pause between passes to avoid rate limiting
        if pass_num < n_passes - 1:
            time.sleep(0.5)

    score = yes_count / total_passes
    human_required = score < threshold
    reason = ""
    if human_required:
        reason = (
            f"confirmation_score={score:.2f} < threshold={threshold:.2f} "
            f"({yes_count}/{total_passes} passes confirmed)"
        )

    return {
        **finding,
        "confirmation_passes": yes_count,
        "confirmation_score": round(score, 3),
        "human_review_required": human_required,
        "human_review_reason": reason,
    }


def load_high_critical_findings(finding_id_filter: str | None) -> list[tuple[str, dict]]:
    output_dir = audit_path("output")
    results = []
    for findings_file in sorted(output_dir.glob("findings_*.json")):
        if "confirmed" in findings_file.name:
            continue
        try:
            data = json.loads(findings_file.read_text())
        except Exception:
            continue
        agent = data.get("agent", "unknown")
        for finding in data.get("findings", []):
            if finding.get("severity") not in TARGET_SEVERITIES:
                continue
            if finding_id_filter and finding.get("id") != finding_id_filter:
                continue
            results.append((agent, finding))
    return results


def load_cached_confirmed(force: bool) -> dict:
    if force:
        return {}
    confirmed_path = audit_path("output") / "findings_confirmed.json"
    if not confirmed_path.exists():
        return {}
    try:
        data = json.loads(confirmed_path.read_text())
        return {f["id"]: f for f in data.get("findings", []) if "confirmation_score" in f}
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser(description="Multi-pass confirmation for High/Critical findings")
    parser.add_argument("--finding-id", help="Confirm a single finding by ID")
    parser.add_argument("--force", action="store_true", help="Ignore cached results")
    args = parser.parse_args()

    cfg = load_config()
    active_mode = cfg.get("active_mode", "normal")
    mp = cfg.get("multi_pass", {})

    if active_mode == "fast":
        print("Skipping multi-pass confirm (fast mode)")
        return

    if not mp.get("enabled", True):
        print("Multi-pass confirmation is disabled in config/agent_policy.json")
        return

    passes_high = mp.get("passes_high", 3)
    passes_critical = mp.get("passes_critical", 5)
    threshold = mp.get("confirmation_threshold", 0.6)

    from llm_runtime import optional_llm
    client = optional_llm("multi_pass_confirm") if HAS_ANTHROPIC else None
    if client is None:
        # Optional enhancer: no key (or SDK) → skip confirmation and continue. High/Critical
        # findings keep their pre-confirmation severity; merged_findings.json + /triage carry the run.
        confirmed_path = audit_path("output") / "findings_confirmed.json"
        confirmed_path.write_text(json.dumps({
            "agent": "multi_pass_confirm",
            "skipped": True,
            "reason": "no ANTHROPIC_API_KEY (or anthropic SDK) — confirmation skipped (optional stage)",
            "findings": [],
        }, indent=2))
        print("Skipped multi-pass confirmation (no API key) — continuing; "
              "High/Critical findings retain pre-confirmation severity.")
        return

    findings_to_check = load_high_critical_findings(args.finding_id)
    if not findings_to_check:
        msg = f"No High/Critical findings found"
        if args.finding_id:
            msg += f" with ID {args.finding_id}"
        print(msg)
        return

    cached = load_cached_confirmed(args.force)
    confirmed_findings = []
    new_count = 0
    cached_count = 0

    print(f"\nMulti-pass confirmation — {len(findings_to_check)} finding(s) to check")
    print(f"  Passes: High={passes_high}, Critical={passes_critical}, Threshold={threshold:.0%}\n")
    print(f"{'ID':<12} {'Severity':<10} {'Title':<40} {'Score':<8} {'Status'}")
    print("-" * 90)

    for agent_name, finding in findings_to_check:
        fid = finding.get("id", "?")
        sev = finding.get("severity", "?")
        title = finding.get("title", "")[:38]

        if fid in cached and not args.force:
            enriched = cached[fid]
            cached_count += 1
            score = enriched.get("confirmation_score", 0)
            status = "✓ cached"
        else:
            n_passes = passes_critical if sev == "Critical" else passes_high
            agent_spec = load_agent_spec(agent_name)
            enriched = confirm_finding(client, finding, agent_spec, n_passes, threshold)
            new_count += 1
            score = enriched.get("confirmation_score", 0)
            status = "✅ confirmed" if not enriched.get("human_review_required") else "⚠️  human review"
            try:
                from viz.event_emitter import emit as _viz_emit
                _viz_emit("CONFIDENCE_SHIFT", source_agent="multi_pass_confirm",
                          target_node_id=fid, payload={
                              "old_confidence": 0.5,
                              "new_confidence": score,
                              "reason": f"Multi-pass confirmation: {n_passes} passes",
                              "calibrated_severity": sev,
                              "human_review_required": enriched.get("human_review_required", False),
                          })
            except Exception:
                pass

        confirmed_findings.append(enriched)
        score_str = f"{score:.2f}"
        print(f"{fid:<12} {sev:<10} {title:<40} {score_str:<8} {status}")

    output = {
        "agent": "multi_pass_confirm",
        "contract": str(audit_path("output")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "findings": confirmed_findings,
    }

    confirmed_path = audit_path("output") / "findings_confirmed.json"
    confirmed_path.write_text(json.dumps(output, indent=2))

    human_required = sum(1 for f in confirmed_findings if f.get("human_review_required"))
    confirmed_ok = len(confirmed_findings) - human_required

    print(f"\nSummary: {confirmed_ok} confirmed ✅  |  {human_required} flagged for human review ⚠️")
    print(f"  New: {new_count}  |  Cached: {cached_count}")
    print(f"  Written to: {confirmed_path}")

    if human_required:
        print(f"\n⚠️  Run /human-queue or `python scripts/human_review_classifier.py` to route flagged findings.")


if __name__ == "__main__":
    main()
