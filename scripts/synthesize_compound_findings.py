#!/usr/bin/env python3
"""
synthesize_compound_findings.py — Compound finding synthesis.

Reads all output/findings_*.json files after specialist agents complete,
evaluates pairs of findings against known compound vulnerability patterns,
and generates CC-NNN compound findings where combinations enable higher-
severity exploits than either component alone.

Usage:
    python scripts/synthesize_compound_findings.py
    python scripts/synthesize_compound_findings.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import optional_llm  # graceful no-key skip (this is an optional enhancer stage)

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
OUT_FILE = audit_path("output") / "findings_compound_synthesis.json"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

# Compound pattern table.  Each entry:
#   pattern_id, component_vuln_types (required), severity_ceiling, description
COMPOUND_PATTERNS = [
    {
        "pattern_id": "COMP-A",
        "name": "Oracle Manipulation + Sandwich",
        "required_types": [
            {"oracle-manipulation", "price-manipulation"},
            {"flash-loan", "front-running"},
        ],
        "severity_ceiling": "Critical",
        "description": (
            "Flash loan manipulates spot price; sandwich extracts value from the protocol's "
            "own AMM-dependent function in the same transaction."
        ),
    },
    {
        "pattern_id": "COMP-B",
        "name": "Reentrancy + Snapshot",
        "required_types": [
            {"reentrancy"},
            {"logic-error", "arithmetic"},  # snapshot category
        ],
        "severity_ceiling": "Critical",
        "description": (
            "Reenter during a balance read used for voting power or reward calculation, "
            "reading a stale (inflated) balance."
        ),
    },
    {
        "pattern_id": "COMP-C",
        "name": "Fee-on-Transfer + Lending Borrow",
        "required_types": [
            {"logic-error"},  # TI-* fee-on-transfer
            {"logic-error", "arithmetic"},  # any lending borrow function
        ],
        "required_agent_prefixes": [["TI"], None],
        "severity_ceiling": "High",
        "description": (
            "Repay credits the argument amount but receives less due to transfer fee; "
            "bad debt grows on each repayment cycle."
        ),
    },
    {
        "pattern_id": "COMP-D",
        "name": "Fee-on-Transfer + Reward Accounting",
        "required_types": [
            {"logic-error"},  # TI-* fee-on-transfer
            {"logic-error", "arithmetic"},  # reward accounting
        ],
        "required_agent_prefixes": [["TI"], ["EA"]],
        "severity_ceiling": "High",
        "description": (
            "Each deposit over-credits reward shares due to transfer fee; "
            "attacker drains yield pool incrementally."
        ),
    },
    {
        "pattern_id": "COMP-E",
        "name": "Rebasing Token + Collateral/Liquidation",
        "required_types": [
            {"logic-error"},  # TI-* rebasing
            {"logic-error", "oracle-manipulation"},
        ],
        "required_agent_prefixes": [["TI"], None],
        "severity_ceiling": "High",
        "description": (
            "Negative rebase drops all collateral values simultaneously; "
            "triggers mass insolvency across all borrowers."
        ),
    },
    {
        "pattern_id": "COMP-F",
        "name": "DoS + Governance Quorum",
        "required_types": [
            {"dos", "gas-griefing"},
            {"logic-error", "access-control"},
        ],
        "severity_ceiling": "High",
        "description": (
            "Block the governance contract's vote function to prevent quorum, "
            "freezing protocol upgrades or emergency actions indefinitely."
        ),
    },
    {
        "pattern_id": "COMP-G",
        "name": "Access-Control + Flash-Loan Callback",
        "required_types": [
            {"access-control"},
            {"flash-loan"},
        ],
        "severity_ceiling": "Critical",
        "description": (
            "Missing auth on flash callback allows attacker to call privileged function "
            "mid-flash with borrowed capital, bypassing normal authorization gates."
        ),
    },
    {
        "pattern_id": "COMP-H",
        "name": "Arithmetic Rounding + Liquidation Logic",
        "required_types": [
            {"arithmetic"},
            {"logic-error"},
        ],
        "severity_ceiling": "High",
        "description": (
            "Rounding error in collateral calculation inflates health factor; "
            "positions that should be liquidatable are not, accumulating bad debt."
        ),
    },
    {
        "pattern_id": "COMP-I",
        "name": "Missing Slippage + Oracle Manipulation",
        "required_types": [
            {"logic-error", "arithmetic"},  # missing slippage check
            {"oracle-manipulation", "price-manipulation"},
        ],
        "severity_ceiling": "High",
        "description": (
            "Attacker manipulates price then executes a slippage-free swap/rebalance "
            "at the manipulated price, extracting value from LPs or the protocol."
        ),
    },
    {
        "pattern_id": "COMP-J",
        "name": "Snapshot Timing + Flash-Loan Governance",
        "required_types": [
            {"logic-error", "arithmetic"},  # snapshot timing
            {"flash-loan"},
        ],
        "severity_ceiling": "Critical",
        "description": (
            "Flash-loan governance attack: borrow tokens, snapshot is taken at callback "
            "time rather than pre-loan, vote passes with borrowed capital, repay."
        ),
    },
    {
        "pattern_id": "COMP-K",
        "name": "Permissionless Access + Reentrancy Callback",
        "required_types": [
            {"access-control"},
            {"reentrancy"},
        ],
        "severity_ceiling": "Critical",
        "description": (
            "An attacker-reachable path (missing auth, open Ownable fallback, or unvalidated "
            "caller) grants a privilege that enables an external callback during a state-changing "
            "function that lacks a reentrancy guard. Attacker exploits the callback window to "
            "double-spend, drain funds, or replay the operation without a flash-loan prerequisite."
        ),
    },
    {
        "pattern_id": "COMP-L",
        "name": "Behavioral Divergence + Reentrancy",
        "required_types": [
            {"logic-error"},
            {"reentrancy"},
        ],
        "required_agent_prefixes": [["BSA"], None],
        "severity_ceiling": "Critical",
        "description": (
            "A documented-vs-actual behavior gap (BSA finding) exposes a state path not "
            "anticipated by the access model. Combined with a missing reentrancy guard on "
            "an adjacent entry point, allows an attacker to reach the divergent state via "
            "callback and execute a second operation against inconsistent state."
        ),
    },
]

SYNTHESIS_SYSTEM = """\
You are a smart contract security auditor specialising in compound vulnerabilities.

