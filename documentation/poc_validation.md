# PoC Validation Layer

Audit-Watch has strong recall (coverage gate + semantic lenses + exact-root-cause synthesis) and integrity
(min-confirm / coverage / confirm gates, API-free). The remaining gap is **proof quality**: surfacing the
right root cause is not the same as proving it. This layer validates whether a candidate PoC actually proves
the finding's claim before it can be called submission-ready.

> **A passing test is not proof.** A validated PoC must prove the specific **root cause**, **attacker path**,
> **state transition**, and **impact** the report claims — at the claimed severity, with no privileged
> shortcut and no false dependence on fork/test-setup artifacts.

## Passing test vs proven finding

A green test only shows that *some* code path ran and *some* assertion held. It says nothing about whether:

- the assertion exercises the **exact offending expression**, or just a downstream symptom;
- the caller is a **realistic unprivileged attacker**, or an owner/admin via `vm.prank`;
- the bug was **reproduced**, or **manufactured** by `vm.store`/a mock that hard-codes the buggy result;
- the **claimed impact** (loss / freeze / overmint / accounting-drift / DoS / authz-bypass) was demonstrated
  with a real before/after state delta, or merely a revert;
- the demonstrated impact actually **supports the claimed severity**.

This layer separates those concerns: deterministic structural checks + reviewer-attested semantics.

## How it works (API-free)

True semantic judgment ("is this a realistic attacker?") cannot be done by pure Python, so the layer splits
the work the same way the rest of the pipeline does — **deterministic gate + reviewer/skill + prompt**:

1. **`poc_inventory.py`** builds the worklist of PoC-required findings (High/Critical always; Medium when the
   impact is fund-loss / freeze / overmint / DoS / accounting-drift / authz-bypass). Eval-layer candidates are
   `not_required_eval_only` — **eval recall is never gated by PoCs**.
2. **`collect_poc_results.py`** runs a chosen test command and records execution (stdout/stderr, exit code,
   pass/fail signal, raw log). It **decides nothing**.
3. A reviewer (a human, or the `/poc-validation` skill using `prompts/poc_validation_review.md`) writes a
   record shaped like `schemas/poc_validation.schema.json` to
   `output/poc_validation/validation_notes/<finding_id>.json`.
4. **`validate_poc.py`** enforces the required-for-proven contract and runs heuristics that **only ever
   downgrade** — it never invents a proof. With no reviewer notes, the status stays conservative (never
   `proven`).
5. **`poc_validation_gate.py`** enforces proof requirements per mode and is consumed before report generation.

## Validation statuses

| Status | Meaning |
|---|---|
| `proven` | Root cause + reachability + state transition + impact all attested and structurally confirmed; exit 0. |
| `partially_proven` | Some proof dimensions hold; at least one (usually impact or reachability) is missing. |
| `inconclusive` | No usable PoC artifact / reviewer attestation yet. |
| `setup_only` | The "attack" is performed by test setup (e.g. `vm.store`) rather than the real path. |
| `invalid_poc` | The test does not exist / the named test is not in the file / it cannot prove the claim. |
| `failed` | The command exited non-zero (test failed or did not compile). |
| `duplicate_proof` | Proves a finding already proven elsewhere; must not be double-counted. |

## Required proof fields (for `proven`)

`validate_poc.py` will only emit `proven` when **all** of:

- `root_cause_proven = true`, `attacker_reachability_proven = true`, `impact_proven = true`,
  `state_transition_proven = true`
- `severity_supported` is non-null
- `why_test_proves_claim` is non-empty and `limitations` is present
- `test_file` and `test_name` exist (and the name appears in the file)
- `command_exit_code = 0`
- no structural downgrade tripped

Heuristic **downgraders** (text scans of the test + log): `vm.store` as the attacker action → `setup_only`;
`vm.prank`/`startPrank` on an owner/admin/governance address → privilege warning; only `vm.expectRevert` with
no value assertion → impact-not-proven unless the claim is DoS/liveness; `createSelectFork` without a disclosed
block → fork warning; missing negative control → warning.

## Modes

| Mode | Behavior |
|---|---|
| `eval` | PoCs **not required**. Warns on invalid/overclaimed claims. **Always PASS** — recall is never gated. |
| `engagement` | High/Critical require `proven` (or a manual waiver). Medium require ≥ `partially_proven` (or waiver). Low pass with static proof if impact is source-obvious. |
| `submission` | High/Critical require `proven`. Medium require `proven`, or `partially_proven` **with** limitations. `invalid_poc` / `inconclusive` / `setup_only` / `failed` block. **Severity overclaim blocks.** |

