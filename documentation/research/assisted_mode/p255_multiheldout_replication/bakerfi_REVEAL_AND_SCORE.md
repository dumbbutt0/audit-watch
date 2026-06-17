# bakerfi — Phase 4: Reveal & score

## Freeze integrity (recorded AFTER the three bakerfi freezes, BEFORE the key was opened)
- `bakerfi_BASE_FREEZE.md`        sha256 `b0075d53808a185b…`
- `bakerfi_SELECTED_LOCI.md`      sha256 `737f633786f44c11…`
- `bakerfi_PROCEDURE_OUTPUTS.md`  sha256 `dd18014a70d7c09e…`

## Reveal source
`audits/bakerfi-2024-05-holdout/reports/` empty → post-freeze WebSearch of verified
`code-423n4/2024-05-bakerfi-findings` issues. Relevant awarded findings:

| issue | sev | locus | awarded mechanism |
|---|---|---|---|
| (harvest) | Med | `StrategyLeverage.harvest`/`_adjustDebt` | after adjustment, collateral is reduced by `deltaDebt + fee` but `newDeployedAmount` treats both collateral and debt as reduced by `deltaDebt` only → `newDeployedAmount` **overstated by the flash-loan fee** → protocol may not receive profit (if profit < fee) |
| #44 | Med/High | `Vault.withdraw` | MEV bots sandwich withdrawals (no slippage protection) to extract user funds |
| #41 | High | `StrategyLeverage` deploy/Aave | supplied WETH to Aave can be irrecoverable |
| #39 | — | `Vault` | first-depositor inflation |

## Per-locus classification
### L4 — `StrategyLeverage._getPosition` staleness OR-logic → **BENIGN**
No awarded finding maps to the `_getPosition` OR-vs-AND staleness gate. My pre-frozen L4 **flagged the dependency**
("void if `getSafeLatestPrice` already reverts on stale") and did not over-claim → no severe FP. Mechanism-
selection: **awarded-mechanism-not-enumerated** (the awarded leverage-surface bugs were #41 irrecoverable-WETH and
the harvest-fee, which L4 didn't target).

### L5 — `StrategyLeverage.harvest` → **SAME_AREA_WRONG_MECHANISM**
Pre-frozen L5 was in the **exact** function and even noted the `deltaDebt` cancellation in `newDeployedAmount`, but
selected the **P&L-only-when-deltaDebt==0** mechanism. The awarded mechanism is the **flash-loan `fee` not being
reflected** in `newDeployedAmount` (collateral down by `deltaDebt + fee`, formula assumes only `deltaDebt`). I
enumerated the cancellation but **did not enumerate the fee term** → wrong mechanism. Mechanism-selection:
**awarded-mechanism-visible-but-not-selected** (the fee is computed at `_adjustDebt`/`flashFee`, visible in scope).
This is the **P254 failure mode reproduced** on the architecturally-rich contest.

### L6 — `StrategyLeverage._undeploy` `_pendingAmount` → **BENIGN**
Routine returned NO_CHAIN (single-tx path refreshes `_pendingAmount`; `onlyOwner`). No awarded match → correct
restraint, no FP. Mechanism-selection: **awarded-mechanism-not-enumerated**.

## bakerfi metrics
| metric | value |
|---|---|
| loci | 3 |
| AWARDED_EQUIVALENT / PARTIAL_AWARD | 0 / 0 |
| SAME_AREA_WRONG_MECHANISM | 1 (L5) |
| BENIGN / severe FP | 2 benign (L4, L6) / 0 severe FP |
| procedure-completed-not-base recoveries | **0** |
| awarded-mechanism-visible-but-not-selected | 1 (L5 — the fee mechanism) |

**Honest note:** the one architecturally-realistic, subtle-accounting target produced **0** clean recoveries and
**reproduced the LoopFi mechanism-selection failure** (L5): the routine engaged the exact awarded function, saw a
real anomaly, but completed the wrong mechanism (P&L gap) and missed the awarded one (fee omission). bakerfi #41
(irrecoverable WETH) and #44 (MEV withdrawal sandwich) were not birthed by base at all (base-hunt misses, not
routine failures).
