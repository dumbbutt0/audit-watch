# DeepBook v3 (Sui Move CLOB) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `MystenLabs/deepbookv3` @ `9f69985`, in-scope core package `packages/deepbook` (CLOB). Covered by the LIVE
**Sui Protocol** HackenProof bounty (deepbookv3 in scope; low rep barrier, "first-time reporters welcome", $5
antispam fee). 6th Sui-Move target validating Audit-Watch's Move support ([[project_move_support]]). Build: `sui
move build` succeeds (current framework). Note: `packages/deepbook_margin` + `predict` are newer, adjacent products
(scope-dependent; not covered here).

## VERDICT: HONEST NEGATIVE — no permissionless bug found in the audited CLOB safety surfaces.
DeepBook v3 is a Mysten-flagship CLOB (heavily audited). The value-extraction-critical layers — custody/auth, vault
solvency, flash loan, and taker fill accounting — are sound, several **by construction**.

## Reviewed and SOUND
- **Custody / auth** (`balance_manager.move`): `TradeProof` (drop-only, can't be stored) is bound to a specific
  `balance_manager_id` + trader; `validate_proof` asserts `object::id(bm) == proof.balance_manager_id` ⇒ a proof for
  manager A can't act on B. `TradeCap`/`DepositCap`/`WithdrawCap` are owner-minted (`validate_owner`) and id-bound;
  deposits/withdrawals go through proof validation. The `<App>` cap-mint path was already hardened with a witness
  (`new_with_custom_owner_caps_v2`) — they fixed the prior type-tag-only spoof. No cap-confusion / unauthorized
  withdrawal path found.
- **Vault solvency** (`vault.move::settle_balance_manager`): settlement moves only the **net `(out − in)` per asset**
  (base/quote/deep) between vault and manager via `balance::split`/`join`. `split` aborts on underflow ⇒ **the vault
  can never pay out more than it holds** (worst case a settle aborts — no insolvency, no value minting). The
  permissionless settle path asserts `balances_in == 0` (deposits only). Solvency is **structurally enforced**.
- **Flash loan** (`vault.move`): `FlashLoan` struct has **no abilities** (hot potato → forced repay); return asserts
  `pool_id` + `type_name` match AND `coin.value() == borrow_quantity` (exact return; DeepBook flash loans are
  fee-free), then rejoins the vault. Can't be dropped, mis-pooled, or under-returned.
- **Taker fill accounting** (`order_info.move::calculate_partial_fill_balances`): the taker's `settled`/`owed` are
  derived from the **same `fills` vector** as the makers' settlements — `settled.base = Σ fill.base_quantity`
  (= makers' base given), `owed.quote = Σ fill.quote_quantity` (= makers' quote received), at maker resting prices;
  fees added to `owed`; unfilled remainder escrowed as a maker order. So a fill can't credit the taker more base/
  quote than the matched makers provide — **conservation by shared derivation**. Fee on executed via taker_fee,
  on remainder via maker_fee.

## Not exhaustively re-derived (deep, heavily-audited remainder)
- `book.move` matching internals (price-time priority, order insertion/iteration, expired-order handling,
  self-match) + `big_vector.move` (1302 SLOC order-storage data structure) + `order_deep_price` fee math. These are
  the most-audited core; sampled and consistent with the conserving design above, not line-by-line re-derived.
- `deepbook_margin` (margin trading: margin_manager 1880, liquidation, oracle) + `predict` — newer/adjacent,
  scope-dependent, not audited here (higher-EV if confirmed in scope, but separate from the core CLOB).

## Bottom line
DeepBook v3's custody, vault solvency, flash loan, and taker fill accounting are sound — solvency and fill
conservation are enforced structurally (balance split/join non-negativity + shared-fills derivation), and the auth
model binds proofs/caps to the balance manager. No permissionless extraction found in the CLOB core →
**honest negative, not submitted.** Build confirmed (`sui move build`). If pursuing further, the newer
`deepbook_margin` layer (if in scope) is the higher-EV surface vs the audited CLOB core.