You will receive two individual findings plus a compound pattern description.
Your job is to determine whether these two findings genuinely combine to enable a
higher-severity exploit than either finding alone. If they do, produce a compound
finding JSON. If they do not, return {"skip": true, "reason": "<why>"}.

The compound finding must satisfy ALL of these conditions:
1. The combined severity is HIGHER than either component alone.
2. The attacker's path actually uses BOTH vulnerabilities simultaneously.
3. The compound is NOT already implied by either component's proof_of_concept.
4. The exploit is physically possible given the contract code described.

Output JSON format (if compound is valid):
{
  "title": "[COMPOUND] <pattern>: <one-line exploit description>",
  "severity": "Critical|High|Medium",
  "vuln_type": "logic-error",
  "description": "Explanation of why the two findings combine into a higher-severity exploit",
  "location": {"file": "<same as most critical component>", "function": "<entry-point function>"},
  "impact": "Concrete combined worst-case outcome with estimated fund loss",
  "proof_of_concept": "Numbered transaction sequence using both vulnerabilities",
  "recommendation": "Both component fixes must be applied; mitigating one is insufficient",
  "confidence": "High|Medium"
}

If the compound is NOT valid, return:
{"skip": true, "reason": "<explanation>"}
"""


_VERDICT_TO_SEVERITY = {
    "CRITICAL_THREAD": "High",
    "HIGH_THREAD": "High",
    "MEDIUM_THREAD": "Medium",
    "LOW_THREAD": "Low",
}

_CATEGORY_TO_VULN_TYPE = {
    "REENTRANCY": "reentrancy",
    "ACCESS_CONTROL": "access-control",
    "ARITHMETIC": "arithmetic",
    "ORACLE": "oracle-manipulation",
    "FLASH_LOAN": "flash-loan",
    "LOGIC": "logic-error",
    "CROSS_CONTRACT": "logic-error",
    "DOS": "dos",
    "ECONOMIC": "logic-error",
}


def _load_promising_threads() -> list[dict]:
    """Load deep-trace promising threads as synthetic finding entries for pattern matching.

    Thread entries are marked with _agent='deep_trace' and _thread=True so the output
    stage knows not to include them as standalone CC- findings.
    """
    threads_path = audit_path("data/threads") / "promising_threads.jsonl"
    if not threads_path.exists():
        return []
    threads = []
    for line in threads_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            t = json.loads(line)
        except json.JSONDecodeError:
            continue
        verdict = t.get("verdict", "")
        if verdict == "DEAD_END":
            continue
        category = t.get("category", "LOGIC").upper()
        vuln_type = _CATEGORY_TO_VULN_TYPE.get(category, "logic-error")
        thread_id = t.get("thread_id", t.get("id", "DT-???"))
        threads.append({
            "id": thread_id,
            "title": t.get("summary", t.get("title", f"Deep trace thread {thread_id}"))[:80],
            "severity": _VERDICT_TO_SEVERITY.get(verdict, "Medium"),
            "vuln_type": vuln_type,
            "description": t.get("summary", t.get("description", "")),
            "location": {
                "file": t.get("chain_id", "unknown"),
                "function": t.get("entry_function", t.get("function", "unknown")),
            },
            "confidence": "Medium",
            "_agent": "deep_trace",
            "_thread": True,  # flag: do not emit as standalone CC- finding
            "_thread_data": t,  # carry full thread for supporting context
        })
    return threads


def _load_all_findings() -> list[dict]:
    import glob
    output_dir = audit_path("output")
    all_findings = []
    for filepath in sorted(glob.glob(str(output_dir / "findings_*.json"))):
        # Skip the compound synthesis output to avoid circular loading
        if "compound_synthesis" in filepath:
            continue
        try:
            data = json.loads(Path(filepath).read_text())
            agent = data.get("agent", "unknown")
            for f in data.get("findings", []):
                f["_agent"] = agent
                all_findings.append(f)
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    # Also include deep-trace promising threads as context for compound pattern matching.
    # These are lightweight synthetic entries — they participate in pattern matching but
    # are NOT emitted as independent CC- findings (see _thread flag).
    all_findings.extend(_load_promising_threads())
    return all_findings


def _vuln_types_for(finding: dict) -> set[str]:
    vt = finding.get("vuln_type", "")
    return {vt} if vt else set()


def _id_prefix(finding: dict) -> str:
    return finding.get("id", "")[:2].upper()


def _matches_pattern(f1: dict, f2: dict, pattern: dict) -> bool:
    """Return True if (f1, f2) satisfy the pattern's required_types."""
    req = pattern["required_types"]
    if len(req) < 2:
        return False

    types1 = _vuln_types_for(f1)
    types2 = _vuln_types_for(f2)

    # Try both orderings: (f1→req[0], f2→req[1]) or (f1→req[1], f2→req[0])
    def satisfies(ta: set, tb: set, ra: set, rb: set) -> bool:
        return bool(ta & ra) and bool(tb & rb)

    if not (satisfies(types1, types2, req[0], req[1]) or
            satisfies(types2, types1, req[0], req[1])):
        return False

    # Optional agent prefix filter
    prefixes = pattern.get("required_agent_prefixes")
    if prefixes:
        p1, p2 = prefixes
        pid1 = _id_prefix(f1)
        pid2 = _id_prefix(f2)
        forward = (not p1 or pid1 in p1) and (not p2 or pid2 in p2)
        reverse = (not p2 or pid1 in p2) and (not p1 or pid2 in p1)
        if not (forward or reverse):
            return False

    return True


