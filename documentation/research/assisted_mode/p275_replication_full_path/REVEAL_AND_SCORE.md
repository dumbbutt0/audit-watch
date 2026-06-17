# P275 — REVEAL_AND_SCORE (Phase 10)

Answer key opened **after** the Phase-9 freeze. Source: `code-423n4/2024-10-ronin-findings` (`report.md`). Scoring
against the frozen set only; no hindsight credit.

## The decisive fact
> **C4 Summary: "The C4 analysis yielded 0 HIGH or MEDIUM risk vulnerabilities."**
> Plus 3 LOW/non-critical reports. The one substantive issue (#32, below) is explicitly **"this downgraded issue has
> been included in this report"** at the sponsor's request — i.e. **not** an awarded High/Medium.

**There is no awarded High/Medium mechanism on this target to recover.** The replication question ("recover ≥1 awarded
mechanism EXACT/STRONG") cannot be answered on a target with zero awarded H/M. → the target is **not diagnostic**.

## The one substantive (downgraded) issue vs my path
**#32 — `LiquidityManagement.katanaV3MintCallback()` address-collision attack** (steals NonfungiblePositionManager
approvals): `CallbackValidation.verifyCallback` only checks `msg.sender == PoolAddress.computeAddress(factory, key)`
(a CREATE2 address); an attacker brute-forces a `key.fee` whose computed address collides with an attacker-deployable
CREATE2 address (160-bit truncation, EIP-3607 class), deploys there, and calls the mint callback to pull victim
approvals.

How my (frozen, pre-reveal) path did against it:
| stage | result |
|---|---|
| recall surfaced the subsystem? | **YES** — `NonfungiblePositionManager.mint` (rank 3), `KatanaV3Pool.mint` (rank 6), and `V3SwapRouter.katanaV3SwapCallback` (rank 4, the **swap** analog of the same callback-validation pattern) |
| coverage/triage routed it? | **YES** — `npm_mint` (ACCESS) and `pool_mint` (SHARE) selected; the callback subsystem was in the PoC queue |
| completion identified the mechanism? | **NO** — I examined the exact analogous check (`computePoolAddress(...) == msg.sender`) in the **swap** callback and explicitly judged it "standard, correct," missing that this CREATE2-address verification is collision-vulnerable |
| match level vs #32 | **SAME_AREA_WRONG_MECHANISM** (examined the precise validation locus, concluded benign, missed the collision vector) |

## My candidates scored
| candidate | class | match | note |
|---|---|---|---|
| M1 pool.swap `tx.origin` auth (PoC PASS) | ACCESS | **NONAWARDED_TRUE_POSITIVE** (deviation real) / not in report | real `tx.origin`-auth deviation; not awarded, not even listed (on-chain-unexploitable as I noted) |
| M3 conservation control (PoC PASS) | SHARE | **BENIGN** (control held) | pool math correct, as expected |
| M2 swap_callback | ORDER | **SAME_AREA_WRONG_MECHANISM** vs #32 | examined the callback validation, judged it correct — missed the collision vector |

## PoC scoring
- `tx.origin` PoCs → **POC_SUPPORTS_NONAWARDED_TP** (proved a real but non-awarded deviation).
- conservation → **POC_REFUTES_CANDIDATE** (control: math is not the bug).
- No PoC supports an awarded mechanism (there are none at H/M).

## False positives
**0 severe concluded/reportable FP.** Nothing was concluded as a vulnerability that the reveal refutes; the `tx.origin`
deviation was explicitly recorded PARTIAL/exploit-unconfirmed, and the conservation control behaved as predicted.
