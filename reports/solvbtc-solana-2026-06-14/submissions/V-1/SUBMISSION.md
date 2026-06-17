<!--
PLATFORM-PASTE-READY report for Solv BTC (Solana) finding V-1. Plain prose + standard code fences only.
Paste each labelled section into the matching field. Facts validated; runnable PoC (cargo test) passes.
Copy from the RAW file, not a rendered preview.

NOTE: this program states "AI-generated reports will not be considered" — the submitter should author the
final writeup in their own words; this file is the analysis + a runnable PoC to support it.
-->

# Field: Target
https://github.com/solv-finance/SolvBTC-Solana-Contract (commit 4c8f194), programs/solvbtc/src/contexts/vault_withdraw.rs

# Field: Category
Business Logic Errors (accounting / NAV validation)

# Field: Severity
Low

# Field: Title
Loosened NAV check in vault_withdraw lets a pending withdrawal be claimed after NAV drops, overpaying the withdrawer by up to ~1% of the current NAV

# Field: Vulnerability details

Withdrawals are two-step: `vault_withdraw_request` burns the user's shares and stores a `WithdrawRequest`
whose `withdraw_amount` is fixed at request time as `Vault::withdrawal_from_shares(shares)` using the
request-time NAV. Later, `vault_withdraw` pays out `withdraw_request.withdraw_amount`.

In the current (post-audit) code, `vault_withdraw` validates the request's NAV against the current NAV with a
1% upward tolerance:

```rust
// vault_withdraw.rs :: withdraw_tokens
// Check 1.01*nav >= nav of withdraw request
let nav_diff = vault.nav * 100 / MAX_FEE;   // MAX_FEE = 10_000  => 1% of current NAV
let max_nav  = vault.nav + nav_diff;        // = current_nav * 1.01
require_gte!(max_nav, withdraw_request.nav, SolvError::NAVExceeded);
let (amount, fee) = Vault::calculate_fee(withdraw_request.withdraw_amount, vault.withdraw_fee);
```

This was changed from the original, stricter check `require_gte!(vault.nav, withdraw_request.nav)`
(`current_nav >= request_nav`) — see the attached `post_audit_navcheck.diff`. The OffsideLabs audit covered
an earlier commit; this loosening is in the unaudited post-audit delta.

Because the payout (`withdraw_amount`) is fixed at the request-time NAV, allowing `request_nav` to exceed the
current NAV by up to 1% means a withdrawal created at a higher NAV can still be completed after the NAV has
dropped by up to ~1%, paying the user the higher (request-time) value. The vault overpays the difference
versus what the user's burned shares are actually worth at the current NAV.

This is Low because the overpayment is bounded to ~1%, the NAV decline that triggers it is oracle-gated and
rate-limited (`Vault::set_nav` caps each update to ±0.05%, so ~20 updates are needed to move 1%) and is not
attacker-forcible, and every withdrawal is gated by the off-chain verifier's ECDSA signature. It is a
correctness/over-payment weakening of the audited behavior, adjacent to the audit's acknowledged finding 4.2
("unexpected withdrawals due to vault configuration changes"), not an unconditional drain.

## Impact

During a NAV decline, any pending withdrawal whose request NAV is up to 1% above the current NAV can be
claimed at the request-time value, transferring up to ~1% of the redeemed amount from the vault to the
withdrawer at the expense of remaining holders. The pre-audit check would have rejected such a claim.

## Suggested fix

Restore the original invariant `require_gte!(vault.nav, withdraw_request.nav)` (only allow completion when the
current NAV is at least the request NAV), or, if a tolerance band is intended, recompute the payout against
the current NAV (`Vault::withdrawal_from_shares(shares)` at `vault.nav`) rather than paying the fixed
request-time `withdraw_amount`, so the user never receives more than their shares are currently worth.

# Field: Validation steps

The PoC is a runnable Rust test that imports the real `solvbtc` crate and uses the actual
`Vault::withdrawal_from_shares` and `Vault::calculate_fee`, plus an exact replica of the `vault_withdraw`
NAV check, to demonstrate the overpayment at the boundary NAV. From the repo root:

```bash
cargo test -p solvbtc --test poc_nav_tolerance -- --nocapture
```

Steps proven:

1. A request is created at `request_nav = 1.01 * ONE_BITCOIN`; `withdraw_amount` is fixed to
   `withdrawal_from_shares(shares)` at that NAV.
2. By claim time the NAV has dropped to `current_nav = ONE_BITCOIN` (= `request_nav / 1.01`).
3. The current (1.01×) check PASSES; the pre-audit check (`current_nav >= request_nav`) FAILS.
4. The payout (request-NAV based) is `1_010_000_000`, while the fair value at the current NAV is
   `1_000_000_000` — an overpayment of `10_000_000` (~100 bps / 1%).

Captured output (passes):

```
running 1 test
request_nav         = 101000000
current_nav (claim) = 100000000
payout (request-nav based) = 1010000000
fair value at current nav  = 1000000000
OVERPAY = 10000000  (~100 bps of fair value)
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

# Field: Attachments
- vulnerable/vault_withdraw_navcheck.rs   (in-scope nav check in withdraw_tokens)
- vulnerable/post_audit_navcheck.diff     (the post-audit loosening: current_nav>=req  ->  current_nav*1.01>=req)
- poc/poc_nav_tolerance.rs                (runnable PoC using the real Vault math)
- poc_output.log                          (captured passing run)
