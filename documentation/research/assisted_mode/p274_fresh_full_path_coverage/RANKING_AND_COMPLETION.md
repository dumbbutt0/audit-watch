# P274 — RANKING_AND_COMPLETION (Phase 6)

B/C profile + five-op completion (STS / AAS / TSE / IDC / CCIT) on the 4 triage-selected mechanisms, each in its routed
award class. Accounting uses the P271 LENDING_COMPLETION_CHECKLIST (read-only, `2929a2154a88`); the non-accounting
classes use class-specific completion questions. **All hypotheses are BLIND** (gondi source only; no answer key).

Class-specific completion questions applied:
- **ACCESS/ORDER:** caller authority · is the struct/loan bound or caller-supplied · order update/fill/cancel authz ·
  signature/nonce/deadline/replay.
- **DOS/SHARE:** unbounded loops · revert-blocks-all · division-by-zero · rounding strands funds · stuck claim path.
- **STATE:** lifecycle ordering (burn-before-withdraw) · stranded/locked funds · post-terminal recovery path.

---

## M1 — `distribute` (ACCOUNTING_LIQUIDATION_BAD_DEBT → mechanism is ACCESS/accounting)
**Locus:** `LiquidationDistributor.distribute(uint256 _proceeds, IMultiSourceLoan.Loan calldata _loan)` →
`_handleLoanManagerCall` → `LoanManager(_tranche.lender).loanLiquidation(...)`.
**Exact hypothesis:** `distribute` is `external` with **no caller/loan-authenticity check** and trusts the entire
`_loan` (including `tranche[].lender`, `loanId`, `principalAmount`, `aprBps`, `accruedInterest`, `startTime`) from
calldata. For any tranche whose `lender` is a registered LoanManager (`getLoanManagerRegistry.isLoanManager`), it
invokes `loanLiquidation` with attacker-chosen parameters. The pool's `loanLiquidation` is `onlyAcceptedCallers` — and
the distributor is an accepted caller — so the pool trusts these forwarded params and runs `_loanTermination`
(writes off a loan, accrues `getCollectedFees`). An attacker can thus **spoof a liquidation callback into a Pool**
without a real auction/liquidation.
**Source evidence:** `distribute` has no `onlyX` modifier and no check that `_loan`/`loanId` corresponds to a real
liquidated loan; `_handleLoanManagerCall` forwards `_tranche.*` verbatim; `Pool.loanLiquidation` is
`onlyAcceptedCallers` and consumes `_loanId/_principalAmount/_apr/_startTime` directly into `_loanTermination`.
**Victim/gainer:** pool LPs (accounting corrupted / loan written off) ; attacker (forces state). Cost = funding the
`safeTransferFrom(msg.sender, lender, total)` transfer.
**Δ vs narrow:** recall-delta (rank ≥5). **Runner-up:** the proceeds-split math (excess pro-rata) — conserves, no bug.
**Completion:** STS ✓ (permissionless entry) · AAS ✓ (attacker calldata `_loan`) · TSE ✓ (callback reached) · IDC
partial (pool accounting outcome needs Pool runtime) · CCIT partial. **Status: COMPLETE on reachability;
PARTIAL on economic outcome.**

## M2 — `wq_withdraw` (DOS_LIVENESS → mechanism is SHARE rounding / liveness)
**Locus:** `WithdrawalQueue._getWithdrawablePerShare()` = `(_totalWithdrawn + balanceOf(this)) / getTotalShares`;
`_getAvailable = getShares[id] * perShare - getWithdrawn[id]`.
**Exact hypothesis:** per-share is integer-divided by `getTotalShares` **before** multiplying by a position's shares,
so `shares * floor(total/totalShares)` systematically under-pays; the remainder (`total mod totalShares` scaled) is
**stranded permanently** in the queue (no sweep). Additionally `getTotalShares == 0` ⇒ division-by-zero revert
(liveness) on any `getAvailable`/`withdraw` before the first mint.
**Source evidence:** division precedes multiplication in `_getWithdrawablePerShare`; no dust-recovery path; `withdraw`
calls `_getAvailable` which calls `_getWithdrawablePerShare`.
**Victim/gainer:** withdrawing LPs (lose dust) ; no direct gainer (funds stuck). **Δ:** recall-delta.
**Completion:** STS ✓ · TSE ✓ · IDC ✓ (sum of available < balance) · economic magnitude small unless totalShares
large. **Status: COMPLETE (rounding/stranding); impact is dust-scale (Low/Med).**

## M3 — `burnAndWithdraw` (STATE_MACHINE_LIFECYCLE → stranded funds)
**Locus:** `UserVault.burnAndWithdraw(_vaultId, _collections, _tokenIds, _tokens)`.
**Exact hypothesis:** `_thisBurn` burns the vault NFT **first**, then withdraws only the caller-enumerated
`_collections/_tokenIds/_tokens`. Any asset deposited in the vault but **not listed** by the caller is **permanently
stranded**: the vault NFT is gone, there is no standalone post-burn withdraw, and re-calling `burnAndWithdraw` reverts
in `_thisBurn` (`ownerOf` of a burned token). There is also **no length-match check** between `_collections` and
`_tokenIds` (other deposit fns revert `LengthMismatchError`; this one does not).
**Source evidence:** order of operations (`_thisBurn` then the withdraw loops); `_withdraw*` are `private` (only reached
via `burnAndWithdraw`); no `LengthMismatchError` guard in `burnAndWithdraw`.
**Victim/gainer:** vault owner (loses unlisted assets) ; no gainer (locked). **Δ:** recall-delta.
**Completion:** STS ✓ · TSE ✓ (burn precedes withdraw) · IDC ✓ (unlisted NFT still owned by vault, vault burned).
**Status: COMPLETE (permanent stranding / footgun); self-inflicted ⇒ Low/Med.**

## M4 — `offers` (ORDER_VALIDATION)
**Locus:** `MultiSourceLoan._processOffersFromExecutionData` / `_validateOfferExecution` / `_checkOffer`.
**Exact hypothesis:** none cleanly derivable blind. The offer path validates signature (EIP-712/1271), expiry,
cancellation (`isOfferCancelled`, `minOfferId`), per-loan principal cap, capacity (`_used + amount > capacity`),
principal/collateral address match, and `maxSeniorRepayment` seniority. The fee-on-fee accounting
(`amount - fee` disbursed; protocol-fee-on-fee) is a candidate but not a confirmed invariant break.
**Completion:** STS ✓ but **no falsifiable exact mechanism**; full emitLoan runtime required to probe fee/capacity
accounting. **Status: PARTIAL — control-flow only, NEEDS_MORE_RUNTIME. Not advanced to PoC.**

---

## PoC plan (Phase 7+)
| mech | class | tier | feasible self-contained? |
|---|---|---|---|
| M1 distribute | ACCOUNTING/ACCESS | B (partial runtime) | yes — distributor + mock registry/LoanManager/ERC20 |
| M3 burnAndWithdraw | STATE | B (runtime) | yes — UserVault + mock ERC721/AddressManager |
| M2 wq rounding | SHARE/DOS | B (runtime) | yes — WithdrawalQueue from a test "pool" |
| M4 offers | ORDER | — | NEEDS_MORE_RUNTIME (no exact hypothesis) |

3 of 4 classes advance to runtime PoC; ORDER stays control-flow.
