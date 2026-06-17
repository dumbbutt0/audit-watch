# F-1 (Critical) + M-1 (Medium) — Broken health-transition guard in `Risk.checkValidTransition`

> **Merged report.** F-1 and M-1 are two opposite-direction symptoms of a **single defect**: the
> value/risk ratio comparison at `Risk.sol:133` is inverted (and its `initRisk==0`-gated backstop is
> dead whenever a position exists). One fix to `checkValidTransition` resolves both. F-1 (Critical,
> fund loss) is the primary impact; M-1 (Medium, liveness) is the same bug seen from the other side.

- **Target:** TipRun contracts (off-chain-match / on-chain-settlement exchange), perp profile. Commit `d5d4d2a…`.
- **Contract:** `src/core/risk/Risk.sol` → `checkValidTransition` (the `CAP_MARGIN_CHECK` provider wired by
  `RiskPlugin`, invoked by `PositionManager.updatePosition` on every position/collateral change).
- **Severity:** Critical (F-1 manifestation — direct path to protocol bad debt / loss of other users' funds);
  Medium (M-1 manifestation — liveness/DoS: cannot de-risk).
- **PoCs (both passing):** `poc/PoC_MarginBypassWithdraw.t.sol` (F-1) and `poc/PoC_DeriskDoS.t.sol` (M-1) ·
  combined log `poc_output.log`.
- **Attacker:** permissionless — a normal user signing their own withdrawal (`ALLOW_WITHDRAW` on their own account).

## Root cause (shared)
`checkValidTransition` is meant to enforce maintenance margin: a position/collateral change is allowed only if the
**updated** account is healthy, or (if already unhealthy) strictly improves. The relevant logic:

```solidity
// Risk.sol (checkValidTransition)
if (updatedTotalRisk <= updatedTotalValue * FXP_32_ONE) { return; }            // (A) healthy → allow
...
checkSmallerInSyntheticHoldings(fullInit, fullUpdated);                         // (B) positions may only shrink
if (initTotalValue * updatedTotalRisk < updatedTotalValue * initTotalRisk) {    // (C) ratio guard — INVERTED
    revert("PM: val/risk dec");
}
if (initTotalRisk == 0) {                                                       // (D) value-decrease guard…
    if (updatedTotalValue < initTotalValue) { revert("PM: val dec"); }          //     …ONLY when risk == 0 (dead)
}
```

Health is `value/risk` (higher = healthier; the account is healthy iff `risk ≤ value·FXP`). Guard (C) is supposed to
reject transitions that lower that ratio. As written it does the **opposite**: it reverts when the updated ratio
*rises* (`initValue·updatedRisk < updatedValue·initRisk` ⟺ `updatedRatio > initRatio`) and passes when the ratio
*falls*. The single backstop that could have caught a value drop, (D), is gated on `initTotalRisk == 0`, so it never
runs once an account holds any position (`R > 0`).

The two manifestations fall straight out of this one inverted comparison:

### Manifestation A — F-1 (Critical): collateral withdrawal bypasses margin
For a **pure collateral withdrawal** synthetic holdings are unchanged, so `updatedRisk == initRisk == R`. Substituting
into (C): `initValue·R < updatedValue·R` ⟺ `initValue < updatedValue`. Removing collateral makes
`updatedValue < initValue`, so (C) is **false → no revert**, and (D) is skipped because `R > 0`. Net: **any account
holding a position (R > 0) can decrease its collateral with no margin check ever reverting** — down to zero, or (via
the direct path) into negative equity. The project's own
`test/PositionManager.Risk.t.sol::test_ArithmeticEdgeCase_NegativeCollateral` documents the bypass — comment:
*"First create a synthetic position to avoid the totalValue decrease restriction."*

### Manifestation B — M-1 (Medium): cannot de-risk an unhealthy account
An account below maintenance margin that tries to **reduce** its position (the legitimate way to recover) passes (B)
(holdings shrank), then hits (C) with `updatedRatio > initRatio` (it got healthier) → reverts `PM: val/risk dec`,
unless it can close enough in one step to become fully healthy. The project's own `test_RiskRatioComparisonLogic`
computes `ratioImproved = initRisk·updatedValue > updatedRisk·initValue`, which is algebraically the (C) revert
condition — i.e. the contract reverts **exactly when the ratio improves.**

A single correction — revert when the updated ratio *decreases* and apply a value-non-decrease check
**unconditionally** (not only when `initRisk == 0`) — closes both A and B.

## Impact
**A (Critical).** On a perp deployment `checkValidTransition` is the only maintenance-margin enforcement (the
withdrawal balance-check `Risk.validateWithdrawal` merely requires bucket-0 collateral ≥ amount). A user can:
deposit collateral → open a leveraged position → **withdraw their entire collateral out of custody** while the
position stays open and unbacked. They keep directional exposure financed entirely by the protocol (a free option):
if it wins they collect; if it loses they have already removed all margin → unrecoverable **bad debt** borne by the
protocol / counterparties. This breaks the core solvency invariant.

**B (Medium).** With partial orderbook fills (the norm), an underwater account cannot recover incrementally: any
partial de-risk that improves health but stays under margin reverts `PM: val/risk dec`. Combined with A (which lets
accounts reach the unhealthy state), positions can be stranded. The same gate sits on the trade and deleverage paths
via `FundingApplyLib.applyAndUpdate → PositionManager.updatePosition`.

## PoCs (both passing)
From `../../harness/`:

```bash
forge test --match-contract PoC_MarginBypassWithdraw -vv   # Manifestation A (F-1)
forge test --match-contract PoC_DeriskDoS -vv              # Manifestation B (M-1)
```

**A — `PoC_MarginBypassWithdraw`:** deposit 10 000 collateral; risk factor 2×; oracle price 1; open long 5 000 →
value `15 000·FXP`, risk `10 000·FXP²` (healthy). Submit a signed `Withdrawal` for the **full 10 000** via
`MultiTransactionProcessor` → **succeeds**. After: collateral `0`, position still long 5 000, `risk > value·FXP`
(under maintenance margin), 10 000 tokens left `LoadingZone` to the attacker.

**B — `PoC_DeriskDoS`:** reach an under-margin account (collateral 2 000 / long 5 000 ⇒ value 7 000·FXP, risk
10 000·FXP²) via A. A fair **partial** de-risk — sell 500 synthetic for 500 collateral (value-neutral, risk ↓ to
9 000·FXP², strictly healthier but still under margin) — **reverts** `PM: val/risk dec`; the position is left
untouched. Only a de-risk large enough to reach *full* health in one step (sell 4 000) is allowed.

## Suggested fix
One change to `checkValidTransition`:
- correct the ratio comparison so it reverts when the **updated** value/risk ratio *decreases* (account gets less
  healthy), with explicit handling of negative `totalValue`; and
- apply the health-non-worsening / value-non-decrease guard **unconditionally** (not only when `initRisk == 0`).

Also make `Risk.validateWithdrawal` account for open-position risk, not just raw bucket-0 collateral.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (broken maintenance-margin validation in `Risk.checkValidTransition` → protocol insolvency / fund loss)
- **Secondary category:** Blockchain → DoS with (Unexpected) revert (Manifestation B / M-1: inverted ratio guard reverts legitimate de-risking)
- **CWE (informative):** CWE-840 (Business Logic Errors); CWE-682 (Incorrect Calculation) for the inverted ratio comparison

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Manifestation A (F-1, collateral-withdraw bypass) | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H` | **9.1** | Critical |
| Manifestation B (M-1, de-risk DoS / unexpected revert) | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L` | **5.3** | Medium |

> A is permissionless and needs no special chain state (any account holding a position). B is the same defect seen from the other direction.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
