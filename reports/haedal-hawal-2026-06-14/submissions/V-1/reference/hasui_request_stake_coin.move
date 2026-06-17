// REFERENCE (audited, correct pattern): hasui-bug-bounty-main/sources/staking.move
// request_stake_coin (293-327): validates user validator vs active set, falls back to vault if not active.

    public fun request_stake_coin(wrapper: &mut SuiSystemState, staking: &mut Staking, input: Coin<SUI>, validator: address, ctx: &mut TxContext): Coin<HASUI> {
        assert_version(staking);
        assert!(!staking.pause_stake, EStakePause);
        // calculate the haSUI amount
        let input_sui_amount = coin::value(&input);
        assert!(input_sui_amount >= MIN_STAKING_THRESHOLD, EStakeNotEnoughSui);
        let amount = get_stsui_by_sui(staking, input_sui_amount);
        assert!(amount > 0, EStakeNoStsuiMint);

        // mint haSUI and transfer to sender
        let sender = tx_context::sender(ctx);
        let ret = coin::mint(&mut staking.stsui_treasury_cap, amount, ctx);

        let active_validators = sui_system::active_validator_addresses(wrapper);
        // user does not select a validator, or selects a invalid validator, just let protocol to select a validator
        if (validator == @0x0 || !is_active_validator(validator, &active_validators)) {
            // deposit sui to vault, and wait for staking later
            vault::deposit(&mut staking.sui_vault, coin::into_balance(input));
        } else { // user selects a validator
            save_user_selected_staking(staking, input, validator);
        };

        // update the counters
        staking.total_staked = staking.total_staked + input_sui_amount;
        staking.stsui_supply = coin::total_supply(&staking.stsui_treasury_cap);

        event::emit(UserStaked {
            owner: sender,
            sui_amount: input_sui_amount,
            st_amount: amount,
            validator: validator,
        });

        ret
    }

    public fun import_stake_sui_vec(wrapper: &mut SuiSystemState, staking: &mut Staking, inputs: vector<StakedSui>, validator: address, ctx: &mut TxContext): Coin<HASUI>  {
        let input_bal = balance::zero();
        while (vector::length(&inputs) > 0) {
            let withdraw_bal = sui_system::request_withdraw_stake_non_entry(wrapper, vector::pop_back(&mut inputs), ctx);
            balance::join(&mut input_bal, withdraw_bal);
        };
        vector::destroy_empty(inputs);

        request_stake_coin(wrapper, staking, coin::from_balance(input_bal, ctx), validator, ctx)
    }

    /// each validator have a balance for user SUI
    fun save_user_selected_staking(staking: &mut Staking, input: Coin<SUI>, validator: address) {
        if (!vec_map::contains(&staking.user_selected_validator_bals, &validator)) {
            vec_map::insert(&mut staking.user_selected_validator_bals, validator, balance::zero());
        };
        let validator_balance = vec_map::get_mut(&mut staking.user_selected_validator_bals, &validator);
        balance::join(validator_balance, coin::into_balance(input));
    }

