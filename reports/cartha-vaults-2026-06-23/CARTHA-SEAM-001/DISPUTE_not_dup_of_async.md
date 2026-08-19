# Dispute — CARTHA-SEAM-001 (ZEROMARK-553) is NOT a duplicate of report #1 (ZEROMARK-1)

| | |
|---|---|
| **This report** | CARTHA-SEAM-001 — "GM-token valuation has a 1e12 decimal mismatch" — HackenProof **ZEROMARK-553** (triaged **High**) |
| **Triager action** | @HP-Triage0xBugSlayer: *"This one is dup of 1. Applying proof."* → folding #553 into report **#1 / ZEROMARK-1** ("Async 0xM deploy/recall window understates NAV") |
| **Status** | **Disputing** the duplicate classification **and** the inherited severity |
| **Severity claim** | Currently **High** (inherited from the merge into #1); on its own merits **Critical** — direct theft of user funds + insolvency + permanent freezing, all proven in `PoC_GmDecimalMismatch.t.sol` (4/4) |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Bottom line** | #1 and #553 share only the *surface symptom* ("share price is wrong when GM is held"). Root cause, error **direction**, activation **time**, and **fix** are all disjoint. Remediating #1 leaves #553's depositor-principal-loss path fully exploitable — so they are not interchangeable, and therefore not duplicates. |

## The two findings are opposite errors

| | **#1 / ZEROMARK-1** (async window) | **#553 / this report** (1e12 decimal scale) |
|---|---|---|
| TVL error | **Under**-stated — in-flight value omitted during the async settlement window | **Over**-stated by exactly **1e12** — 18-dec GM value summed onto 6-dec USDC |
| When active | Only *during* the deploy/recall window (GM not yet minted; vault holds neither USDC nor GM) | Steady state, **the moment the vault holds GM** — i.e. *after* #1's window has closed and settlement completed |
| Who is hurt / how | An attacker who **times** a deposit into the window mints **excess** cheap shares → dilutes LPs | An **honest** depositor is minted **1e12× too few** shares → deterministic **principal loss**; no attacker, no timing |
| Root cause | `_totalValueLocked()` ignores pending in-flight value | `gmValueInUsdc` never normalizes the GM leg's decimals |
| Fix | Track pending in-flight value / settlement callback | Rescale the GM leg by `10^(18 − assetDecimals)` |

**A single root cause cannot make TVL simultaneously too low (in-flight omission) and 1e12× too high
(decimal scale).** And the two are active at *different times*: #1 exists in the window *before* GM is
minted; #553 exists once the vault *holds* GM — exactly the resolved end-state that #1's report
describes. **#1's resolved state is #553's precondition.**

## Code proof — the 1e12 is a scale error, not a timing artifact

`PoolDeployLib.gmValueInUsdc` returns an **18-decimal** USD figure and it is added straight onto the
**6-decimal** USDC balance, with no normalization:

```solidity
// src/libraries/PoolDeployLib.sol
uint256 internal constant GM_PRICE_PRECISION = 1e30;
...
int256 gmPrice = _getGmPrice(...);                         // 1e30 per WHOLE GM token  (proven below)
return (gmBalance * uint256(gmPrice)) / GM_PRICE_PRECISION; // (18-dec * 1e30) / 1e30 = 18-DEC USD

// src/CarthaVault.sol  (_totalValueLocked, see SUBMISSION.md:69-72)
return IERC20($.asset).balanceOf(address(this)) /* 6-dec */ + _gmValueInUsdc($) /* 18-dec */;
```

Dimensional analysis (full derivation in `SUBMISSION.md` §"Unit proof"):

```
gmValueInUsdc = gmBalance[native,18-dec] × gmPrice[USD/whole × 1e30] / 1e30 = USD × 1e18   (18-dec)
6-dec USDC + 18-dec GM  →  the GM leg is larger by 10^(18 − 6) = 1e12
```

The GM price scale (`1e30` per *whole* token, not per native unit) is **proven from the in-scope
0xMarkets source**, not assumed: `MarketUtils.getMarketTokenPrice` returns `FLOAT_PRECISION` (`1e30`),
commented "1 USD", in the `supply == 0` branch, and `WEI_PRECISION × poolValue / supply` in the general
branch (`MarketUtils.sol:156-163`, `Precision.sol`). The PoC asserts this by **replaying that exact
formula** on realistic GMX-scale inputs.

### The fixes are disjoint — apply either, the other bug survives

- **#1's fix** (track pending in-flight value in `_totalValueLocked()`) leaves `gmValueInUsdc`
  **byte-for-byte unchanged** → the 1e12 over-statement, and the depositor principal loss it causes, is
  **fully intact**.
- **#553's fix** (normalize decimals: `gmValueRaw / 10^(18 − assetDecimals)` inside `gmValueInUsdc`)
  does **nothing** to the async settlement window → #1's window dilution is **fully intact**.
- Report #1 **never identifies or remediates** the decimal-scale defect at all.

Two non-overlapping code changes, on different lines, each required to close a different loss path. By
the standard "is the protocol still vulnerable after the other is fixed?" test, these are separate
issues.

### PoC isolates #553 from any timing effect

`poc/PoC_GmDecimalMismatch.t.sol` reproduces #553 with GM valued **correctly** (1e30 per whole token).
`test_RealReaderPriceScale_Is1e30PerWholeToken` replays the real
`MarketUtils.getMarketTokenPrice` formula (`WEI_PRECISION × poolValue / supply`) rather than trusting a
mock price, then shows the seam yields `100_000e18` for $100k of GM (vs the true `100_000e6`) — a pure
1e12 scale error with **no async window in the test at all**. All 4 tests pass (`poc/run_output.txt`).

## Honesty note

Some programs dedup by "same vulnerable area" rather than "same root cause," and both findings do live
in the TVL accounting path — so a strict reviewer could lean on proximity. The decisive, program-neutral
point is the **practical** one: **after report #1 is fixed, the protocol still deterministically loses
honest depositors' principal via the 1e12 scale error.** An unmitigated, separately-fixed loss path is
the definition of a distinct issue — not a duplicate.

## Severity — Critical, not High (once separated from #1)

#553 is rated **High** only because it was merged into #1 (an async-window report rated High) — it
**inherited** that severity. Evaluated on its own merits, the impact maps directly to three of this
program's accepted **Critical** impacts, all proven in `poc/PoC_GmDecimalMismatch.t.sol` (4/4 passing):

- **Direct theft of user funds (at-rest).** Once the vault holds GM, a depositor is minted ~1e12× too
  few shares. In the PoC, `user2` deposits **$100,000** and recovers **$0** (their `release()` rounds to
  0 and reverts `InsufficientVaultBalance`), while an earlier holder `user1` — who deposited the same
  $100k — withdraws **$199,999.99**: their own deposit *plus* user2's entire stranded principal. One
  honest user's principal is transferred to another, permissionlessly and deterministically.
- **Insolvency.** `_totalValueLocked()` is inflated 1e12× the moment GM is held, corrupting
  `_convertToShares` / `_convertToAssets` and the global share price — the vault redeems early holders
  for far more than their backing.
- **Permanent freezing of funds.** The under-minted depositor's `release()` reverts and cannot recover
  principal.

The trigger is **normal operation** (a routine keeper `deployToPool` — the protocol's core yield
feature), requires **no privileged role** and **no attacker timing**. Direct fund loss with no
preconditions is this program's definition of Critical.

```
user2 deposited (USDC): 100000000000   recovered: 0             (total, permanent principal loss)
user1 deposited (USDC): 100000000000   recovered: 199999999999  (steals user2's principal)
```

---

## Paste-ready reply — duplicate dispute

> Respectfully, ZEROMARK-553 is not a duplicate of #1. They share only the surface symptom ("share
> price is wrong when GM is held"); the root cause, error direction, activation time, and fix are
> disjoint.
>
> **Opposite error direction.** #1 *under*-states TVL (in-flight value omitted during the async
> settlement window) → NAV too low → an attacker who *times* a deposit mints *excess* cheap shares and
> dilutes LPs. #553 *over*-states TVL by exactly 1e12 (the 18-decimal GM leg is summed with 6-decimal
> USDC with no normalization, `PoolDeployLib.gmValueInUsdc` → `CarthaVault._totalValueLocked()`) → NAV
> too high → honest depositors are minted *1e12× too few* shares (deterministic principal loss, no
> attacker, no timing). One root cause cannot make TVL simultaneously too low and 1e12× too high.
>
> **Active at different times.** #1 exists only in the window *before* GM is minted (vault holds
> neither USDC nor GM). #553 exists in steady state *the moment the vault holds GM* — exactly after
> #1's window has closed and settlement completed. #1's resolved state is #553's precondition.
>
> **Disjoint fixes.** #1 is fixed by tracking pending in-flight value / a settlement callback in
> `_totalValueLocked()`. #553 is fixed by normalizing the GM leg's decimals (`/ 10^(18−assetDecimals)`)
> in `gmValueInUsdc`. Applying #1's fix leaves the `gmValueInUsdc` line unchanged → the 1e12
> principal-loss path stays fully exploitable; applying #553's fix leaves #1's window dilution fully
> live. #1 does not identify or remediate the decimal-scale defect at all.
>
> The GM price scale (`1e30` per *whole* token) and the resulting 1e12 are proven from the in-scope
> 0xMarkets source (`MarketUtils.sol:156-163`, `Precision.sol`) and isolated in PoC
> `PoC_GmDecimalMismatch.t.sol::test_RealReaderPriceScale_Is1e30PerWholeToken`, which reproduces #553
> with GM priced correctly and no async window — so it cannot be a timing artifact. After #1 is fixed,
> the protocol still deterministically loses depositor principal via this scale error, which is what
> makes it a separate, independently-unmitigated issue.

