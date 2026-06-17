# P287 — POC_RESULTS (pre-reveal)

## LRTDepositPool.getRsETHAmountToMint — Tier-C, 3/3 PASS → PASS_SUPPORTED
Mechanism: oracle price consumed without staleness/normalization. Flaw locus: `ChainlinkPriceOracle.getAssetPrice`
(`latestAnswer()`, no `updatedAt`/staleness guard) transitively consumed by `getRsETHAmountToMint`.
| layer | test | result |
|---|---|---|
| L1 entry (EOA) + reference | `test_fresh_price_mints_correctly_PASS_SUPPORTED` | ✔ fresh 1:1 price → 1:1 mint |
| **L2 state-flip (bug)** | `test_stale_price_silently_misvalues_mint_PASS_SUPPORTED` | ✔ stale `latestAnswer()` consumed with NO revert; mint=100e18 at stale price vs 150e18 at true price |
| L3 control | `test_control_guarded_oracle_reverts_on_stale` | ✔ a staleness-guarded oracle REVERTS on the stale read |
`Suite result: ok. 3 passed; 0 failed; 0 skipped.`

**Named state-flip (L2):** after 30 days with no feed update, `getRsETHAmountToMint(asset, 100e18)` still returns a value
computed from the stale answer (no revert); the true-price value (1.5) would be 150e18 — a 50% mis-mint. The control
proves the fix is exactly the missing staleness guard.

**Classification: PASS_SUPPORTED** — the pre-reveal mechanism (missing oracle staleness/normalization on the mint
valuation path) is runtime-proven and source-faithful. Tier-C faithful reproduction; not a submission package.
Fabricated passes: 0. severe FP: 0.
