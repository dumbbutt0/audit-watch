# P202 — Medium-demotion scorecard (decent-2024-01)

Does the refined gate still demote Medium over-HIGH on the same corpus where it confirms Highs? **Mixed — it
regresses on one over-claimed mechanism.**

## Matched awarded Mediums (5) → ceiling vs calibrated
| awarded Medium | blind surface | ceiling | calibrated | outcome |
|---|---|---|---|---|
| **M-03** Missing AC on UTB.receiveFromBridge (fees/signature bypass) | decent-01/02/03 | CRITICAL/HIGH | **HIGH_CONFIRMED** | ❌ **over-HIGH NOT fixed** (gate over-confirmed an awarded Medium on 3 surfaces) |
| M-02 Free use via DecentEthRouter.bridgeWithPayload direct | decent-10 | HIGH | NEEDS_HARNESS | ◑ not over-HIGH (held at harness; over-cautious) |
| M-04 Loss from fixed fee calculations | decent-05 | HIGH | **MEDIUM** | ✅ correctly demoted |
| M-01 Permanent loss if swap data outdated | (decent-06 surface, diff mechanism) | — | — | recall: blind found a different (unawarded) UniSwapper mechanism |
| M-05 Refunded ETH stuck in DecentBridgeAdapter | decent-10 (partial) | HIGH | NEEDS_HARNESS | ◑ held at harness |

## Over-HIGH on matched awarded-Mediums
- Ceiling: **5/5** rated ≥HIGH.
- Calibrated: **3/5 still over-HIGH** (decent-01/02/03, all the **M-03 receiveFromBridge** mechanism), 1 correctly
  demoted (decent-05/M-04), 1 held at harness (decent-10/M-02).
- **Gate fixed 2/5; the 3 it failed are all the same over-claimed mechanism (M-03).**

## Root cause of the regression
The receiveFromBridge access-control finding is awarded **Medium** because, in practice, UTB does not custody user
funds between transactions — so the realistic impact is fee/signature bypass, not theft. The blind layer
**over-claimed** it as permissionless theft of "UTB-held funds" (CRITICAL). The refined gate's "magnitude
demonstrable from the shown evidence" criterion was satisfied by the blind agent's confident (over-)assertion, so
the gate **confirmed HIGH**. The gate trusts the blind output's magnitude claim; it has no independent check that
the funds-held precondition actually holds → it inherits the blind layer's over-claim.

## Verdict on this axis
**Medium demotion: REGRESSED** on over-claimed mechanisms. The DoS/precision/admin demotions still work (decent-05
M-04 → Medium; decent-14 → Medium), but a Medium whose blind output asserts theft is over-confirmed High.
