# Audit-Watch — Research-Family Promotion Status

Authoritative rollup of the research-only detector families and whether any is ready for **production
promotion** (routing/wiring). All families are research-only / un-wired (`is_gate:false`,
`research_only:true`, `routes_in_production:false`, `routed_manifest_ids:[]`); per the platform hard rule
(`platform_invariants.md`, `research_methodology.md`, CLAUDE.md) **promotion is a separate, later, human
decision** — RESEARCH-STABLE ≠ production.

## Conclusion (current — updated after the Phase-12 generalization benchmark)

> **Research portfolio validated as vulnerability *families*; the *detectors* are anchor-overfit and do
> NOT generalize. No production promotion.**
> The shapes are real and recurring across unrelated protocols, but the **Phase-12 benchmark**
> (`documentation/evals/promotion_benchmark/`) tested the 6 detectors against **3 new protocols / 3
> architectures** (Velodrome, Renzo, Wildcat) containing **≥6 family-shaped *awarded* bugs** and they
> recovered **zero**. Precision generalized (0 FP on ~1,000+ new functions); recall did not. Each miss
> traces to an FP-control/vocabulary chosen to fit the anchor. `first_non_anchor_recovery = NONE` for all.

## Phase-13 generalization attempt (value_flow_v2)

`value_flow_parity` was generalized (3 deterministic wrong-value sub-shapes; 0 anchor FP; anchor M-02
preserved) under a **train/holdout firewall**. Result: **Training Recall 3/6, Holdout Recall (primary)
0/3, FP Rate 0.** The shapes transfer across the training protocols but **did not transfer to an
uninspected holdout** (its wrong-value bugs are different sub-shapes). So value_flow is now *better* (3
transferable, FP-clean sub-shapes) but **still fails the generalization criteria** — `Holdout Recall = 0%`.
No promotion. Evidence: `documentation/evals/promotion_benchmark/generalization_results.md`. The new
**Generalization/Holdout Recall** is the primary KPI for promotion (above raw recovery count or FP rate).

## Promotion bar (6 criteria — ALL required)

A research family is promotable only when:
1. **≥4** answer-key recoveries
2. **≥2** protocol architectures
3. **0** high-confidence FP across the 20-subject eval
4. corpus route-rate **< 0.02**
5. **≥1 non-anchor recovery outside the detector's design subject**
6. **≥2 non-anchor recoveries** (generalization — not re-detecting the design architecture; added Phase 12)

This supersedes the earlier 3-criteria parity bar (`documentation/evals/value_flow_parity_eval/parity_cluster_status.md`).
Criteria 4–6 guard against architecture-narrow detectors that only echo their anchor. **Phase-12 status:
every family fails criteria 1, 2, 5, 6 (recall/generalization) and passes 3, 4 (precision).**

## Families & status

`registry_position_lifecycle` is a **distinct family**, NOT part of the parity cluster:
`parity = sibling/path mismatch` · `registry_position_lifecycle = lifecycle/registry invariant omission`.

| Family | Concern | Bugs (answer-key) | Arch | high/med FP | route-rate | non-anchor-outside-subject | Bar met | Status |
|--------|---------|---|:--:|:--:|:--:|:--:|:--:|--------|
| `sibling_function_parity` | sibling missing-component (intra-contract) | 1 — Blackhole M-04 | 1 (ve3,3) | 0 | ~0 | no | ✗ | research-stable |
| `cross_contract_sibling_parity` | missing-component (cross-contract) | 1 — Size M-06 | 1 (lending) | 0 | 0.0003 | no | ✗ | research-stable |
| `value_flow_parity` | wrong-value (validator-arg basis) | 1 — Size M-02 (med) | 1 (lending) | 0 | 0.0002 | no | ✗ | research-prototype |
| **`registry_position_lifecycle`** | **lifecycle/registry omission** | **2 — NOYA H-23 (high) + H-18 (med)** | **1 (connector-yield)** | **0** | **0.0003** | no (SNXV3 in-subject) | ✗ | **research-stable** |
| `multicall_invariant` | `bytes[]` self-delegatecall invariant | 3 (narrow campaign) | 1 | 0 routed | tight | — | ✗ | research-stable (narrow-confirmed) |
| `permit_asset_binding` | Permit2 asset-binding-missing | 1 — Revert #368 | 1 | 0 | tight | — | ✗ | research-stable |

Per-family eval evidence: `documentation/evals/{sibling_function_parity,cross_contract_sibling_parity,
value_flow_parity,registry_position_lifecycle}_eval/routing_score.md`;
`documentation/evals/{multicall_invariant_final_evaluation_report.md, permit_asset_binding_validation.md}`.

## Portfolios

**Structural-comparison portfolio** (the 4 cross-function-structure families — sibling, cross-contract,
value-flow, registry):

```
recovered answer-key bugs : 5   (Blackhole M-04 · Size M-06 · Size M-02 · NOYA H-23 · NOYA H-18)
architecture groups       : 3   (Blackhole ve(3,3) · Size lending · NOYA connector-yield)
high/medium FP            : 0
```

