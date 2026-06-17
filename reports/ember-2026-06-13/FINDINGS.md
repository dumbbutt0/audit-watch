# Ember Vaults (Sui Move) — audit findings (HackenProof, ember-protocol/Ember-Vaults)

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `ember-protocol/Ember-Vaults` @ `28a2d8e` (public). Sui Move, package `ember_vaults`,
published-at `0x4e1634…f863`. Scope = `sources/` only (`[test_only]` excluded). Critical $10–15k / High $5k,
KYC + **runnable PoC required**. First real-world use of Audit-Watch's new Move support + `sui move test` harness.

Modules: `vault.move` (1810, core), `gateway.move` (446, entries), `admin.move` (402, caps/config),
`queue.move` (115, FIFO), `math.move` (145), `events.move` (791, events only). Architecture = **rate-based
async-withdrawal vault**: a `rate_manager`-set exchange `rate` (fixed-point 1e9, NOT balanceOf-derived → classic
first-depositor inflation does not apply); deposits/mints are synchronous, redemptions are queued and processed by
the operator at the rate-at-processing-time.

## VERDICT: full review complete → HONEST NEGATIVE. No permissionless High/Critical found.
The highest-residual-risk area (multi-account cancel/skip/process share accounting) is PoC-proven consistent via a
runnable `sui move test` invariant harness (3 adversarial scenarios, all pass). Nothing submitted; no finding
manufactured. This also validates Audit-Watch's new Move support on a second real Sui target.

### Reviewed and SOUND
- **math.move**: `mul`/`div` (floor) + `div_ceil`, all u128-intermediate with checked (`as u64`) downcast that
  ABORTS on overflow — no silent wrap. Rounding direction is controllable.
- **Conversion rounding consistently favors the vault**: deposit shares = `mul(amount,rate)` (floor);
  mint assets-in = `div_ceil(shares,rate)` (ceil); withdrawal payout = `div(shares,rate)` (floor). A
  deposit→redeem round-trip can only LOSE to rounding, never extract.
- **deposit_asset_v2 / mint_shares_v2**: real `Balance<T>` accounted, `min_shares`/`max_amount` slippage guards,
  `max_tvl` enforced post-mint, blacklist + sub-account gating. Shares minted via treasury cap = exact.
- **redeem_shares**: user share `Balance<R>` escrowed into `pending_shares_to_burn`; request enqueued; invariant
  `pending_shares_to_burn == Σ pending request shares` maintained.
- **process_request / process_withdrawal_requests(_up_to_timestamp)**: FIFO dequeue; burns or returns shares
  exactly once; `assert balance >= withdraw_amount` (head-of-line blocking = liveness/DoS only, OOS; funds not
  lost). Per-account `pending_withdrawal_requests` removed at index 0 each time — consistent with global FIFO.
- **cancel_pending_withdrawal_request**: only MARKS (pushes seq to `cancel_withdraw_request`); shares returned at
  processing time, not immediately → no double-return. Can only cancel own, existing, not-already-cancelled req;
  cannot cancel a processed req.
- **Fund movement without shares** (`withdraw_from_vault_without_redeeming_shares`,
  `deposit_to_vault_without_minting_shares(_v2)`): gated `sender == vault.operator` + whitelisted `sub_account`
  (operator = privileged → OOS).
- **update_vault_rate**: `rate_manager`-gated, `rate_update_interval` rate-limited, magnitude-bounded
  (`max_rate_change_per_update` + global `min_rate`/`max_rate`); fees charged at old rate first. Privileged → OOS.
- **Platform fee**: time-based `tvl * fee_percentage * elapsed / DENOM`, asset-denominated to `fee.accrued`,
  privileged config → not a permissionless drain.
- **gateway.move**: thin pass-through; AdminCap-gated entries forward the cap, permissionless entries
  (deposit/mint/redeem/cancel) forward to the verified v2 fns; no check bypass. v1 `deposit_asset`/`mint_shares`/
  `charge_platform_fee`/`update_vault_fee_percentage` abort as deprecated (live = v2).

### admin.move + create_vault — reviewed, SOUND
- **admin.move**: every config mutator is `&AdminCap`-gated (privileged → OOS); bounds sanity-checked
  (`min_rate>0`, `min≤max`, `default∈[min,max]`, `max_fee<1e9`, `rate_interval≥60s`). `verify_supported_package`
  (version==VERSION, upgrade gate) and `verify_protocol_not_paused` are simple/correct. `initialize_module`
  creates AdminCap + ProtocolConfig once at publish.
- **create_vault**: `&AdminCap`-gated; asserts **`coin::total_supply(treasury_cap) == 0`** (prevents creating a
  vault over a receipt token with pre-existing supply — a real shares↔assets desync defense); admin/operator
  non-zero+distinct+not-sub-accounts; initial `rate = config.default_rate`; `min_withdrawal_shares>0`; `fee≤max`.

### Withdrawal-accounting invariant harness (the highest-risk area) — PoC-PROVEN consistent
`tests/zzz_withdrawal_accounting_invariant.move` (runnable `sui move test`, 3/3 pass). Invariant asserted after
EVERY redeem/cancel/process step: `pending_shares_to_burn == Σ get_account_total_pending_withdrawal_shares ==
Σ per-account request.shares`. Scenarios: (1) 3 accounts interleaved redeem + cancel-1st + cancel-2nd +
blacklist-skip + partial(3)/full(5) processing; (2) cancel a MIDDLE request then redeem MORE after the cancel;
(3) same user double-cancels (non-adjacent) processed in FIFO order. In all, the invariant held and the escrow
fully drained to 0 with an empty queue → no shares lost, duplicated, or stranded by the cancel/skip/FIFO-index logic.

## Bottom line
Full review of all in-scope `sources/` modules (math/queue/vault/gateway/admin) complete. The Ember Vaults vault is
carefully built and vault-favoring: rounding favors the vault, deposit/mint/redeem/fee/fund-movement are correctly
gated (operator/admin/AdminCap; rate privileged+bounded), `create_vault` guards receipt-token-supply desync, and
the intricate async cancel/process share accounting is PoC-proven consistent. **No permissionless High/Critical
found → honest negative, not submitted.** Residual (non-payable / OOS): operator/rate_manager are trusted roles
(privileged-address attacks OOS); head-of-line blocking on an underfunded queue is liveness/DoS (OOS). PoC harness:
`tests/zzz_withdrawal_accounting_invariant.move`.
