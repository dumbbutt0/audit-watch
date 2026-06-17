# P270 — POC_RESULTS (Phase 7)

Isolated project `pocs/p270/wise/`. wise-lending `contracts/` copied read-only to `wise_src/` (contest tree
unmodified); deps cloned pinned (forge-std v1.9.6 · OZ v4.9.6); solc 0.8.24 / evm shanghai. `@pendle`-importing
oracle libs + the contest's own `.t.sol` skipped from compilation (not on the share path).

```
cd pocs/p270/wise && forge test --match-path test/P270_PendleShare.t.sol -vv
```

## Result — the one feasible partial-runtime PoC ran; the two heavy ones did not
| candidate | route | PoC | observed | classification |
|---|---|---|---|---|
| **C-pp** PendlePowerFarmToken share-accounting | PARTIAL_RUNTIME | **PASS** | victim deposit 1000 → **997 shares / 997 redeemable** (only the 0.3% mintFee); not zeroed | **mechanism REFUTED / GUARDED** (true negative) |
| C-liq WiseCore liquidation | PARTIAL_RUNTIME | **not run** | requires full deposit→borrow→price-drop→liquidate stack (+ WiseSecurity/OracleHub) | **NEEDS_MORE_RUNTIME** (harness-weight) |
| C-bd FeeManager bad-debt | PARTIAL_RUNTIME | **not run** | requires full borrow→insolvency→liquidation→bad-debt flow | **NEEDS_MORE_RUNTIME** (harness-weight) |

## C-pp detail (the runnable one)
The triage-routed Pendle-share mechanism was tested with a faithful partial-runtime harness (real
`PendlePowerFarmToken` + minimal Pendle controller/market mock; reward path no-op'd — the `syncSupply` modifier pulls
the full reward-sync, confirming why this is a *heavy/partial* route). Result: **first-depositor / share-price
inflation does NOT hold here** — assets are tracked internally (`underlyingLpAssetsCurrent`, no directly-donatable
`balanceOf`), the mint is proportional (share price invariant), and `_validateSharePriceGrowth` time-bounds growth.
The victim recovers ~their deposit. **C-pp is a true negative (guarded by design).** L1/L2/L3: L1 attacker EOA
deposit; L2 `victimShares`/`underlyingLpAssetsCurrent` asserted; L3 victim recovers 997/1000 → no inflation.

## Honest harness-weight finding
Even the "internal" share path triggers the reward-sync (controller + market), and the awarded-class liquidation /
bad-debt mechanisms require the full WiseLending stack. The two highest-award-class candidates were correctly *routed*
(SELECT_FOR_PARTIAL_RUNTIME) by triage but their PoCs are **not completed in scope** (NEEDS_MORE_RUNTIME) — a genuine
PoC-harness-weight limit on a large lending protocol, not a routing failure. No contest/production source edited.

## Freeze hashes (sha256[:16])
`P270_PendleShare.t.sol` `a959817f13baabca` · selector_decisions `4bc665965d611573` · triage_decisions
`d00487303f8cb2b5` · POC_INTENT `fb02f1dfeac93c0b`. No answer key consulted up to here.
