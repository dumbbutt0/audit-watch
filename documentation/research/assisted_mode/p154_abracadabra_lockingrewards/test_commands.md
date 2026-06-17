# P154 — Test Commands

## Setup (deps cloned into pocs/p154/lib, removed after the run)
```
cd audits/abracadabra-2024-03-holdout/pocs/p154/lib
git clone --depth 1 https://github.com/foundry-rs/forge-std
git clone --depth 1 https://github.com/transmissions11/solmate
git clone --depth 1 https://github.com/Vectorized/solady
git clone --depth 1 --branch v4.9.6 https://github.com/OpenZeppelin/openzeppelin-contracts
```

## Run
```
cd audits/abracadabra-2024-03-holdout/pocs/p154
forge test -vv      # solc 0.8.23, evm_version shanghai (set in foundry.toml)
```

## Result (full log in execution_output.txt)
```
[PASS] test_control_boost_legitimate_during_active_lock()
[PASS] test_corrected_prompt_processing_removes_overaccrual()
[PASS] test_mechanism_boost_persists_after_expiry_unprocessed()
[PASS] test_quantify_overaccrual_window2()
Suite result: ok. 4 passed; 0 failed; 0 skipped
```

## Cleanup (post-run, per integrity rule)
```
rm -rf audits/abracadabra-2024-03-holdout/pocs/p154/lib audits/abracadabra-2024-03-holdout/pocs/p154/out \
       audits/abracadabra-2024-03-holdout/pocs/p154/cache
```
The harness (`foundry.toml` + `test/*.t.sol` + `execution_output.txt`) is retained and re-runnable by
re-cloning the four deps above.
