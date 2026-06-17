# P147 — Target Selection

## Constraint
Need a value/recipient-provenance divergence in an audit with **no local answer key** (→ `duplicate_unknown`),
runtime-PoC-able, source-verifiable. Of the on-disk audits, the eval set (noya/blackhole/size/quantamm/swan/zaros)
has answer keys; the **holdouts do not**.

## Candidates reviewed (honest filtering)
| target | verdict | why |
|---|---|---|
| loopfi `MultiFeeDistribution.getReward`/`_getReward` | **control (no bug)** | pays `msg.sender`/`user` consistently |
| loopfi `MultiFeeDistribution.claimFromConverter(onBehalf)` | **control (intended)** | pays `rewardConverter` **by NatSpec** (Compounder role) — design, not divergence |
| velodrome-bench `RewardsDistributor` | rejected | ancestor of blackhole's distributor; lacks the AVM feature → no B5 analog |
| predy `GammaTradeMarket` | not pursued | heavy perps math; no quick source-verifiable divergence |
| **centrifuge `UserEscrow.transferOut`** | **SELECTED** | tiny (51 lines, local deps), source-clean recipient-provenance divergence (validated subject = `destinations[token][destination]`, paid subject = `receiver`); trivial real deploy |

## Why centrifuge UserEscrow
- **No local answer key** ⇒ `duplicate_status=duplicate_unknown` (the P147 goal).
- **Real recipient-provenance divergence**: funds escrowed for `destination` are payable to a different `receiver`
  via a stale/unrelated `allowance == max` proxy that the escrow never reduces.
- **Light deps** (`Auth`, `SafeTransferLib`, solc 0.8.21, no OZ) ⇒ real-contract PoC (strongest evidence class).
- A clean **corrected reference** (`receiver == destination`) and **control** (`receiver == destination`) exist.

## Honesty note
This matches a recognized Centrifuge finding class, but P147 makes **no novelty/awarded claim** — only
`duplicate_unknown` (no local record) — and the intent-dependence (NatSpec "additional protection") is flagged for
human review.
