# P106 — Selection Failure Taxonomy

**Status: research-only, un-wired. Analysis + design. No detector, no threshold, no ranker built.**
Invariant of this layer: **"Ranker: prioritize, don't promote."**

Companion: `rank_signal_design.md` (feature catalog + measured discrimination + per-finding table) and
`rank_signal_probe.json` (the measurements). Source: P105 corpus (15 awarded findings / 9 burned subjects).

## Why selection fails today
P105 showed enumeration coverage is 100% but `function_position` is **alphabetical** — awarded functions sit
mid-list (e.g. 193/211, 169/180). Root cause in source: the existing ranker
`auto_validate_invariants._rank_score`/`_RANK_W` is **evidence-gated** — six of its seven signals read
`evidence.rank_signals`, which is empty before the validation layer, so every candidate scores ~0 and the order
collapses to alphabetical. Selection never happens pre-validation.

## Failure modes
Each mode is mapped to the awarded findings it explains, backed by the probe's measured signals.

### FM-1 — Evidence-gated rank-collapse (dominant; all 15)
No per-candidate evidence ⇒ `rank_signals` empty ⇒ score 0 ⇒ alphabetical. Affects **every** finding. This is the
structural cause; FM-2…FM-5 explain why the *naive fixes* don't fully solve it.

### FM-2 — Category saturation (the P105 trap)
`category_match` fires on ~everything, so it can't rank. The probe confirms a milder version persists even on
function bodies: `category_specificity` has base rate **0.747** (fires on 75% of the surface) → lift only **0.10**.
Feeding whole-file source (as `run_subject` does) makes it total saturation; per-body helps but doesn't fix it.
Lesson encoded in the design: "fires on the awarded fn" ≠ "discriminates."

### FM-3 — Surface-size dominance
Large contracts bury the awarded function in the alphabetical list. Worst cases (P105 `function_position`):
`WLD-H-01` 193/211, `TRF-H-01` 169/180. Any ranker that does not actively float a signal leaves these unreachable
for a human with limited PoC budget.

### FM-4 — Core-only / accounting-subtlety signal (the residual gap)
The awarded function triggers only **core** invariant categories and shows no surface-level value-movement, because
the harm is in *how* state updates, not *whether* value moves. The probe's **thin** findings (≤1 SHARP elevating
feature) are exactly this class: `PHI-H-05` `_removeCredIdPerAddress` (access/index), `PHI-M-07` `buyShareCredFor`
(lifecycle/DoS), `KLD-M-02` `checkCalldata` (index off-by-one in a view), `WLD-M-05` `grantRole` (access control),
`SS-M-11` `spotPurchase` (cap bypass via self-purchase inflation), `RAM-M-01` `getPeriodReward` (reward accounting).
**These are evidence-free-unrankable by design** — they need the validation layer to elevate (→ P107/P108).

### FM-5 — Cross-contract blindness
The bug lives across an external-call boundary; the entry function looks benign in isolation. `exploitability_
external_call` is rare (base rate **0.064**) but decisive when present — it elevates exactly **1/15**: `IQ-M-01`
`moveLiquidity` (the P104 finding). Confirms the cross-contract class is sharp-but-sparse: a high-value feature for
the few it fits, not a general ranker.

## Per-finding dominant mode
| Finding | Contract.fn | Dominant mode(s) | Sharp signals |
|---|---|---|---|
| VUL-H-01 | ILOPool.claim | FM-1 | 4 (value, fund, writes, missing-update) |
| MUN-H-05 | LandManager.transferToUnoccupiedPlot | FM-1 | 2 (writes, missing-update) |
| TRF-H-01 | TraitForgeNft.mintWithBudget | FM-1, FM-3 | 2 (value, writes) |
| TRF-M-18 | EntityForging.forgeWithListed | FM-1 | 2 (value, writes) |
| PHI-H-05 | Cred._removeCredIdPerAddress | FM-4 | 1 (writes) |
| PHI-M-07 | Cred.buyShareCredFor | FM-4 | 1 (missing-update) |
| KLD-M-02 | Timelock.checkCalldata | FM-4 | 1 (writes) |
| RAM-M-02 | RamsesV3Pool.flash | FM-1 | 2 (value, writes) |
| RAM-M-01 | GaugeV3.getPeriodReward | FM-4, FM-5 | 1 (fund) |
| WLD-H-01 | WildcatMarketWithdrawals.executeWithdrawal | FM-1, FM-3 | 3 (fund, writes, missing-update) |
| WLD-M-05 | AccessControlHooks.grantRole | FM-4 | 1 (missing-update) |
| SS-H-01 | SecondSwap_StepVesting.transferVesting | FM-1 | 3 (fund, writes, missing-update) |
| SS-H-03 | SecondSwap_StepVesting.claimable | FM-1 | 2 (fund, writes) |
| SS-M-11 | SecondSwap_Marketplace.spotPurchase | FM-4 | 1 (writes) |
| IQ-M-01 | LiquidityManager.moveLiquidity | FM-5 | 4 (value, ext-call, writes, missing-update) |

## Takeaway for P107
- ~9/15 findings carry ≥2 SHARP evidence-free signals → a combined evidence-free ranker can plausibly float them.
- ~6/15 (FM-4 class) carry ≤1 SHARP signal → evidence-free ranking has a **ceiling**; these need the validation
  layer (P107 combine + P108 conversion). State this honestly; do not pretend features alone solve selection.
- Two existing-ranker assumptions are challenged by measurement (see `rank_signal_design.md`): `defense_gap` has
  **negative lift** pre-validation, and `actor_clarity` is a near-universal **filter**, not a discriminator.