RETRIEVER_TOOLS = [
    {
        "name": "search_kb",
        "description": "Search the Solodit/Code4rena/Sherlock knowledge base for audit findings similar to a compound vulnerability pattern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vuln_type": {
                    "type": "string",
                    "enum": ["reentrancy", "access-control", "arithmetic", "oracle-manipulation",
                             "flash-loan", "logic-error", "dos", "other"],
                },
                "query": {"type": "string"},
            },
            "required": ["vuln_type", "query"],
        },
    },
    {
        "name": "search_immunefi",
        "description": "Search the Immunefi bug-bounty report database for precedents matching a compound vulnerability pattern.",
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
    """Execute a retriever subprocess and return its stdout as a JSON string."""
    import subprocess as _sp
    if tool_name == "search_kb":
        cmd = [sys.executable, str(ROOT / "tools" / "retriever.py"),
               tool_input.get("vuln_type", "other"), tool_input.get("query", "")]
    else:
        cmd = [sys.executable, str(ROOT / "tools" / "immunefi_retriever.py"),
               tool_input.get("vuln_type", "other"), tool_input.get("query", "")]
    try:
        result = _sp.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else "[]"
    except Exception:
        return "[]"


def _extract_json(text: str) -> dict:
    """Extract a JSON object from a text response (handles mixed prose + JSON)."""
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start: i + 1])
                    except json.JSONDecodeError:
                        break
    return {"skip": True, "reason": "could not parse Claude response"}


