# Evidence bundle

- Subject/commit: IQ-AI @ `db0d369b`; in-scope `src/LiquidityManager.sol` sha256(first14) `9a68efe4b6664f`.
- PoC: `p104/M01PreCreatePairPoC.t.sol` — `forge test --match-test test_M01_attacker_precreate_low_fee_is_adopted --evm-version cancun`.
- Vulnerable-source result: exploit reproduced (intended feeBps 100, attacker-adopted feeBps 1).
- Mitigation regression: PASS (guard reverts on the attacker pair; clean migration still succeeds) (source restored to `9a68efe4b6664f` afterward).
- Unrelated tests: PASS.
- Runtime evidence file: `documentation/research/assisted_mode/p104/reproduction_output.txt` (sha256:12 `240185a1b96a`), executed on a Fraxtal mainnet fork @ block 12,918,968.
- No external/answer-key dependence; derived and reproduced from source.
