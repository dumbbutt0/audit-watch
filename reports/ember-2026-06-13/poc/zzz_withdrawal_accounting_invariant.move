// AUDIT HARNESS (not protocol code): stress the multi-account cancel/skip/process share-accounting in vault.move.
// Core invariant (must hold after EVERY redeem/cancel/process step):
//   pending_shares_to_burn  ==  Σ_users get_account_total_pending_withdrawal_shares(user)
//                           ==  Σ_users Σ (their pending request.shares)
// A divergence means shares were lost, duplicated, or stranded in the escrow balance — a fund/accounting bug.
#[test_only]
module ember_vaults::zzz_withdrawal_accounting_invariant {
    use sui::test_scenario::{Self, Scenario};
    use sui::coin;
    use ember_vaults::test_utils::{Self, USDC, UltraUSDC};
    use ember_vaults::vault::{Self, Vault};
    use ember_vaults::admin::ProtocolConfig;
    use ember_vaults::queue;

    const DEP: u64 = 3_000_000;

    fun users(): vector<address> {
        vector[test_utils::alice(), test_utils::charlie(), @0xDAD]
    }

    // Σ per-account pending shares (table) and Σ per-account request.shares (vectors) must both equal the escrow.
    fun check_invariant(scenario: &mut Scenario, tag: u64) {
        test_scenario::next_tx(scenario, test_utils::bob());
        let vault = test_scenario::take_shared<Vault<USDC, UltraUSDC>>(scenario);

        let escrow = vault::get_pending_shares_to_redeem<USDC, UltraUSDC>(&vault);
        let us = users();
        let mut sum_table = 0u64;
        let mut sum_vec = 0u64;
        let mut i = 0;
        while (i < vector::length(&us)) {
            let u = *vector::borrow(&us, i);
            sum_table = sum_table + vault::get_account_total_pending_withdrawal_shares<USDC, UltraUSDC>(&vault, u);
            let reqs = vault::get_account_pending_withdrawal_requests<USDC, UltraUSDC>(&vault, u);
            let mut j = 0;
            while (j < vector::length(&reqs)) {
                let (_, _, shares, _, _, _) = vault::decode_withdrawal_request(vector::borrow(&reqs, j));
                sum_vec = sum_vec + shares;
                j = j + 1;
            };
            i = i + 1;
        };
        // tag*10 + k error codes so a failure pinpoints the step
        assert!(escrow == sum_table, tag * 10 + 1);
        assert!(escrow == sum_vec, tag * 10 + 2);

        test_scenario::return_shared(vault);
    }

    fun do_redeem(scenario: &mut Scenario, receipt: coin::Coin<UltraUSDC>, shares: u64, user: address): (coin::Coin<UltraUSDC>, u128) {
        let (rem, req) = test_utils::redeem_shares<USDC, UltraUSDC>(scenario, receipt, shares, user, user);
        let (_, _, _, _, _, seq) = vault::decode_withdrawal_request(&req);
        (rem, seq)
    }

    fun do_cancel(scenario: &mut Scenario, user: address, seq: u128) {
        test_scenario::next_tx(scenario, user);
        let mut vault = test_scenario::take_shared<Vault<USDC, UltraUSDC>>(scenario);
        let config = test_scenario::take_shared<ProtocolConfig>(scenario);
        vault::cancel_pending_withdrawal_request<USDC, UltraUSDC>(&mut vault, &config, seq, test_scenario::ctx(scenario));
        test_scenario::return_shared(config);
        test_scenario::return_shared(vault);
    }

