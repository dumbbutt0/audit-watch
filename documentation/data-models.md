# Data Models

This document describes the major data formats used in the pipeline, including their producer, consumers, and required fields.

---

## findings_*.json (per-agent output)

**Path pattern:** `audits/<id>/output/findings_<agent_name>.json`
**Producer:** Each specialist agent
**Consumers:** `tools/report_generator.py`, `scripts/synthesize_compound_findings.py`, `scripts/cross_agent_connector.py`
**Schema:** `schema/findings_schema.json`

```json
{
  "agent": "reentrancy",
  "contract": "contracts/Vault.sol",
  "timestamp": "2026-05-21T10:00:00Z",
  "findings": [
    {
      "id": "RE-001",
      "title": "Reentrancy in withdraw() allows collateral desync",
      "severity": "Critical",
      "vuln_type": "reentrancy",
      "description": "The withdraw() function calls an external token contract before updating the user's balance...",
      "location": {
        "file": "contracts/Vault.sol",
        "function": "withdraw",
        "line_start": 142,
        "line_end": 158
      },
      "impact": "Attacker can drain the vault of all collateral through recursive calls.",
      "recommendation": "Move the balance update before the external call (CEI pattern).",
      "confidence": "High",
      "code_snippet": "function withdraw(...) external {\n  token.transfer(msg.sender, amount);\n  balances[msg.sender] -= amount;\n}",
      "proof_of_concept": "1. Attacker calls withdraw()\n2. During transfer callback, attacker calls withdraw() again...",
      "kb_references": ["SOL-12345"],
      "invariant_violated": "ACC-001"
    }
  ]
}
```

**Required fields per finding:** `id`, `title`, `severity`, `vuln_type`, `description`, `location`, `impact`, `recommendation`, `confidence`

**Finding ID format:** `<PREFIX>-<THREE_DIGIT_NUMBER>` where PREFIX is 2–3 uppercase letters (RE, AC, AR, OR, FL, LG, DS, SN, EA, TI, CC, UP, BSA, SG, PC, SC, AM, DT, BT, MT, CC_CA)

---

## merged_findings.json

**Path:** `audits/<id>/output/merged_findings.json`
**Producer:** `tools/report_generator.py`
**Consumers:** `scripts/triage_findings.py`, `scripts/run_impact_chain_escalation.py`, `scripts/multi_pass_confirm.py`, `data/findings/<ID>.json` population script

The deduplicated, scored aggregate of all per-agent findings. The primary input for all downstream pipeline stages.

```json
{
  "audit_id": "xterio-2026-05",
  "generated_at": "2026-05-21T12:00:00Z",
  "finding_count": 12,
  "findings": [
    {
      "id": "XTR-001",
      "title": "...",
      "severity": "High",
      "vuln_type": "access-control",
      "agent": "access_control",
      "duplicate_of": null,
      "compound_with": null,
      "cross_agent_note": null
    }
  ]
}
```

---

## submit.jsonl

**Path:** `audits/<id>/data/triage/submit.jsonl`
**Producer:** `scripts/triage_findings.py`
**Consumers:** `scripts/final_submission_pack.py`, `scripts/human_review_classifier.py`, `scripts/run_specialist_review.py`
**Format:** Newline-delimited JSON, one finding per line

```json
{"finding_id": "XTR-001", "title": "TokenGateway grace period bypass...", "severity": "High", "recommended_severity": "High", "vuln_type": "access-control", "decision": "submit", "score": 31, "file": "contracts/TokenGateway.sol", "function": "setManagerOf", "confidence": "High", "triaged_by": "claude-sonnet-4-6"}
```

---

## poc_required.jsonl

**Path:** `audits/<id>/data/triage/poc_required.jsonl`
**Producer:** `scripts/triage_findings.py`
**Consumers:** `scripts/build_poc_queue.py`

Same format as `submit.jsonl` with `"decision": "poc_required"`.

---

## rejected.jsonl

**Path:** `audits/<id>/data/triage/rejected.jsonl`
**Producer:** `scripts/triage_findings.py`, `scripts/pre_submission_gate.py`
**Consumers:** `scripts/record_fp_autopsy.py` (reads for autopsy candidates)

```json
{"finding_id": "GL-001", "title": "...", "decision": "rejected", "decision_reason": "nonReentrant guard applied via ReentrancyGuard inheritance", "invalidation_tags": ["already_guarded"], "score": 8}
```

---

## gate_results.jsonl

**Path:** `audits/<id>/data/triage/gate_results.jsonl`
**Producer:** `scripts/pre_submission_gate.py`
**Consumers:** `scripts/triage_findings.py` (reads to skip API call for hard-rejected findings)

```json
{
  "finding_id": "AC-003",
  "evaluated_at": "2026-05-21T11:00:00Z",
  "overall_verdict": "FAIL",
  "invalidation_tags": ["already_guarded"],
  "gates": {
    "reachability": {"verdict": "PASS"},
    "state_realism": {"verdict": "PASS"},
    "privilege": {"verdict": "PASS"},
    "defense": {"verdict": "FAIL", "reason": "nonReentrant inherited from ReentrancyGuard, no evasion path"},
    "economics": {"verdict": "PASS"},
    "poc": {"verdict": "PASS"},
    "severity": {"verdict": "PASS"},
    "duplicate": {"verdict": "PASS"}
  }
}
```

---

## pattern_check_results.jsonl

**Path:** `audits/<id>/data/fp_autopsies/pattern_check_results.jsonl`
**Producer:** `scripts/fp_pattern_check.py`
**Consumers:** `scripts/pre_submission_gate.py` (Gate 8)

