# P105 — Reproducibility benchmark (surfacing layer, retrospective)

**What this is:** the deterministic surfacing layer (`inventory` + `enumerate`, via the frozen `run_subject`) run across already-burned blind subjects and scored against documented awarded findings. Objective for coverage/enumeration; retrospective (not blind) for relevance labels.

## Caveats (read first)
- RETROSPECTIVE CEILING, not a blind result: every subject's key was opened in P81e-P102. Enumeration/coverage are objective (the code cannot see the key); only the relevance labels below are post-hoc.
- FUNCTION-GROUNDED SUBSET: each subject scores the awarded findings I can map to a concrete public/external entrypoint that exists in the located source. Several contests had additional findings (severity-demoted, missing-function, cross-contract-only, or NOT_RUN buckets) that are not function-grounded here; recall is reported over THIS benchmark subset and labelled as such.
- WHOLE-FILE SIGNALS: run_subject passes the entire contract source_text to enumerate(), so most keyword signals fire and category coverage is near-saturated. The MEANINGFUL recall metric is therefore function_enumerated (inventory coverage, the P103 repair); category_match is reported but flagged near-trivial.
- run_subject keys source_text by FILE STEM == contract name; functions in a contract whose name != filename stem get empty source_text (core-4 invariants + low confidence) but are STILL enumerated. function_enumerated stays robust.
- Only IQ-AI M-01 carries validation+PoC evidence (P104, CONFIRMED). All other validation/PoC columns are honestly NOT_ATTEMPTED (recall-layer benchmark; no per-subject evidence supplied).

## Aggregate
- Subjects run: **9**; grounded findings scored: **15** (+2 unsurfaceable, excluded).
- **Enumeration coverage (function_enumerated), all:** 100% (15/15)
- Enumeration coverage, high-grounding only: 100% (10/10)
- Invariant generated on awarded fn: 100% (15/15)
- Category match (near-saturated by design): 100% (15/15)
- **False promotions (precision): 0**
- Validation attempted/validated: 1/1 (recall-layer run; evidence supplied only for IQ-AI M-01)
- PoC attempted/succeeded: 1/1 (conversion rate 100% (1/1))

> SURFACING layer is benchmarked across N subjects (objective, retrospective ceiling). Whole-loop conversion is NOT: validation/PoC are NOT_ATTEMPTED except IQ-AI M-01 (P104). category_match is near-saturated by design (whole-file source_text); function_enumerated (inventory coverage, the P103 repair) is the meaningful recall signal.

## Per-finding

| Subject | Finding | Contract.fn | Cat | Sev | Gnd | Fn enum | Inv gen | Cat gen | Fn pos | Validated | PoC try | PoC ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vultisig-2024-06 | VUL-H-01 | ILOPool.claim | reward_fee_distribution | High | high | YES | YES | YES | 15/31 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| munchables-2024-07 | MUN-H-05 | LandManager.transferToUnoccupiedPlot | negative_space_missing_update | High | inferred | YES | YES | YES | 42/113 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| traitforge-2024-07 | TRF-H-01 | TraitForgeNft.mintWithBudget | index_array_integrity | High | high | YES | YES | YES | 169/180 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| traitforge-2024-07 | TRF-M-18 | EntityForging.forgeWithListed | ordering_race | Medium | high | YES | YES | YES | 16/180 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| phi-2024-08 | PHI-H-05 | Cred._removeCredIdPerAddress | role_access | High | high | YES | YES | YES | 17/118 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| phi-2024-08 | PHI-M-07 | Cred.buyShareCredFor | ordering_race | Medium | inferred | YES | YES | YES | 22/118 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| kleidi-2024-10 | KLD-M-02 | Timelock.checkCalldata | index_array_integrity | Medium | inferred | YES | YES | YES | 59/97 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| ramses-2024-10 | RAM-M-02 | RamsesV3Pool.flash | reward_fee_distribution | Medium | high | YES | YES | YES | 46/68 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| ramses-2024-10 | RAM-M-01 | GaugeV3.getPeriodReward | reward_fee_distribution | Medium | inferred | YES | YES | YES | 10/68 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| wildcat-2024-08 | WLD-H-01 | WildcatMarketWithdrawals.executeWithdrawal | per_user_accounting | High | high | YES | YES | YES | 193/211 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| wildcat-2024-08 | WLD-M-05 | AccessControlHooks.grantRole | role_access | Medium | high | YES | YES | YES | 8/211 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| secondswap-2024-12 | SS-H-01 | SecondSwap_StepVesting.transferVesting | per_user_accounting | High | high | YES | YES | YES | 49/85 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| secondswap-2024-12 | SS-H-03 | SecondSwap_StepVesting.claimable | per_user_accounting | High | inferred | YES | YES | YES | 45/85 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| secondswap-2024-12 | SS-M-11 | SecondSwap_Marketplace.spotPurchase | cap_limit | Medium | high | YES | YES | YES | 29/85 | NOT_ATTEMPTED | no | NOT_ATTEMPTED |
| iq-ai-2025-01 | IQ-M-01 | LiquidityManager.moveLiquidity | cross_contract_consistency | Medium | high | YES | YES | YES | 43/51 | VALIDATED | YES | YES |

