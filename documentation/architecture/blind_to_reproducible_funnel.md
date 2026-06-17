# Blind-to-Reproducible Funnel

A **read-only** dashboard surface (`/funnel`) that tracks a research-track finding through its whole
lifecycle — from a surfaced lead, through blind conversion and the severity gate, into a PoC handoff,
to an **executable, reproduced** proof, and finally to *submission readiness*. It extends the existing
dashboard (it does not replace it) and mirrors the isolated-page pattern of the validation console
(`/validation`) and the candidate-detail view (`/candidates`).

> **Core invariant: this surface signals readiness; it does not submit, route, or set a production
> severity.** Pipeline status is **computed reject-first** from evidence — a record's declared status is
> never trusted over the gate functions. `REPRODUCED` means an executable proof exists; it does **not**
> mean submitted. `SUBMITTED` only ever appears when a human records it.

This funnel exists because, as of P82, the scanner demonstrated the full path end-to-end for the first
time, and the dashboard had no model for PoC-readiness or submission-readiness:
- **P81e** — fresh sealed-key *blind* conversion PASS; Vultisig 2024-06 **H-01 `ILOPool.claim`** found
  blind as a CLEAN_HIT; safety clean (0 SOURCE_FALSE / 0 unsupported-READY / 0 HARD_FAIL / 0 severity FP);
  controls clean.
- **P82** — PoC handoff pilot **REPRODUCED**; an executable Foundry test proves the H-01 fee-loss
  mechanism, fails on vulnerable source for the expected reason, passes under a minimal patch, breaks no
  unrelated tests.

## The funnel stages

```
Lead surfaced → Investigation started → Investigation safe → Converted → Severity gated
  → PoC handoff → Reproduced → Submission package → Human review → (human-recorded) Submitted
```

Computed pipeline statuses (`scripts/funnel.py` `PIPELINE_STATUS`):

| Stage | Status | Meaning |
|---|---|---|
| Lead | `LEAD_SURFACED` / `INVESTIGATION_STARTED` / `INVESTIGATION_SAFE` | surfaced by a lens; investigation begun; no SOURCE_FALSE/unsupported-READY/HARD_FAIL |
| Converted | `CONVERTED_CLEAN_HIT` / `CONVERTED_STRONG_PARTIAL` / `CONVERTED_ADJACENT` | blind conversion result |
| Rejected | `REJECTED_OR_ABSTAINED` | rejected or honestly abstained (NEEDS_CONTEXT) |
| Severity | `SEVERITY_GATED` | demoted/blocked by the severity-impact gate |
| PoC | `POC_HANDOFF_STARTED` / `POC_REPRODUCED` / `PARTIAL_REPRO` / `NOT_REPRODUCED` | PoC effort state |
| Submission | `SUBMISSION_PACKAGE_STARTED` / `SUBMISSION_READY_HUMAN_REVIEW` | drafting / ready for a human to verify scope, dupe, program rules, wording |
| Other | `BLOCKED` / `NOT_RUN` | explicit blocker; not investigated (excluded from denominators) |

Note `SUBMITTED` is **not** a pipeline status. It is only a value of `submission_status`, set by a human.
The pipeline tops out at `SUBMISSION_READY_HUMAN_REVIEW`.

## Promotion rules (reject-first, default-deny)

Each gate returns `(ok, reasons)`; `ok` is True only when **every** condition holds.

- **→ `POC_HANDOFF_STARTED`** (`can_promote_to_poc_handoff`): conversion ∈ {CLEAN_HIT, STRONG_PARTIAL}
  **and** severity gate passed **and** adversarial review PASS or bounded-uncertainty **and** no severity-FP
  marker **and** no SOURCE_FALSE / unsupported-READY / HARD_FAIL.
- **→ `POC_REPRODUCED`** (`can_promote_to_poc_reproduced`): executable test/trace exists **and** vulnerable
  source fails for the expected reason (recorded) **and** the source-grounded bug chain is complete **and**
  no unsupported claims **and** the root-cause patch passes when one is provided **and** unrelated tests are
  not broken.
- **→ `SUBMISSION_READY_HUMAN_REVIEW`** (`can_promote_to_submission_ready`): `POC_REPRODUCED` or a strong
  `PARTIAL_REPRO` **and** an evidence bundle exists **and** a pre-submission gate exists **and** duplicate
  check ≠ DUPLICATE_CONFIRMED **and** scope check ≠ OUT_OF_SCOPE **and** severity check == SUPPORTED **and**
  no unsupported claims remain.

## Data objects

