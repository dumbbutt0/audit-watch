# Assisted-Mode Operating Model (P98)

**Status:** RESEARCH-ONLY, advisory, un-wired. Repositions Audit-Watch from autonomous blind discoverer to a
**human-in-the-loop validator**. Date: 2026-06-03.

## Why
P97 (the pre-registered decision run) fired the stop condition for fully autonomous blind discovery: the system
completed traces and ordering checks but tested the **wrong invariant** (P96's `adversarial_ordering_check`
faithfully verified a true-but-irrelevant invariant and rubber-stamped a REJECT). Invariant **selection** is the
capability boundary. Assisted-mode removes that one failing step — a human or external tool **supplies** the
candidate invariant — and keeps every component that is demonstrably strong.

## The workflow

| Stage | Input | Component (existing, reused) | Reject-first rule |
|---|---|---|---|
| **INPUT** | human/tool candidate invariant + hypothesis | `schemas/assisted_candidate_intake.schema.json` | `candidate_invariant` is **required, non-empty** — no invariant, no run (`BLOCKED_UNSUPPORTED_CLAIM`) |
| **TRIAGE** | the 5-step localized trace | `investigation/localized_depth_trace.py` (v3/v3.1/v3.2) | `INSUFFICIENT_TRACE`/`NEEDS_CONTEXT` → `NEEDS_MORE_CONTEXT` |
| **STRESS** | relied-upon invariant + ≥3 orderings / counterexample | `investigation/adversarial_ordering_check.py` (P96) | `REOPEN`→`NEEDS_MORE_CONTEXT`; `NEEDS_EXECUTION`→`NEEDS_EXECUTION`; `REJECT_CONFIRMED`→`REJECTED_SOURCE_PROVEN_SAFE` |
| **VERIFY** | impact assessment + bundle | `maximal_consequence_check.assess` → `severity_impact_gate.gate` (frozen `193abf9f`) → `hygiene_validate.validate` + adversarial review | unsupported escalator / severity demote-or-FP → `BLOCKED_UNSUPPORTED_CLAIM`; hygiene fail → `NEEDS_MORE_CONTEXT` |
| **REPRODUCE** | validated candidate | `scripts/handoff_generator.py` (P84) | PoC handoff is **human-gated**; scaffold is reject-first / DO_NOT_SUBMIT until executable proof exists |
| **PACKAGE** | reproduced PoC | `scripts/handoff_generator.py` submission docs | scope/duplicate PENDING → `BLOCKED_SCOPE_OR_DUPLICATE_PENDING` |
| **TRACK** | all of the above | `scripts/funnel.py` + dashboard (`source=assisted`) | `SUBMITTED` is human-only and not a pipeline status |
| **HUMAN FINAL** | the bundle | the human auditor | scope · duplicate · final wording · **submit / no-submit** |

## The driver
`scripts/assisted/validate_candidate_invariant.py` runs TRIAGE→STRESS→VERIFY in order over a candidate intake
file and emits a bundle (`validation_report.md`, `trace.json`, `ordering_check.json`, `consequence_check.json`,
`severity_gate.json`, `decision.json`). Decision states:

- `VALIDATED_FOR_POC_HANDOFF` — PASS_CANDIDATE survived depth trace + ordering + consequence + severity + hygiene.
- `REJECTED_SOURCE_PROVEN_SAFE` — invariant holds across the enumerated orderings (a confirmed negative; **not** a finding).
- `NEEDS_MORE_CONTEXT` — missing trace/ordering evidence, or a reopen.
- `NEEDS_EXECUTION` — only a runtime confirmation remains; a test idea is required.
- `BLOCKED_UNSUPPORTED_CLAIM` — no invariant, an unsupported escalator, or a severity demote/FP (**a severity FP blocks handoff**).
- `BLOCKED_SCOPE_OR_DUPLICATE_PENDING` — submission package requested but human scope/duplicate review is pending.

The intake may carry analyst-supplied evidence blocks the checks consume: `depth_trace`,
`adversarial_ordering`, `impact_assessment` (and optional `defense_ledger` / `adversarial_review`). Absent
evidence is reject-first: you cannot reach `VALIDATED_FOR_POC_HANDOFF` without supplying it.

## Hard boundaries
Never selects the invariant · never sets production severity · never auto-submits · never routes · does not
modify `severity_impact_gate` (frozen `193abf9f`) or any P81e–P97 frozen artifact. `VALIDATED_FOR_POC_HANDOFF`
is a **recommendation to a human**, gated by the same checks the funnel's `can_promote_to_poc_handoff` enforces.

## Production cadence (P99)
Per-candidate (or daily) loop — full detail in `runbook.md`, gates in `human_final_gate.md`:
1. **Intake** candidates (human/tool supply the invariant).
2. **Validate** candidates (`validate_candidate_invariant.py`: depth-trace → ordering → consequence → severity → hygiene).
3. **Attempt a PoC only for validated candidates** (`VALIDATED_FOR_POC_HANDOFF` / `NEEDS_EXECUTION`).
4. **Generate a submission package only for reproduced candidates** (REPRODUCED).
5. **Human reviews** scope / duplicate / severity (the human final gate).
6. **Human records the submit / no-submit decision.**
7. **Outcome is recorded later** (`record_assisted_outcome.py` → `assisted_mode/outcomes/`); the dashboard shows
   SUBMITTED only from an explicit outcome record.
8. **Lessons feed back into templates / prompts — never into historical scores** or frozen artifacts.

### What Audit-Watch is and is not
- Audit-Watch is **not** an autonomous submission bot.
- Audit-Watch **does not submit** reports.
- Audit-Watch **does not decide scope or duplicate status** without human review.
- Audit-Watch **is** a validation and evidence-preparation system, with the human as the final decision-maker.
