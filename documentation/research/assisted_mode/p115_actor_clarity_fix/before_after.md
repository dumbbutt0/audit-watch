# P115 — actor_clarity signature-modifier fix: before / after

**What P114 found:** `rank_signal_probe`'s `actor_clarity` (permissionless) read only the function BODY, so access
MODIFIERS declared in the signature (`onlyBorrower`, `onlyPhiFactory`) were missed and privileged functions ranked
as permissionless. **What P115 does:** `actor_clarity` now also reads the function SIGNATURE, and the cross-subject
discovery selectors apply the permissionless soft gate, so privileged functions are correctly demoted. Research-only,
un-wired. No frozen machinery changed; no production wiring.

## The two-part fix
1. **Flag (`scripts/assisted/rank_signal_probe.py`):** new `_function_signatures()` captures the declaration
   (incl. modifiers); `_features_for(..., signature=...)` marks a function role-guarded if a guard appears in the
   body OR the signature (reusing `map_invariant_defenses._PRIMS["role_auth_modifier"]` for `only*` plus a small
   `requiresauth|restricted|authorized` set). `_function_bodies`' return contract is unchanged (self_kill depends on
   it) — signatures are a separate helper.
2. **Selection gate (`assisted_fresh_run.select_candidate`, `terminal_distribution.select_next_n`):** the global
   cross-subject sort now applies the permissionless soft gate `(0 if permissionless else 1, -score, …)` — mirroring
   `rank_candidates_prototype.rank_surface` — so the corrected flag actually demotes privileged functions. (Without
   this second part the flag fix would be cosmetic, because the discovery selectors sorted by score alone.)

## Per-case (the P114 cases)
| Function | actor_clarity BEFORE (body-only) | AFTER (signature-aware) | Signature modifier |
|---|---|---|---|
| WildcatMarket.closeMarket | 1.0 (wrong) | **0.0 (privileged)** | `external onlyBorrower nonReentrant …` |
| PhiNFT1155.claimFromFactory | 1.0 (wrong) | **0.0 (privileged)** | `external payable whenNotPaused onlyPhiFactory` |
| RamsesV3Pool.swap | 1.0 | 1.0 (unchanged — no role modifier) | `external override` |
| WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches | 1.0 | 1.0 (unchanged — `nonReentrant` is not a role guard) | `public nonReentrant …` |

## actor_clarity discrimination (P106 metric), recomputed in-memory
| | lift | surface_base_rate | mean_awarded_percentile |
|---|---|---|---|
| BEFORE | −0.0451 | 0.9853 | 0.9402 |
| AFTER | **0.1664** | **0.7317** | 0.8981 |

The base rate dropped from 0.985 → 0.732 because privileged functions are no longer counted as permissionless, so
`actor_clarity` is now a **sharper filter** (positive lift) rather than a near-universal blunt one. _(The historical
`p106/rank_signal_probe.json` is preserved at the pre-fix numbers; this delta is recorded here, not by mutating P106.)_

## Effect on the discovery selection
- **P113 unchanged:** the #1 fresh candidate is still `RamsesV3Pool.swap` (permissionless) — P113's result stands.
- **Corrected next-3 (was closeMarket / repayAndProcess / claimFromFactory):** now all permissionless —
  `repayAndProcessUnpaidWithdrawalBatches`, `MigrationManager.burnRemainingPurchasedNFTs`,
  `CuratorRewardsDistributor.distribute`. The two privileged functions are demoted out of the top.
  _(These corrected next-3 were not deeply analyzed here — P115 is a ranking fix, not a new discovery run; they are
  the candidates a future fresh run would investigate.)_

## No regression
- **P105 enumeration coverage unchanged: 100% (15/15).** Coverage = `function_enumerated` via inventory and does not
  depend on `actor_clarity`, so the awarded-finding recall is untouched.
- Frozen-5 + pipeline-4 byte-identical; `_function_bodies` contract unchanged; historical p106–p114 bundles not
  mutated; no production wiring.

## Takeaway
The P114-surfaced ranking-precision gap is closed: privileged functions are correctly identified and no longer top
the discovery ranking, while coverage and the confirmed P113 result are unaffected. Ranking precision improved
without touching recall or any frozen component.
