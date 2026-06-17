# P270 — REVEAL_AND_SCORE (Phase 9, POST-FREEZE)

## Freeze integrity (recorded BEFORE opening the answer key)
BASE_AND_HARNESS_FREEZE `a3cc46edbfd9eea4` · DASHBOARD_SURFACE `b572bf64c59b9026` · SELECTOR_OUTPUTS `85456aa9241c1728`
· IMPACT_FIRST_TRIAGE `0b113dbc7d17675f` · RANKING_AND_COMPLETION `02d703728ad13a5f` · POC_INTENT `fb02f1dfeac93c0b`
· selector_decisions `4bc665965d611573` · triage_decisions `d00487303f8cb2b5` · P270_PendleShare.t.sol
`a959817f13baabca`.
Reveal source: `code-423n4/2024-02-wise-lending-findings/report.md` (PUBLIC), opened after freeze. Awarded: **5 High +
17 Medium**.

## Awarded Highs vs my routed candidates — the awards land in the routed subsystems+loci
| awarded High | subsystem | my routed candidate | match |
|---|---|---|---|
| **H-03** incorrect **bad-debt accounting** (partial liquidations inflate global bad debt w/o position-level deduction), bricks claimFeesBeneficial | **FeeManager bad-debt** | **C-bd** (FeeManager paybackBadDebt bad-debt accounting) | **SUBSYSTEM+LOCUS match; mechanism FAMILY-level** (I hypothesized "bad-debt payback bookkeeping error across paths"; did not pin the partial-liquidation global-vs-position deduction) |
| **H-04** liquidators pay less for uncollateralized positions (liquidation % applied to **both private+public collateral** instead of only private) | **WiseCore liquidation** | **C-liq** (WiseCore liquidation collateral/share misallocation) | **SUBSYSTEM+LOCUS match; mechanism FAMILY-level** (I hypothesized "liquidation collateral/share misallocation"; did not pin the private-vs-public split) |
| H-02 erase position debt for free (`_removePositionData`) | WiseCore/position | adjacent (liquidation/core area surfaced) | SUBSYSTEM-area |
| H-01 reentrancy via receive | WiseCore | (recall surfaced deposit/withdraw core) | not targeted |
| H-05 wrong nftId for PowerFarm Aave-position check | Pendle power farm | C-pp area (Pendle farm) | DIFFERENT mechanism (position-type detection, not share inflation) |

Awards concentrate in: WiseLending core · **FeeManager bad-debt** · **WiseCore liquidation** · PowerFarms · WiseSecurity
— i.e. exactly the subsystems the impact-first triage routed (bad-debt, liquidation, Pendle-farm).

## My candidate scoring
| id | mechanism | PoC | awarded match | classification |
|---|---|---|---|---|
| **C-liq** | WiseCore liquidation misallocation | not run (heavy) | **H-04 locus** | **FAMILY_LEVEL_MATCH** (right subsystem+locus+family; not exact root cause; not PoC-completed) |
| **C-bd** | FeeManager bad-debt accounting | not run (heavy) | **H-03 locus** | **FAMILY_LEVEL_MATCH** (right subsystem+locus+family; not exact; not PoC-completed) |
| C-pp | Pendle-share first-depositor inflation | PASS (refuted) | not this mechanism (H-05 is position-type detection) | **BENIGN** (true negative; correctly refuted) |

## Mechanism-recovery scoring (strict)
- **EXACT_AWARDED_MECHANISM: 0** · **STRONG_MECHANISM_MATCH: 0** (no PoC/runtime support; hypotheses family-level).
- **FAMILY_LEVEL_MATCH: 2** — C-liq→H-04, C-bd→H-03 (correct subsystem + locus + bug family at two awarded Highs).
- **SUBSYSTEM_ONLY_RECALL: YES** — the routed set hit the award-dense subsystems (bad-debt, liquidation, Pendle).
- **BENIGN: 1** (C-pp, correctly refuted).
- **FALSE_POSITIVE (severe concluded/reportable): 0** — nothing concluded/reportable; C-pp is a true negative.
- **PoC:** C-pp POC_REFUTES_CANDIDATE; C-liq/C-bd PoC not attempted (NEEDS_MORE_RUNTIME, full-stack heavy) → no
  POC_SUPPORTS_AWARDED this round.

## Per-awarded-issue chain (the routed Highs)
H-03 & H-04: **dashboard-surfaced YES · recall-delta YES · selector-preserved YES (KEEP_BOTH) · triage-selected YES
(SELECT_FOR_PARTIAL_RUNTIME) · completed PARTIAL (family-level) · PoC NOT attempted (heavy) · exact NO / family YES**.

## Headline (the genuine advance)
For the first time in the arc, the **selection layers steered the PoC queue onto the EXACT awarded loci of multiple
awarded Highs** (H-03 bad-debt, H-04 liquidation) — the P268 triage de-scope is fixed on fresh data, and routing now
lands on awarded loci. **But 0 exact recovery**: the mechanism hypotheses were FAMILY-level (not pinned exact) and
the confirming PoCs were **harness-weight-blocked** (NEEDS_MORE_RUNTIME) on a large lending stack. The bottleneck
moved one stage further down — from *selection* (fixed) to *completion/PoC depth* on heavy protocols.
