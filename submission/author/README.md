# submission/author — candidate authoring

Turns raw, explicit finding artifacts into a schema-shaped
`submission_candidate.json` that the **submission gate** can evaluate.

This is a **translator**. It is the front of the workflow:

```
raw finding artifacts
  -> candidate_author.py        (this module)
  -> submission_candidate.json
  -> submission_gate.py         (the authority)
  -> readiness_report.md
  -> human approval only
```

## Non-goals (hard rules)

- **It does not submit anything.** There is no auto-submit code path.
- **It does not decide readiness.** Only `submission/gates/submission_gate.py`
  produces a readiness status. The author writes a fixed cautious placeholder
  (`recommended_status = "NEEDS_MORE_PROOF"`) and never `READY_TO_SUBMIT…`.
- **It is not a pipeline adapter.** It imports nothing from `audit_context`,
  `run_pipeline`, `output/`, `data/triage/`, or any runtime audit directory, and
  it never reads or mutates `program_scope.json` or frozen eval snapshots.
- **It reads only the files you pass on the command line.** No repository
  scanning, no network, no hidden state.
- **It never fabricates evidence.** Missing code lines, traces, PoC output,
  duplicate checks or scope claims stay *missing* (recorded in
  `authoring_metadata.evidence_gaps`) so the gate can return `NEEDS_MORE_PROOF`.
- `human_approval_required` is always `true`.

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

Only `--report` and `--out` are required. Every omitted optional input becomes a
recorded evidence gap (not a fabricated value). `--run-gate` runs the gate
*locally* to show you the cautious verdict; a `DO_NOT_SUBMIT` result is **not** an
authoring failure. `--no-timestamp` makes output deterministic for tests.

Exit codes: `0` authoring succeeded (any gate verdict, incl. DO_NOT_SUBMIT);
`1` authoring failed (missing required input, unreadable file, or the produced
JSON failed schema validation).

## What gets extracted

`candidate_author.py` looks for explicit markdown headings / `Label:` lines such
as Title, Root Cause, Vulnerability Details, Impact, Severity, Entry Point,
Preconditions, Attack Path, Affected Contracts/Functions, Code References,
Reproduction, Assumptions, Limitations. Structured facts (PoC pass/fail, duplicate
status, defenses) are read only from explicit markers. See
`documentation/submission_engine/candidate_author.md` for the full extraction and
safe-default table.

## Tests

```bash
/home/dummy/.local/bin/pytest tests/submission/test_candidate_author.py -v
```