## Paste-ready reply — severity escalation

> **Severity — this warrants Critical, not High.** ZEROMARK-553 is currently rated High because it was
> merged into report #1 (an async-window report); on its own merits the impact is Critical-tier and maps
> directly to this program's accepted Critical impacts:
> - **Direct theft of user funds:** in the PoC, a depositor who deposits while the vault holds GM is
>   minted ~1e12× too few shares; their `release()` rounds to 0 and reverts (`InsufficientVaultBalance`)
>   — they recover **$0** of a $100k deposit — while an earlier holder withdraws **$199,999.99** (their
>   own deposit *plus* the new depositor's stranded principal). One user's principal is transferred to
>   another, permissionlessly and deterministically.
> - **Insolvency:** `_totalValueLocked()` is inflated 1e12× the moment GM is held, corrupting
>   `_convertToShares` / `_convertToAssets` and the global share price — the vault pays redemptions
>   exceeding its backing.
> - **Permanent freezing:** the under-minted depositor's `release()` reverts and cannot recover principal.
>
> This is triggered by **normal operation** (a routine keeper `deployToPool`), requires **no privileged
> role**, and is fully reproduced in `PoC_GmDecimalMismatch.t.sol` (4/4 passing). Direct fund loss with
> no preconditions is the program's definition of Critical.
