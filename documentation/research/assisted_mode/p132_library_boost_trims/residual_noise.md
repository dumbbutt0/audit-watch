# P132 — Residual Noise (after trims)

After the two trims, the noya boost-delta is **60 functions** (was 67 distinct / 70 raw): 8 awarded + 52
non-awarded.

## Composition of the remaining 52 non-awarded boosts
- **On-class value/TVL/price logic (majority):** `_getPositionTVL` across Aave/Camelot/Compound/Curve/Dolomite/
  Frax/Gearbox/Lido/UNIv3/…, `LPToUnder`, `balanceOfLPToken`, `getBorrowBalanceInBase`,
  `neededAssetsForWithdraw`, `AccountingManager._getValue`, etc. These are the **same manipulable-value surface**
  as the awarded bugs — productive deep-pass candidates (valid-unawarded → human review), **not** noise.
- **Lower-value but non-trivial getters:** a handful of `_getUnderlyingTokens`/registry getters that contain
  real logic (e.g. build a token array, read a mapping) — intentionally kept by the conservative trivial rule.

## Why this residual is acceptable
- The two trims targeted exactly the **provably-noise** classes (mock contracts; empty/trivial-return bodies)
  and removed all of them (3 mock + 4 trivial) without touching any function with real behavior.
- The remaining volume is **on-class value logic**, which is the intended P130/P131 recall widening, not noise.
  Further trimming would risk removing genuine value_exit leads (the awarded class) — out of scope for a
  precision/noise phase and explicitly disallowed by "do not reject meaningful behavior."

## Not addressed here (future)
- **Human-graded FP** of the on-class residual remains unmeasured (P131 limit) — only a human-graded specialist
  run can convert the residual into a measured FP rate.
- **Enumeration/scope misses** (e.g. `SNXConnector._getPositionTVL` absent from the manifest;
  `OmnichainManagerBaseChain.updateTVL` untagged) are outside the ranking/trim lever — a separate phase
  (enumeration/scope or callgraph reachability).
