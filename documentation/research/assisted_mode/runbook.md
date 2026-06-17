# Assisted-Mode Runbook (P99)

How a human/tool-supplied candidate moves safely from intake to recorded outcome. RESEARCH-ONLY, advisory,
un-wired. Audit-Watch **validates and prepares evidence**; it does not submit, and it does not decide
scope/duplicate. Reject-first at every gate. See also `assisted_mode_operating_model.md`,
`assisted_mode_human_checklist.md`, `human_final_gate.md`.

## A. Candidate intake
Human or external tool supplies an `assisted_candidate_intake` (`schemas/assisted_candidate_intake.schema.json`):
- `candidate_invariant` (**required, non-empty** — the property the bug would break),
- `source_refs` (file:line), `suspected_break`, `affected_actor`, `attacker_or_trigger_actor`, `entrypoint`,
- `supplied_by`, `requested_check` ∈ {VALIDATE, FALSIFY, TRACE_ONLY, POC_HANDOFF, SUBMISSION_PACKAGE}.
No invariant → stop (`BLOCKED_UNSUPPORTED_CLAIM`).

## B. Validation — `scripts/assisted/validate_candidate_invariant.py`
Runs the proven components in order; reject-first:
1. `localized_depth_trace` — 5-step concrete trace; `INSUFFICIENT_TRACE`/`NEEDS_CONTEXT` → `NEEDS_MORE_CONTEXT`.
2. `adversarial_ordering_check` — ≥3 orderings or a counterexample; `REOPEN` → `NEEDS_MORE_CONTEXT`,
   `REJECT_CONFIRMED` → `REJECTED_SOURCE_PROVEN_SAFE`, `NEEDS_EXECUTION` → `NEEDS_EXECUTION`, `PASS_CANDIDATE` → continue.
3. `maximal_consequence_check` — unsupported escalator → `BLOCKED_UNSUPPORTED_CLAIM`.
4. `severity_impact_gate` (frozen `193abf9f`) — demote/FP → `BLOCKED_UNSUPPORTED_CLAIM` (a severity FP blocks handoff).
5. `hygiene_validate` — not ok → `NEEDS_MORE_CONTEXT`.
6. Optional **isolated key-blind adversarial review** (author ≠ judge) for a second opinion before PoC.
Decision `VALIDATED_FOR_POC_HANDOFF` is a recommendation to a human — not a finding, not a submission.

## C.0 Harness preparation — `scripts/assisted/harness_prep.py` (P110/P111)
Before attempting (or abandoning) a PoC for `VALIDATED_FOR_POC_HANDOFF` / `NEEDS_EXECUTION`, prepare the runtime
harness so the human isn't starting from zero:
```
python scripts/assisted/harness_prep.py --subject <id> --contract <C> --function <fn>
# or:  --intake <assisted_candidate_intake.json>   (uses its source_refs)
```
It reuses the P110 classifier + scaffold generator (read-only) and writes a bundle to
`documentation/research/assisted_mode/<candidate>/harness_prep/`:
- `harness_feasibility.json` — classification + dependency map + actor model + environment + required components + blockers,
- `<C>_<fn>.scaffold.t.sol` — an **inert** Foundry skeleton (banner + actors + handles + setUp TODOs + `vm.skip(true)`),
- `harness_prep.md` — the human checklist (fork? deploy order? init? funding? actors?) and which TODOs to fill.

**Classification ∈ {HARNESS_SIMPLE, HARNESS_MODERATE, HARNESS_COMPLEX, HARNESS_BLOCKED}** is an advisory **effort
estimate only — never a gate and never a candidate-status change.** BLOCKED means runtime infrastructure is
unavailable (missing deployable / external infra); it is NOT a verdict that the candidate is safe or a finding —
reject-first still governs. The scaffold **prepares** execution; it never proves it. The human fills the scaffold's
TODOs to produce the Stage-C fixture below.

## C. PoC handoff
- **Attempt a PoC** only for `VALIDATED_FOR_POC_HANDOFF` (or `NEEDS_EXECUTION` with a concrete test idea) — starting
  from the C.0 scaffold + checklist.
- **Stop at `NEEDS_EXECUTION`** when the only remaining unknown is runtime behaviour and no executable fixture is
  feasible yet (e.g. C.0 returned `HARNESS_BLOCKED`) — record the test idea + the harness blockers; do not claim reproduction.
- Build the smallest executable fixture against the real in-scope contracts (`handoff_generator` scaffold is
  reject-first / `DO_NOT_SUBMIT`). Classify:
  - **REPRODUCED** — executable test fails on vulnerable source and passes under a minimal patch; source chain complete.
  - **PARTIAL_REPRO** — harness + source chain complete but a concrete fixture/build blocker remains.
  - **NOT_REPRODUCED** — the behaviour does not reproduce → the candidate is not a finding (reject-first).

## D. Submission package (only for REPRODUCED, human-reviewable)
Under `<candidate>/submission_package/`:
- `submission_draft.md` — **platform-neutral** report; NO internal tool/eval/scanner/blind/phase language.
- `evidence_bundle.md` — commit, source refs, PoC path/command, vulnerable + patch output, source-restore hash,
  caveats, no external/answer-key dependence.
- `pre_submission_gate.md` — reject-first checklist; verdict `READY_FOR_HUMAN_REVIEW` only if the sole open items
  are human scope/duplicate/program-rule.
- `reviewer_notes.md` — INTERNAL; keeps the assisted-mode caveat; why real / why severity / what to run.
- `optional_platform_fields.md` — copy-ready fields, marked DRAFT/NOT FINAL.

## E. Human final gate (see `human_final_gate.md`)
A human checks scope, duplicate/public-known, program severity, final wording, reruns the PoC, and records one of:
`APPROVED_TO_SUBMIT` / `DO_NOT_SUBMIT_*` / `NEEDS_REPORT_EDIT` / `NEEDS_MORE_EVIDENCE`. Audit-Watch never sets this.

## F. Outcome recording — `scripts/assisted/record_assisted_outcome.py`
After the human decides (and, if submitted, after the program responds), record an
`assisted_outcome_record` (`schemas/assisted_outcome_record.schema.json`) into
`documentation/research/assisted_mode/outcomes/`. Invariants the recorder enforces:
- `submitted=true` requires `human_final_gate=APPROVED_TO_SUBMIT` (`BLOCKED_INVALID_GATE`);
- `outcome ∈ {accepted, duplicate, rejected}` requires `submitted=true` (`BLOCKED_INVALID_OUTCOME_STATE`);
- schema-valid only (`BLOCKED_SCHEMA_ERROR`); otherwise `RECORD_OK`.
Outcomes: `pending / accepted / duplicate / informative / rejected / invalid / withdrawn / needs_revision`. The
dashboard shows SUBMITTED **only** from a record with `submitted=true` — never inferred from
`READY_FOR_HUMAN_REVIEW`.

## Lessons loop
`lessons_learned` / `followup_actions` feed back into **templates and prompts**, never into historical scores or
frozen artifacts.
