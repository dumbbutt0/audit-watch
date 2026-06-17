# P204 — false-High controls (decent-06, decent-12)

These were v1/v2 `HIGH_CONFIRMED` but **unawarded** (not in decent's H/M). L3 tests whether material impact is
realizable under source-valid honest custody.

## decent-06 — UniSwapper.swapNoPath "drain valuable balance" → DEMOTE
Harness: `pocs/test/D06_swapNoPath.t.sol` (real `UniSwapper.sol`). Run log: `pocs/run_log.txt`.
- `swapNoPath` is `public` (no `onlyUtb`) → permissionless (capability confirmed).
- Honest custody: `UniSwapper` holds **no** valuable token (no source-valid flow leaves residuals there).
- Attacker calls `swapNoPath(junk → valuable)`; `_sendToRecipient` does `transfer(valuable)` from UniSwapper's
  **zero** balance → **reverts**. Attacker drains nothing; UniSwapper valuable balance stays 0. **PASS**
  (`test_D06_no_drain_under_honest_custody`).
- **L3 verdict: MEDIUM_OR_LOWER_CALIBRATED** — the "drain" requires an **unsourced residual balance** in UniSwapper;
  realizing it would need arbitrary mock custody, which L3 disallows. (If such a residual were source-shown, revisit.)

## decent-12 — DecentEthRouter redeem double-withdrawal → NEEDS_HARNESS (source obstacle)
Not harnessed; the source obstacle is decisive and documented (per the L3 standard's "no arbitrary mock custody"):
- The double-withdrawal needs the attacker to (a) hold redeemable `dcntEth` and (b) carry a stale `balanceOf` LP
  credit, then call `redeemEth` (burns dcntEth, no `balanceOf` decrement) **and** `removeLiquidityEth`.
- But `addLiquidityEth()` mints dcntEth to **`address(this)` (the router)**, not to the depositor (the depositor
  only gets a `balanceOf` credit). `redeemEth` requires the caller to **hold/transferFrom** dcntEth.
- ⇒ **No source-valid flow gives the attacker redeemable dcntEth.** Realizing the double-withdrawal requires
  artificially granting the attacker dcntEth (arbitrary custody) → **NEEDS_HARNESS_FOR_SEVERITY**, not a confirmed
  High. (The redeemEth-doesn't-decrement-balanceOf bug may still be real, but its *material* exploitation is not
  source-validly realizable in this prototype — exactly the capability-vs-realized-impact distinction L3 enforces.)

## Net
Both v1/v2 false-Highs are removed by L3: decent-06 demoted (no drain under honest custody), decent-12 routed to
NEEDS_HARNESS (no source-valid path to material impact). Neither remains HIGH_CONFIRMED.