def _call_claude(f1: dict, f2: dict, pattern: dict, client) -> dict:
    # Build supporting thread context if either finding is a deep_trace thread
    thread_context = ""
    for f in (f1, f2):
        if f.get("_thread") and f.get("_thread_data"):
            td = f["_thread_data"]
            thread_context += (
                f"\nSupporting deep-trace thread ({f['id']}):\n"
                f"  verdict: {td.get('verdict')}\n"
                f"  hop_trace: {json.dumps(td.get('hop_trace', td.get('path', [])))}\n"
                f"  summary: {td.get('summary', '')}\n"
            )

    # Strip internal pipeline keys before sending to Claude
    def _clean(f: dict) -> dict:
        return {k: v for k, v in f.items() if not k.startswith("_")}

    user_msg = (
        f"Pattern: {pattern['pattern_id']} — {pattern['name']}\n"
        f"Pattern description: {pattern['description']}\n\n"
        f"Finding A:\n{json.dumps(_clean(f1), indent=2)}\n\n"
        f"Finding B:\n{json.dumps(_clean(f2), indent=2)}\n"
        + (f"\n{thread_context}" if thread_context else "")
        + "\nDoes this pair form a valid compound vulnerability? "
          "You may call search_kb or search_immunefi to look up precedents before deciding. "
          "If yes, produce the compound finding JSON. "
          "If no, return {\"skip\": true, \"reason\": \"...\"}."
    )

    messages = [{"role": "user", "content": user_msg}]
    for _ in range(5):  # max 5 tool-use rounds
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYNTHESIS_SYSTEM,
            tools=RETRIEVER_TOOLS,
            messages=messages,
        )
        if resp.stop_reason == "end_turn":
            text = next((b.text for b in resp.content if hasattr(b, "text")), "")
            return _extract_json(text)
        if resp.stop_reason == "tool_use":
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break
    return {"skip": True, "reason": "tool loop exhausted without end_turn"}


def _severity_rank(sev: str) -> int:
    return {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}.get(sev, 99)



