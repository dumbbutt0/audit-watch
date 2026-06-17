# P234 — Targeted Precision Gate (closeout)

> **Type:** blind measurement gate. No answer keys, no public duplicate hunting. L3 records written only for
> runtime-confirmed candidates. No submit/route/promote/sync; no production/detector/severity/prompt/dashboard edits.

## Targets used (2 fresh, blind)
- **Lambowin 2024-12** (cross-chain/router/launchpad; ~601 LOC; foundry, vendored lib/).
- **DYAD 2024-04** (oracle/accounting CDP stablecoin; ~691 LOC; foundry, vendored lib/).
Report/output/answer-key files were never opened; candidate generation was pure-blind from source.

## Candidate counts by class
| Target | Total | HIGH | MED | LOW | NOISE |
|---|---|---|---|---|---|
| Lambowin | 12 | 5 | 4 | 3 | 0 |
| DYAD | 7 | 4 | 2 | 1 | 0 |
| **Total** | **19** | **9** | **6** | **4** | **0** |

## Selected 3 HIGH_SIGNAL (frozen before harnessing; ≥1/target, meaty not easy-only)
| Candidate | Target | Mechanism |
|---|---|---|
| LAMBO-01 | Lambowin | `VirtualToken.cashIn` mints `msg.value`(=0) on the ERC20 branch → deposit locked |
| DYAD-01 | DYAD | `liquidate()` never seizes `vaultsKerosene[id]` → liquidator under-paid → bad debt |
| DYAD-03 | DYAD | `UnboundedKerosineVault.assetPrice()` `tvl - dyad.totalSupply()` underflow → system DoS |

## Result of each proof attempt
| Candidate | Status | forge | harness time | failed attempts | scaffold/recipe reuse | key manual insight |
|---|---|---|---|---|---|---|
| LAMBO-01 | **CONFIRMED_L3** | 2/2 | <1h | 0 | OZ5 from pocs/p223/vendor; real-source-copy recipe | ERC20 branch must be deployed (conditional reachability) |
| DYAD-03 | **CONFIRMED_L3** | 2/2 | ~1h | 1 (ds-test remap) | DEPENDENCY_MAP pattern (remap to in-repo dyad lib); external-only mocks | cast mocks to `Vault`/`Dyad` types; control TVL≥supply |
| DYAD-01 | **CONFIRMED_L3** | 2/2 | ~1.5h | 0 logic (build remaps only) | full real CDP lifecycle (DNft/Dyad/Licenser/Vault), free dNFT mint | drive real deposit→mint→price-drop→liquidate; assert kerosene `id2asset` unchanged |

forge totals: **LAMBO 2/2 · DYAD 4/4** (DYAD-03 2 + DYAD-01 2) = **6/6 across pocs/p234**.

## L3 records created (runtime-confirmed only)
`output_research/l3_readiness/{LAMBO-01, DYAD-03, DYAD-01}.json` — all l3_status=PASS, poc_tier=L3_REAL_CONTRACT_POC,
research_only, not routed. `decide()` classifies all three **medium** (no clean attacker-profit path → not promoted;
**0 false-Highs**).

## Precision measurement
| Metric | Value |
|---|---|
| HIGH_SIGNAL selected | 3 |
| confirmed (CONFIRMED_L3) | 3 |
| refuted | 0 |
| blocked (harness/build) | 0 |
| **confirmed precision** | **3/3 = 100%** |
| confirmed-or-plausible precision | 3/3 = 100% |
| avg proof effort | ~1h/candidate, ≤1 fix iteration each |
| avg scaffold/recipe reuse | high (real-source-copy recipe + DEPENDENCY_MAP dep-wiring on both targets) |

## Failure analysis
No non-confirmed candidates → no false-positive / incomplete-path / missing-precondition / defense-covers /
harness-limit / insufficient-evidence cases among the **selected**. (See "biggest FP source" for the unselected risk.)

## Biggest false-positive source (risk surface, not realized)
The HIGH candidates most at risk of being FPs were the ones deliberately **not selected**: the MEV/economic
"missing-slippage" findings (LAMBO-02/07/10 — flagged HIGH on a code smell, but economic exploitability is
conditional on a sandwich and not deterministically runtime-confirmable) and the owner-config DoS (LAMBO-03/09 —
require a privileged/reverting owner). These are the recall stack's main over-claim surface; live hunting should
route MEV/economic and admin-precondition HIGHs to manual economic review rather than expecting clean L3.

## Biggest proof-conversion bottleneck
Build/dependency wiring: DYAD pins `solc =0.8.17` (had to install) and uses non-relative imports needing `src/` +
`ds-test/` remaps. This matched P232's "dependency wiring is the #1 friction" finding — and it was a quick
lookup/fix (in-repo lib reused via remapping), not a blocker. The DYAD-01 full-CDP fixture was the most code but
converged cleanly (free dNFT mint + the established recipe).

## Scaffold reuse summary
The P232/P233 specifics (HarnessBase.expectEventOrder, MutableIndexPool) were not needed here (these are not
event-order/index-timeline bugs). What carried over and paid off: (1) the **real-source-copy + external-only-mock +
L1/L2/L3+control recipe**; (2) the **DEPENDENCY_MAP discipline** — both targets' deps were already in-repo
(`lib/`), so wiring was remapping, not vendoring; (3) the **Fixture pattern** for DYAD-01 (deploy/wire real
contracts, drive real actions).

## Final Verdict

# A — LIVE_HUNT_READY

Pass condition met: **3/3 selected HIGH_SIGNAL confirmed L3** (≥2/3) · **0 severe false-Highs** (decide all medium)
· no answer-key dependence · no forbidden-file changes · no unrealistic mocks (external-only, faithful) · low avg
proof effort (~1h each). High-signal candidates from fresh blind targets convert cleanly across both a router and
an oracle/accounting architecture.

## Recommendation
**Begin aggressive live hunting WITH HUMAN REVIEW.** Honest caveats carried forward:
1. The gate selected the strongest-evidence, deterministically-confirmable candidates (per the phase's own
   selection rules). MEV/economic and admin-precondition HIGHs were excluded and remain a **lower-precision class**
   — route those to manual economic review, not auto-L3.
2. `decide()` conservatively rated all three **medium** (no attacker-profit path); **severity calibration for
   protocol-bad-debt / system-DoS / conditional fund-lock remains a human-owned call** (recurring theme P212/P221/
   P227). Human review must set final severity.
3. n=3 is a small sample; verdict A is explicitly "ready *with human review*", not unsupervised autonomy.
No further precision gate is required before supervised live hunting.
