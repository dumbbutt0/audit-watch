# decent-2024-01-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: cross-chain / NFT bridge (UTB + Decent bridge over LayerZero/Stargate). Sealed-key hash
2eafbdf52cb3d1f8 (not opened at freeze time). In-scope read in full: UTB, UTBExecutor, UTBFeeCollector,
UTBOwned, UniSwapper, DecentEthRouter, DecentBridgeExecutor, DcntEth, StargateBridgeAdapter,
DecentBridgeAdapter, BaseAdapter. Advisory lenses: 0 candidates (all 3).

## Candidates (base hunt)
| id | sev | locus | mechanism |
|---|---|---|---|
| D-C1 | Critical | DcntEth.setRouter | `setRouter(address)` has NO access control (public, no onlyOwner). Attacker sets self as `router`, then `mint(self, huge)` (onlyRouter) → mints unlimited DcntEth → `DecentEthRouter.redeemEth/redeemWeth` (transferFrom dcntEth, withdraw WETH) drains all bridge reserves. |
| D-H1 | High | UniSwapper.swapExactIn / swapExactOut / swapNoPath | These are `public payable` (NOT `onlyUtb`; only `swap()` is gated). Directly callable by anyone; pull tokenIn from caller then `_sendToRecipient` sends tokenOut from the swapper's own balance → drains any tokens resident in the swapper / abuses approvals. |
| D-H2 | High | UTB.receiveFromBridge | `public`, no access control / no caller check. Meant to be called only by a bridge adapter; anyone can call it to drive `_swapAndExecute` (performSwap + executor.execute) with attacker-chosen target/payload/refund. |
| D-M1 | Medium | UTBFeeCollector.collectFees | Fee ECDSA signature over `keccak(packedInfo)` has no nonce / chainId / deadline → signature replay; a captured fee signature is reusable. |
| D-M2 | Medium | UTBExecutor.execute / DecentBridgeExecutor._executeEth | On failed `target.call`, refund via `refund.call`/`payable(from).transfer` — return value of refund `.call` ignored / `.transfer` to a contract `from` can revert → funds stuck or silently lost. |
| D-L1 | Low | DecentEthRouter.redeemEth/redeemWeth/onlyIfWeHaveEnoughReserves | reserve check uses `>` not `>=` (off-by-one: cannot redeem when balance == amount). |
| D-L2 | Low | UTB.performSwap | native path `require(msg.value >= amountIn)` but excess `msg.value - amountIn` not refunded. |

## Gate / proof status
P245 coverage gate: would BLOCK triage until 52 critical items READ_FULL (all read here). Proof conversion:
BLOCKED_BY_BUILD (no vendored deps). Advisory lens contribution: 0.

FREEZE: candidates above are final pre-reveal.