def _generate_dynamic_compounds(
    findings: list[dict],
) -> list[tuple[dict, dict, dict]]:
    """
    Procedurally discover novel compound candidates from finding pairs.

    Checks two heuristics:
    1. SHARED STATE — both findings reference the same named state variable
       (camelCase word ending in Balance/Amount/Reserve/Supply/Debt/Shares/
        Index/Rate/Price/Cap/Total/Pool/Lock/Fee)
    2. CEI + READER — exactly one finding is a CEI violation; the other reads
       state from the same function scope, forming a reentrancy-stale-read pair

    Returns list of (f1, f2, synthetic_pattern) suitable for the same evaluation
    loop used for the hardcoded COMPOUND_PATTERNS.
    """
    STATE_VAR_RE = re.compile(
        r"\b([a-z][a-zA-Z0-9_]{3,}(?:Balance|Amount|Reserve|Supply|Debt|Shares|"
        r"Index|Rate|Price|Cap|Total|Pool|Lock|Fee|Slot))\b"
    )
    CEI_KEYWORDS = [
        "external call before", "state update after", "checks-effects-interactions",
        "CEI violation", "reentrancy", "callback before state", "transfer before update",
    ]

    def _desc(f: dict) -> str:
        return (
            (f.get("description") or "")
            + " "
            + (f.get("proof_of_concept") or "")
            + " "
            + (f.get("title") or "")
        ).lower()

    def _vars(f: dict) -> set[str]:
        return set(STATE_VAR_RE.findall(_desc(f)))

    def _is_cei(f: dict) -> bool:
        d = _desc(f)
        return any(kw.lower() in d for kw in CEI_KEYWORDS)

    candidates: list[tuple[dict, dict, dict]] = []
    seen: set[frozenset] = set()

    for i, f1 in enumerate(findings):
        for j, f2 in enumerate(findings[i + 1:], i + 1):
            pair_key = frozenset([f1.get("id", ""), f2.get("id", "")])
            if pair_key in seen:
                continue

            # ── Heuristic 1: shared state variable ──────────────────────────
            vars1 = _vars(f1)
            vars2 = _vars(f2)
            shared = vars1 & vars2
            if shared:
                seen.add(pair_key)
                pattern = {
                    "pattern_id": f"DYN-SHARED-{i}-{j}",
                    "name": f"Shared State Interaction ({', '.join(sorted(shared)[:2])})",
                    "required_types": [set(), set()],  # bypass type check — already matched
                    "severity_ceiling": "High",
                    "description": (
                        f"Both findings interact with shared state variables: "
                        f"{', '.join(sorted(shared)[:3])}. "
                        f"Combined exploitation may amplify impact beyond either finding alone."
                    ),
                    "_dynamic": True,
                }
                candidates.append((f1, f2, pattern))
                continue

            # ── Heuristic 2: CEI violation + stale-state reader ─────────────
            cei1, cei2 = _is_cei(f1), _is_cei(f2)
            if cei1 ^ cei2:  # exactly one is a CEI finding
                cei_f, reader_f = (f1, f2) if cei1 else (f2, f1)
                loc_cei = str((cei_f.get("location") or {}).get("function") or "")
                loc_reader = str((reader_f.get("location") or {}).get("function") or "")
                if loc_cei and loc_reader and loc_cei != loc_reader:
                    seen.add(pair_key)
                    pattern = {
                        "pattern_id": f"DYN-CEI-{i}-{j}",
                        "name": f"CEI Violation + Stale-State Reader ({loc_cei[:30]}→{loc_reader[:30]})",
                        "required_types": [set(), set()],
                        "severity_ceiling": "Critical",
                        "description": (
                            f"CEI violation in {loc_cei} allows attacker to re-enter "
                            f"{loc_reader} while state is temporarily invalid."
                        ),
                        "_dynamic": True,
                    }
                    candidates.append((cei_f, reader_f, pattern))

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthesize compound findings from all agent outputs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print matching pairs without calling Claude")
    args = parser.parse_args()

    findings = _load_all_findings()
    if not findings:
        print("No findings loaded. Run specialist agents first.")
        out = {"agent": "compound_synthesis", "findings": []}
        OUT_FILE.write_text(json.dumps(out, indent=2))
        return 0

    print(f"Loaded {len(findings)} findings from specialist agents.")

    # Find candidate pairs that match any compound pattern
    candidates: list[tuple[dict, dict, dict]] = []
    for i, f1 in enumerate(findings):
        for f2 in findings[i + 1:]:
            if f1.get("id") == f2.get("id"):
                continue
            for pattern in COMPOUND_PATTERNS:
                if _matches_pattern(f1, f2, pattern):
                    candidates.append((f1, f2, pattern))

    # Phase 2: dynamic compound discovery
    dyn_candidates = _generate_dynamic_compounds(findings)
    candidates.extend(dyn_candidates)

    print(f"Candidate compound pairs to evaluate: {len(candidates)} "
          f"({len(dyn_candidates)} dynamic)")
    if not candidates:
        print("No compound patterns matched.")
        out = {"agent": "compound_synthesis", "findings": []}
        OUT_FILE.write_text(json.dumps(out, indent=2))
        return 0

    if args.dry_run:
        for f1, f2, pat in candidates:
            print(f"  {pat['pattern_id']} — {f1.get('id')} × {f2.get('id')}")
        return 0

    # Optional enhancer: needs the API. With no key, skip the per-pair LLM evaluation and
    # write an empty compound set — the deterministic merge (report_generator.py) still carries
    # all standalone specialist findings forward.
    client = optional_llm("synthesize_compound")
    if client is None:
        print("  Skipped compound synthesis (no API key) — wrote empty set; specialist "
              "findings still carry the run.")
        out = {"agent": "compound_synthesis", "contract": "various", "findings": []}
        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUT_FILE.write_text(json.dumps(out, indent=2))
        return 0

    # Load compound synthesis agent spec for context (passed as prefix to system prompt)
    agent_spec_path = AGENTS_DIR / "compound_synthesis.md"
    agent_spec = agent_spec_path.read_text() if agent_spec_path.exists() else ""

    compound_findings = []
    counter = 1
    seen_pairs: set[frozenset] = set()

    for f1, f2, pattern in candidates:
        pair_key = frozenset([f1.get("id", ""), f2.get("id", ""), pattern["pattern_id"]])
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        print(f"  Evaluating {pattern['pattern_id']}: {f1.get('id')} + {f2.get('id')} …", end="", flush=True)
        result = _call_claude(f1, f2, pattern, client)

        if result.get("skip"):
            print(f" skip ({result.get('reason', '')[:60]})")
            continue

        # Validate severity escalation
        max_component_sev = min(_severity_rank(f1.get("severity", "Low")),
                                _severity_rank(f2.get("severity", "Low")))
        compound_sev = _severity_rank(result.get("severity", "Low"))
        if compound_sev >= max_component_sev:
            print(f" skip (no severity escalation)")
            continue

        finding_id = f"CC-{counter:03d}"
        counter += 1

        compound = {
            "id": finding_id,
            "title": result.get("title", f"[COMPOUND] {pattern['name']}"),
            "severity": result.get("severity", pattern["severity_ceiling"]),
            "vuln_type": "logic-error",
            "description": result.get("description", pattern["description"]),
            "location": result.get("location", {"file": "various", "function": "various"}),
            "impact": result.get("impact", ""),
            "proof_of_concept": result.get("proof_of_concept", ""),
            "recommendation": result.get("recommendation", ""),
            "confidence": result.get("confidence", "Medium"),
            "compound_components": [f1.get("id", ""), f2.get("id", "")],
            "compound_pattern": pattern["pattern_id"],
        }
        compound_findings.append(compound)
        print(f" => {finding_id} ({compound['severity']})")
        try:
            from viz.event_emitter import emit as _viz_emit
            _viz_emit("BRANCH_CREATED", source_agent="synthesize_compound_findings",
                      target_node_id=finding_id, payload={
                          "branch_trigger": pattern.get("name", pattern.get("pattern_id", "")),
                          "label": f"{finding_id}: {pattern.get('name', '')}",
                          "pattern_id": pattern.get("pattern_id", ""),
                          "component_ids": [f1.get("id", ""), f2.get("id", "")],
                          "severity": compound["severity"],
                          "severity_ceiling": pattern.get("severity_ceiling", ""),
                      })
        except Exception:
            pass

    out = {
        "agent": "compound_synthesis",
        "contract": "various",
        "findings": compound_findings,
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(out, indent=2))

    print(f"\n  Compound findings generated: {len(compound_findings)}")
    print(f"  Output written to: {OUT_FILE}")
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
