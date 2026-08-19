# Research-Detector Promotion — Decision Brief (for the human)

**Status: PREPARED FOR A HUMAN DECISION. Nothing here has been wired. No config/routing changed.**

This brief assembles (1) the evidence, (2) the exact production wiring points a promotion *would* touch,
(3) the promotion bar status per family, and (4) a rollback story. It exists so the promotion decision can
be made from one page. The authoritative evidence rollup is
`research_family_promotion_status.md`; the per-detector scope/anchors are in `detector_registry.md`.

**Assembled recommendation: HOLD (do not promote any family to production routing now).** The 6-criteria
bar is unmet by every family, and three independent generalization tests (Phase-12/13/14) each returned
**0 holdout recall**. A reversible middle path that needs *no* promotion is already available (see §5).

---

## 1. The families (portfolio: 5 answer-key bugs / 3 architectures / 0 FP)

| Family | Concern | Answer-key bugs | Arch | Anchor |
|---|---|---|:--:|---|
| `multicall_invariant_v1` | `bytes[]` self-delegatecall multicall invariant | 3 (narrow campaign) | 1 | OZ/UniV3 multicall + Size M-01 |
| `permit_asset_binding` | Permit2 asset-binding-missing (Shape A) | 1 | 1 | Revert Lend H-01 / #368 |
| `sibling_function_parity` | sibling missing-component (intra-contract) | 1 | 1 | Blackhole M-04 |
| `cross_contract_sibling_parity` | missing-component (cross-contract) | 1 | 1 | Size M-06 |
| `value_flow_parity` | wrong-value (validator-arg basis) | 1 (med) | 1 | Size M-02 |
| `registry_position_lifecycle` | lifecycle/registry invariant omission (distinct family, not parity) | 2 | 1 | NOYA H-23 + H-18 |

All carry the platform invariant quartet today: `is_gate:false` · `research_only:true` ·
`routes_in_production:false` · `routed_manifest_ids:[]`.

## 2. Why the evidence says HOLD

- **6-criteria bar, every family fails 1, 2, 5, 6** (recall + generalization); all pass 3, 4 (precision).
  Bar: ≥4 recoveries · ≥2 architectures · 0 high-conf FP · route-rate <0.02 · ≥1 non-anchor-outside-subject
  recovery · ≥2 non-anchor recoveries.
- **Phase-12** (Velodrome/Renzo/Wildcat, ≥6 family-shaped *awarded* bugs on 3 new architectures):
  **0 recovered.** Precision generalized (0 FP on ~1,000+ new functions); recall did not. Each miss traces
  to an FP-control/vocab chosen to fit the anchor. `first_non_anchor_recovery = NONE`.
- **Phase-13** (`value_flow_v2`, train/holdout firewall): Training 3/6, **Holdout 0/3**, 0 FP. Better, still
  fails generalization.
- **Phase-14 / 14c** (agentic deep-pass + fresh-holdout): Training 50%→83%, **Holdout 0/3**; the 14c fresh
  blind test on `2024-03-abracadabra-money` reached **40% candidate-coverage** and a genuine blind M-10
  recovery — real signal the queue isn't memorizing, but the wall is now **routing/vocab recall**, one level
  above reasoning. Verdict: **PARTIAL generalization, no promotion.**

The blocker is *not* corpus size — the new protocols already contained family-shaped awarded bugs the
detectors missed. The blocker is **detector generalization**. Routing a single architecture-narrow detector
into production risks FP on architectures it was never validated against; the 0-FP record is a research-corpus
property, not a production guarantee.

## 3. Exact wiring points a promotion WOULD change (none touched here)

If the human decides to promote, these are the precise switches — enumerated so the blast radius is known:

1. **Master flag** — `config/agent_policy.json → research_platform.enabled` (currently `false`). This is the
   opt-in; with it `false` the platform is un-wired and changes no routing.
2. **Per-artifact invariants** — flip `research_only:true`→`false`, `routes_in_production:false`→`true`,
   populate `routed_manifest_ids` for the promoted family only. (Emitted by each detector's
   `*_taxonomy.py`/`*_audit.py` and asserted by `scripts/normalize_research_findings.py`.)
3. **Composition layers** — `scripts/normalize_research_findings.py` (*"rank, don't relabel"*) +
   `scripts/evidence_bundle_gate.py` (*"assemble, don't adjudicate"*, `is_gate:false`) would need their
   output wired into the production gauntlet entry (Step 2 findings set or a pre-3.4 feed), and the bundle
   gate's `is_gate` reconsidered.
4. **Pipeline invocation** — `run_pipeline.sh` invokes **no** detector today (that's what "un-wired" means).
   Promotion adds a step that runs the family and merges its output into `output/findings_*.json` so it rides
   the **unchanged** 3.4 ICE → 3.5 multi-pass → 3.6 fp_pattern_check → 3.7 gates → 3.8 dupe → 3.9 confirm → 4
   triage gauntlet (the fuzz-lane P141 pattern is the reference for "new producer, unchanged gauntlet").
5. **Advisory allowlist (already partially open)** — `config/agent_policy.json → mechanism_advisory.
   mechanism_advisory_allowed_detectors` already lists `registry_position_lifecycle`, and
   `surface_research_only_advisories` (currently `false`) gates whether research-only detectors surface into
   human review. This is the P135 *advisory* channel — distinct from routing (see §5).
6. **Test suite** — `tests/conftest.py` auto-marks research tests `research` (excluded by `pytest -m 'not
   research'`). Promotion moves the promoted family's tests into the production suite.

## 4. Rollback story

The platform is **additive and un-wired**, so rollback is cheap and total:
- **Instant kill switch:** set `research_platform.enabled=false` → production routing is byte-identical to
  today (the gauntlet never sees the detector's output).
- **Full revert:** `git revert` the wiring commit (the §3 changes are one commit) + restore the invariant
  quartet on the promoted artifacts. Because no production file depends on the detectors today, nothing
  downstream breaks.
- **Regression guard:** `./run_pipeline.sh eval-regression` (27 protected catches) must stay 🟢 across the
  promotion and any rollback; a promoted detector that suppresses/reorders a protected catch fails the gate.

## 5. The reversible middle path (available now, needs no promotion)

`registry_position_lifecycle` is **already** in `mechanism_advisory_allowed_detectors`. Flipping
`surface_research_only_advisories=true` would surface research-detector output into **human review as
advisory-only** (`advisory_only=true`, `submission_ready=false`, `requires_human_review=true`) — capped at
10/detector, 40 total — **without** routing, severity assignment, or gate participation. This is strictly
weaker than promotion and fully reversible via the same flag. If the goal is "let a human see these hits on
real audits" rather than "let them auto-route," this is the safe lever and it is one boolean.

## 6. What would reopen the promotion question

Per Phase-12/14c: a family reaching the 6-criteria bar **including ≥2 non-anchor recoveries across ≥2
architectures**, via a deliberate **generalization** pass (broaden affixes/vocab/value-provenance,
each re-validated for 0-FP on the anchor corpus) re-run against the Phase-12 benchmark as a regression test.
The current sharpest lever is **sampler-vocab breadth**, validated on a 3rd fresh holdout under the same
train/holdout firewall. Until then: research-only, un-wired, human-promotion-gated.
