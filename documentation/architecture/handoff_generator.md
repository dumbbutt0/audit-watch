# Handoff Bundle Generator (P84)

Generalizes the one-off **P82 (executable PoC)** + **P83 (submission package)** handoff into a repeatable,
finding-type-aware generator. Given a *promoted finding descriptor*, it emits a complete handoff bundle so that
every future promoted finding produces the same artifacts — with **finding-type-specific narrative templates
but the identical reject-first gate**.

> **Core invariant: "scaffold, don't prove."** The generator NEVER fabricates a result. It emits skeletons to
> be filled from in-scope source and an executable PoC. It never emits a PASS for a finding-specific gate item,
> never emits `REPRODUCED` or `READY_FOR_HUMAN_REVIEW`, and the PoC scaffold carries a guard
> (`assertTrue(false, …)`) that cannot report a false pass. A freshly generated bundle is verified to be
> **un-promotable** by the same `scripts/funnel.py` gates the rest of the platform uses.

Research-only and **un-wired** (`research_only:true`, `routes_in_production:false`, `is_gate:false`; no
reference from `run_pipeline.sh` / `llm_runtime.py` / `agent_policy.json` / `runtime_policy.json`).

## What it emits
For a descriptor it writes a bundle directory containing:
- `submission_draft.md` — platform-neutral report skeleton (same section structure as the proven P83 H-01 draft).
- `evidence_bundle.md` — pinned-version / source-refs / command / failing-output / patch / suite / provenance skeleton.
- `pre_submission_gate.md` — the strict reject-first 9-item checklist; verdict token starts at `DO_NOT_SUBMIT`.
- `reviewer_notes.md` — severity / not-dust / mechanism / patch-proves-root-cause / triager-steps skeleton.
- `<Contract><Function>PoC.t.sol` — a non-passing Foundry scaffold encoding the type's invariant + the
  Level-3 (L1 entry / L2 state-flip / L3 outcome) structure.
- `run_plan.md` — the reproduction plan + the type's L3 requirements + negative control.
- `funnel_record.json` — a Blind-to-Reproducible Funnel record with `poc_status=NOT_STARTED`,
  `submission_status=NOT_STARTED` (un-promotable by construction).

## Finding-type model
- **Narrative fragments** (type-specific) live in `config/handoff_finding_types.json`: root-cause skeleton,
  severity argument, non-dust argument, mitigation options, PoC invariant pattern, evidence prompts.
- **L3 PoC requirements / negative control / severity rationale** are pulled from the existing
  `templates/proof_requirements/<bug_class>.json` taxonomy — reused, not duplicated.
- **The gate is identical across types.** Only the narrative differs; the reject-first checklist + funnel gates
  are shared.

### Seed types (P84)
| `finding_type` | Label | `proof_requirements` bug_class |
|---|---|---|
| `shared_position_fee_routing` | Shared-accounting / fee-routing | `shared_position_fee_routing` (new; the H-01 class) |
| `access_control_privileged` | Access-control / privileged | `missing_auth_accounting_drift` |
| `oracle_price_manipulation` | Oracle / price manipulation | `oracle_slot0_manipulation` |
| `reward_accrual_state_lifecycle` | Reward-accrual / state-lifecycle (P86) | `reward_accrual_state_lifecycle` (new; the Munchables H-05 class — dirty/stale flags, per-user reward checkpoints, reset/update omissions, permanent reward loss) |
| `validation_liveness_counter_scope` | Validation-liveness / counter-scope (P88) | `validation_liveness_counter_scope` (new; the TraitForge H-01 class — global counter vs per-scope limit, invalid validation domain, permanent function-brick, mint/claim/withdraw/settle/forge path blocked, lifecycle phase cannot complete) |

The fee-routing templates are validated to reproduce the **section structure of the proven P83 H-01 package**
(golden test `test_feerouting_template_matches_h01_package_structure`), so the canonical worked example
generalizes rather than being a one-off.

## API (`scripts/handoff_generator.py`, pure logic)
- `render_bundle(descriptor)` → `{filename: content}` in memory (no writes).
- `generate_bundle(descriptor, out_dir, force=False)` → writes the bundle, then **validates reject-first**
  before returning a manifest. Refuses frozen phase dirs and non-empty dirs (without `force`).
- `validate_bundle(out_dir)` → `{ok, violations}`: all files present, PoC has the non-passing guard, gate
  verdict token is `DO_NOT_SUBMIT`, finding-specific items 4–9 are not PASS, and the funnel record cannot be
  promoted to reproduced / submission-ready.
- `build_fields` / `build_funnel_record_stub` — descriptor → placeholders / funnel stub.

### Descriptor fields
`finding_type` (required, must be a registry key), `contract`, `function` (required); optional `finding_id`,
`subject`, `commit` (a real hash pins gate item 1 — a *fact*, not a finding-claim), `title`, `summary`,
`solc_pragma`, and optional `conversion`/`severity_gate`/`adversarial_result`/`safety` carried into the funnel
record.

## How a finding flows through it
```
promoted finding (funnel: CONVERTED_* + safety-clean)
  → generate_bundle()                         # scaffolds PoC + submission package (un-promotable)
  → human/agent implements the PoC from source (L1/L2/L3), removes the guard
  → PoC FAILS on vulnerable source for the expected reason  → fill evidence_bundle / draft / notes
  → pre_submission_gate items 4–9 become PASS                → funnel can advance to POC_REPRODUCED
  → only then, with items 2 (scope) + 3 (duplicate) still PENDING for the human, READY_FOR_HUMAN_REVIEW
```
This is exactly the path H-01 took manually (P82→P83); P84 makes it repeatable.

## Files
| Path | Role |
|---|---|
| `config/handoff_finding_types.json` | finding-type registry (narrative fragments) |
| `templates/proof_requirements/shared_position_fee_routing.json` | new L3 taxonomy entry (H-01 class) |
| `templates/handoff/*.tmpl` | base templates (submission/evidence/gate/notes/PoC/run-plan) |
| `scripts/handoff_generator.py` | pure-logic generator + reject-first validator |
| `tests/handoff/test_handoff_generator.py` | generation / reject-first / refusals / golden-match tests |
| `documentation/research/_p84_demo/<type>/` | one generated demo bundle per seed type (illustrative) |

## Demo
`documentation/research/_p84_demo/` holds one generated bundle per seed type (illustrative subjects). Each is a
scaffold: its gate reads `DO_NOT_SUBMIT`, its PoC carries the non-passing guard, and its funnel record is
un-promotable — demonstrating the reject-first guarantee on real output.

## Next
Run a **second fresh blind→PoC repeat** on a new sealed-key subject and drive its top finding through this
generator end-to-end, to prove the H-01 success was not a one-off.
