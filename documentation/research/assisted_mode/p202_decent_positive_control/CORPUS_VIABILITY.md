# P202 — corpus viability (decent-2024-01-holdout)

## Selected via PCS (positive control)
decent-2024-01 was ACCEPTed by the Positive-Control Screening phase as the best corpus to test High-confirmation:
- **4 High / 5 Medium** (count-only viability).
- **4/4 Highs** classified contract-level AND source-reachable AND permissionless/attacker-controlled, impact ∈
  {theft, permanent-loss} (the firewall screening tags; the orchestrator did not receive the verbatim titles/loci).
- **5 Mediums** → enough to keep measuring over-HIGH demotion in the same run.

## Why viable for a TWO-SIDED test
- **High-preservation axis:** 4 source-reachable contract-Highs → unlike zetachain (P201, 0 matched contract-Highs),
  decent's Highs are in the audited Solidity and reachable from the sampled surfaces (UTB / executor / swapper /
  bridge router / adapters). This is the positive control the campaign lacked.
- **Medium-demotion axis:** 5 Mediums → continued over-HIGH measurement.

## Controlled boundary (this phase)
- Only the PCS **count-level** facts are used pre-run (4H / 5M / 4 source-reachable contract-Highs).
- Finding bodies are **not** reopened before the blind run; no titles/loci are exposed to the blind subagents or to
  the fresh calibration subagent.
- Full `report.md` opened only at scoring (Step 6), after FREEZE 1 + FREEZE 2.

## Caveats
- Bounded 14-surface sample → out-of-sample **signal**, not full recall; the number of *mechanism-matched* awarded
  findings (set at scoring) determines power.
- The orchestrator holds a PCS-contamination prior (see CONTAMINATION_MITIGATION.md) → calibration is firewall-applied.
- In-scope source spans `src/` + `lib/decent-bridge/src/` (the audited bridge contracts), per PCS scope note.
