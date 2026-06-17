// REFERENCE: hawal-bug-bounty-main/sources/walstaking.move get_min_total_validator
// auto-select iterates ONLY staking.active_validators -> an injected validator can't capture other users' auto-staked WAL.

    fun get_min_total_validator(staking: &Staking): ID {
        let active_validators = staking.active_validators;
        let length = vector::length(&active_validators);
        assert!(length > 0, EStakeActiveValidatorsIsNull);

        let mut i = 0;
        let mut min_id = active_validators[0];
        let mut has_non_pool_validator = false;
        // Take the nodes that have not yet pledged
        while (i < length) {
            let validator = active_validators[i];
            if (!table::contains(&staking.pools, validator)) {
                min_id = validator;
                has_non_pool_validator = true;
                break
            };
            i = i + 1;
        };

        // If all validators are in the staking.pools, find the one with the smallest total_staked
        if (!has_non_pool_validator) {
            let mut p = 1;
            let pool_frist = table::borrow(&staking.pools, active_validators[0]);
            let mut min_total: u64 = pool_frist.total_staked;
            min_id = active_validators[0];
            while (p < length) {
                let validator = active_validators[p];
                let pool = table::borrow(&staking.pools, validator);
                if (pool.total_staked < min_total) {
                    min_id = validator;
                    min_total = pool.total_staked;
                };

                p = p + 1;
            };
        };

        return min_id
    }
