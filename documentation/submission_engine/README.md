# Submission Engine

A strict, **standalone** submission-readiness layer that decides whether a
candidate finding is fit to be submitted to a bug-bounty program / contest.

Its single job: take a self-contained `submission_candidate.json` and return
exactly one of four statuses — and **never** submit anything itself.

```
DO_NOT_SUBMIT
NEEDS_MORE_PROOF
READY_FOR_HUMAN_REVIEW
READY_TO_SUBMIT_AFTER_APPROVAL
```

> **Human approval is always mandatory.** Even a perfectly clean candidate only
> reaches `READY_TO_SUBMIT_AFTER_APPROVAL`. There is no code path in this layer
> that performs or triggers a submission.

## Candidate authoring (front of the workflow)

The gate consumes a `submission_candidate.json`. To produce one from raw finding
artifacts (report.md, poc.log, scope.md, …), use the **candidate author**:

```
raw artifacts -> submission/author/candidate_author.py -> submission_candidate.json -> gate
```

The author is a strict *translator* — it never submits, never decides readiness,
reads only the files passed on the CLI, and never fabricates evidence (unknown
stays missing). See **[candidate_author.md](candidate_author.md)** for the full
workflow, extraction rules, and safety guarantees.

```bash
python -m submission.author.candidate_author \
  --report report.md --out submission_candidate.json --run-gate --readiness-out readiness_report.md
```

## Platform draft rendering (after readiness)

Once the gate returns a **non-blocking** status, a candidate can be turned into a
platform-shaped human draft (Immunefi / Code4rena) with the **platform renderer**:

```
candidate -> gate -> non-blocking status -> platform DRAFT -> clean copy (optional) -> human copy/paste
```

The optional **clean copy** strips the internal watermark + Human Review
Checklist into a separate file (the original draft is preserved). It refuses
non-gated or blocking-status input and is convenience output, not proof of
readiness. See **[platform_renderer.md](platform_renderer.md#clean-copy-strip-internal-artifacts)**.

A draft is emitted **only** for `READY_FOR_HUMAN_REVIEW` /
`READY_TO_SUBMIT_AFTER_APPROVAL` (never for `DO_NOT_SUBMIT` / `NEEDS_MORE_PROOF`),
always requires a gate result, and always carries a `DRAFT ONLY — NOT SUBMITTED`
watermark. It performs no submission and no browser/API automation. See
**[platform_renderer.md](platform_renderer.md)**.

```bash
python -m submission.renderers.platform_renderer \
  --candidate submission_candidate.json --platform immunefi --run-gate --out immunefi_submission.md
# or in one step from the author:
python -m submission.author.candidate_author \
  --report report.md --out submission_candidate.json --emit-platform immunefi --platform-out immunefi_submission.md
```

## Isolation

This layer is fully decoupled from the detection pipeline. It imports nothing
from `audit_context.py`, reads nothing from `output/` or `data/triage/`, and
touches no pipeline config, frozen snapshots, or eval artifacts. It only reads
the `submission_candidate.json` file(s) it is explicitly pointed at.

```
submission/
  schemas/submission_candidate.schema.json   # Draft-07 schema for the candidate artifact
  gates/                                      # the 8 gates + orchestrator (standalone)
  templates/                                  # readiness report + Immunefi/Code4rena templates
  checklists/                                 # human pre-submission checklist + severity map
  examples/                                   # six worked candidate files
tests/submission/                            # pytest suite (valid + invalid examples)
documentation/submission_engine/             # this folder
```

## The core artifact: `submission_candidate.json`

A flat record describing one candidate finding. All required fields and their
enums are defined in `submission/schemas/submission_candidate.schema.json`.
Key fields: `finding_id, title, root_cause, affected_contracts,
affected_functions, attacker_entrypoint, attacker_capabilities,
privilege_required, scope_status, in_scope_asset, out_of_scope_risks,
impact_category, severity_claim, severity_justification, bounty_program_mapping,
call_trace, state_transition, asset_delta, proof_type, poc_path, poc_status,
reproduction_steps, duplicate_check_status, known_issue_check_status,
prior_audit_overlap, false_positive_risks, invalidating_conditions,
defense_analysis, assumptions, evidence_links, triager_summary,
recommended_status, human_approval_required`.

`human_approval_required` must be `true`; the gate forces it true in its output
regardless of the input.

## The eight hard gates

| # | Gate | Blocks (FAIL) on | Needs proof on | Warns on |
|---|------|------------------|----------------|----------|
| 1 | scope | out-of-scope asset/impact, excluded assumption, social-eng/leaked-key/phishing/infra, admin/governance unless allowed | — | uncertain scope, privileged-but-in-scope |
| 2 | attacker_reachability | — | missing entrypoint / call path / preconditions / state setup / defense-bypass | — |
| 3 | impact_severity | no concrete impact; severity inflation (claim > ceiling) | — | unmapped severity; worst/realistic not separated |
| 4 | poc | mainnet/public-testnet attack; fabricated assumptions | High/Critical without runnable+compiling PoC, repro steps, state delta | — |
| 5 | duplicate_known_issue | confirmed duplicate | search not performed | possible duplicate / prior-audit overlap |
| 6 | evidence_completeness | — | missing code lines / functions / call trace / state transition / artifact | — |
| 7 | invalidation_defense | a defense blocks the path with no rebuttal | defenses missing or unexplained | uncertainty marked |
| 8 | human_approval | — | — | input tried to set approval=false (overridden) |

## Aggregation (favor caution)

Each gate emits `FAIL > NEEDS_PROOF > WARN > PASS`. The overall status is the
**highest-precedence** verdict across all gates:

- any `FAIL` → `DO_NOT_SUBMIT`
- else any `NEEDS_PROOF` → `NEEDS_MORE_PROOF`
- else any `WARN` → `READY_FOR_HUMAN_REVIEW`
- else → `READY_TO_SUBMIT_AFTER_APPROVAL`

`NEEDS_PROOF` deliberately outranks `WARN`: the layer favors
`NEEDS_MORE_PROOF` over a risky submission. A candidate that fails schema
validation is blocked outright (`DO_NOT_SUBMIT`).

## Severity-inflation policy

When the claimed severity exceeds what the impact category + proof can support
(see `submission/checklists/severity_mapping.md`), the impact/severity gate
returns `FAIL` with a downgrade note naming the supportable severity. Re-file at
the supportable level rather than submitting the inflated claim.

## Running it

```bash
# single candidate
python submission/gates/submission_gate.py --candidate submission/examples/01_valid_high_confidence.json

# whole directory, with machine-readable + markdown output
python submission/gates/submission_gate.py --dir submission/examples/ \
    --json-out /tmp/verdicts.json --report-out /tmp/reports/

# treat NEEDS_MORE_PROOF as a non-zero exit too (CI)
python submission/gates/submission_gate.py --dir submission/examples/ --strict
```

Exit codes: `0` = all ready/human-review, `1` = at least one DO_NOT_SUBMIT (or
NEEDS_MORE_PROOF under `--strict`), `2` = schema/parse failure.

## Tests

```bash
/home/dummy/.local/bin/pytest tests/submission/ -v
```
