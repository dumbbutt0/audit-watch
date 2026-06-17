// AUDIT HARNESS (not protocol code): reserve-level cToken accounting conservation for Suilend.
// Banks the highest-value rounding/accounting invariants on the deposit/redeem + interest surface:
//   (1) a cToken deposit->redeem round-trip can NEVER return more liquidity than deposited (rounding favors pool);
//   (2) interest accrual only GROWS the cToken exchange rate (depositors never lose value to a rounding bug);
//   (3) over many interleaved deposits/redeems the reserve's internal `available_amount` stays exactly equal to
//       the real held Balance (no value created or leaked).
#[test_only]
module suilend::zzz_reserve_conservation {
    use sui::test_scenario::{Self};
    use sui::balance;
    use sui::clock;
    use suilend::decimal::{Self, Decimal};
    use suilend::reserve::{
        Self,
        create_for_testing,
        deposit_liquidity_and_mint_ctokens,
        redeem_ctokens,
        fulfill_liquidity_request,
        ctoken_ratio,
        compound_interest,
    };
    use suilend::reserve_config::default_reserve_config;
    use suilend::test_usdc::TEST_USDC;

    public struct EVAL_LM has drop {}

    // available, ctoken_supply, borrowed chosen to give a non-integer cToken ratio (=2.5) so rounding bites.
    fun new_reserve(scenario: &mut test_scenario::Scenario): reserve::Reserve<EVAL_LM> {
        create_for_testing<EVAL_LM, TEST_USDC>(
            default_reserve_config(scenario.ctx()),
            0,            // array_index
            6,            // mint_decimals
            decimal::from(1),          // price
            0,                         // price_last_update_ts
            10_000_000,                // available_amount
            6_000_000,                 // ctoken_supply
            decimal::from(5_000_000),  // borrowed_amount  -> total=15M, ratio=2.5
            decimal::from(1),          // cumulative_borrow_rate
            0,                         // interest_last_update_ts
            scenario.ctx(),
        )
    }

    // (1) round-trip can't profit: deposit L -> ctokens -> redeem -> fulfill -> liquidity out L'; assert L' <= L.
    #[test]
    fun test_ctoken_roundtrip_no_profit() {
        let mut scenario = test_scenario::begin(@0xA11CE);
        let amounts = vector[1u64, 7, 333, 1000, 99_999, 1_234_567];
        let mut i = 0;
        while (i < vector::length(&amounts)) {
            let l = *vector::borrow(&amounts, i);
            let mut reserve = new_reserve(&mut scenario);

            let ctokens = deposit_liquidity_and_mint_ctokens<EVAL_LM, TEST_USDC>(
                &mut reserve,
                balance::create_for_testing<TEST_USDC>(l),
            );
            let req = redeem_ctokens<EVAL_LM, TEST_USDC>(&mut reserve, ctokens);
            let out = fulfill_liquidity_request<EVAL_LM, TEST_USDC>(&mut reserve, req);

            // INVARIANT: a deposit immediately followed by redeem never yields more than was put in.
            assert!(balance::value(&out) <= l, 100 + i);

            balance::destroy_for_testing(out);
            std::unit_test::destroy(reserve);
            i = i + 1;
        };
        test_scenario::end(scenario);
    }

    // (2) interest accrual only grows the cToken exchange rate (never shrinks it).
    #[test]
    fun test_interest_only_grows_ctoken_value() {
        let mut scenario = test_scenario::begin(@0xA11CE);
        let mut reserve = new_reserve(&mut scenario);
        let mut clk = clock::create_for_testing(scenario.ctx());

        let ratio0: Decimal = ctoken_ratio<EVAL_LM>(&reserve);
        let mut t = 0u64;
        let mut prev = ratio0;
        // advance time in steps, compounding each step; ratio must be monotonically non-decreasing.
        while (t < 10) {
            clock::set_for_testing(&mut clk, (t + 1) * 365 * 24 * 60 * 60 * 1000); // +1 year per step (ms)
            compound_interest<EVAL_LM>(&mut reserve, &clk);
            let r = ctoken_ratio<EVAL_LM>(&reserve);
            assert!(r.ge(prev), 200 + t); // never decreases
            prev = r;
            t = t + 1;
        };
        assert!(prev.ge(ratio0), 299);

        clock::destroy_for_testing(clk);
        std::unit_test::destroy(reserve);
        test_scenario::end(scenario);
    }

    // (3) internal available_amount counter stays exactly equal to the real held Balance across many ops.
    #[test]
    fun test_available_amount_matches_held_balance() {
        let mut scenario = test_scenario::begin(@0xA11CE);
        let mut reserve = new_reserve(&mut scenario);

        let ops = vector[500_000u64, 250_000, 1_000_000, 50_000, 777_777];
        let mut i = 0;
        while (i < vector::length(&ops)) {
            let a = *vector::borrow(&ops, i);
            // deposit
            let mut ct = deposit_liquidity_and_mint_ctokens<EVAL_LM, TEST_USDC>(
                &mut reserve,
                balance::create_for_testing<TEST_USDC>(a),
            );
            // INVARIANT: counter == real balance held
            let bals = reserve::balances<EVAL_LM, TEST_USDC>(&reserve);
            assert!(reserve::available_amount<EVAL_LM>(&reserve) == balance::value(reserve::balances_available_amount<EVAL_LM, TEST_USDC>(bals)), 300 + i);

            // redeem half the freshly minted ctokens back out
            let half = balance::value(&ct) / 2;
            let to_redeem = balance::split(&mut ct, half);
            let req = redeem_ctokens<EVAL_LM, TEST_USDC>(&mut reserve, to_redeem);
            let out = fulfill_liquidity_request<EVAL_LM, TEST_USDC>(&mut reserve, req);

            let bals2 = reserve::balances<EVAL_LM, TEST_USDC>(&reserve);
            assert!(reserve::available_amount<EVAL_LM>(&reserve) == balance::value(reserve::balances_available_amount<EVAL_LM, TEST_USDC>(bals2)), 400 + i);

            balance::destroy_for_testing(out);
            std::unit_test::destroy(ct);
            i = i + 1;
        };

        std::unit_test::destroy(reserve);
        test_scenario::end(scenario);
    }
}