### Unsurfaceable findings (excluded from recall denominators)
- vultisig-2024-06 VUL-M-01: missing-function class: the bug is an absent function/check, so there is no enumerable entrypoint to surface
- iq-ai-2025-01 IQ-H-01: constructor-constant / out-of-scope: not an enumerable runtime public/external entrypoint

### Per-subject coverage / staging
- **vultisig-2024-06** (P81e): public/external enumerated=31, staged_files=15 (collisions 0), runtime=12ms; false_promotions=0
- **munchables-2024-07** (P85): public/external enumerated=113, staged_files=13 (collisions 0), runtime=46ms; false_promotions=0
- **traitforge-2024-07** (P87): public/external enumerated=180, staged_files=19 (collisions 0), runtime=37ms; false_promotions=0
- **phi-2024-08** (P89): public/external enumerated=121, staged_files=9 (collisions 0), runtime=46ms; false_promotions=0
- **kleidi-2024-10** (P91): public/external enumerated=97, staged_files=17 (collisions 0), runtime=55ms; false_promotions=0
- **ramses-2024-10** (P93): public/external enumerated=73, staged_files=23 (collisions 0), runtime=31ms; false_promotions=0
- **wildcat-2024-08** (P95): public/external enumerated=222, staged_files=39 (collisions 0), runtime=88ms; false_promotions=0
- **secondswap-2024-12** (P97): public/external enumerated=85, staged_files=15 (collisions 0), runtime=19ms; false_promotions=0
- **iq-ai-2025-01** (P102/P103/P104): public/external enumerated=55, staged_files=7 (collisions 0), runtime=23ms; false_promotions=0

## Reading the result
- High & consistent `function_enumerated` => the **coverage** half of P104's surfacing is **capability, not luck**: the P103 inventory repair captures the awarded entrypoint across every architecture tested (incl. the hard cases: a sibling-file `executeWithdrawal` and an underscore-named-but-`public` `_removeCredIdPerAddress`).
- **Honest counterweight — coverage != ranking.** `function_position` is alphabetical, not scored: awarded functions sit mid-list (e.g. 193/211, 169/180). In the recall-only run there is NO ranking signal, because ranking needs the per-candidate evidence/validation layer (the P102 selection ceiling). So a human still faces the whole enumerated surface; the pipeline guarantees the answer is IN the set, not that it is on top.
- `false_promotions=0` confirms the recall-only run promotes nothing without evidence (precision preserved): recall widened, promotions did not.
- Net: **coverage generalizes; selection/ranking and whole-loop conversion remain evidence-and-capability-bound** (the separately-studied P107/P108 gap). This benchmark is a retrospective CEILING over a function-grounded subset, not a blind recall measurement.