Manual waivers: `output/poc_validation/waivers.json` → `{"waived": ["FID-1", ...]}`. Escape hatch (logged):
`AUDITWATCH_POCGATE_OVERRIDE=1`.

## Examples of invalid PoCs

- **Storage-mutation attack** — `vm.store(target, slot, value)` sets the "exploited" state directly; the real
  function is never driven by the attacker → `setup_only`.
- **Prank-as-admin** — `vm.prank(owner); target.privilegedFn()` proves an authorized action, not an attack →
  privilege warning, not reachability.
- **Revert-only** — `vm.expectRevert(); target.f();` proves a revert, not loss. Valid **only** for a DoS/liveness
  claim.
- **Mock manufactures the bug** — a mock returns the buggy value unconditionally; the real contract is never
  exercised → root cause not proven.
- **Undisclosed fork** — `createSelectFork(rpc)` with no pinned block and no disclosed addresses → not
  reproducible.

## Examples of strong PoCs

- Calls the **real public entrypoint** as an unprivileged EOA; reads the named slot/balance **before and
  after**; asserts a delta that matches the claim (`assertEq(token.balanceOf(victim), 0)`).
- Includes a **negative control**: the protected path reverts for the unauthorized actor, or the patched
  contract behaves differently.
- Discloses **all setup**: fork block, deployed addresses, mocks, balances, roles — and none of it grants the
  attacker impossible privileges.
- States `severity_supported` equal to the demonstrated impact and lists honest `limitations`.

## Where it sits in the pipeline

The layer is **standalone** — it is not wired into the eval `full`/`review-gate` flow, so eval recall stays
unblocked. For a real engagement/submission, run it after the existing gates and before report generation:

    coverage gate  ->  confirm gate  ->  min-confirm  ->  PoC validation gate  ->  pre_submission_gate.py (Step 3.7)  ->  report

Commands:

    ./run_pipeline.sh poc-inventory
    ./run_pipeline.sh poc-collect --finding-id <id> --test-file <f> --test-name <n> --command "forge test --match-test <n> -vvv"
    ./run_pipeline.sh poc-validate [<finding-id>]
    ./run_pipeline.sh poc-gate-eval          # never blocks
    ./run_pipeline.sh poc-gate-engagement
    ./run_pipeline.sh poc-gate-submission

## API-free `/poc-validation` skill workflow

The deterministic scripts enforce the proof contract but cannot *infer* semantic proof — that judgment is
supplied in-session by the **`/poc-validation` skill** (credit-free, no API), exactly like `/triage` and
`/coverage-sweep`. The split is deliberate: **the skill writes semantic notes; `validate_poc.py` is the source
of truth and only ever downgrades.** Eval mode stays PoC-free throughout.

1. **`./run_pipeline.sh poc-inventory`** — build the worklist of PoC-required findings.
2. **`./run_pipeline.sh poc-collect …`** — if a test command exists, run it and capture the log (optional).
3. **`./run_pipeline.sh poc-validation-prepare`** — package one context bundle per finding (claim + source +
   test + raw log + current proof gaps) into `output/poc_validation/bundles/`. Runs no tests.
4. **Run the `/poc-validation` skill** in Claude Code. It reads each bundle, applies
   `prompts/poc_validation_review.md`, inspects the real source/test with the Read tool, and writes
   **conservative** reviewer notes (JSON only) to `output/poc_validation/skill_outputs/<finding_id>.json` —
   never marking a test proven just because it passed.
5. **`./run_pipeline.sh poc-validation-write`** — `poc_validation_write.py` validates each skill output, rejects
   missing/unknown ids (use `--allow-unknown` to accept extras), normalizes it into a schema-valid
   `validation_notes/<id>.json`, writes `poc_validation_write_summary.json`, then runs `validate_poc.py`.
6. **`./run_pipeline.sh poc-gate-engagement`** (or `poc-gate-submission`) — enforce the proof bar.

`./run_pipeline.sh poc-validation` does steps 3 + a pause for the skill; `poc-validation-full` chains
inventory → prepare → pause → (resume) write + validate + engagement gate.

