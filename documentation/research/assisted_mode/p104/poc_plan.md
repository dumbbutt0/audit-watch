# P104 — PoC plan (executed)

## Environment
- Subject: IQ-AI @ `db0d369b`. Harness: **Fraxtal mainnet fork**, block **12,918,968**, RPC
  `https://rpc.frax.com` (archive — confirmed it serves that block). `forge --evm-version cancun`
  (contracts use `mcopy`). Deps via `npm install` (dev-fraxswap / @openzeppelin / forge-std).
- **Why local mocking is insufficient:** the Fraxswap factory/pair + BAMM factory + currency token + a funded
  whale are real deployed Fraxtal state at hardcoded addresses; the project's own `test/MoveLiquidityTest.sol`
  is itself a Fraxtal fork test. `shareToBamm` defaults to 0, so the BAMM branch is skipped (no BAMM needed).

## Steps (vulnerable PoC — `M01PreCreatePairPoC.t.sol`)
1. Deploy `AgentFactory`; set bytecodes; `targetCCYLiquidity=1000e18`, `initialPrice=0.1e18`.
2. As whale: `createAgent(...)`; drive the BootstrapPool past the end-criterion via `buy`.
3. **Attacker** (`0xA11CE`, no protocol role): `fraxswapFactory.createPair(currency, token, 1)` (1 bps fee).
4. **Attacker** calls `manager.moveLiquidity()` (permissionless).
5. Assert: `getPair(currency, token) == attackerPair` (adopted) and adopted swap fee `= 1 bps` ≠ intended `100`.

**Expected failure condition (the loss):** the protocol migrates into the attacker's pair; the pool's swap fee is
the attacker's `1 bps` instead of the intended `100 bps` → ~99% lost fee revenue; attacker also controls the
pool's initial price/reserves.

## Result
`test_M01_attacker_precreate_low_fee_is_adopted` → **PASS** (intended feeBps 100, attacker-adopted feeBps 1). See
`reproduction_output.txt`.

## Mitigation regression (`M01PatchRegression.t.sol`, guard applied then source restored)
- `test_patch_blocks_attacker_low_fee_pair` → moveLiquidity **reverts** (`"M01: unexpected pre-existing pair fee"`).
- `test_patch_allows_clean_migration` → clean migration still succeeds.
Guard: `require((10_000 - fraxswapPair.fee()) == fee)` in the pair-exists branch. Source restored to frozen hash
`9a68efe4b6664f` after testing.