Validated as a cluster, but **no single detector** meets criteria 1+2+5 — each is still anchored to one
architecture. The cluster's strength is breadth-of-shape, not any one routable family.

**Original research detectors** (`multicall_invariant`, `permit_asset_binding`): independently
RESEARCH-STABLE, also architecture-narrow, also below the bar. Tracked in `detector_registry.md`.

## Why not promote (the conservative call)

- Each family has fired on **one** protocol architecture (sibling→Blackhole, cross/value→Size,
  registry→NOYA, multicall/permit→their anchors). Criterion 2 (≥2 architectures) and criterion 5
  (non-anchor recovery outside the design subject) are unmet everywhere.
- Routing a single architecture-narrow detector risks production FP on the architectures it was never
  validated against. The portfolio's 0-FP record is a *research-corpus* property, not a production
  guarantee.
- The platform hard rule already forbids autonomous promotion; this rollup records *why* the conservative
  default is also the correct one right now.

## What would change the decision (revised by Phase 12)

Promotion becomes reconsiderable only when a family reaches the 6-criteria bar **including ≥2 non-anchor
recoveries across ≥2 architectures**. The Phase-12 benchmark showed the blocker is **not** corpus size —
the new protocols already contained family-shaped *awarded* bugs the detectors missed. The blocker is
**detector generalization**: each lens's FP-controls/vocabulary are bound to its anchor. So the next step
(if pursued) is a deliberate **generalization** pass (broaden affixes/vocab/value-provenance per
`promotion_benchmark/corpus_gap_analysis.md`), **each re-validated for 0-FP on the anchor corpus**, then
re-run the Phase-12 benchmark (now the regression test). Until a family shows ≥2 non-anchor recoveries:
**research-only, un-wired, human-promotion-gated.**

## Phase-14 update — the agentic deep-pass (Experiment E1)

Rather than generalize the deterministic detectors further, Phase-14 tested whether an **agentic deep-pass
over detector candidates** crosses the wall (`documentation/evals/promotion_benchmark/agentic_deep_pass_results.md`).
Result: **Training Recall 50%→83%** (recovered Velodrome H-03 + M-10 that the detector routed only at *low*),
**Holdout Recall 0/3**, **0 hallucinated findings**. The 4-rung ablation attributes the training gain to
**reasoning** (not packaging, not KB). The holdout 0 has a precise cause: the deterministic lenses route **0**
candidates on ECG's wrong-value bugs, so a deep-pass-over-routed-candidates never sees them — the wall is
**routing recall**, one level above reasoning. **No promotion** (the deep-pass is research-only / un-wired,
`deep_pass` SKILL_MAP entry `optional:True`). It does not change any detector-family status; it reframes the
next lever as **surface/routing breadth** (E1b: a bounded high-surface deep-pass queue), re-measured under the
same train/holdout firewall.

**Phase-14c (E1c) — fresh-holdout generalization test.** The E1b sampler was run **frozen** (not tuned) on a
brand-new protocol (`2024-03-abracadabra-money`) with **blind** reasoning (C4 report unread until the decisions
were hashed). Result: Fresh Holdout Candidate Coverage Recall **2/5 = 40%** at a tolerable Queue Size **79**,
plus a genuine **blind** recovery of C4 **M-10** (`MagicLpAggregator._getReserves` missing-return → LP oracle
= 0). **Verdict: PARTIAL generalization** — the queue is not memorizing the benchmark (it found a real awarded
bug on an unseen protocol), but coverage is **vocabulary-limited** (the name-regex misses `latestAnswer`/
`buyShares`). **No promotion** — it sharpens the next lever to **sampler-vocab breadth, validated on a 3rd fresh
holdout** (same overfit discipline). Docs: `documentation/evals/promotion_benchmark/fresh_holdout_results.md`.


## P311 — Advisory-only promotion (human-gated, 2026-06-10)
The 8 P303/P305/P307 lenses (nonstandard_permit, erc4626_limit_fidelity, eip712_domain_separator_staleness,
beneficiary_guard_parity, admin_capability_parity, crosschain_min_gas_unchecked, crosschain_refund_recipient,
fee_wrapper_bypass) were PROMOTED **advisory-only** by human decision: wired to RUN in run_pipeline.sh
(coverage_review_gate + coverage-gate) and SURFACED in advisory_escalation_gate.json under
`promoted_advisory_lens_hits` (routed_to:advisory_only). They are FP-safe (0 candidates on every unrelated codebase)
but KNOWINGLY OVERRIDE criteria 1/2/5/6 of the promotion bar above (0 proven non-anchor recoveries). Mitigation:
advisory-only — they NEVER apply_update / route / gate / set severity (`promoted_advisory_routed` is always 0). The
strict-escalation upgrade (route → needs_deep_pass) is DEFERRED until each earns >=2 non-anchor recoveries. Reversible:
remove the run_pipeline invocations + the advisory_escalation_gate PROMOTED_ADVISORY_LENSES block + restore the flags.