```json
{"finding_id": "RE-002", "checked_at": "...", "recommended_action": "proceed", "similarity_score": 0.32, "matched_rule_id": null}
{"finding_id": "RE-003", "checked_at": "...", "recommended_action": "reject", "similarity_score": 0.91, "matched_rule_id": "FP-RULE-007", "match_reason": "nonReentrant present via inheritance"}
```

---

## findings_confirmed.json

**Path:** `audits/<id>/output/findings_confirmed.json`
**Producer:** `scripts/multi_pass_confirm.py`
**Consumers:** `scripts/pre_submission_gate.py`, `scripts/human_review_classifier.py`

Contains all High/Critical findings from `merged_findings.json` enriched with confirmation fields:

```json
{
  "findings": [
    {
      "id": "RE-001",
      "confirmation_passes": 3,
      "confirmation_score": 0.83,
      "human_review_required": false,
      "human_review_reason": null,
      ...original finding fields...
    }
  ]
}
```

---

## findings_ice.json

**Path:** `audits/<id>/output/findings_ice.json`
**Producer:** `scripts/run_impact_chain_escalation.py`
**Consumers:** `prompts/submission_writer.md` (mandatory read before writing any submission)

Contains `merged_findings.json` findings enriched with an `ice` block per finding:

```json
{
  "findings": [
    {
      "id": "AC-001",
      ...original finding fields...,
      "ice": {
        "corrupted_state": "isManagerOf[token][attacker] = true",
        "consumers": ["TokenGateway.addMinter()", "TokenGateway.onlyManagerOrGateway"],
        "poc_level": 2,
        "severity_ceiling": "High",
        "consumer_search_confidence": "medium",
        "hold": false,
        "needs_manual_review": false
      }
    }
  ]
}
```

**ice block fields:**
- `corrupted_state` — the state variable that becomes incorrect
- `consumers` — protocol functions that read the corrupted state
- `poc_level` — highest PoC level achieved (0–5)
- `severity_ceiling` — maximum severity justifiable given PoC level
- `consumer_search_confidence` — low/medium/high (reliability of rg-based search)
- `hold` — true if high-risk vuln type with no consumers found; routes to manual review
- `needs_manual_review` — true for low-confidence searches

---

## VizEvent (events.jsonl)

**Path:** `data/sessions/<session_id>/events.jsonl`
**Producer:** Any pipeline script calling `from viz.event_emitter import emit`
**Consumers:** `viz/server.py` (serves to frontend via WebSocket)
**Schema:** `schemas/viz_event.schema.json`

```json
{
  "event_id": "a3f12b45-...",
  "event_type": "HYPOTHESIS_BORN",
  "timestamp": "2026-05-21T10:15:00Z",
  "source_agent": "reentrancy_agent",
  "target_node_id": "HYP-003",
  "audit_session_id": "a3f12b45",
  "payload": {
    "hypothesis_text": "Collateral desync via reentrancy in withdraw()",
    "linked_contracts": ["LendingPool.sol"],
    "severity_ceiling": "CRITICAL",
    "confidence": 0.6,
    "exploit_class": "reentrancy"
  }
}
```

---

## audit meta.json

**Path:** `audits/<id>/meta.json`
**Producer:** `scripts/audit_manager.py new`
**Consumers:** Dashboard, `generate_status.py`

```json
{
  "audit_id": "xterio-2026-05",
  "name": "Xterio Bug Bounty",
  "contest_id": "xterio-immunefi-2026-05",
  "platform": "Immunefi",
  "language": "Solidity",
  "framework": "hardhat",
  "contract_path": "/absolute/path/to/contracts",
  "status": "active",
  "deadline": "2026-06-30",
  "max_bounty": 80000,
  "currency": "USD",
  "scope": {
    "contracts": [
      {
        "name": "TokenGateway",
        "proxy": "0x7127f0...",
        "implementation": "0x9cbf16...",
        "chains": ["ethereum", "base"],
        "file": "contracts/TokenGateway.sol"
      }
    ]
  },
  "notes": "..."
}
```

---

## Reasoning Graph Node (in-memory)

Defined in `schemas/reasoning_graph.schema.json`. The in-memory state managed by `viz/graph_state.py`.

**HypothesisNode key fields:** `id` (HYP-NNN), `status` (LIVE/CONVERGED/INVALIDATED/PRUNED/ESCALATED), `confidence` (0.0–1.0), `severity_ceiling`, `exploit_class`, `kb_matches`, `assumptions`, `blockers`, `confidence_history`

**BranchNode key fields:** `id` (BR-NNN-A), `parent_hypothesis`, `branch_type` (EXPLOIT_PATH/CONSTRAINT_RELAXATION/VARIANT/COUNTERFACTUAL), `depth`

**EvidenceNode key fields:** `id`, `attached_to`, `evidence_type` (CODE_REF/SOLODIT_MATCH/STATIC_ANALYSIS/POC_RESULT/AGENT_REASONING), `confidence_delta`

---

## data/findings/<ID>.json (finding definitions)

**Path:** `audits/<id>/data/findings/<finding_id>.json`
**Producer:** Report generator post-processing script (run after `report_generator.py`)
**Consumers:** `scripts/generate_status.py`, `scripts/analyze_poc_completeness.py`, `scripts/run_quality_checklist.py`

Per-finding definition file used by pipeline tools that need to look up a specific finding without parsing all merged_findings.json.

```json
{
  "finding_id": "XTR-001",
  "title": "TokenGateway grace period bypass",
  "severity": "High",
  "vuln_type": "access-control",
  "bug_class": "access_control",
  "claimed_severity": "High",
  "file": "contracts/TokenGateway.sol",
  "function": "setManagerOf",
  "confidence": "High",
  "duplicate_of": null,
  "agent": "access_control"
}
```
