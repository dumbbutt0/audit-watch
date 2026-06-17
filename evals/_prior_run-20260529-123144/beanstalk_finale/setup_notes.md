# Phase 1 — Target Setup Notes (Beanstalk Finale eval)

## Provenance / integrity disclosure (read first)
This is a **benchmark**, not a live submission target. Critically, the independent Audit-Watch run
on this target **already happened, blind, earlier** and is preserved at `audits/beanstalk-2024-05/`
(workspace `created_at` `2026-05-28T21:49:53Z`; finding artifacts timestamped through
`2026-05-29 07:57`). That run completed **before** the answer key was ever opened in this project.

A fresh "blind" re-run is deliberately **not** performed here because (a) the operator is now
answer-key-aware (re-running would not be blind), and (b) the eval must spend **zero API credits**.
Per the eval's own rules ("do not rewrite history after reading the answer key"; "preserve
timestamps proving the independent run happened first"), the legitimate Phase-2 artifact is the
pre-existing blind run — used as-is, read-only. No pipeline stage was executed for this eval.

## Target
- **Contest:** CodeHawks `2024-05-beanstalk-the-finale` (Cyfrin). _Note: the local `meta.json`
  labels the platform "Code4rena / beanstalk-code4rena-2024-05" — a local mislabel; the canonical
  source is the CodeHawks competition._
- **Source location (in-repo):** `contracts/2024-05-beanstalk-the-finale/protocol/contracts`
  (recorded as `meta.primary_contract_dir`). No external download required — source already vendored.
- **nSLOC:** 12,285 (per the contest scope).
- **Known valid findings (answer key, sealed until Phase 3):** 81 total — 22 High / 31 Medium / 28 Low.
- **Commit hash:** not recorded in `meta.json`; source is the vendored contest snapshot under
  `contracts/2024-05-beanstalk-the-finale/`.

## Build / test
- **Framework:** Foundry (`foundry.toml` under `protocol/`). Build/test: `forge build` / `forge test`.
- **Static analysis:** Slither via `tools/static_analysis.py` → `output/static.json` (ran in the blind run).

## Dependency setup
Standard Audit-Watch setup (`pip install -r requirements.txt`; Slither/solc); the blind run used the
repo `.venv`. No additional setup was needed for this read-only eval.

## Failed setup steps
None for the eval itself (read-only). For the original blind run: the LLM-backed validation half
(triage / multi-pass / synthesis / PoC) did **not** execute (no API key that session), so the
independent results reflect the **raw detection layer only** — a HIT here means "a detector found
it," not "the pipeline would have submitted it." This is carried into every downstream deliverable.

## Eval workspace
- `evals/beanstalk_finale/` — independent results, board, scorecard, failure analysis, artifacts.
- `documentation/evals/beanstalk_finale/` — pipeline_discovery, optimization_plan, final_eval_report, backlog.
- Prior analysis (backing detail, hyphen dir): `documentation/evals/beanstalk-finale/`.
