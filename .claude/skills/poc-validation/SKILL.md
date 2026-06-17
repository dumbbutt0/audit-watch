---
name: poc-validation
description: "Credit-free, skill-in-session PoC validation. Reads one prepared bundle at a time (finding claim + source + PoC test + raw run output) and writes conservative reviewer notes that say whether the PoC actually proves the root cause, attacker reachability, state transition, and impact — never marking a test proven just because it passed. Reasons over bundles from poc_validation_prepare.py and writes per-finding notes, then poc_validation_write.py normalizes them and validate_poc.py decides proof. Activate when user says: /poc-validation, validate the PoC, review this PoC, does the test prove the finding, write validation notes, check PoC proof, or after poc-validation-prepare."
---

# PoC Validation (skill-in-session)

Supplies the **semantic** half of PoC validation with **no API calls**. The deterministic scripts enforce and
downgrade; you provide the honest reviewer judgment they cannot. **A passing test is never automatically proof.**
The validator is the source of truth — your notes only ever *propose*; `validate_poc.py` re-derives the final
status and can only downgrade.

## When to use

After `poc-inventory` (and `poc-collect` if a test command exists), when findings still need validation notes.
Checklist: `prompts/poc_validation_review.md`. Schema: `schemas/poc_validation.schema.json`.

## Procedure

1. **Prepare bundles (deterministic):**
   ```
   python scripts/poc_validation_prepare.py        # or --finding-id X / --status missing_poc / --max-items N
   ```
   Writes `output/poc_validation/bundles/<finding_id>.json` + `bundles/index.json`.

2. **Validate each bundle (you, in-session).** Read `bundles/index.json`, then each bundle. For every finding:
   - Read the **finding claim**, the **source span**, the **PoC test**, and the **raw run output**. The bundle
     carries excerpts — but open the real files with the Read tool; do not judge from the excerpt alone.
   - Apply **`prompts/poc_validation_review.md`** literally, answering every question with `file:line` evidence.
   - **Be conservative.** Only set a `*_proven` boolean true when the test demonstrates it on the **real path**:
     - `root_cause_proven` — the assertion exercises the exact offending expression, not a downstream symptom.
     - `attacker_reachability_proven` — an unprivileged EOA reaches it; flag `vm.prank`/`startPrank` on an
       owner/admin/governance address as an **impossible privilege**, not reachability.
     - `impact_proven` — loss/freeze/overmint/drift/DoS/authz-bypass shown with a real before/after delta. A
       bare `vm.expectRevert` proves impact **only** for a DoS/liveness claim.
     - `state_transition_proven` — explicit pre-state and post-state reads with a matching delta.
   - **Flag and downgrade** when you see: `vm.store` standing in for the attack (**setup-only**); a mock that
     hard-codes the buggy result; an undisclosed fork block; a missing negative control; or a demonstrated
     impact below the claimed severity (**severity overclaim** → set `severity_supported` to the true level).
   - When unsure, choose the weaker classification.

3. **Emit notes — JSON only** — one file per finding to
   `output/poc_validation/skill_outputs/<finding_id>.json`, including: `finding_id`, the four `*_proven`
   booleans, `guard_bypass_proven`, `severity_supported`, `privilege_assumptions`, `fork_assumptions`,
   `setup_assumptions`, `excluded_assumptions`, `pre_state`, `actions`, `post_state`, `observed_delta`,
   `expected_delta`, `invariant_violated`, `why_test_proves_claim`, `what_test_does_not_prove`, `limitations`,
   `evidence`, `reviewer_notes`, and `recommended_validation_status`. No markdown, no prose outside the JSON.

4. **Normalize + validate (deterministic):**
   ```
   python scripts/poc_validation_write.py     # normalizes notes -> validation_notes/<id>.json
   python scripts/validate_poc.py             # the validator decides the final status
   ```

## Allowed classifications (`recommended_validation_status`)

`proven` | `partially_proven` | `inconclusive` | `invalid_poc` | `setup_only` | `duplicate_proof` |
`needs_better_assertions` | `needs_fork_context` | `needs_negative_control`

## Output

Report per-finding the recommended classification and the one-line reason, then run the write + validate
commands and show the resulting `validation_status` (which may downgrade your recommendation). For a real
engagement, finish with `./run_pipeline.sh poc-gate-engagement` (or `poc-gate-submission`).
