# P203 — v1 vs v2 scorecard (frozen decent artifacts)

v2 regrade by a **fresh key-blind firewall subagent** (`e2100588`), source-substantiating each mechanism against
decent source; scored against the already-opened P202 key by the orchestrator.

## Headline
| metric | v1 | v2 |
|---|---|---|
| HIGH_CONFIRMED mechanisms (of 8 v1-High) | 8 | **7 retained** (only decent-06 M1 downgraded) |
| HIGH_CONFIRMED **surfaces** | 6 (01,02,03,06,09,12) | **6 (identical)** |
| **H-01 (decent-09) retained High** | High | **High ✓** |
| **M-03 (decent-01/02/03) demoted from High** | High | **High — NOT demoted ✗** |
| over-HIGH on matched awarded-Medium | [01,02,03] | **[01,02,03] (unchanged)** |
| false HIGH_CONFIRMED surfaces | [01,02,03,06] | **[01,02,03,06] (unchanged)** |
| genuine High demoted to Medium | 0 | **0 ✓** |
| genuine High → NEEDS_HARNESS | decent-11,13 | decent-11,13 |
| downgrades from missing custody / asserted-only magnitude | — | 1 / 1 (decent-06 M1 only) |

## What v2 changed
- **Almost nothing at the surface level.** Only **1 of 8** v1-HIGH mechanisms (decent-06 M1 swapExactIn/Out — attacker
  funds their own swap → fee/routing bypass, not contract drain) was downgraded. Its surface (decent-06) **stays
  HIGH** via decent-06 M2 (swapNoPath drain). So the HIGH_CONFIRMED surface set is **identical** to v1.
- **H-01 correctly retained** (DcntEth setRouter → mint/burn; source proves attacker-controlled value path). ✓
- **M-03 NOT fixed.** The independent v2 agent kept receiveFromBridge (decent-01/02/03) HIGH_CONFIRMED, citing the
  arbitrary `executor.execute(target, payload, paymentOperator)` capability with UTB as caller as source-proven
  material (it labelled custody `ACCOUNTING_BALANCE_PROVEN`).

## Verdict
`V2_GATE_FAILED_FALSE_HIGH` — M-03 remains High and false-Highs are unchanged. The source-substantiation rule did
**not** fix the over-confirmation; it did **not** harm High preservation (H-01 kept; 0 false demotions).
