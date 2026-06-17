# Submission Workflow

End-to-end path from a candidate finding to an approved, human-filed submission.
The automated layer stops at "ready"; **a human always submits**.

```
   candidate finding
        │
        ▼
  ┌─────────────────────────────┐
  │ 1. Author submission_candidate.json │   (human or agent)
  └─────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────┐
  │ 2. Run submission_gate.py    │   (deterministic, standalone)
  └─────────────────────────────┘
        │
        ├── DO_NOT_SUBMIT ────────► stop. Fix scope/privilege/duplicate/severity, or drop.
        │
        ├── NEEDS_MORE_PROOF ─────► add PoC / call trace / evidence, re-run.
        │
        ├── READY_FOR_HUMAN_REVIEW ─► human compares duplicates / resolves uncertainty.
        │
        └── READY_TO_SUBMIT_AFTER_APPROVAL
                 │
                 ▼
        ┌─────────────────────────────┐
        │ 3. Render platform template  │   templates/immunefi_submission.md
        │    (Immunefi / Code4rena)    │   templates/code4rena_submission.md
        └─────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │ 4. Human reviews + approves  │   checklists/pre_submission_checklist.md
        └─────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │ 5. Human submits manually    │   (the layer never auto-submits)
        └─────────────────────────────┘
```

## Step 1 — Author the candidate

Copy the closest example from `submission/examples/` and fill every required
field. The richer the candidate, the further it can advance:

- **Scope**: set `scope_status`, `in_scope_asset`, and
  `bounty_program_mapping.impact_in_scope`. List any out-of-scope dependency in
  `out_of_scope_risks` — the gate treats a depended-on entry there as a blocker.
- **Reachability**: fill `attacker_entrypoint`, `call_trace`, `assumptions`,
  `state_transition`, and `defense_analysis`.
- **Proof**: for High/Critical, attach a runnable PoC (`proof_type=runnable_poc`,
  `poc_status=passing|compiling`, `poc_path`, `reproduction_steps`).
- **Duplicates**: actually perform the searches and set
  `duplicate_check_status` / `known_issue_check_status` honestly; record overlaps
  in `prior_audit_overlap`.

## Step 2 — Run the gate

```bash
python submission/gates/submission_gate.py \
    --candidate path/to/submission_candidate.json \
    --report-out path/to/readiness_report.md
```

Read the readiness report. `Blockers` must be empty to advance past
`DO_NOT_SUBMIT`; `Needs more proof` must be empty to advance past
`NEEDS_MORE_PROOF`.

## Step 3 — Render the platform submission

Only after the gate clears the candidate, fill the platform template
(`templates/immunefi_submission.md` or `templates/code4rena_submission.md`).
Do **not** carry internal sections (Quality Checklist, Severity Justification
headings) into the submitted text, and avoid "permanently"/"all funds"
overclaims unless literally proven.

## Step 4 — Human approval

Walk `checklists/pre_submission_checklist.md`. A human must read the readiness
report, confirm each gate item, and explicitly approve **this** submission.

## Step 5 — Human submits

The submission is filed by a human on the platform. This layer has no
integration that submits on its behalf — by design.

## Why this is isolated from the detection pipeline

The submission engine never reads `output/`, `data/triage/`, or
`audit_context.py`, and never writes into pipeline directories. It consumes only
the candidate file you hand it. This keeps submission decisions auditable and
keeps the detection pipeline untouched. If you want to seed a candidate from an
existing finding, do the mapping by hand (or with a separate read-only tool kept
under `submission/`); the gate itself stays standalone.
