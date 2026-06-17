# basin — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue (isolated/manual blind read + isolated checkpoints), not an ad hoc hunt. Sealed
key not read. Disclosed-exposed area (Well MEV/donation, p160) avoided in selection.

## Generation basis (exact command/path)
- Surface: `audits/basin-2024-07-holdout/output/coverage_manifest.json` (26 in-scope fns).
- Checkpoints: `python scripts/accounting_checkpoint_audit.py --manifest audits/basin-2024-07-holdout/output/coverage_manifest.json --out .../outputs/basin_accounting_checkpoint.json --quiet` (+ `state_transition_*`). Invariants re-verified: `emits_findings:false`, 0 concluded.
- Base read: `contracts/src/functions/Stable2.sol`, `WellUpgradeable.sol` (Well.sol swap/donation area avoided).

## Checkpoint records (advisory)
accounting 8 recs / 6 loci: Stable2.{calcRate×2, calcReserveAtRatioSwap×2, calcLpTokenSupply, calcReserveAtRatioLiquidity, _calcRate} (A5 index ×5, A1 rounding ×3), WellUpgradeable.init ×1. state-transition: 0 recs.

## Frozen base candidate set
| id | sev(blind) | locus | mechanism observed | checkpoint |
|---|---|---|---|---|
| **B1** | Med | `Stable2.decodeWellData` (L310–325) | copy-paste: second `if (decimal0 == 0) decimal1 = 18` re-checks **decimal0** instead of **decimal1** → when token1 decimals unset (0), `decimal1` stays 0 → `getScaledReserves` scales reserves[1] by `10**(18-0)` → mis-scaled reserves → wrong Stable2 pricing | A1/A5 on calc* |
| **B2** | Low/Med | `Stable2.calcReserveAtRatioSwap`/`calcReserveAtRatioLiquidity` (L220–238, L288–303) + `calcLpTokenSupply` (L88–102) | 255-iter loops **fall through with no revert** on non-convergence → return 0 / unconverged value; inconsistent with `calcReserve` which `revert("did not find convergence")` | A5 idx |
| **B3** | Med | `WellUpgradeable.init` (L33–49) / upgrade path | `init` is `reinitializer(2)`, no access control; implementation (`___self`) init/ownership + minimal-proxy UUPS upgrade auth surface | ST hit on init |

### Checkpoint-hit suspicious loci with no base candidate
| locus | checkpoint | why no candidate |
|---|---|---|
| `Stable2.calcRate`/`_calcRate` +1e6 precision | A1/A5 | natspec acknowledges ±1 rounding; no divergence on blind read |

## Ranking (pre-reveal)
1. **B1** decodeWellData copy-paste (clearest, mechanical) 2. **B3** WellUpgradeable init/upgrade 3. **B2** silent non-convergence

## Three-way state tag
| id | tag | base chain state |
|---|---|---|
| B1 | BASE_BORN_INCOMPLETE | bug seen; who-loses / exploit path / severity not computed |
| B2 | BASE_BORN_INCOMPLETE | missing-revert seen; force-non-convergence + consumer impact not traced |
| B3 | BASE_BORN_INCOMPLETE | init/upgrade surface seen; concrete takeover/brick not traced |
| Stable2.calcRate precision | CHECKPOINT_HIT_SUSPICIOUS_LOCUS | fired; no candidate |
| (none) | BASE_COMPLETED_CHAIN | base completed 0 full chains |

**FREEZE:** final before selection/reveal. Hash recorded in basin_REVEAL_AND_SCORE.md before key opened.
