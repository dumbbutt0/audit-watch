# PoC Validation Review

You are validating whether a candidate PoC actually **proves** a finding's claim — not whether a test passes.
A passing test is not proof. A validated PoC must prove the specific **root cause**, **attacker path**,
**state transition**, and **impact** the report claims, at the claimed severity, with no privileged shortcut
and no false dependence on fork/test-setup artifacts.

> A green check is evidence of execution, not of exploitability. Prove the claim, not the harness.

Read the finding, the affected source (`file:line`), the test file, and the captured run log. Answer each
question with evidence (`file:line` / test span / log line):

1. **What exactly does the PoC prove?** — name the concrete state/balance/authorization change demonstrated.
2. **What does it NOT prove?** — gaps between the test and the report claim.
3. **Root cause vs symptom** — does the assertion exercise the exact offending expression/function, or only a
   downstream symptom?
4. **Is the caller a realistic attacker?** — an unprivileged external EOA, unless the finding explicitly scopes
   a privileged actor. Flag any `vm.prank`/`startPrank` on an owner/admin/governance/deployer address.
5. **Does setup grant impossible permissions?** — roles, allowances, balances, or ownership the attacker could
   not obtain on-chain.
6. **Direct storage mutation?** — does the test use `vm.store` (or equivalent) to stand in for the attacker's
   action rather than calling the real path? If the bug is *created* by setup, it is `setup_only`/`invalid_poc`.
7. **Is the claimed impact demonstrated?** — loss / freeze / overmint / accounting-drift / DoS / authz-bypass
   shown directly. A mere revert proves impact ONLY when the claim is DoS/liveness.
8. **Are pre-state and post-state compared?** — explicit before/after reads of the named slots/balances, with a
   delta that matches the claim.
9. **Are the relevant guards exercised?** — identify the modifiers/checks that should stop the attacker and show
   they do not (or explain why they are not applicable).
10. **Is the test asserting the right invariant?** — the assertion maps to the violated invariant, not a proxy.
11. **Is there a negative control?** — the protected/patched path behaves differently; the unauthorized actor is
    rejected; a duplicate path is not double-counted.
12. **Does the result support the claimed severity?** — set `severity_supported` to the severity the
    demonstrated impact actually warrants. If it is below the claimed severity, that is an overclaim.
13. **Submission-ready, or only eval/triage evidence?** — submission-ready requires proven root cause +
    reachability + state transition + impact + a non-empty `why_test_proves_claim` and stated `limitations`.

**FP discipline:** do not upgrade on test-pass alone; do not accept copied/re-implemented logic as proof of the
real contract; do not accept an undisclosed fork block; do not let a mock that hard-codes the buggy result count
as proof. When in doubt, choose the weaker classification.

**Final classification (pick one):**
`proven` | `partially_proven` | `inconclusive` | `invalid_poc` | `setup_only` | `duplicate_proof` |
`needs_better_assertions` | `needs_fork_context` | `needs_negative_control`

**Write the result** as a record shaped like `schemas/poc_validation.schema.json` to
`output/poc_validation/validation_notes/<finding_id>.json`. `proven` requires all of:
`root_cause_proven`, `attacker_reachability_proven`, `impact_proven`, `state_transition_proven` = true;
`severity_supported` non-null; `why_test_proves_claim` non-empty; `limitations` present; `test_file`/`test_name`
exist; `command_exit_code` = 0. `validate_poc.py` re-checks these deterministically and will only ever downgrade.
