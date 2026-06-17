# vultisig-2024-06-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: ILO (Initial Liquidity Offering) on Uniswap V3 + NFT vesting (Krystal ILOPool/ILOManager/
ILOVest/ILOWhitelist). Solidity 0.7.6 (unchecked arithmetic). Sealed-key hash 9f6adb9a8ff29753 (not opened
at freeze). Read in full: ILOPool, ILOManager, ILOVest, ILOWhitelist (+ skimmed Uniswap-helper libs).
Advisory lenses: 0 candidates (all 3).

## Candidates (base hunt)
| id | sev | locus | mechanism |
|---|---|---|---|
| V-H1 | High | ILOPool.claim / buy | A bought position's `feeGrowthInside{0,1}LastX128` baseline is never initialized at `buy` (stays 0). First `claim` computes `fees = (feeGrowthInside_now − 0) × positionLiquidity` → over-collects fees accrued before the position existed; across NFTs the claimed fees can exceed fees actually collected → drains principal / other users. |
| V-H2 | High | ILOPool.claimRefund / launch (`_refundTriggered`) | `refundable` modifier flips `_refundTriggered=true` on the FIRST `claimRefund` after `refundDeadline`; once set, `launch()` is permanently blocked (`require(!_refundTriggered)`). If the manager hasn't launched by the deadline, any single user can grief the whole ILO into refund-only, blocking a soft-cap-met launch. |
| V-M1 | Medium | ILOManager.initialize | `initialize(...)` is `whenNotInitialized` but has NO access control; anyone can front-run it to set `initialOwner`/fees/feeTaker → ownership hijack of the manager. |
| V-M2 | Medium | ILOManager.launch | `launch()` is permissionless and requires `slot0 price == initialPoolPriceX96`; an attacker can swap the Uniswap pool a wei off-price to make `launch` revert → launch DoS (until manually re-synced). |
| V-M3 | Medium | ILOPool.claim / buy (0.7.6) | Unchecked arithmetic: `amountCollected0 − amount0` to feeTaker and `maxCapPerUser − raiseAmount` can underflow/wrap (no SafeMath in 0.7.6) on edge values. |
| V-L1 | Low | ILOPool.buy | `buy(raiseAmount, recipient)` whitelists `recipient` but pulls funds from `msg.sender` — anyone can buy on behalf of a whitelisted address. |
| V-L2 | Low | ILOPool.launch | vesting loop over `_vestingConfigs` unbounded → gas/DoS with many configs. |

## Gate / proof status
P245 gate: would block until 47 critical READ_FULL (all read). Proof: BLOCKED_BY_BUILD. Lens contribution: 0.
FREEZE: final pre-reveal.
