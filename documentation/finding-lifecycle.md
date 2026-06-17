# Finding Lifecycle

This document traces a finding from initial hypothesis to final submission or rejection.

---

## State Diagram

```
CONTRACT SOURCE
      │
      ▼
[Step 0-2] Agent spawns hypothesis
      │
      ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                     HYPOTHESIS STATE                        │
  │  LIVE ──────→ CONVERGED (evidence accumulated, submitted)   │
  │  LIVE ──────→ INVALIDATED (gate fails, tag applied)         │
  │  LIVE ──────→ ESCALATED (compound chain found)              │
  │  LIVE ──────→ PRUNED (low confidence, no consumer path)     │
  └─────────────────────────────────────────────────────────────┘
      │                              │
      ▼                              ▼
[Step 3.4] ICE pass            [Invalidated → rejected.jsonl]
      │
      ▼
[Step 3.5] Multi-pass confirm
      │
      ├──→ confirmation_score < 0.6 → human_review_required = true
      │
      ▼
[Step 3.6] FP pattern check
      │
      ├──→ similarity > 0.85 → flagged for hard reject
      │
      ▼
[Step 3.7] Pre-submission gate (8 gates)
      │
      ├──→ FAIL → invalidation tag applied → rejected.jsonl
      ├──→ 3+ WARNs → human_review_queue.jsonl
      │
      ▼
[Step 4] Triage scoring (7 components, 35 max)
      │
      ├──→ score >= 28 → submit.jsonl
      ├──→ score 22–27 → poc_required.jsonl
      ├──→ score 16–21 → downgraded.jsonl
      ├──→ duplicate → merged.jsonl
      └──→ score < 16 → rejected.jsonl
            │
            ▼
      [Step 4.5] Human review classifier
            │
            ├──→ 2+ criteria → human_review_queue.jsonl
            └──→ AI-confirmable → ai_confirmed.jsonl
                  │
                  ▼
            [Steps 5–8] Specialist review, PoC, checklist, gate
                  │
                  ▼
            submission_pack.md
```

---

## Status Values

| Status | Meaning | Set by |
|--------|---------|--------|
| `LIVE` | Hypothesis exists, evidence being gathered | Agent spawn |
| `CONVERGED` | Evidence confirmed the finding; triage decision: submit | `triage_findings.py` |
| `INVALIDATED` | Hard gate failure; finding cannot proceed | `pre_submission_gate.py`, `defense_mapper.py`, `record_fp_autopsy.py` |
| `ESCALATED` | Compound chain found; finding combined with another to reach higher severity | `cross_agent_connector.py`, `synthesize_compound_findings.py` |
| `PRUNED` | Low confidence; no consumer path found; no protocol impact | `run_impact_chain_escalation.py`, manual review |

---

## Triage Buckets

| Bucket | File | Criteria |
|--------|------|----------|
| Submit | `data/triage/submit.jsonl` | Score >= 28, no PoC needed |
| PoC Required | `data/triage/poc_required.jsonl` | Score 22–27, needs proof |
| Downgraded | `data/triage/downgraded.jsonl` | Score 16–21; submit at lower severity |
| Merged | `data/triage/merged.jsonl` | Duplicate of another finding (same root cause + fix) |
| Rejected | `data/triage/rejected.jsonl` | Score < 16, or hard invalidation tag |

Rejected findings include a `decision_reason` field and list any `invalidation_tags` applied by the gates.

---

## Invalidation Tags

Hard invalidation tags prevent a finding from reaching `submit.jsonl` without explicit human override (`invalidation_tag_override` field). They are set by `defense_mapper.py`, `pre_submission_gate.py`, or `record_fp_autopsy.py` and cannot be removed by AI-generated hypotheses.

| Tag | Set by | Meaning |
|-----|--------|---------|
| `already_guarded` | `defense_mapper.py` (Step 1.5), Gate 4 | Existing modifier provides full coverage with no evasion path |
| `admin_only` | Gate 3 | Only attack path requires trusted admin compromise |
| `impossible_state` | Gate 2 | Required contract state cannot realistically exist |
| `non_exploitable` | Gate 1 | Auth blocker present and no realistic trigger path |
| `no_profitability` | Gate 5 | Attack causes no profit or damage, or attack cost exceeds profit |
| `duplicate_finding` | Gate 8 | Same root cause and fix as another finding in the batch |
| `duplicate_pattern` | Step 3.6 / Gate 8 | Matches known-invalid FP pattern at > 0.85 similarity |
| `requires_compromised_key` | Gate 3 | Requires a private key compromise as a precondition |
| `unverifiable_assumption` | Gate 2 | Core exploit assumption cannot be verified |
| `unrealistic_liquidity` | Gate 5 | Attack requires market conditions that cannot exist |

---

## File-to-State Mapping

| Pipeline file | What state it represents |
|---------------|-------------------------|
| `output/findings_<agent>.json` | Raw hypothesis from one agent (LIVE) |
| `output/findings_compound_synthesis.json` | ESCALATED compound findings (CC-NNN prefix) |
| `output/findings_cross_agent.json` | ESCALATED cross-agent compounds (CC_CA-NNN prefix) |
| `output/merged_findings.json` | All findings after dedup and report synthesis |
| `output/findings_ice.json` | Merged findings enriched with ICE blocks |
| `output/findings_confirmed.json` | High/Critical findings with confirmation_score |
| `data/triage/submit.jsonl` | CONVERGED — ready to submit |
| `data/triage/poc_required.jsonl` | LIVE — needs proof before CONVERGED |
| `data/triage/downgraded.jsonl` | CONVERGED at lower severity |
| `data/triage/rejected.jsonl` | INVALIDATED or PRUNED |
| `data/triage/gate_results.jsonl` | Per-finding gate verdicts (all 8 gates) |
| `data/triage/human_review_queue.jsonl` | Requires human auditor before any state transition |
| `data/triage/ai_confirmed.jsonl` | AI-confirmable (no human required) |
| `data/fp_autopsies/pattern_check_results.jsonl` | FP similarity scores per finding |
| `data/fp_autopsies/rejection_rules.jsonl` | Accumulated FP rules from past audits |

---

## Assumption Count

Every finding has an `assumption_count` — the number of preconditions required that are not guaranteed by the protocol. Real exploits typically have 0–2 assumptions. Findings with 4+ assumptions trigger a Gate 2 warning and should be reviewed carefully before submission.

Assumption count is recorded in `data/findings/<ID>.json` and included in `data/evaluation/ground_truth.jsonl` when actual contest outcomes are known.

---

## Ground Truth and Calibration

After contest results are known, record them to calibrate pipeline accuracy:

```bash
python scripts/ingest_ground_truth.py \
  --finding-id XTR-001 --outcome accepted --severity high \
  --assumption-count 2 \
  --assumptions "market must be initialized" "attacker has ETH for gas"

python scripts/evaluate_pipeline_accuracy.py
```

`data/evaluation/ground_truth.jsonl` is a human-only write path. AI components cannot modify it. It is the calibration anchor that prevents recursive AI trust contamination.
