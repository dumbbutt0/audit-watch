# P106 — Rank Signal Design (evidence-free pre-ranking)

**Status: research-only, un-wired. DESIGN + MEASUREMENT only.** No combined score, no ordering, no threshold, no
wiring — that is P107. Invariant: **"Ranker: prioritize, don't promote."**
Measured by `scripts/assisted/rank_signal_probe.py` over the P105 corpus (15 awarded findings / 9 subjects);
raw data `rank_signal_probe.json`. Taxonomy: `selection_failure_taxonomy.md`.

## Method
For every public/external function in each subject's surface, compute an **evidence-free, source-derived** feature
vector — on the **function body** (not the whole file; this de-saturates the keyword signals that wrecked P105).
Then, per awarded finding, report the awarded function's percentile/rank within its subject's surface per feature.
A feature is a *ranking* signal only if the awarded function lands HIGH **and** the signal is selective:

> **lift = mean_awarded_percentile − surface_base_rate.** High lift = SHARP (rare in surface, high on awarded).
> High percentile + high base rate = BLUNT (necessary but non-discriminating). Negative lift = MISLEADING.

## Feature catalog + measured discrimination
Aligned to the existing `_RANK_W` vocabulary so P107 can wire the same names into `_rank_score`.

| Feature | ← _RANK_W | Source signal (on body) | lift | mean pct | base rate | verdict |
|---|---|---|---|---|---|---|
| consequence_value_movement | consequence | transfer/mint/burn/`call{value`/safeTransfer | **0.89** | 0.96 | 0.07 | **SHARP** |
| exploitability_external_call | exploitability | staticcall/`.call(`/interface/factory/oracle/hook | **0.86** | 0.93 | 0.06 | **SHARP, sparse** (cross-contract) |
| consequence_fund_reachability | consequence | withdraw/claim/redeem/release/collect/rescue | **0.83** | 0.93 | 0.11 | **SHARP** |
| missing_update_asymmetry | (new, negative_space) | set/update with no matching reset/clear | 0.46 | 0.80 | 0.34 | MODERATE |
| state_write_breadth | (new) | count of state writes | 0.41 | 0.88 | 0.47 | MODERATE (broad) |
| category_specificity | (new) | # non-core invariant categories fired | 0.10 | 0.85 | 0.75 | **WEAK** (still saturated, FM-2) |
| actor_clarity | actor_clarity | public/external & no role guard | −0.05 | 0.94 | 0.99 | **BLUNT** (filter, not ranker) |
| defense_gap | defense_gap | # fired categories with DOES_NOT_COVER (+½ partial) | −0.20 | 0.58 | 0.78 | **MISLEADING pre-validation** |

### Two measured challenges to the existing ranker
- **`defense_gap` (current weight 3) has NEGATIVE lift.** Per-function, awarded vulnerable functions have *fewer*
  defense gaps than the surface average — their bug is subtler than "no guard" (they often contain require/state
  updates; trivial functions don't). Defense gap is a **validation-time** signal (needs the trace), not a pre-rank
  one. P107 should NOT weight it for evidence-free ordering.
- **`actor_clarity` is a filter, not a discriminator** (base rate 0.99). Use permissionless-ness to *gate* the
  candidate set, not to rank within it.

## Per-finding explanation (the pass condition)
For each awarded finding: the SHARP evidence-free signals that fire (with awarded percentile), i.e. which signals
should have elevated it. `*` = thin (≤1 sharp signal) ⇒ FM-4 residual, needs the validation layer.

| Finding | Contract.fn | SHARP signals (percentile) | Should-elevate? |
|---|---|---|---|
| VUL-H-01 | ILOPool.claim | value(1.0), fund(1.0), writes, missing-update | yes — fee/value siphon surfaces strongly |
| MUN-H-05 | LandManager.transferToUnoccupiedPlot | writes, missing-update | yes — stale-state class is the missing-update signal |
| TRF-H-01 | TraitForgeNft.mintWithBudget | value, writes | yes |
| TRF-M-18 | EntityForging.forgeWithListed | value, writes | yes |
| PHI-H-05* | Cred._removeCredIdPerAddress | writes | partial — access/index harm has no value signal (FM-4) |
| PHI-M-07* | Cred.buyShareCredFor | missing-update | partial — lifecycle/DoS subtlety (FM-4) |
| KLD-M-02* | Timelock.checkCalldata | writes | partial — index off-by-one in a view (FM-4) |
| RAM-M-02 | RamsesV3Pool.flash | value, writes | yes — protocol-fee miscalc surfaces |
| RAM-M-01* | GaugeV3.getPeriodReward | fund | partial — reward accounting subtlety (FM-4/FM-5) |
| WLD-H-01 | WildcatMarketWithdrawals.executeWithdrawal | fund, writes, missing-update | yes |
| WLD-M-05* | AccessControlHooks.grantRole | missing-update | partial — access control (FM-4) |
| SS-H-01 | SecondSwap_StepVesting.transferVesting | fund, writes, missing-update | yes |
| SS-H-03 | SecondSwap_StepVesting.claimable | fund, writes | yes |
| SS-M-11* | SecondSwap_Marketplace.spotPurchase | writes | partial — cap-bypass-by-inflation is subtle (FM-4) |
| IQ-M-01 | LiquidityManager.moveLiquidity | value, ext-call, writes, missing-update | yes — cross-contract signal is decisive |

**Coverage of the pass condition:** all 15 have a measured, source-backed explanation. 9/15 carry ≥2 sharp signals
(evidence-free ranking can plausibly float them); 6/15 (the FM-4 `*` rows) carry ≤1 — the honest ceiling of
evidence-free ranking.

## Hand-off to P107 (combine — do NOT build here)
- **Primary weights:** consequence_value_movement, consequence_fund_reachability, exploitability_external_call
  (sharp, low base rate). **Secondary:** missing_update_asymmetry, state_write_breadth.
- **Gate (not weight):** actor_clarity (permissionless) as a candidate filter.
- **Drop from evidence-free score:** defense_gap (negative lift) and category_specificity (saturated) — defer both
  to the validation layer.
- **P107 boundary:** combine the above into a score, ORDER candidates, and measure **top-k recall** of the awarded
  function vs the alphabetical baseline. Expect a real lift on the 9 multi-sharp findings and ~flat on the 6 FM-4
  rows — which then motivate **P108** (evidence/conversion to elevate the access-control/accounting-subtlety class).
- Keep `_rank_score`'s evidence-gated signals for post-validation ranking; P107 adds the evidence-free pre-rank as a
  separate stage, not a replacement.