**Why a skill, not just the validator:** the validator can check that `vm.store` is present, that the exit code
is 0, that an assertion exists — but it cannot read the finding and judge whether the assertion proves *that*
root cause, whether the caller is a realistic attacker, or whether the demonstrated impact supports the claimed
severity. The skill answers those questions; the validator then re-derives the status from the skill's booleans
and structure, so a skill that over-claims `proven` is still downgraded if the structure does not hold.

## Engagement report + dashboard (operator view)

`poc_engagement_report.py` is the operator's readiness view: it buckets every PoC-required finding so you can
see at a glance **what to submit now, what is blocked, and exactly what to fix**. Run it after the validator and
the engagement gate:

    ./run_pipeline.sh poc-engagement-report      # python scripts/poc_engagement_report.py
    python scripts/dashboard.py                  # surfaces the same status (http://localhost:8765)

It writes `output/poc_validation/engagement_report.{json,md}` and a small dashboard artifact
`output/dashboard/poc_validation_status.json`. Bucketing reuses `poc_validation_gate.evaluate`, so the report
never diverges from the gate. It changes no proof verdict and overwrites no validation note.

**The 13 buckets** (each finding lands in exactly one):

| Bucket | Meaning / what to do |
|---|---|
| `submission_ready` | Passes the submission gate — submit as-is. |
| `engagement_ready_but_not_submission_ready` | Usable for the engagement; not yet submission-grade (e.g. Medium `partially_proven` without limitations). |
| `needs_better_assertions` | Add a real impact/value assertion. |
| `needs_negative_control` | Add an unauthorized/patched-path control. |
| `needs_fork_context` | Needs a fork test with a disclosed block. |
| `missing_poc` | No PoC test exists — write one. |
| `missing_collected_log` | A test is referenced but was never run/captured — run `poc-collect`. |
| `invalid_poc` | The test does not prove the claim — reject/rewrite. |
| `setup_only` | The "attack" is performed by setup (`vm.store`), not the real path. |
| `severity_overclaim` | Demonstrated impact is below the claimed severity — downgrade or strengthen. |
| `duplicate_proof` | Proves a finding already proven elsewhere. |
| `inconclusive` | No usable proof yet. |
| `eval_only_not_required` | Eval-only — never needs a PoC. |

**Dashboard.** `scripts/dashboard.py` reads `output/dashboard/poc_validation_status.json` and exposes it on
`/api/state` under the `poc_validation` key; the frontend shows a "PoC Validation" card (submit-ready /
High-Critical blocked / missing-PoC / invalid-or-setup-only counts, the active `mode`, and the **top 3 fix
items**). If the report has not been run, the key is `{}` and the dashboard degrades gracefully — no existing
section is affected. Offline (backend unreachable) the card previews from `dashboard/mock-data.js`
(`window.MOCK_STATE.poc_validation`); a standalone fixture lives at
`dashboard/mock_data/poc_validation_status.json`. Mock data only affects the offline fallback, never live state.

### Engagement vs submission report

The report runs in two modes (default `engagement`):

    python scripts/poc_engagement_report.py --mode engagement   # ./run_pipeline.sh poc-engagement-report
    python scripts/poc_engagement_report.py --mode submission   # ./run_pipeline.sh poc-submission-report

`submission_ready` always means *passes the submission gate*. `*_blocked` means *fails the **mode's** gate*
(engagement vs submission), and the active `mode` is recorded in `engagement_report.{json,md}` and the
dashboard artifact. In **submission** mode the bucketing is stricter: a finding that passes the engagement gate
but fails the (stricter) submission gate no longer rests in `engagement_ready_but_not_submission_ready` — it
falls through to its specific gap bucket (`needs_*` / `inconclusive`), so the fix-list points at the exact gap.

### The fix-list — exactly what to do next

`poc_engagement_report.py` also writes `output/poc_validation/fix_list.{md,json}`: every finding that is not yet
submission-ready (and not eval-only), grouped by **next action** and ordered by urgency — High/Critical blocked,
then Medium blocked, then closest-to-ready, then missing PoC, then cleanup. `fix_list.md` is a checklist; each
item gives the `shortest_next_step` and the exact missing requirements. Fix-action vocabulary:
`write_missing_poc · add_collected_log · add_reachability_assertion · add_impact_assertion ·
add_negative_control · add_fork_context · downgrade_severity · remove_invalid_setup · resolve_duplicate ·
reject_poc · manual_review`. The dashboard surfaces the top fix items, the submission blockers, and the
findings closest to ready. Workflow: **the engagement report says where each PoC stands; the fix-list says
exactly what to do next.**

