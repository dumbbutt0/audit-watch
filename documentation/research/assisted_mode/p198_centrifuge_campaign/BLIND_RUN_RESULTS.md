# P198 — blind adjudication run results (firewall-sealed)

12 blind **Sonnet** subagents, each given only its frozen prompt (`deep_trace.md` + verbatim source of one
surface). Prompts token-scanned before the run (zero finding-IDs / answer-key / report refs; only the prompt's own
generic `awarded` menu words). Raw outputs preserved verbatim in `raw_outputs/`; token-scanned after (zero
answer-key IDs cited → blind confirmed). This is **in-session blind execution** (the P196 mechanism B), not the
budgeted auto-executor.

## Per-surface verdict + headline selected mechanism (blind, source-grounded)
| id | surface | verdict | headline selected mechanism(s) |
|---|---|---|---|
| IM-01 | handleExecutedCollectInvest | HIGH | trancheTokensPayout==0 unguarded -> price corruption; recipient-spoof credit redirect |
| IM-02 | handleExecutedCollectRedeem | HIGH | currencyPayout==0 burns tokens for zero payout; burn-before-price NAV |
| IM-03 | handleExecutedDecreaseInvestOrder | HIGH | no accounting write -> replay double-payout; user-field redirect |
| IM-04 | processDeposit | HIGH | maxDeposit not decremented -> over-issue / Escrow drain affecting other holders; stale price |
| IM-05 | processRedeem | HIGH | receiver != user redirect; stale redeemPrice; _toUint128 truncation |
| IM-06 | _calculateTrancheTokenAmount | MEDIUM | **rounding-DOWN systematically disadvantages user**; price==0 DoS |
| IM-07 | decreaseRedeemRequest | HIGH | user param != msg.sender -> cancel any member's order; _toUint128 truncation |
| ESC-08 | UserEscrow.transferOut | HIGH | max-only irrevocable allowance -> drain to colluding receiver; no per-call cap |
| ESC-09 | UserEscrow.transferIn | HIGH | credit-before-receipt; unconstrained source -> pull pre-approver's tokens |
| LP-10 | LiquidityPool.withdraw | HIGH | receiver free param -> approved operator redirects owner currency |
| TR-11 | Tranche.transfer | HIGH | restricted modifier may check only one party (recipient) |
| RM-12 | RestrictionManager.detectTransferRestriction | HIGH | **checks hasMember(to) but NOT hasMember(from)** |

**Adjudication-stack behaviour (the P183–P188 lens):** mechanism *enumeration* fired strongly (≥3 inventoried, 2+
carried per surface), carry-forward and NEEDS_HARNESS escalation behaved as on quantamm (runtime-dependent disputes
routed to unresolved, not rejected), and reject-first produced source-backed rejections (e.g. EVM-atomicity
rejections of decrement-before-transfer; `onlyGateway`/auth rejections of direct-EOA paths). So the stack's
machinery transferred intact to the RWA architecture. The blind agents independently re-derived two awarded RWA
mechanisms verbatim on the exact functions (RM-12→M-08, IM-06→M-07) without any answer-key exposure — the core
generalization evidence. Scoring + precision analysis in `GENERALIZATION_SCORECARD.md`.