    #[test]
    fun test_withdrawal_accounting_invariant_multi_account() {
        let alice = test_utils::alice();
        let charlie = test_utils::charlie();
        let dave = @0xDAD;

        let mut scenario = test_scenario::begin(test_utils::bob());
        test_utils::initialize(&mut scenario);

        // --- deposits: each user gets shares ---
        let ra = test_utils::deposit_assets<USDC, UltraUSDC>(&mut scenario, alice, DEP);
        let rc = test_utils::deposit_assets<USDC, UltraUSDC>(&mut scenario, charlie, DEP);
        let rd = test_utils::deposit_assets<USDC, UltraUSDC>(&mut scenario, dave, DEP);
        let unit = coin::value(&ra) / 3; // redeem in thirds

        // --- interleaved redeems → queue order [a1, c1, a2, d1, c2] ---
        let (ra, a1) = do_redeem(&mut scenario, ra, unit, alice);
        let (rc, c1) = do_redeem(&mut scenario, rc, unit, charlie);
        let (ra, a2) = do_redeem(&mut scenario, ra, unit, alice);
        let (rd, d1) = do_redeem(&mut scenario, rd, unit, dave);
        let (rc, c2) = do_redeem(&mut scenario, rc, unit, charlie);
        check_invariant(&mut scenario, 1);

        // --- cancels: alice cancels her 2nd (a2), charlie cancels his 1st (c1) ---
        do_cancel(&mut scenario, alice, a2);
        do_cancel(&mut scenario, charlie, c1);
        check_invariant(&mut scenario, 2);

        // --- blacklist dave so d1 is skipped+returned at processing ---
        test_utils::black_list_address(&mut scenario, dave, true);
        check_invariant(&mut scenario, 3);

        // --- process 3 of 5: a1(pay), c1(cancelled→return), a2(cancelled→return) ---
        test_utils::process_withdrawal_request<USDC, UltraUSDC>(&mut scenario, 3);
        check_invariant(&mut scenario, 4);

        // --- process remaining: d1(blacklisted→return), c2(pay) ---
        test_utils::process_withdrawal_request<USDC, UltraUSDC>(&mut scenario, 5);
        check_invariant(&mut scenario, 5);

        // --- final: queue empty, escrow fully drained ---
        test_scenario::next_tx(&mut scenario, test_utils::bob());
        {
            let vault = test_scenario::take_shared<Vault<USDC, UltraUSDC>>(&scenario);
            assert!(queue::len(vault::get_withdrawal_queue<USDC, UltraUSDC>(&vault)) == 0, 100);
            assert!(vault::get_pending_shares_to_redeem<USDC, UltraUSDC>(&vault) == 0, 101);
            test_scenario::return_shared(vault);
        };

        // consume leftover receipts
        coin::burn_for_testing(ra);
        coin::burn_for_testing(rc);
        coin::burn_for_testing(rd);
        test_scenario::end(scenario);
    }

    fun assert_drained(scenario: &mut Scenario) {
        test_scenario::next_tx(scenario, test_utils::bob());
        let vault = test_scenario::take_shared<Vault<USDC, UltraUSDC>>(scenario);
        assert!(queue::len(vault::get_withdrawal_queue<USDC, UltraUSDC>(&vault)) == 0, 200);
        assert!(vault::get_pending_shares_to_redeem<USDC, UltraUSDC>(&vault) == 0, 201);
        test_scenario::return_shared(vault);
    }

    // Cancel a MIDDLE request, then redeem MORE after the cancel (cancel-index stability vs a growing vector).
    #[test]
    fun test_cancel_middle_then_redeem_more() {
        let alice = test_utils::alice();
        let mut scenario = test_scenario::begin(test_utils::bob());
        test_utils::initialize(&mut scenario);

        let ra = test_utils::deposit_assets<USDC, UltraUSDC>(&mut scenario, alice, DEP);
        let unit = coin::value(&ra) / 5;
        let (ra, _a1) = do_redeem(&mut scenario, ra, unit, alice);
        let (ra, a2) = do_redeem(&mut scenario, ra, unit, alice);
        let (ra, _a3) = do_redeem(&mut scenario, ra, unit, alice);
        check_invariant(&mut scenario, 1);

        do_cancel(&mut scenario, alice, a2);          // cancel the middle one
        check_invariant(&mut scenario, 2);

        let (ra, _a4) = do_redeem(&mut scenario, ra, unit, alice);   // redeem more AFTER cancel
        check_invariant(&mut scenario, 3);

        // process all: a1 pay, a2 return(cancelled), a3 pay, a4 pay
        test_utils::process_withdrawal_request<USDC, UltraUSDC>(&mut scenario, 10);
        check_invariant(&mut scenario, 4);
        assert_drained(&mut scenario);

        coin::burn_for_testing(ra);
        test_scenario::end(scenario);
    }

    // Same user cancels TWO requests (non-adjacent), processed in FIFO order (cancel-list multi-entry removal).
    #[test]
    fun test_same_user_double_cancel() {
        let charlie = test_utils::charlie();
        let mut scenario = test_scenario::begin(test_utils::bob());
        test_utils::initialize(&mut scenario);

        let rc = test_utils::deposit_assets<USDC, UltraUSDC>(&mut scenario, charlie, DEP);
        let unit = coin::value(&rc) / 4;
        let (rc, c1) = do_redeem(&mut scenario, rc, unit, charlie);
        let (rc, _c2) = do_redeem(&mut scenario, rc, unit, charlie);
        let (rc, c3) = do_redeem(&mut scenario, rc, unit, charlie);
        check_invariant(&mut scenario, 1);

        do_cancel(&mut scenario, charlie, c1);        // cancel 1st
        do_cancel(&mut scenario, charlie, c3);        // and 3rd  -> cancel_list = [c1, c3]
        check_invariant(&mut scenario, 2);

        // process all: c1 return, c2 pay, c3 return
        test_utils::process_withdrawal_request<USDC, UltraUSDC>(&mut scenario, 10);
        check_invariant(&mut scenario, 3);
        assert_drained(&mut scenario);

        coin::burn_for_testing(rc);
        test_scenario::end(scenario);
    }
}
