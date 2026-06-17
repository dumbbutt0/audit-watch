# Candidate Authoring

The **candidate author** (`submission/author/`) is the front of the submission
engine. It converts raw, explicit finding artifacts into a complete,
schema-shaped `submission_candidate.json` that the **submission gate** can then
evaluate.

```
raw finding artifacts
  -> candidate_author.py        (translate)
  -> submission_candidate.json
  -> submission_gate.py         (decide — the authority)
  -> readiness_report.md
  -> human approval only
```

## Purpose

Authoring a complete candidate by hand is tedious and error-prone, and the gate
needs every field populated to make a sound decision. The author automates the
*translation* step only: it reads the artifacts a human already produced and maps
them onto the schema. It makes **no security judgement** of its own.

## Non-goals (hard guarantees)

- **No submission.** There is no auto-submit code path anywhere in the module.
- **No readiness decision.** The author writes a fixed cautious placeholder
  (`recommended_status = "NEEDS_MORE_PROOF"`) and **never**
  `READY_TO_SUBMIT_AFTER_APPROVAL`. Only `submission_gate.py` computes a real
  status; the gate's verdict governs.
- **Not a pipeline adapter.** It imports nothing from `audit_context`,
  `run_pipeline`, `output/`, `data/triage/`, or any runtime audit directory, and
  never reads or mutates `program_scope.json` or frozen eval snapshots.
- **Reads only the files passed on the CLI.** No repository scanning, no network,
  no hidden state.
- **Never fabricates evidence.** Missing code lines, traces, PoC output,
  duplicate checks or scope claims stay *missing* — recorded in
  `authoring_metadata.evidence_gaps` — so the gate can return `NEEDS_MORE_PROOF`.
- `human_approval_required` is always `true`.

## Architecture

| File | Responsibility |
|---|---|
| `candidate_author.py` | CLI + `build_candidate(inputs)` orchestration + optional in-process gate run |
| `evidence_extractors.py` | pure, stdlib-only parsers (sections, severity, PoC log, duplicate status, defenses, file:line refs) |
| `normalize.py` | enum normalization (severity/platform/impact/privilege), file/line normalization, address/hash tagging, safe defaults |

The optional `--run-gate` path imports the existing gate
(`submission/gates/submission_gate.py` and `render.py`) **in-process**, purely as
a local validation call. It reuses the gate; it does not fork or weaken it.

## CLI

```bash
python -m submission.author.candidate_author \
  --report report.md \
  --triage triage_notes.md \
  --poc-output poc.log \
  --scope scope.md \
  --program program.json \
  --duplicate-search duplicate_search.md \
  --defense-notes defense_notes.md \
  --out submission_candidate.json \
  --run-gate \
  --readiness-out readiness_report.md
```

| Flag | Required | Meaning |
|---|---|---|
| `--report` | yes | finding report markdown |
| `--out` | yes | output candidate JSON path |
| `--triage` | no | triage notes (used for `triager_summary`) |
| `--poc-output` | no | PoC run log (classified into `poc_status`/`proof_type`) |
| `--scope` | no | scope markdown (confirms `in_scope_asset`) |
| `--program` | no | `program.json` (program/platform/impact-table mapping) |
| `--duplicate-search` | no | duplicate-search notes |
| `--defense-notes` | no | defense analysis |
| `--run-gate` | no | run the gate locally (does **not** submit) |
| `--readiness-out` | no | write the gate's readiness report markdown |
| `--emit-platform` | no | render a platform DRAFT (`immunefi`/`code4rena`) after authoring; implies a gate run. Emitted only for non-blocking statuses; never submits. See [platform_renderer.md](platform_renderer.md) |
| `--platform-out` | no | write the platform draft markdown here |
| `--no-timestamp` | no | omit `authoring_timestamp` (deterministic output) |

**Exit codes:** `0` authoring succeeded (any gate verdict, including
`DO_NOT_SUBMIT`); `1` authoring failed (missing required input, unreadable file,
or the produced JSON failed schema validation).

## Input file expectations

The report is plain markdown. The author looks for explicit markdown headings or
`Label:` lines. Recognised section aliases include:

- Identity: `Title`, `ID`
- Narrative: `Root Cause`, `Vulnerability Details`, `Impact`, `Summary`
- Reachability: `Entry Point`, `Preconditions`, `Attack Path` / `Call Trace`
- Code: `Affected Contracts`, `Affected Functions`, `Code References`,
  `file.sol:120-135` references anywhere in the text
