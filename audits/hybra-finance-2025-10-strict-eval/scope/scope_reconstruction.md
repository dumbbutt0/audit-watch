# Hybra Finance — Scope Reconstruction (blind, pre-answer-key)

**Source:** repo `scope.txt` + `out_of_scope.txt` + `README.md` only. Answer key NOT accessed.
**Repo:** code-423n4/2025-10-hybra-finance @ `17d72f0b95e6d320e13c4e33ffc68eaad440e8a7`.

## Why this target (eval purpose)
Hybra is a **reward-saturated** ve(3,3) DEX (fork of Blackhole). 12 of 14 in-scope contracts mint/burn shares
or touch reward/emission/voting state, so the run-level `has_reward_layer` gate is ON and the
`reward_accounting` secondary trigger fires on every share-mutation clear. This is the exact condition the
Silo eval could not test (Silo had one reward layer). The eval measures whether that broad firing **converts
real reward bugs** or **over-routes into noise**.

## In scope (14 files, ~3,891 nSLOC)
| File | nSLOC | Reward role |
|---|---|---|
| VotingEscrow.sol | 801 | veNFT locks, merge/split/extend, voting checkpoints (V-1..V-4, C-1/C-2) |
| CLPool.sol | 795 | CL AMM core, fee-growth accounting (G-3, M-1/M-2) — solc 0.7.6 |
| GaugeManager.sol | 410 | distribute emissions to gauges by weight (E-1/E-2) |
| GovernanceHYBR.sol | 366 | gHYBR wrapper; veNFT split/merge fund accounting |
| GaugeV2.sol | 273 | legacy-pair gauge: rewardPerToken/earned/checkpoint (R-1..R-3) |
| GaugeCL.sol | 258 | CL gauge: reward vs active-liquidity-range match (Area-of-concern #1) |
| CLFactory.sol | 205 | CL pool factory |
| VoterV3.sol | 195 | vote weights, gauge registry, claim routing (W-1..W-3) |
| RewardHYBR.sol | 186 | rHYBR: convert claimed reward -> veHYBR/HYBR/gHYBR (Area #3) |
| MinterUpgradeable.sol | 169 | epoch emission cap + rollover + rebase (E-1, epoch cycle) |
| HYBR.sol | 81 | base emission token |
| HybrSwapper.sol | 81 | swap helper |
| GaugeFactoryCL.sol | 71 | CL gauge factory |
| DynamicSwapFeeModule.sol | ~ | dynamic fee (note: Peckshield already flagged a fee-calc improvement) |

Out of scope: all CL periphery (SwapRouter, NonfungiblePositionManager, Quoter, libs), interfaces, `contracts/`
flattened tree, Bribes.sol, APIHelpers. (Bribe logic is referenced by invariants E-3/E-4 but `Bribes.sol`
itself is OUT of scope — bribe bugs only count if they live in an in-scope contract.)

## Reward hot spots to deep-read (where H/M reward bugs live)
1. **GaugeV2 / GaugeCL** — `rewardPerToken`/`rewardPerTokenStored`, `earned`, `_updateReward`/checkpoint
   ordering vs `deposit`/`withdraw`/`_deposit`/`getReward`; lastUpdateTime; CL range-vs-reward match.
2. **VotingEscrow** — `merge`/`split`/`increaseUnlockTime`/`deposit_for` effect on **already-distributed but
   unclaimed** rewards/voting checkpoints (Area #2); transfer side-effects.
3. **MinterUpgradeable / GaugeManager / VoterV3** — epoch rollover `update_period`/`distribute`, emission cap,
   proportionality, claim-across-epochs.
4. **RewardHYBR / GovernanceHYBR** — claim->convert success under all paths; gHYBR deposit/withdraw + veNFT
   split/merge fund conservation.
5. **CLPool** — feeGrowthGlobal/feeGrowthInside accounting, first-depositor/donation, rounding (0.7.6).

## Scoring constraints (publicly-known / ineligible — NOT HITs)
- **Blackhole-fork**: any finding acknowledged in the original Blackhole C4 audit (2025-05) is ineligible
  unless the Hybra code delta increases impact. Score conservatively — a generic ve(3,3) bug present in
  Blackhole is likely a dup.
- **Peckshield Sept-2025** (ineligible): ERC7702 check, voting-delegate dust DoS, admin-key trust
  (centralization), DynamicSwapFeeModule fee-calc, SugarHelper estimateAmount.
- **V12 (Zellic) findings**: out of scope (quarantined `Hybra-V12-output.md`, not read).
- **Storage-slot migration** artifacts and pure **centralization/admin-key** issues: ineligible.

## Trusted roles
hybraMultisig (4/6), hybraTeamMultisig (2/2), emergencyCouncil, GOVERNANCE / VOTER_ADMIN / GAUGE_ADMIN /
BRIBE_ADMIN, MinterUpgradeable.team, owner. Pure "trusted role can rug" = out (Peckshield #3).
