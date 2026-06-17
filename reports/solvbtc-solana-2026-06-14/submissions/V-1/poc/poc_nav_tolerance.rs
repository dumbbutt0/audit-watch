// PoC for SolvBTC finding V-1 (Low): the post-audit-loosened nav check in vault_withdraw lets a
// pending withdrawal (payout fixed at request-time nav) be claimed after the vault NAV has DROPPED by
// up to ~1%, overpaying the withdrawer vs the current NAV.
//
// IN-SCOPE CODE (unaudited post-audit delta; OffsideLabs audited an earlier commit):
//   programs/solvbtc/src/contexts/vault_withdraw.rs  (withdraw_tokens):
//       // Check 1.01*nav >= nav of withdraw request
//       let nav_diff = vault.nav * 100 / MAX_FEE;            // = 1% of current nav  (MAX_FEE = 10_000)
//       let max_nav  = vault.nav + nav_diff;                 // = current_nav * 1.01
//       require_gte!(max_nav, withdraw_request.nav, NAVExceeded);
//       let (amount, fee) = Vault::calculate_fee(withdraw_request.withdraw_amount, vault.withdraw_fee);
//   The PRE-AUDIT check was: require_gte!(vault.nav, withdraw_request.nav)  (current_nav >= request_nav).
//   withdraw_request.withdraw_amount is fixed at REQUEST time = Vault::withdrawal_from_shares(shares) at request nav
//   (programs/solvbtc/src/contexts/vault_request_withdraw.rs::open_request_account).
//
// This test uses the REAL Vault math (solvbtc::state::Vault) + the REAL constants, and replicates the exact
// nav-check from vault_withdraw.rs, to prove: at the boundary current_nav = request_nav / 1.01 the new check
// PASSES, the payout (request-nav based) exceeds the current-nav fair value by ~1%, and the old check FAILS.
//
// Run:  cargo test -p solvbtc --test poc_nav_tolerance -- --nocapture

use anchor_lang::prelude::Pubkey;
use solvbtc::constants::{MAX_FEE, ONE_BITCOIN};
use solvbtc::state::vault::Vault;

fn make_vault(nav: u64, withdraw_fee: u16) -> Vault {
    Vault {
        admin: Pubkey::default(),
        mint: Pubkey::default(),
        fee_receiver: Pubkey::default(),
        treasurer: Pubkey::default(),
        deposit_currencies: Default::default(),
        verifier: [0u8; 64],
        oracle_updated: 0,
        oracle_manager: Pubkey::default(),
        nav,
        withdraw_fee,
        bump: 255,
    }
}

// Exact replica of the nav check in vault_withdraw.rs::withdraw_tokens (current code).
fn new_check_passes(current_nav: u64, request_nav: u64) -> bool {
    let nav_diff = (current_nav as u128 * 100 / MAX_FEE as u128) as u64; // 1% of current nav
    let max_nav = current_nav + nav_diff; // current_nav * 1.01
    max_nav >= request_nav
}

// The pre-audit check (what the code did before the post-audit "Check 1.01*nav" change).
fn old_check_passes(current_nav: u64, request_nav: u64) -> bool {
    current_nav >= request_nav
}

#[test]
fn poc_nav_tolerance_allows_one_percent_overpayment_on_nav_drop() {
    // withdraw_fee = 0 so the overpayment is shown net of fees (the fee is orthogonal).
    let withdraw_fee: u16 = 0;

    // Shares the user burned in vault_withdraw_request.
    let shares: u64 = 1_000_000_000; // 10 units at 1e8 scale

    // --- Request time: NAV is high. withdraw_amount is FIXED here. ---
    let request_nav: u64 = ONE_BITCOIN + ONE_BITCOIN / 100; // 1.01 * ONE_BITCOIN
    let vault_at_request = make_vault(request_nav, withdraw_fee);
    let withdraw_amount = vault_at_request
        .withdrawal_from_shares(shares)
        .expect("withdrawal_from_shares");
    // This is what vault_withdraw will pay out (after a 0% fee).
    let (payout, _fee) = Vault::calculate_fee(withdraw_amount, withdraw_fee).expect("calculate_fee");

    // --- Claim time: NAV has DROPPED to the boundary where the NEW check still passes. ---
    // New check passes iff current_nav * 1.01 >= request_nav  =>  current_nav >= request_nav / 1.01.
    let current_nav: u64 = ONE_BITCOIN; // = request_nav / 1.01 exactly (ONE_BITCOIN*1.01 == request_nav)
    let vault_now = make_vault(current_nav, withdraw_fee);

    // The HONEST payout at the current NAV (what the user's shares are actually worth now).
    let fair_now = vault_now
        .withdrawal_from_shares(shares)
        .expect("withdrawal_from_shares now");

    println!("request_nav         = {request_nav}");
    println!("current_nav (claim) = {current_nav}");
    println!("payout (request-nav based) = {payout}");
    println!("fair value at current nav  = {fair_now}");
    let overpay = payout - fair_now;
    let overpay_bps = (overpay as u128 * 10_000 / fair_now as u128) as u64;
    println!("OVERPAY = {overpay}  (~{overpay_bps} bps of fair value)");

    // L3 OUTCOME: the new check ACCEPTS this claim, the old check would REJECT it,
    // and the user is overpaid by ~1% vs the current NAV.
    assert!(new_check_passes(current_nav, request_nav), "new (1.01x) check should PASS at the boundary");
    assert!(!old_check_passes(current_nav, request_nav), "pre-audit check should REJECT (current_nav < request_nav)");
    assert!(payout > fair_now, "payout must exceed current-nav fair value (overpayment)");
    assert_eq!(overpay, 10_000_000, "overpay is exactly 1e7 = 1% of the 1e9 fair value");
    assert_eq!(overpay_bps, 100, "overpayment is ~100 bps (1%)");
}
