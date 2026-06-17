# Scorecard — Beanstalk Finale (eval2, API-free)

_Re-matched against THIS run's 48 merged findings. Run was fully API-free; stopped at review_gate (Step 4)._

- **Total public findings:** 81
- **Exact HIT:** 15
- **PARTIAL HIT:** 19
- **ADJACENT:** 9
- **MISS:** 38
- **Pipeline-only FP:** 8
- **Overall exact hit rate:** 18.5%  (15/81)
- **Useful detection rate (HIT+PARTIAL):** 42.0%  (34/81)
- **Any-touch (incl. ADJACENT):** 53.1%
- **Worst category:** Protocol Integrity (0/5 meaningful)
- **Best category:** Silo/Floods (6/6 meaningful, all PARTIAL)
- **Most common miss reason:** wrong contract inspected (12 findings)
- **Most wasteful FP source:** speculative-reachability (AR-001, DS-004) + privileged/lifecycle-misread (BSA-005, DT-011, SG-004)
- **PoC success rate:** N/A (run stopped at review_gate / Step 4)

## Hit rate by severity (inferred buckets 22H/31M/28L)

| Severity | n | Exact HIT | HIT rate | Meaningful (HIT+PARTIAL) | Meaningful rate |
|---|---|---|---|---|---|
| High | 22 | 11 | 50.0% | 13 | 59.1% |
| Medium | 31 | 4 | 12.9% | 14 | 45.2% |
| Low | 28 | 0 | 0.0% | 7 | 25.0% |

_Severity buckets inferred to match CodeHawks' published aggregate (per-finding official severity absent from the answer key); treat as indicative._

## Hit rate by category

| Category | n | HIT | Meaningful | Meaningful rate |
|---|---|---|---|---|
| L2 Migration | 33 | 10 | 19 | 57.6% |
| Oracle | 9 | 2 | 4 | 44.4% |
| Silo/Floods | 6 | 0 | 6 | 100.0% |
| Protocol Integrity | 5 | 0 | 0 | 0.0% |
| Auth/Permit | 4 | 2 | 2 | 50.0% |
| Field/Plots | 4 | 0 | 0 | 0.0% |
| Silo/Convert | 3 | 1 | 2 | 66.7% |
| Silo/Stalk | 3 | 0 | 0 | 0.0% |
| Tractor | 2 | 0 | 0 | 0.0% |
| Oracle/L2 | 2 | 0 | 0 | 0.0% |
| L2 Migration/Barn | 2 | 0 | 1 | 50.0% |
| Oracle/Barn | 1 | 0 | 0 | 0.0% |
| Silo/Rewards | 1 | 0 | 0 | 0.0% |
| Barn/ERC1155 | 1 | 0 | 0 | 0.0% |
| Pipeline/Tractor | 1 | 0 | 0 | 0.0% |
| Silo/Whitelist | 1 | 0 | 0 | 0.0% |
| Auth/Events | 1 | 0 | 0 | 0.0% |
| Protocol Integrity/Oracle | 1 | 0 | 0 | 0.0% |
| Tractor/Pipeline | 1 | 0 | 0 | 0.0% |

## REGRESSION vs prior eval baseline

| Metric | Prior (eval1) | eval2 (API-free) | Delta |
|---|---|---|---|
| Exact HIT | 24 | 15 | -9 |
| PARTIAL | 21 | 19 | -2 |
| ADJACENT | 9 | 9 | +0 |
| MISS | 27 | 38 | +11 |
| Meaningful detection % | 55.6% | 42.0% | -13.6 pts |

**Regression read.** eval2 regressed -13.6 points on meaningful detection (55.6% -> 42.0%), driven almost entirely by **-9 exact HITs**. The lost HITs are NOT reasoning failures on bugs that were attempted — they are **whole-contract coverage holes**: the prior run's `token_integration` C.sol-constant sweep (hardcoded WETH #133, PIPELINE #419, L2 Chainlink registry #135), the `dos` plot-spam finding (#379), the ERC1155 mint-acceptance DoS (#273), and the LibWell 18-decimal finding (#184) did not regenerate this run. The ReseedWhitelist stalk-ordering HIT (#452) also flipped to MISS because eval2's BSA-001 slot was occupied by the (unrelated) oracle inverted-ternary instead.

**Where the api-free deep-analysis HELD or GAINED.** The migration/oracle/flood domains the api-free deep_analysis targeted held up: the headline migration cluster (replay #397/#471, =vs+= #328, loop-counter #398, global-stalk/roots #251/#327, EXTERNAL_L1_BEANS=0 #131, internal balances #325) all remained clean HITs, and the Chainlink inverted-ternary (#68/#303) and convert-sandwich (#519) HIT. Silo/Floods went 0 HIT but 6/6 PARTIAL (vs prior mostly-PARTIAL) — flood reasoning is present but still not converted to user-loss scenarios. So the deep-analysis preserved the *core invariant cluster*; the regression is a *breadth* (coverage) loss, not a *depth* loss in the targeted domains.