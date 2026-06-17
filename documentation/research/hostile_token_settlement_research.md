# Research detector: `hostile_token_settlement` (RESEARCH-ONLY, un-wired)

> is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[]. Built P238 to close the
> P236 second-leverage recall gap (hostile-token behavior in must-succeed settlement paths). Scope: settlement-path
> hostile-token DoS ONLY. Does NOT detect Safe-management, create-time reentrancy, Seaport-invariant, or economic
> issues.

## 1. Research
Gap (P236, verdict B, family 2): cleanup/settlement flows that assume a token transfer must succeed, where an
attacker- or user-selected token can revert / blacklist / return-false / reenter and **block the required cleanup**
→ permanent lock or DoS of another user. Architectural (any order/market/rental/lending settlement that pushes a
third-party token to a counterparty), not reNFT-specific. Precision tension: "settlement transfers a token" is
everywhere — the lens must fire only when (a) the flow is a *cleanup*, (b) the transfer is *must-succeed*, (c) the
token is *attacker-selected*, (d) there is *no containment*, and (e) the recipient is a *counterparty* (not the
caller's own asset).

## 2. Taxonomy
One finding shape: **hostile_token_settlement_dos**. Five-signal AND gate:
S1 cleanup-verb function (stop/reclaim/close/settle/liquidate/withdraw/refund/finalize/resolve/claim/...) ·
S2 must-succeed token push (transfer/transferFrom/safeTransfer*/safeTransferFrom/_safeTransfer/_transferERC721/1155/
low-level call) not wrapped in try/catch · S3 attacker/order-sourced token (item.token / items[ / consideration /
offer / untrusted token param) · S4 missing containment (no try/catch, pull-payment, or allowlist) · S5 counterparty
recipient (lender/renter/recipient/treasury/…). S3 order/array-sourced → high; bare token param → medium.
IN scope: settlement/escrow/reclaim flows pushing user-selected tokens. OUT: caller's-own withdrawals; allowlisted/
immutable assets; try/catch- or pull-payment-contained flows; admin-only (downgrade to low).

## 3. Ground-truth corpus
- **In-repo anchor (runnable):** reNFT 2024-01 `PaymentEscrow._settlePayment` (`_safeTransfer` of `item.token` from
  the Seaport order, loop, no try/catch) + `Reclaimer.reclaimRentalOrder` (`safeTransferFrom` of `item.token`).
- **Web-confirmed:** reNFT C4 H-01 (#614 — malicious consideration-tip ERC20 reverts → stopRent locks), #64
  (blacklisting payment ERC20 → stuck), #605 (blacklisted lender → stopRent freeze).
- **Negatives/controls:** caller's-own `withdraw(msg.sender)`; allowlisted-token settle; try/catch-isolated settle;
  pull-payment record-debt settle; admin-only settle.

## 4. Prototype (this detector)
- `scripts/hostile_token_settlement_taxonomy.py` — pure 5-signal classifier.
- `scripts/hostile_token_settlement_audit.py` — manifest-driven runner (in-scope + non-test; +1 helper resolution so
  inlined `_settlePayment`/`_safeTransfer`/`_transferERC721` transfers are seen; dedup one per contract+shape;
  4 research flags; `--out`).
- `config/hostile_token_settlement_patterns.json` — cleanup verbs, transfer primitives, attacker-source markers,
  containment/pull-payment/allowlist markers, counterparty terms, suppressions, fp_controls.
- `tests/hostile_token_settlement/` — 8 synthetic fixtures + admin-downgrade + reNFT replay (10 tests, all pass).

## 5–7. Validation / scope / stability
reNFT full-workspace replay (22,345 items, 160 in-scope): **2 candidates, both HIGH, 0 FP** —
`PaymentEscrow._settlePayment` (H-01 / #64 / #605) and `Reclaimer.reclaimRentalOrder` (reclaim DoS). `Stop.stopRent`
correctly does not fire (its transfers are cross-contract; the lens fires on the contract that holds the must-succeed
transfer — precise root attribution). Recovery is mechanism-based (cleanup-verb + order-sourced token + missing
containment), not answer-key matching.

A precision bug was caught and fixed during validation: the bare pull-payment marker `"owed"` matched **"all*owed*"**
inside Reclaimer's `OnlyRentalSafeAllowed` error and falsely suppressed the reclaim candidate; tightened to the
record-debt form (`owed[` / `owed +=` / `debt[`). Lesson: substring markers must be anchored to their syntactic form.

- **Scope classification:** NARROW SCOPE CONFIRMED — settlement/cleanup must-succeed-transfer DoS.
- **Stability classification:** **PROMISING-BUT-NEEDS-REFINEMENT** (single anchor, 0 FP). Un-wired; promotion is a
  separate human decision after a 15–20 target validation campaign.
