# P141 — Manual Deep-Pass Outputs (verbatim, blind)

All outputs below are genuine blind `manual_in_session` deep-pass results from fresh uncontaminated subagents
(no repo/answer-key access). One is new this phase (A1, SolvencyV2); the rest are reused verbatim from the P138
corpus (`p138_value_provenance_corpus/blind_outputs.md`).

## A1 — NEW this phase: SolvencyV2.convertAmountsToValues (noya)
Fresh subagent `aa6d4aac2a89ed1b9`, given only the queued neutral packet (function body + `toValue` callee + the
`getPrice`/`decimals` signatures). **Decision: `strong_clear` (high).**

> ROUTE: value-provenance (units/decimals within a per-asset loop). TRACE: index `i` is uniform across
> `_assets[i]` (identity for `getPrice` **and** `decimals`), `_amounts[i]` (quantity), and `values[i]` (output).
> `validated_subject == mutated_subject` at every point; `toValue` applies the standard `amount*price/10**decimals`
> with decimals belonging to the same asset. CRITIC: no off-by-one / wrong-key / operand swap; length guard
> (`DifferentArrayLength`) prevents index divergence; `_amounts[i]==0` → `values[i]=0` correct; state-free view.
> The only residual is whether the oracle price carries its own decimal scaling — an **out-of-family**
> units-normalization question unresolvable from the bundle, **not** a wrong-subject divergence. → **strong_clear**.

Honest reading: a **clean control**. The subagent did not over-flag the out-of-family decimals concern into a
false finding, and correctly did not push it to needs_human on the *provenance* question.

## A2 — RewardsDistributor… carried: NoyaValueOracle._getValue (noya)
Reused P137 blind result (subagent in P137). **Decision: `finding` (high)** — multi-hop loop reuses static `asset`
instead of loop-carried `quotingToken` (stale-loop-var value provenance). (Same artifact as P140.)

## B1 — RewardsDistributor.claim_many (blackhole)
P138 blind `a67fb918317d02d07` (B5). **`finding` (high)** — recipient under-resolved: `ownerOf(tokenId)` vs
`avm.getOriginalOwner` for AVM-managed tokenIds (recipient subject diverges from entitled subject). *P138 note: this
recall used legitimate AVM ownerOf-vs-getOriginalOwner bundle context.*

## B2 — RewardsDistributor.claim (blackhole)
P138 blind `a8b0c3cd763de3d36` (C1, clean HIGH). **`strong_clear` (high)** — single-token claim, recipient + amount
from the same tokenId; explicit no-divergence reasoning.

## B3 — RewardsDistributor.claimable (blackhole)
P138 blind `af34d02a9bfb2d68a` (C3, clean MEDIUM). **`strong_clear` (high)** — pure view accrual for the queried
tokenId; no subject divergence, no state effect.

## C1 — SellCreditMarket.validateSellCreditMarket (size)
P138 blind `a281e3db7ab349438` (B4). **`needs_human` (medium)** — wrong-basis: cash `params.amount` checked against
CREDIT-named `minimumCreditBorrowAToken`; exact divergence located, exploit direction not traceable from the
bundle → honest needs_human (not a silent clear).

## C2 — AccountingLibrary.debtTokenAmountToCollateralTokenAmount (size)
P138 blind `a403bf1955e6383ae` (C5, clean MEDIUM). **`strong_clear` (high)** — debt→collateral unit conversion with
correct price/decimals basis; no operand/basis swap.
