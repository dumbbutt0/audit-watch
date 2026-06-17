// EXCERPT from zo_staking::pool (OUT-OF-SCOPE dependency) — shows refresh_pool is PRIVATE
// and pool_acc_reward_per_share() returns the raw STORED accumulator (stale).

    fun refresh_pool<S, R>(
        pool: &mut Pool<S, R>,
        current_timestamp: u64,
    ) {
        if (current_timestamp <= pool.last_updated_time || current_timestamp < pool.start_time) {
            return
        };

        let applicable_end_time = if (pool.end_time < pool.last_updated_time) {
            pool.last_updated_time
        } else {
            pool.end_time
        };

        let calculation_end_time = if (current_timestamp > applicable_end_time) {
            applicable_end_time
        } else {
            current_timestamp
        };

        if (calculation_end_time > pool.last_updated_time && pool.staked_amount > 0 && pool.reward_rate > 0) {
            let time_diff = calculation_end_time - pool.last_updated_time;

            assert!(MAX_U128 / pool.reward_rate >= (time_diff as u128), ERR_MATH_OVERFLOW);
            let reward_amount = (time_diff as u128) * pool.reward_rate;
            
            let reward_per_share = (((reward_amount as u256) * (SCALE_FACTOR as u256)) / (pool.staked_amount as u256)) as u128;
            assert!(reward_per_share <= MAX_U128, ERR_MATH_OVERFLOW);

            assert!(MAX_U128 - reward_per_share >= pool.acc_reward_per_share, ERR_MATH_OVERFLOW);
            pool.acc_reward_per_share = pool.acc_reward_per_share + reward_per_share;
        };

        pool.last_updated_time = calculation_end_time;

    public fun pool_last_updated_time<S, R>(p: &Pool<S, R>): u64 {
        p.last_updated_time
    }

    public fun pool_staked_amount<S, R>(p: &Pool<S, R>): u64 {
        p.staked_amount
    }

    public fun pool_reward_rate<S, R>(p: &Pool<S, R>): u128 {
        p.reward_rate
    }

    public fun pool_start_time<S, R>(p: &Pool<S, R>): u64 {
        p.start_time
    }

    public fun pool_end_time<S, R>(p: &Pool<S, R>): u64 {
        p.end_time
    }

    public fun pool_acc_reward_per_share<S, R>(p: &Pool<S, R>): u128 {
        p.acc_reward_per_share
    }
