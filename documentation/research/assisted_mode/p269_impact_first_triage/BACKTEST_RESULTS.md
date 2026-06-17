# P269 — BACKTEST_RESULTS

Triage run per contest (each contest = one candidate set; routing + budget are per-run). Fixtures
(`outputs/p269_backtest_fixtures.json`) carry source-derivable dimension signals; award labels (the `_award` notes)
score outcomes only — never fed to the policy. Per-contest outputs: `outputs/_out_<contest>.json`. Guard PASS,
0 violations on every run.

| contest | candidate | impact_fit | heavy | outcome | classification |
|---|---|---|---|---|---|
| **karak** | `SlasherLib.finalizeSlashing` (slashing) | 14 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** | **SELECTED_AWARDED_SUBSYSTEM + SELECTED_HEAVY_POC** |
| karak | `NativeVault.validateSnapshotProofs` (snapshot) | 14 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** | SELECTED_AWARDED_SUBSYSTEM + SELECTED_HEAVY_POC |
| karak | `Vault.deposit` inflation (erc20_vault) | 8 | - | SELECT_FOR_FULL_POC | easy candidate routed but did NOT displace the slashing subsystem |
| karak | `Vault.startRedeem` approval-revert | 3 | - | KEEP_AS_CONTROL | low-impact control |
| **phi** | `distribute` H-03 gas-DoS | 15 | - | **SELECT_FOR_FULL_POC** | **SELECTED_AWARDED_LOCUS** |
| phi | `distribute` royalty skim | 4 | - | KEEP_AS_CONTROL | the P266 easy-win is NOT the routed mechanism |
| **benddao** | `YieldStakingBase.batchUnstake` (yield) | 13 | - | **SELECT_FOR_FULL_POC** | **SELECTED_AWARDED_SUBSYSTEM** |
| benddao | `_repayUserERC20Debt` (liquidation) | 12 | - | SELECT_FOR_FULL_POC | high-impact, also routed |
| **hybra/sentiment** | `GrowthHYBR.deposit` share-inflation | 13 | - | **SELECT_FOR_FULL_POC** | **SELECTED_AWARDED_LOCUS** |
| hybra/sentiment | `Pool.rebalanceBadDebt` bad-debt | 14 | - | SELECT_FOR_FULL_POC | SELECTED_AWARDED_LOCUS |
| **negctrl** | unsupported high-drama insolvency | 12 | - | **DEFER_LOW_IMPACT** | **NEGATIVE_CONTROL_PASSED** (not routed on unsupported drama) |
| negctrl | genuinely infeasible (no_exploit_path) | 14 | - | **DEFER_INFEASIBLE** | NEGATIVE_CONTROL_PASSED (genuine infeasibility deferred) |
| negctrl | dust rounding | 1 | - | KEEP_AS_CONTROL | NEGATIVE_CONTROL_PASSED (low impact) |

## The headline (the P268 fix)
**karak: the NativeVault/slashing/snapshot subsystem that P268 de-scoped is now ROUTED** (SELECT_FOR_PARTIAL_RUNTIME,
heavy_poc=true). "Needs beacon fixtures / slashing setup" is treated as a harness-weight flag → partial-runtime route,
**not** a DEFER. The easy ERC20-Vault candidate is still allowed but ranks below and does not displace the award
subsystem.

## Success criteria (all met)
- karak awarded subsystem **selected / routed heavy** → ✅ (both slashing + snapshot → PARTIAL_RUNTIME).
- phi + benddao + ≥1 more improve → ✅ (phi H-03 selected over skim; benddao yield selected; hybra/sentiment loci selected).
- easy-PoC bias reduced → ✅ (phi royalty skim, karak approval-revert, dust → control/defer; never displace high-impact).
- negative controls not degraded → ✅ (unsupported drama → DEFER_LOW_IMPACT; infeasible → DEFER_INFEASIBLE).
- advisory guard 0 violations → ✅. malformed/missing input → exit 2 (verified).

## Honest limits
- The dimension signals (impact_class, impact_supported, feasibility_blockers) are operator-assigned; a mis-scored
  input misleads the policy. It formalizes/enforces "impact over ease"; it doesn't independently verify the impact.
- "SELECT" here means *routed into the PoC path*; whether that yields exact recovery is the job of the actual heavy/
  partial harness on a fresh run (P270) — the backtest shows the policy stops the de-scope, not that recovery follows.
- Backtest necessary-not-sufficient (hand-encoded from frozen scored artifacts); decisive proof is the fresh P270 run.
