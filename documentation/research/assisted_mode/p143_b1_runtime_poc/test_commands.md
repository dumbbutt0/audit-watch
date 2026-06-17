# P143 — Test Commands

## Run
```bash
cd audits/noya-2024-04-eval/pocs/p143
forge test -vv
```

## Restore build deps (if `lib/` was cleaned)
`lib/` (forge-std + OZ v5) is a removable build dependency; recreate with:
```bash
cd audits/noya-2024-04-eval/pocs/p143
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
git clone --depth 1 --branch v5.0.2 https://github.com/OpenZeppelin/openzeppelin-contracts lib/openzeppelin-contracts
```

## Result
```
[PASS] test_vulnerable_multi_hop_uses_static_asset_and_misvalues   vulnerable=20e18
[PASS] test_corrected_reference_uses_loop_carried_quote_token      corrected=6e18
[PASS] test_single_hop_control_matches                            real==corrected==6e18
[PASS] test_equivalent_price_control_no_divergence                real==corrected==6e18
4 passed; 0 failed; 0 skipped
Logs: vulnerable_output_wad=20e18 · corrected_output_wad=6e18 · delta_wad=14e18
```

## Notes
- `real_function_called: true` · `public_entrypoint_called: true` (real `NoyaValueOracle.getValue`) ·
  `copied_logic_used: false` for the subject (the corrected reference is a copy-with-one-fix used only as the
  control).
- Solc 0.8.20 (matches the production pragma). Cosmetic `@Title` natspec warnings originate from noya's
  `IPositionRegistry.sol`, not the PoC.