- Severity: `Severity`, `Worst Case`, `Realistic Case`, `Program Table Mapping`
- Proof: `Asset Delta`, `State Before` / `State After`, `Reproduction`
- Residual: `Assumptions`, `Limitations`, `False Positive`, `Out of Scope`

`program.json` recognises: `program`, `platform`, `scope_reference`,
`in_scope_impacts` (list), `privileged_in_scope` (bool), `in_scope_assets`
(list). Unknown program booleans are **omitted** from `bounty_program_mapping`
so the scope gate stays cautious (it only treats explicit `false` / non-`true`
as a signal).

## Extraction rules & safe defaults

Every required field is one of: **extracted**, **conservatively derived**,
**safely defaulted**, or **marked missing**.

| Field | Behaviour when absent / unclear |
|---|---|
| `severity_claim` | default `Informational`; a stated claim is **preserved verbatim** and never reconciled with impact (the gate downgrades) |
| `impact_category` | keyword-derived; default `info` (lets the gate flag a high claim with no concrete impact) |
| `privilege_required` | default `none`; promoted only when explicit role language is present (`onlyOwner` → `admin`, `governance` → `governance`) |
| `scope_status` | default `uncertain`; `in_scope` only when an affected asset is explicitly listed in `scope.md` / `program.in_scope_assets` |
| `proof_type` / `poc_status` | from the PoC log; default `reasoning_only` / `none`. `"0 failed"` is **not** read as a failure |
| `duplicate_check_status` / `known_issue_check_status` | default `not_searched` when no duplicate-search file is given; otherwise the explicit conclusion |
| `call_trace`, `defense_analysis`, `evidence_links`, … | empty when not present (the gate then returns `NEEDS_MORE_PROOF`) |
| `recommended_status` | always the fixed placeholder `NEEDS_MORE_PROOF`; never a readiness verdict |
| `human_approval_required` | always `true` |

Line numbers and function names are never invented: a report that names a
contract but no line stays line-less; a function named without a line keeps the
function and leaves the line missing.

### `authoring_metadata`

The author attaches an `authoring_metadata` object (allowed by the schema's
`additionalProperties: true`, so the schema is **not** modified) containing:
`authored_by`, `source_files`, `author_confidence` (`low`/`medium`, never
`high`), `evidence_gaps` (a human-readable list of what is missing), `notes`, and
an optional `authoring_timestamp`. This is provenance/honesty metadata; it carries
no readiness verdict and no submission instruction.

## How missing evidence is handled

Missing inputs do not crash the author and are never papered over. Each gap is
appended to `authoring_metadata.evidence_gaps`, and the corresponding schema field
is left empty / defaulted so the gate's evidence, PoC, duplicate and defense gates
return `NEEDS_MORE_PROOF`. This is the intended behaviour: the author favours
"incomplete, honestly" over "complete, fabricated".

## Running the gate after authoring

Either pass `--run-gate` (and optionally `--readiness-out`) to the author, or run
the gate separately:

```bash
python submission/gates/submission_gate.py \
  --candidate submission_candidate.json \
  --report-out readiness_report.md
```

A `DO_NOT_SUBMIT` verdict is **not** an authoring failure — the author still
exits `0`, because it did its job (it translated the artifacts). The gate, and
then a human, decide what happens next.

## Safety guarantees (summary)

1. No auto-submit capability exists.
2. No pipeline imports or runtime-state reads.
3. Only CLI-provided files are read.
4. No evidence is fabricated; unknown stays unknown.
5. The author never emits a readiness verdict.
6. `human_approval_required` is always `true`.
7. The existing gate and schema are untouched.

## Examples

The worked examples live under `tests/fixtures/submission_author/`:

| Fixture | Gate verdict |
|---|---|
| `valid_medium_reward_bug` | `READY_TO_SUBMIT_AFTER_APPROVAL` |
| `duplicate_possible` | `READY_FOR_HUMAN_REVIEW` |
| `needs_proof_no_trace` | `NEEDS_MORE_PROOF` |
| `missing_scope` | `NEEDS_MORE_PROOF` |
| `invalid_privileged_bug` | `DO_NOT_SUBMIT` (privileged-only) |
| `severity_inflated_critical` | `DO_NOT_SUBMIT` (+ downgrade note) |

## Testing

```bash
/home/dummy/.local/bin/pytest tests/submission/test_candidate_author.py -v
```
