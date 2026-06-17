# Audit-Watch — Current Platform State

A snapshot of what exists and its status. The single most important distinction: **research-only / un-wired** vs
**production / wired**. Nothing in the research track routes, submits, or sets production severity/exploitability.

## Status legend
- **VALIDATED (research-only, un-wired):** built, tested, validated; `routes_in_production:false`.
- **PLANNED (research-track):** not built; a future research-track layer.
- **PRODUCTION (wired):** pre-existing, part of the live audit pipeline.

---

## Validated Components — research-only, un-wired
| Component | Files | What it does | Status / evidence |
|---|---|---|---|
| `multicall_invariant` | `scripts/multicall_invariant_{taxonomy,audit}.py`, `config/multicall_invariant_patterns.json` | detect `bytes[]` self-delegatecall multicall executors | RESEARCH-STABLE / NARROW SCOPE CONFIRMED (20-target eval) |
| B1 inherited-multicall sidecar | `scripts/build_inherited_multicall_sidecar.py` | surface inherited OZ/UniV3 multicall for the deriving contract (visibility only) | research-only; B1 PARTIALLY VISIBILITY; 0 new FP |
| `permit_asset_binding` | `scripts/permit_asset_binding_{taxonomy,audit}.py`, `config/permit_asset_binding_patterns.json` | detect Permit2 asset-binding-missing (Shape A) | RESEARCH-STABLE / HIGH PRECISION VALIDATED (7 + 20-target) |
| `sibling_function_parity` | `scripts/sibling_function_parity_{taxonomy,audit}.py`, `config/sibling_function_parity_patterns.json` | sibling missing-component (intra-contract) | RESEARCH-STABLE / architecture-narrow (Blackhole M-04; 0 FP) |
| `cross_contract_sibling_parity` | `scripts/cross_contract_sibling_parity_{taxonomy,audit}.py`, `config/cross_contract_sibling_parity_patterns.json` | missing-component across module contracts | RESEARCH-STABLE / NARROW (Size M-06; 0 FP) |
| `value_flow_parity` | `scripts/value_flow_parity_{taxonomy,audit}.py`, `config/value_flow_parity_patterns.json` | wrong-value (validator-arg basis) | RESEARCH-PROTOTYPE / narrow (Size M-02; 0 FP) |
| `registry_position_lifecycle` | `scripts/registry_position_lifecycle_{taxonomy,audit}.py`, `config/registry_position_lifecycle_patterns.json` | lifecycle/registry invariant omission (**distinct family, not parity**) | RESEARCH-STABLE / narrow (NOYA H-23 + H-18; 0 FP) |
| Normalization layer | `scripts/normalize_research_findings.py`, `config/research_finding_normalization.json`, `schemas/research_finding_normalized.schema.json` | one comparable record per candidate + review_priority ("rank, don't relabel") | research-only; demo over both detectors |
| Evidence Bundle Gate | `scripts/evidence_bundle_gate.py`, `config/evidence_bundle_gate.json`, `schemas/evidence_bundle.schema.json` | evidence-completeness triage ("assemble, don't adjudicate") | research-only; demo 6/6 READY |

**Tests:** `tests/{multicall_invariant,permit_asset_binding,sibling_function_parity,cross_contract_sibling_parity,
value_flow_parity,registry_position_lifecycle,research_normalization,evidence_bundle_gate}/` — all passing.
**Integrity:** the frozen-platform files verify 0-drift across phases. All components are **un-wired** (no
reference from routing/gates/run_pipeline/agent_policy/submission). Family-level promotion status (the
5-criteria bar; "validated, no promotion yet"): `research_family_promotion_status.md`.

## Research / Planned Components — research-track, NOT built
- **Judge layer** (research-track) — would consume READY evidence bundles to estimate plausibility. *Not built.*
- **PoC feasibility layer** (research-track) — would estimate PoC-ability / missing proof. *Not built.*
- **Submission readiness layer** (research-track) — would gate research findings for human submission review.
  *Not built.*

> These are **distinct** from the production systems below. Production already has wired judge/PoC/submission; the
> research-track versions (which would consume evidence bundles) do not exist yet, and bridging the research track
> into production is a future, human decision.

## Production Components — pre-existing, wired (NOT part of the research track)
| System | Representative files | Role |
|---|---|---|
| Audit pipeline (ICE) | `run_pipeline.sh`, CLAUDE.md Steps 0.5→9 | analyze → specialists → synthesis → ICE → gates → triage → PoC → submit |
| Coverage manifest + Step 3.9 gate | `scripts/build_coverage_manifest.py`, coverage gate | enumerates denominator; hard-blocks the review gate |
| Step-2 specialists | `agents/`, `/ite-audit` | reentrancy/access/oracle/… recall lenses |
| Triage + severity | `scripts/triage_*.py`, `scripts/calibrate_severity.py`, `schemas/severity_calibration.schema.json` | ICE re-score, calibrated severity (human-reviewed) |
| Exploitability model | `scripts/model_exploitability.py`, `schemas/exploitability.schema.json` | per-finding exploitability modeling |
| Judge simulation | `scripts/judge_simulate.py`, `schemas/judge_simulation.schema.json` | 5-persona adversarial judge |
| PoC engine | `scripts/{build_poc_queue,generate_poc_plan,generate_poc_test,run_poc_tests,poc_validation_gate}.py` | L1–L3 PoC build/run/validate |
| Submission engine | `submission/` (gates: defense/duplicate/evidence/human_approval/impact_severity/poc/reachability/scope + code4rena/immunefi renderers) | submission-readiness gating; **never auto-submits** |
| Confirm / dupe gates | `scripts/{multi_pass_confirm,confirm_gate,pre_submission_gate,pre_submission_dupe_screen}.py` | confirmation + duplicate screening |

> The production pipeline is human-in-the-loop and gate-protected; it does not autonomously submit, and severity/
> exploitability are calibrated with human review. See `documentation/pipeline.md` and `documentation/architecture.md`.

---

## One-line summary
**Validated & research-only:** 6 detectors (multicall · permit · sibling · cross-contract · value-flow ·
registry-lifecycle) + B1 sidecar + normalization layer + evidence-bundle gate (un-wired, 0-drift; portfolio
5 bugs / 3 architectures / 0 FP — **validated, no promotion yet**, see `research_family_promotion_status.md`). **Planned & research-only:** judge / PoC-feasibility / submission-readiness research layers.
**Production & wired (separate track):** the full ICE audit pipeline incl. its own exploitability/judge/PoC/
submission systems. The two tracks are **not connected**; connecting them is a future decision.
