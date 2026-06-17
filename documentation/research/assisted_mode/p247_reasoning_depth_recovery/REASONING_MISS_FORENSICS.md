# P247 — Phase A: Reasoning-Miss Forensics

Forensic reconstruction of the **21 reasoning-bound misses** from P246 (area read; coverage / unread-surface
/ blocked-by-build excluded). For each: system path (what the frozen hunt concluded), ground-truth path
(awarded exploit chain, from the revealed answer key), and the **single first-divergence label**. Weights
H=3/M=1. Answer keys used ONLY to reconstruct ground-truth — no heuristic is added to the system.

Divergence labels: DEFENSE_MISUNDERSTOOD · STATE_MACHINE_MISUNDERSTOOD · LIFECYCLE_MISUNDERSTOOD ·
CROSS_CONTRACT_REASONING_FAILURE · ECONOMIC_REASONING_FAILURE · PERMISSION_MODEL_FAILURE ·
ACCOUNTING_REASONING_FAILURE · IMPACT_REASONING_FAILURE · UNKNOWN.

## decent (7)
| ID | Sev | System path (concluded) | Ground-truth path | First divergence |
|---|---|---|---|---|
| H-02 | H | read `_getCallParams` (GAS_FOR_RELAY hardcoded); treated dst gas as handled | user-supplied `_dstGasForCall` unenforced → too-little gas → dst call OOG; LZ marks msg delivered (INFLIGHT→SUCCESS/STORED) though it failed → funds/exec lost | **CROSS_CONTRACT_REASONING_FAILURE** (didn't trace dst-chain execution outcome / LZ delivery semantics) |
| H-03 | H | D-M2: flagged failed-call refund path as "stuck/grief" | refund on failed exec is sent to a **wrongly-set `from`** (mis-propagated through UTB→adapter→router→executor) → permanent loss to random addr | **CROSS_CONTRACT_REASONING_FAILURE** (didn't trace the `from` data-flow across hops) |
| H-04 | H | D-L1: noticed reserve check, flagged `>` off-by-one | when dst router WETH reserves < amount, `onOFTReceived` sends unbacked dcntEth to `_to`; user's bridged ETH is lost | **STATE_MACHINE_MISUNDERSTOOD** (reserve-shortfall branch consequence not traced) |
| M-01 | M | did not flag postBridge swap staleness | Stargate `sgReceive` reverts on stale swap data but Stargate still delivers tokens + caches the call; only retryable with same stale data → tokens stuck | **CROSS_CONTRACT_REASONING_FAILURE** (Stargate composer external retry/caching semantics) |
| M-02 | M | flagged a different fee bypass (receiveFromBridge) | calling `DecentEthRouter.bridgeWithPayload` directly bypasses the UTB fee-collection layer entirely | **PERMISSION_MODEL_FAILURE** (which entrypoints sit outside the fee gate) |
| M-04 | M | read Stargate adapter fixed `SG_FEE_BPS`; treated as fine | Stargate fee is variable; fixed-bps assumption → surplus tokens delivered beyond `amountIn` are stranded in the adapter | **ECONOMIC_REASONING_FAILURE** (external variable-fee economics) |
| M-05 | M | read `_bridgeWithPayload` (refundAddress=`payable(msg.sender)`); didn't trace identity | msg.sender is the DecentBridgeAdapter (a contract that can't recover), so LZ native refunds are stuck | **CROSS_CONTRACT_REASONING_FAILURE** (msg.sender identity across the call chain) |

## vultisig (3)
| ID | Sev | System path | Ground-truth | First divergence |
|---|---|---|---|---|
| H-02 | H | V-L1: noted whitelist checks `recipient` not buyer (rated Low) | `checkWhitelist` gates the wrong party → any non-WL account can buy and also split buys across accounts to bypass the per-user 3-ETH cap → bricks WL launch | **PERMISSION_MODEL_FAILURE** (who the whitelist actually gates) |
| M-02 | M | did not flag slippage on `claim` | `claim`'s `pool.burn` returns have no slippage bound; a frontrun price-manip on the Uniswap pool makes the investor claim far less | **ECONOMIC_REASONING_FAILURE** (AMM price-manip/slippage on burn) |
| M-03 | M | examined `buy`/`maxCapPerUser`; missed transfer bypass | the per-user cap is enforced on the NFT position, but transferring the NFT to a fresh account lets a user buy again → bypasses `maxCapPerUser` | **LIFECYCLE_MISUNDERSTOOD** (NFT-ownership lifecycle breaks the per-user invariant) |

## kleidi (3)
| ID | Sev | System path | Ground-truth | First divergence |
|---|---|---|---|---|
| M-01 | M | read `pause()` proposal loop; dismissed | `_liveProposals` is attacker-growable; given exposed threshold keys, flooding proposals griefs the pause/cancel loop (and enables theft) | **STATE_MACHINE_MISUNDERSTOOD** (growable proposal set → DoS, not adversarially traced) |
| M-02 | M | K-M3: flagged calldata-index logic as fragile | length is computed `end − start` (needs `+1`); a parameter that fills all its bytes makes `checkCalldata` revert spuriously | **ACCOUNTING_REASONING_FAILURE** (index/length arithmetic off-by-one) |
| M-03 | M | did not flag | `updateExpirationPeriod` reverts when `newPeriod < currentPeriod` for an existing proposal window (expiry-vs-timestamp interaction) | **STATE_MACHINE_MISUNDERSTOOD** (proposal-expiry state interaction) |

## centrifuge (4)
| ID | Sev | System path | Ground-truth | First divergence |
|---|---|---|---|---|
| M-02 | M | read LP permit fns; didn't flag | permit signature binds to the tranche TOKEN, not the pool; multiple pools share a tranche token → a mempool attacker reuses the sig on a different pool with a higher fee | **CROSS_CONTRACT_REASONING_FAILURE** (sig scope across pools sharing a token) |
| M-04 | M | C-L1: noted deposit/mint callable for others | `deposit`/`mint` lack access control and take no tokens → an attacker pre-mints a wei for the victim, DoSing the victim's deposit | **PERMISSION_MODEL_FAILURE** (missing access control on deposit/mint) |
| M-05 | M | C-H1: flagged orderbook/decrease-limits accounting | claiming via `deposit()` drains shared escrow shares so other investors can't claim their maxDeposit/maxMint | **ACCOUNTING_REASONING_FAILURE** (shared-escrow share accounting) |
| M-07 | M | C-H1: flagged rounding drift generally | `trancheTokenAmount` must round UP on withdraw (favor vault) per EIP-4626; code rounds down | **ACCOUNTING_REASONING_FAILURE** (rounding direction) |

## munchables (4)
| ID | Sev | System path | Ground-truth | First divergence |
|---|---|---|---|---|
| H-01 | H | read `lockOnBehalf`/`_lock`; flagged setLockDuration instead | `lockOnBehalf(victim)` resets the victim's `unlockTime = now + duration` on every call → attacker repeatedly extends it, freezing withdrawals | **STATE_MACHINE_MISUNDERSTOOD** (unlockTime state transition not adversarially traced) |
| M-01 | M | read approve/disapprove; dismissed | `approveUSDPrice` lacks a disapproval check → a price feed can both disapprove and approve the same proposal | **STATE_MACHINE_MISUNDERSTOOD** (approval/disapproval dual-state) |
| M-03 | M | MU-M2: flagged remainder reset (loss direction) | the carried remainder is re-added to quantity in subsequent locks and re-counted for NFTs → players mint extra NFTs | **ACCOUNTING_REASONING_FAILURE** (remainder double-count) |
| M-04 | M | read setLockDuration; missed missing harvest | `setLockDuration` doesn't `forceHarvest` before changing the lock → schnibbles reward accounting is wrong | **ACCOUNTING_REASONING_FAILURE** (missing harvest in reward accounting) |

## First-divergence tally (21 findings / 31 weighted)
| Label | count | weighted |
|---|---|---|
| CROSS_CONTRACT_REASONING_FAILURE | 5 | 9 |
| STATE_MACHINE_MISUNDERSTOOD | 5 | 9 |
| ACCOUNTING_REASONING_FAILURE | 5 | 5 |
| PERMISSION_MODEL_FAILURE | 3 | 5 |
| ECONOMIC_REASONING_FAILURE | 2 | 2 |
| LIFECYCLE_MISUNDERSTOOD | 1 | 1 |
| DEFENSE_MISUNDERSTOOD / IMPACT / UNKNOWN | 0 | 0 |
| **Total** | **21** | **31** |

Note: notably **0 DEFENSE_MISUNDERSTOOD** — these are not "accepted a guard that doesn't hold" failures;
they are failures to *construct the exploit chain / trace state & cross-contract flow* in the first place
(the system mostly never proposed a candidate to reject). This is the key handoff to Phase D.
