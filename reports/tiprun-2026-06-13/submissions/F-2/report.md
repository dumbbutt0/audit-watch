# F-2 (High/Critical) — Account freeze / liquidation lock when notional exceeds the top risk segment

- **Target:** TipRun, perp profile. Commit `d5d4d2a…`.
- **Contracts:** `src/core/config/GeneralConfig.sol` → `getRiskFactor`; `src/core/risk/Risk.sol` →
  `getAssetValueAndRisk`.
- **Severity:** High → Critical (the short variant is attacker-initiated and yields unrecoverable bad debt).
- **PoC:** `poc/PoC_RiskSegmentFreeze.t.sol` (2 passing tests) · log `poc_output.log`.
- **Attacker / trigger:** an oracle price move (no action on the victim) freezes any account over the cap; on the
  **short** side an attacker can deliberately engineer it to dodge liquidation.

## Root cause
`getRiskFactor` walks the asset's risk-factor segments and returns `(segment.risk, true)` for the first segment whose
`upperBound` covers the position's notional; if the notional exceeds **every** segment it returns `(0, false)`.
`Risk.getAssetValueAndRisk` then executes `require(riskOk, "Risk: no risk")` and **reverts** — it does not clamp to
the top tier:

```solidity
// Risk.getAssetValueAndRisk
(int256 riskFactor, bool riskOk) = generalConfig.getRiskFactor(asset.packed.getAssetId(), absAmount, oraclePrice);
if (!priceOk) { require(!riskOk, "Risk: price missing but risk exists"); return (0, 0); }
require(riskOk, "Risk: no risk");   // <-- reverts when notional > top segment
```

Because **every** position-touching operation (withdraw, trade, liquidate, deleverage, settlement) routes through
`checkValidTransition → getAccountPositionStatus → getAssetValueAndRisk`, a single asset whose notional crosses the
cap **freezes the entire account**.

## Impact
The trigger is a plain **oracle price increase** (notional = `price × |amount|`), not any action on the account. When
an asset pumps — exactly when accounts go underwater and most need liquidating — affected accounts become
**un-liquidatable** (the protocol cannot recover the bad debt) and their owners cannot withdraw or de-risk. The
freeze persists until the price falls back under the cap or an admin reconfigures the asset.

**Attacker-controlled (short side):** for a short, notional rises as price rises — i.e. precisely as the short goes
underwater. An attacker sizes a short so its maintenance-margin breach lands above the segment cap; the account then
reaches a state that is simultaneously **insolvent and frozen**, so it can never be liquidated and the attacker walks
away from the loss → direct protocol bad debt. This makes F-2 a deliberate exploit, not just an unlucky-price freeze.

## PoC (both passing)
`forge test --match-contract PoC_RiskSegmentFreeze -vv` (from `../../harness/`):
- `test_PoC_priceRiseFreezesAccountAndBlocksLiquidation` — long 5 000 @ price 1 (notional 5 000 ≤ cap 10 000) healthy;
  raise price to 3 (notional 15 000) ⇒ `getAccountPositionStatus`, any resize/liquidation, and a withdrawal batch all
  revert `Risk: no risk` (frozen, funds locked).
- `test_PoC_shortDodgesLiquidationByFreezing` — short 3 000 @ price 1 (healthy); raise price to 4 ⇒ equity
  `10 000 − 4×3 000 = −2 000` (insolvent) yet every liquidation/resize reverts `Risk: no risk` — the insolvent short
  is un-liquidatable.

## Suggested fix
In `getRiskFactor`, **clamp** to the last segment's risk when notional exceeds all segments (never return `false`);
or handle `riskOk == false && priceOk == true` in `Risk` without reverting. A maintenance-margin engine must never
revert on a too-large position — that is exactly the state in which liquidation must remain possible.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Blockchain → DoS with (Unexpected) revert (`getRiskFactor` returns `(0,false)` past the top risk segment → `require(riskOk,"Risk: no risk")` reverts → account frozen, including un-liquidatable → bad debt)
- **CWE (informative):** CWE-755 (Improper Handling of Exceptional Conditions); CWE-691 (Insufficient Control Flow Management)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Account freeze / liquidation-lock | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H` | **7.4** | High |

> AC:H reflects the precondition that notional must exceed the top configured risk segment (reachable via a large position or an oracle move).

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
