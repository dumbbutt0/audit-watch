# Phase 78 — Agentic Workflow Hygiene: Verification Skills + Missed-Step Review

**Result: PASS.** Added the **seatbelts** around the P77 deep-pass: two verification skills, a missed-step review workflow
(spec + deterministic stub), and a deterministic **hygiene validator** that makes missed verification steps **fail closed**.
A P77 bundle cannot reach `POC_REQUIRED`/`READY_FOR_HUMAN_REVIEW` unless verification is complete and (for READY) an
**adversarial review PASSed**. Hygiene-only: no new detector logic, no parked-detector/value-flow change, no production
wiring. 114 regression tests green.

## Objective & why
The previous agentic workflow missed critical steps (helper/modifier/library defenses, later-invariant coverage, attacker
reachability, source falsification, by-design vs bug, impact-before-promotion, author-judging-own-claim). P78 encodes the
manual audit verification process so those misses become **structurally visible or blocking** — promotion requires encoded
verification, not a suspicious pattern.

## Relationship to P77
P77 emits the universal bundle + enforced state machine; P78 **wraps** it. The skills fill the bundle, the hygiene
validator + missed-step workflow enforce fail-closed promotion. Reuses `transitions.py` (assert_transition / FORBIDDEN_LABELS),
`deep_pass.py` (FALSIFIERS / DEFENSE_LEDGER_FIELDS), `lead_schema.FLAGS`. P77 core files are **byte-identical**
(`deep_pass 57c29fff`, `lead_schema 3c57f04e`, `transitions 2c00069c`).

## Changed / new files + paths
| file | hash |
|---|---|
| `.claude/skills/audit-candidate-verification/SKILL.md` | skill (verification loop A–H) |
| `.claude/skills/adversarial-bundle-review/SKILL.md` | skill (isolated kill-the-bundle reviewer) |
| `documentation/workflows/candidate_missed_step_review.md` | workflow spec (Option C — no JS runtime) |
| `scripts/investigation/hygiene_validate.py` | `b9e18f299571f34b` |
| `scripts/investigation/missed_step_workflow_stub.py` | `3f566f9aa4786f94` |
| `tests/investigation/test_workflow_hygiene.py` | 10 tests |

## Clarification applied
`unknown`/`source_unavailable` blocks `READY_FOR_HUMAN_REVIEW` **only when the defense is critical/relevant** (by detector
family or listed in `bundle.critical_defenses`). A defense classified `irrelevant` needs no source proof beyond that
classification. Verified: non-critical unknown + irrelevant defense → READY allowed; critical unknown → blocked
(NEEDS_CONTEXT).

## Validator behavior (`hygiene_validate.py`, exits nonzero on violation)
production-routing/flags · forbidden finality language anywhere · status enum · **legal `state_trace`** (each step via
`assert_transition` → catches the detector→finding shortcut) · required fields · REJECTED needs a source-backed reason.
For promotion-like statuses: defense ledger present · **survived all 10 falsifiers** · **no unknown CRITICAL defense** · no
blocking defense · attacker `transaction_sequence` + broken invariant + measurable impact. POC_REQUIRED: `poc_needed`
named. READY: `poc_needed=false` **and adversarial review = PASS**.

## Missed-step workflow (`missed_step_workflow_stub.py`)
5 isolated verifier roles (Reachability, Defense-Ledger, Source-Falsifier, Invariant&Impact, Provenance&Transition) + a
fail-closed Synthesizer → `{final_status, blocking_checks, missed_steps, required_fixes, promotion_allowed, reason}`. In
real use the roles are isolated agents driven by the two skills; the stub encodes the same synthesis so it is testable.

## Examples of missed steps now blocked
| missed step | result |
|---|---|
| no defense ledger (helper/modifier/library not traced) | promotion blocked (NEEDS_CONTEXT) |
| unknown critical defense but claimed READY | hygiene FAIL |
| source-falsifier (later invariant covers path) fired | REJECTED |
| no attacker `transaction_sequence` but POC_REQUIRED | hygiene FAIL |
| forbidden finality language ("valid finding"/"submission ready") | hygiene FAIL |
| detector→finding direct trace `[STATIC_LEAD, READY]` | ForbiddenTransition / hygiene FAIL |
| adversarial review UNKNOWN | promotion blocked |
| routed source / production-routing flag | refused / hygiene FAIL |

## Test results
`tests/investigation` **19 passed** (P77 9 + P78 10); `hygiene_validate --self-test` OK; `missed_step_workflow_stub
--self-test` OK. Full regression **114 passed** (investigation 19 + signature_replay 22 + access_control 51 + candidates 22).
Parked detectors + value-flow byte-identical; no-wiring CLEAN.

## Promotion decision
**No promotion.** P78 creates hygiene infrastructure that makes missed steps visible and fail-closed. Nothing routed to
production.

## Recommended next
P79 eval comparing **baseline** vs **defense-first** vs **defense-first + missed-step workflow + adversarial review**,
scored by CLEAN_HIT / STRONG_PARTIAL / REJECT_CORRECT / ABSTAIN_CORRECT / WRONG_MECHANISM / SOURCE_FALSE / OVERFIT /
HARD_FAIL. North star: **high recall at the lead layer, near-zero false-positive promotion at the review layer.**

## Reproduce
```
python3 scripts/investigation/hygiene_validate.py --self-test
python3 scripts/investigation/missed_step_workflow_stub.py --self-test
~/.local/bin/pytest tests/investigation/ -q                                  # 19 passed
~/.local/bin/pytest tests/signature_replay/ tests/access_control/ tests/candidates/ -q   # regression
```
