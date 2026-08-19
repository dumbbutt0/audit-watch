# Cartha Vaults — Dedup / Independence Map

**Purpose.** CARTHA-SEAM-001 (GM 1e12 decimal mismatch) was submitted and accepted (High). The next
Cartha submissions (DT-001, DOS-001) touch the *same TVL-accounting area*, so a triager's first
reflex is "isn't this a duplicate of the bug already paid?" This map gives each finding a
source-grounded "why it's distinct" line, and records which low-value findings were *correctly*
merged away (so they are **not** submitted separately and don't read as padding).

Commit `4c51f2a8915f438976b57134d646b55199a11318`.

## Independent findings — submit each separately

| Finding | One-line "not a dup" defense | Decisive source |
|---|---|---|
| **CARTHA-SEAM-001** (Critical/High) — GM decimal mismatch | The GM leg returns an **18-dec** USD value summed with **6-dec** USDC → TVL over-stated ~1e12×. A *valuation-scale* bug. | `PoolDeployLib.sol:108` `(gmBalance*gmPrice)/GM_PRICE_PRECISION` summed at `CarthaVault.sol:940` |
| **DT-001** (High) — async deploy/recall window dilution | Over-mint happens in the window when the vault holds **neither** USDC (sent out) **nor** GM (not yet minted); TVL understated **regardless of GM scale**. A *TVL-completeness* bug — survives a SEAM fix. PoC values GM correctly to isolate it. | USDC leaves at `PoolDeployLib.deploy`; `_totalValueLocked()` reads current balances only `CarthaVault.sol:940` |
| **DOS-001** (High) — one child's reverting GM read bricks all parent ops | The GM read **reverting** (not its value) propagates through `totalAssets()`'s unguarded cross-child loop and freezes every parent op. A *liveness / fault-isolation* bug — survives both a SEAM fix and a DT-001 fix. PoC values GM correctly; the freeze is purely the missing try/catch. | `CarthaParentVault.sol:356` `child.totalValueLocked()` with no try/catch; ext calls `PoolDeployLib.sol:119-124` |

**Why all three coexist:** they are three orthogonal failure modes of the same GM-valuation seam —
**wrong scale** (SEAM), **missing in-flight value** (DT-001), and **unhandled revert** (DOS-001).
Each has a distinct root cause and a distinct fix; fixing any one leaves the other two exploitable.
The DT-001 and DOS-001 PoCs both deliberately value GM **correctly** (`setMarketTokenPrice(1e30)` +
1:1 mint) precisely to prove they do not depend on SEAM.

## Merged duplicates — do NOT submit separately (folded into a survivor)

| Merged ID | Survivor | Why it's the same bug | Source |
|---|---|---|---|
| **AR-001** (truncate-to-0 of GM TVL for small balances) | **CARTHA-SEAM-001** | Same single line `(gmBalance*gmPrice)/GM_PRICE_PRECISION`; AR-001 is the truncation-to-0 edge, SEAM the 1e12 over-weight. One fix (rescale by 1e12) resolves both. | `PoolDeployLib.sol:108`, `GM_PRICE_PRECISION` L20 |
| **EA-001** (async window dilution) | **DT-001** | Same async deploy/recall window, same over-mint, same remediation; EA-001 is a re-derivation of DT-001. | `CarthaVault.sol:940`; `PoolDeployLib.deploy` |
| **DT-005** (uncapped `penaltyBps`) | **AC-002** | Same uncapped `penaltyBps` in `executeForceExit`; identical line and mechanism. | `CarthaParentVault.sol:713,721` |

## If a triager pushes back

- *"DT-001 is the same as the decimal bug you were paid for."* → DT-001 reproduces with GM valued
  **correctly** (PoC test uses `setMarketTokenPrice(1e30)` + 1:1 mint); the 2× over-mint comes from the
  in-flight window, not the scale. A SEAM fix does not touch `_totalValueLocked()`'s balance-only read.
- *"DOS-001 is the same accounting area."* → DOS-001 needs no mis-valuation at all; it is a hard
  **revert** in the cross-child loop (`CarthaParentVault.sol:356`, no try/catch). It fires even after
  SEAM and DT-001 are both fixed.
- *"AR-001 / EA-001 / DT-005 look like separate findings."* → They were **intentionally merged** and
  are not submitted on their own; this map records the survivor for each.