### Per-finding fix workflow (`poc-fix`)

The fix-list tells you *what* is blocked and *why*. `poc-fix <finding_id>` turns that into the next concrete
action for **one** finding — it stages the right command or bundle and writes a fix session:

    ./run_pipeline.sh poc-fix DPF-036
    ./run_pipeline.sh poc-fix DPF-036 --mode submission
    ./run_pipeline.sh poc-fix DPF-036 --collect-command "forge test --match-test test_transferPlots -vvv"

By `recommended_next_action`, `poc_fix.py` does the right thing: `write_missing_poc` shows the finding summary +
proof goal + suggested test path and stages the `/poc-validation` bundle; `add_collected_log` runs
`collect_poc_results.py` if you pass `--collect-command`, else prints a ready-to-copy template;
`add_reachability_assertion` / `add_impact_assertion` / `add_negative_control` / `manual_review` stage the bundle
and attach the right checklist; `add_fork_context` lists the required fork assumptions; `downgrade_severity`,
`remove_invalid_setup`, `resolve_duplicate`, `reject_poc` print targeted guidance. It writes
`output/poc_validation/fix_sessions/<finding_id>.{json,md}` (use `--json` to print the session to stdout).

It **never** runs `/poc-validation` automatically — for semantic actions it prints
`Run /poc-validation on output/poc_validation/bundles/<finding_id>.json`. The chain is: **the fix-list says
what's blocked → `poc-fix` stages the next action → `/poc-validation` does the semantic review →
`validate_poc.py` is the source of truth.** Findings already `submission_ready` or `eval_only_not_required` are
reported as nothing-to-fix; an unknown finding exits non-zero.

### Batch fix workflow (`poc-fix-all`)

`poc-fix` handles one finding; `poc-fix-all` prepares the **whole engagement's** PoC-fix queue in one pass —
it walks the fix-list in priority order, stages a fix session (and `/poc-validation` bundle) for every
actionable finding, and writes a consolidated **operator worklist**:

    ./run_pipeline.sh poc-fix-all
    ./run_pipeline.sh poc-fix-all --mode submission
    ./run_pipeline.sh poc-fix-all --limit 10
    ./run_pipeline.sh poc-fix-all --actions add_impact_assertion,add_negative_control

Other flags: `--severity High,Medium`, `--include-ready` (also list already-submission-ready findings),
`--overwrite` (re-stage existing sessions), `--json`. Priority order: High/Critical blocked → Medium blocked →
closest-to-submission-ready → missing collected logs → missing PoCs → duplicate/reject/cleanup.

**Read `output/poc_validation/operator_worklist.md`** — a priority-ordered checklist grouped by next action.
Items whose bundle is staged are marked **bundle ready → /poc-validation**; work down the list, then run
`/poc-validation` on the staged bundles (`output/poc_validation/bundles/<id>.json`) and `validate_poc.py`. The
dashboard surfaces `operator_worklist_count` and `next_batch_actions`.

> **Safety:** `poc-fix-all` stages work — it does **not** execute test commands. Collect commands are only
> templated, never run, unless `--run-collect` is set, and even then it only runs a command already present in
> the data — it never invents a forge command. A failure staging one finding is recorded and the batch
> continues. It writes no validation notes and weakens no gate; the validator remains the source of truth.

## Using it for real bounty submissions

1. `poc-inventory` — see which High/Critical/Medium findings still need a PoC (`missing_poc`).
2. Write a Foundry/forge PoC that calls the real entrypoint as an attacker and asserts the impact.
3. `poc-collect …` — run it and capture the log.
4. Review with `prompts/poc_validation_review.md`; write the `validation_notes/<id>.json` honestly (do not
   set a boolean true unless the test proves it; set `severity_supported` to the demonstrated impact).
5. `poc-validate` then `poc-gate-submission`. Fix whatever the `recommended_next_action` says
   (`add_impact_assertion`, `add_reachability_assertion`, `add_negative_control`, `downgrade_severity`, …)
   until the finding is `proven` and `submission_ready`. Only then submit.
