# P199 — High-vs-Medium discriminators (evidence-grounded)

Derived by contrasting the **12 genuine-High** cases in the dataset (P189 deep-run misses awarded High) against
the **8 over-HIGH Medium/Low** cases. All from existing artifacts.

## Genuine-High cases and what makes them High
| case | mechanism | High discriminator present |
|---|---|---|
| revert-lend H-04 | `V3Utils.execute` no caller/ownership check | **direct theft / value extraction** (drain any position), permissionless executable |
| revert-lend H-02 | onERC721Received reentrancy / collateral swap | **fund drain**, attacker-controlled executable path |
| revert-lend H-05 | `_getReferencePoolPriceX96` slot0 manipulation | **protocol insolvency** (borrow vs inflated collateral), no admin prereq |
| revert-lend H-06 | `_cleanupLoan` reentrancy / liquidation block | unbacked-loan **fund loss** / liquidation bypass |
| zaros H-01/H-02/H-07/H-09 | weth-reward misdistribution / restake value loss / debt miscalc / rebalance revert | **fund misallocation / loss** affecting depositor funds |
| panoptic H-02/H-03 | settleLiquidation/settleBurn reentrancy & commission bypass | **vault drain / fee theft** |

**Common High evidence:** a *proven, permissionless* path to **direct theft / value extraction**, **protocol-wide
insolvency**, **permanent fund loss**, or **unauthorized privileged state transition** — with **material
magnitude** and **no trusted/admin prerequisite** and **no narrow timing/config dependency**.

## Over-HIGH Medium cases — which discriminators they LACK
| case | theft/extraction? | insolvency? | permanent loss? | priv-transition? | what it actually is |
|---|---|---|---|---|---|
| M-06 oracle revert (quantamm) | ✗ | ✗ | ✗ (recoverable) | ✗ | liveness/DoS |
| M-03/M-10 afterUpdate | ✗ | ✗ | ✗ | ✗ | gas-DoS / griefing |
| L-02 precision | ✗ | ✗ | ✗ | ✗ | dust precision |
| AK-M2 stuck NFT | ✗ | ✗ | ✗ (recoverable) | ✗ | griefing / liveness |
| panoptic M-02/M-03 | ✗ | ✗ | ✗ | ✗ | bounded local mispricing |
| centrifuge M-04/M-05 | ✗ | ✗ | ✗ | ✗ | deposit-DoS / escrow-share starvation |
| centrifuge M-08 | ✗ | ✗ | ✗ | ✗ | compliance/restriction gap |

**Every over-HIGH Medium fails all four High discriminators.** They are griefing/DoS, precision/dust, bounded
local mispricing, or compliance — categories that, per the CLAUDE.md scale, are **Medium** ("incorrect behaviour,
significant griefing, DoS").

## The discriminating question (single test)
> Is there a **proven, permissionless** path to **theft / extraction / protocol-wide insolvency / permanent fund
> loss / unauthorized privileged transition**, of **material magnitude**, with **no trusted-actor prerequisite**
> and **no narrow timing/config dependency**?

- **Yes** → High (the genuine-High set passes).
- **No — it's DoS/griefing/precision/compliance/bounded-local, or magnitude/privilege/reachability is unproven** →
  Medium (or NEEDS_HARNESS if a harness would settle magnitude/reachability).

This test cleanly separates all 12 genuine-Highs from all 8 over-HIGH Mediums in the dataset.
