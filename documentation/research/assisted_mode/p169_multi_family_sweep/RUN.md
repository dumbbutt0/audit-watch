# P169 — Multi-family bug sweep (tokemak), reject-first, hygiene-filtered

Scanned 15 bug families at once (protocol_src only), pooled with family labels, scored, investigated the top
**4** across families (within the 3–5 target; not one-per-family). Predictions logged before investigation.
**0 harnesses built** (all refuted; never forced). Success metric = reportables per harness.

## Corpus
**tokemak-2023-06-semantic-tvl** — richest multi-family surface in the probe (oracle 169 · liquidation 31 ·
fee 19 · rounding 8 vs renzo / recall / maia-talos). LMP vaults, oracles, rebalancers, reward adapters, fee
accounting.

## Family coverage table (protocol_src signals → pooled → selected)
| # | Family | signals | pooled | best score | selected | note |
|---|---|---|---|---|---|---|
| 1 | recipient/ownership correction | (with 10) | 1 | 6 | **H18** | Maverick adapter sendTo overload |
| 2 | batch vs single | 2 | 1 | 6 | (H18) | same sendTo sibling pair |
| 3 | checkpoint/rewardDebt/index order | 8 | 1 | 4 | **H21** | GPToke reward checkpoint |
| 4 | sibling auth mismatch | — | 0 | — | no | rewarder/vault fns uniformly role-gated |
| 5 | accounting invariant drift | 94 | 1 | 5 | (H19) | LMPVault NAV accounting |
| 6 | stale balance / cached reserve | 0 | 0 | — | family_depleted | no protocol_src hits |
| 7 | rounding / precision | 8 | 1 | 5 | **H19** | LMPVault withdraw rounding |
| 8 | oracle / value provenance | 38 | 0 | 2 | no | RootPriceOracle registry is onlyOwner; reads are trusted/registered → low attacker-recipient score |
| 9 | cross-function desync | — | 0 | — | family_depleted | no concrete divergence surfaced |
| 10 | user-controlled recipient | 62 | 1 | 5 | **H20** | PeripheryPayments.sweepToken |
| 11 | unchecked external call/callback | (14) | 0 | 2 | no | adapters nonReentrant; callbacks role-scoped |
| 12 | liquidation / solvency | 41 | 0 | 2 | no | LiquidationRow keeper/role-gated |
| 13 | fee accounting | 8 | 0 | 2 | no | fees → feeSink/feeRecipient (fixed party) |
| 14 | escrow/withdrawal/claim | 62 | 1 | 4 | (H21/H19) | claim/withdraw value paths |
| 15 | multicall/batching | 14 | 0 | 3 | no | router multicall is self-scoped delegatecall to own fns |

## Top candidates investigated (all predicted `static_false_positive`; all matched)
- **H18 — MaverickRewardsAdapter `claimRewards(rewarder)` vs `claimRewards(rewarder, sendTo)`** (recipient/
  sibling-divergence). **NO_ATTACKER_PROFIT (G3):** it is a **delegatecall library** — `_claimRewards` uses
  `account = address(this)` and `reward.getReward(sendTo)`; called directly on the deployed library
  `address(this)` is the empty library (earned=0 → nothing); via the vault `sendTo` is vault-controlled. The
  `sendTo` overload is a convenience, not an exploitable divergence.
- **H19 — LMPVault `withdraw`/`redeem`** (rounding/accounting drift). **SOURCE_REFUTED (G4):** both carry
  `noNavDecrease` + `ensureNoNavOps` (the exact rounding-drift invariant — a withdrawal must not decrease
  NAV/share for remaining holders); `previewWithdraw` rounds shares **up**; `withdraw` reverts `TooFewAssets`.
  The candidate premise is explicitly guarded.
- **H20 — PeripheryPayments `sweepToken(token, min, recipient)`** (user-controlled recipient).
  **NO_ATTACKER_PROFIT (G3):** transfers `balanceOf(address(this))` (the **router's** resident balance);
  routers hold no resident user funds between txs → attacker only sweeps donated dust (canonical UniV3
  PeripheryPayments / DESIGN_INTENT for stuck dust).
- **H21 — GPToke `collectRewards()`** (checkpoint/claim). **NO_ATTACKER_PROFIT (G3):** pays the caller their
  **own** accrual; `rewardDebtPerShare[user]` is updated **before** distribution (correct checkpoint order —
  no double-claim / reorder).

## Rejected families (why) / family_depleted
- **6 stale-reserve** and **9 cross-fn-desync**: `family_depleted` — no concrete protocol_src candidate.
- **8 oracle**, **11 callback**, **12 liquidation**, **13 fee**, **15 multicall**: signals present but
  top-scoring entries are trusted-registry / nonReentrant / keeper-role-gated / fixed-recipient → below the
  top-5 score; not selected (per "do not force representation from every family").

## Prediction vs outcome
H18 SFP→SFP · H19 SFP→SFP · H20 SFP→SFP · H21 SFP→SFP — **4/4 correct** (campaign calibration **12/12**).

## Result vs success metric
**reportables_per_harness 1/1** · **0 new harnesses** · **prediction_accuracy 12/12** · **fabrication_rate
0/17**. 0 reportables. Meaningful negatives across 4 distinct families: a delegatecall-library self-scope, an
explicit NAV-drift guard, a router resident-only sweep, and a correct checkpoint order. The multi-family sweep
did not surface a top-tier convertible across the whole bug surface in tokemak — consistent with the campaign's
finding that convertibles are scarce.

## Scorecard after P169
candidates 17 · reportable 1 · runtime_confirmed 1 · harnesses_built 1 · harnesses_avoided 16 ·
source_refutations 5 · gate_refutations 11 · reportables_per_harness 1/1 · prediction_accuracy 12/12 ·
fabrication_rate 0/17.

## Note on calibration honesty
For the highest-scored candidates, the reachability/scoring source-peek can pre-resolve the bucket before the
formal Step-1; predictions were logged reflecting the genuine reject-first prior at selection. Calibration here
measures that prior's quality (4/4 this run) — not a blind guess.
