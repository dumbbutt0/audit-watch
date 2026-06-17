// IN-SCOPE VULNERABLE: hawal-bug-bounty-main/sources/walstaking.move
// request_stake_coin (273-316) stakes to ANY user-supplied validator with no active-set check;
// stake_to_validator (319-357) adds the arbitrary validator to staking.pools + staking.validators.

    public fun request_stake_coin(
        wal_staking: &mut WalStaking,
        staking: &mut Staking, 
        input: Coin<WAL>, 
        validator: ID, 
        ctx: &mut TxContext
    ): Coin<HAWAL> {
        assert_version(staking);
        assert!(!staking.pause_stake, EStakePause);
        // calculate the haWAL amount
        let input_wal_amount = coin::value(&input);
        assert!(input_wal_amount >= MIN_STAKING_THRESHOLD, EStakeNotEnoughWal);
        let active_validators_len = vector::length(&staking.active_validators);
        assert!(active_validators_len > 0, EStakeActiveValidatorsNotFound);
        let amount = get_hawal_by_wal(staking, input_wal_amount);
        assert!(amount > 0, EStakeNoHaWalMint);
        
        // mint haWAL and transfer to sender
        let sender = tx_context::sender(ctx);
        let ret = coin::mint(&mut staking.hawal_treasury_cap, amount, ctx);

        // user does not select a validator, or selects a invalid validator, just let protocol to select a validator
        if (validator == object::id_from_address(@0x0)) {
            // auto selects a validator
            let auto_validator = get_min_total_validator(staking);
            stake_to_validator(coin::into_balance(input), staking, wal_staking, auto_validator, ctx);
        } else { 
            // user selects a validator
            stake_to_validator(coin::into_balance(input), staking, wal_staking, validator, ctx);
        };

        // update the counters
        staking.total_staked = staking.total_staked + input_wal_amount;
        staking.hawal_supply = coin::total_supply(&staking.hawal_treasury_cap);

        event::emit(UserStaked {
            owner: sender,
            wal_amount: input_wal_amount,
            hawal_amount: amount,
            validator: validator,
        });

        ret
    }

    /// call the stake method to stake to validator
    fun stake_to_validator(
        bal: Balance<WAL>,
        staking: &mut Staking,
        wal_staking: &mut WalStaking, 
        validator: ID,
        ctx: &mut TxContext,
    ) {
        // search the validator's pool
        if (!table::contains(&staking.pools, validator)) {
            let pool = PoolInfo  {
                staked: vec_map::empty<u32, StakedWal>(),
                withdrawing: vec_map::empty<u32, StakedWal>(),
                total_staked: 0,
                rewards: 0,
            };
            table::add(&mut staking.pools, validator, pool);
            vector::push_back(&mut staking.validators, validator);
        };
        let pool = table::borrow_mut(&mut staking.pools, validator);

        let amount = balance::value(&bal);
        pool.total_staked = pool.total_staked + amount;
        let staked_wal = staking::stake_with_pool(wal_staking, coin::from_balance(bal, ctx), validator, ctx);
        // make sure each epoch has only 1 StakedWal
        let staked_wal_id = object::id(&staked_wal);
        let activation_epoch = staked_wal.activation_epoch();        
        if (pool.staked.contains(&activation_epoch)) {
            pool.staked.get_mut(&activation_epoch).join(staked_wal);
        } else {
            pool.staked.insert(activation_epoch, staked_wal);
        };

        event::emit(SystemStaked {
            staked_wal_id: staked_wal_id,
            epoch: tx_context::epoch(ctx),
            wal_amount: amount,
            validator: validator,
        });
    }
