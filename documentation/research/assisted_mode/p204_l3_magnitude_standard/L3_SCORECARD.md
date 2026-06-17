# P204 — L3 scorecard

Executable harnesses (real decent contracts + mocked external deps, honest custody). 5/5 tests pass
(`pocs/run_log.txt`). v2 labels from P203 (`e2100588`); L3 from harness results.

## Per-target
| target | awarded | v1 | v2 | **L3** | harness result |
|---|---|---|---|---|---|
| **H-01** setRouter→mint | High | HIGH | HIGH | **HIGH_CONFIRMED** | attacker minted 1e6 ether unbacked (material) ✅ |
| **M-03** receiveFromBridge | Medium | HIGH | HIGH | **MEDIUM_OR_LOWER** | no material theft under honest custody (victim safe, treasury safe, self-funded) ✅ demoted |
| decent-06 swapNoPath | (unawarded) | HIGH | HIGH | **MEDIUM_OR_LOWER** | no drain (no residual valuable balance) ✅ demoted |
| decent-12 redeem dbl-withdraw | (unawarded) | HIGH | HIGH | **NEEDS_HARNESS** | no source-valid path to redeemable dcntEth ✅ routed |
| H-02/H-03/H-04 (partials) | High | n/a | NEEDS_HARNESS | NEEDS_HARNESS | recall-misses; out of harness scope; unchanged |

## Aggregate
| metric | v2 | L3 |
|---|---|---|
| HIGH_CONFIRMED surfaces (decent-01..14) | 6 | **1** (H-01/decent-09 only) |
| false HIGH_CONFIRMED | M-03 (×3) + decent-06 + decent-12 | **0** |
| genuine High preserved | H-01 | **H-01** ✅ |
| genuine High wrongly demoted to Medium | 0 | **0** ✅ |
| Medium over-HIGH (M-03) | 3 surfaces | **0** ✅ |
| moved to NEEDS_HARNESS by L3 | — | decent-12 (+ H-02/03/04 already) |
| moved to MEDIUM by L3 | — | M-03, decent-06 |
| harness failures due to setup limits | — | 0 |

## Verdict
**L3 confirms the one genuine High (H-01) via executable material impact and removes every v2 false-High.** The
HIGH bucket goes from 6 (precision ~1/6) to **1 (precision 1/1)** with **0 genuine-High loss** — the first time any
gate variant achieved clean two-sided separation on decent.