- **PoC evidence** (per finding): `poc_status` (NOT_STARTED / IN_PROGRESS / REPRODUCED / PARTIAL_REPRO /
  NOT_REPRODUCED), `poc_phase`, `poc_artifact_dir`, `test_file`, `test_command`, `vulnerable_result`,
  `patched_result`, `unrelated_tests_result`, `minimal_patch_validated`, `source_chain_complete`,
  `unsupported_claims_present`, `remaining_blockers`, `human_submission_ready`.
- **Submission readiness** (per finding): `submission_status` (NOT_STARTED / DRAFTING /
  READY_FOR_HUMAN_REVIEW / BLOCKED / SUBMITTED), `draft_path`, `evidence_bundle_path`,
  `pre_submission_gate_path`, `reviewer_notes_path`, `duplicate_check_status`, `scope_check_status`,
  `severity_check_status`, `final_human_gate`.
- **Funnel metrics**: leads surfaced, investigated, clean hits, strong partials, severity FPs before/after
  gate, controls promoted incorrectly, PoC handoffs started, PoCs reproduced, partial reproductions, not
  reproduced, submission packages ready for human review, blocked submissions, top blocker reasons.
  **NOT_RUN records are excluded from every denominator** and reported separately as `not_run`.

## Data sources (read-only)

Records live in `documentation/research/funnel/funnel_records.json` — truthful transcriptions of the actual
P81e/P82 runs. The loader (`funnel.load_records`) normalizes each record and **enriches read-only** from the
frozen phase artifacts named in each record's `source_refs`:
- `_p81e/scores.json` — conversion result, safety counters, severity-gate behavior, controls.
- `_p82_h01_claim_poc/_freeze/phase82_freeze.json` — cross-checks the asserted PoC status (a mismatch is
  surfaced as a `consistency_warning`; enrichment never *upgrades* a status).
- `_p82_h01_claim_poc/handoff_report.md` / `bug_chain.md` — the human-readable evidence bundle.

The frozen artifacts under `_p81e/` and `_p82_h01_claim_poc/` are the source of truth and are **never**
mutated by this surface.

## Canonical worked example — Vultisig 2024-06 / H-01 (P82)

| Field | Value |
|---|---|
| Subject | Vultisig 2024-06 |
| Finding | H-01 |
| Function | `ILOPool.claim` |
| Conversion | CLEAN_HIT (P81e, blind) |
| Pipeline status | **`POC_REPRODUCED`** |
| PoC status / phase | REPRODUCED / P82 |
| PoC command | `forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv` |
| Vulnerable result | Fails as intended — INVESTOR_2 reverts/loses when claiming second after another claimant collects fees |
| Patch validation | PASS — `collect(max,max)` → `collect(uint128(amount0), uint128(amount1))` makes the invariant hold; source restored |
| Impact | LPs lose their fee share to `feeTaker`; once fees are material, later claims revert and vested funds are locked |
| Submission status | **NOT_STARTED** |
| Human readiness | Ready for P83 submission package, **not auto-submitted** |

On the dashboard this row shows the green **POC_REPRODUCED** status **and** a distinct amber
"⚠ NOT submitted — human review required" note — the reject-first display guarantee in action. The submission
gate is intentionally *not* satisfied (no pre-submission gate exists yet), so the finding cannot advance to
`SUBMISSION_READY_HUMAN_REVIEW` until a human builds the P83 package.

## Files

| Path | Role |
|---|---|
| `scripts/funnel.py` | pure logic — enums, normalization, reject-first gates, metrics, row builder, read-only loader |
| `documentation/research/funnel/funnel_records.json` | seed data (Vultisig H-01 + P81e context rows) |
| `scripts/dashboard.py` `/funnel`, `/api/funnel` | thin read-only routes |
| `dashboard/funnel.html`, `dashboard/funnel.js` | standalone page (metrics strip + findings table) |
| `tests/funnel/test_funnel.py` | gate / reject-first / NOT_RUN / backward-compat / seed tests |

## Related
- **Handoff bundle generator** (`handoff_generator.md`): turns a promoted funnel finding into the same
  PoC + submission-package bundle automatically (finding-type templates, identical reject-first gate). Its
  generated `funnel_record.json` stubs slot straight into this funnel as un-promotable scaffolds.

## How to run
```bash
python scripts/dashboard.py        # FastAPI on http://localhost:8765
# open http://localhost:8765/funnel
```
Fully isolated from the production pipeline dashboard at `/`. It reads only research-track artifacts and
never routes, submits, or sets a production severity.
