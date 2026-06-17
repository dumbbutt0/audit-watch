# basin — Phase 4: Reveal & score

## Freeze integrity (recorded AFTER the three basin freezes, BEFORE the key was opened)
- `basin_BASE_FREEZE.md`        sha256 `163de89440bf42c5…`
- `basin_SELECTED_LOCI.md`      sha256 `fcc0ebbba610a443…`
- `basin_PROCEDURE_OUTPUTS.md`  sha256 `99e7719bae75824a…`

## Reveal source
`audits/basin-2024-07-holdout/reports/` empty (no local key) → post-freeze WebSearch/WebFetch of verified
`code-423n4/2024-07-basin-findings` issues. Relevant awarded findings:

| issue | sev | locus | awarded mechanism |
|---|---|---|---|
| **#17** | **High** | `Stable2.decodeWellData` | copy-paste: second `if (decimal0 == 0)` re-checks decimal0 instead of decimal1 → `decimal1` never defaulted to 18 → underflow/mis-scale in `calcLpTokenSupply`/`calcReserve`/`calcRate` |
| (convergence) | Med | `Stable2.calcReserveAtRatioLiquidity`/`Swap` | Newton's method can exhaust 255 iters and **silently exit**; `reserve` named-return never set → returns **0**, function useless / mispricing |

## Per-locus classification
### L1 — `Stable2.decodeWellData` → **AWARDED_EQUIVALENT (High, #17)** ✅
Pre-frozen L1 named the exact typo (`decimal0` re-checked instead of `decimal1`) and (STS/IDC) the mis-scale →
`calcRate` corruption → mispricing impact. Base tag `BASE_BORN_INCOMPLETE` ("bug seen; impact not computed") →
**routine completed the impact**. Mechanism-selection: **awarded-mechanism-selected** (selected mechanism (a)).
Procedure-completed-not-base recovery #1.

### L2 — `Stable2` silent non-convergence → **AWARDED_EQUIVALENT (Med)** ✅
Pre-frozen L2 (TSE/STS) named exactly: the 255-iter loops fall through with **no revert** and return **0** (named
return never set), unlike `calcReserve`. That is the awarded mechanism. Base tag `BASE_BORN_INCOMPLETE` ("missing
revert seen; consumer impact not traced") → **routine completed** the silent-0→consumer-mispricing reasoning.
Mechanism-selection: **awarded-mechanism-selected**. Procedure-completed-not-base recovery #2.

### L3 — `WellUpgradeable.init`/upgrade → **BENIGN** (correct refute)
Routine REFUTED the UUPS-impl-takeover (auth checks block direct-impl upgrade). No awarded WellUpgradeable
init/upgrade finding exists → the refutation was correct (no false positive). Mechanism-selection:
**awarded-mechanism-not-enumerated** (n/a — no award at this locus).

## basin metrics
| metric | value |
|---|---|
| loci | 3 |
| AWARDED_EQUIVALENT | **2 (L1 High, L2 Med)** |
| PARTIAL_AWARD | 0 |
| SAME_AREA_WRONG_MECHANISM | 0 |
| BENIGN / severe FP | 1 benign (L3) / 0 severe FP |
| procedure-completed-not-base recoveries | **2 (L1, L2)** |
| awarded-mechanism-selected (of awarded-loci) | **2/2** |

**Honest note:** both basin bugs are *mechanical/math* (copy-paste typo; missing revert) — a bug-class where the
base read already births ~most of the candidate; the routine's completion contribution is the **impact** step,
which is real but thin-margin (mirrors LoopFi L2). "Selecting" the mechanism for a single-mechanism typo is near-
trivial, so basin's 2/2 selection is not strong evidence of improved selection on *subtle* bugs.
