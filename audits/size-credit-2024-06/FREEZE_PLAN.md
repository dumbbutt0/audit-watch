# Freeze plan — liquidation_health_accounting promotion (Size + Ethos)

Mirrors the NOYA POST-VALIDATION freeze convention (no production code/prompt/validator/submission changes).

## Deterministic artifacts (byte-hash, repo-relative, in `pre_answer_key_snapshot/_baseline_hashes.txt`)
**Size** (`audits/size-credit-2024-06/`):
- `output/coverage_manifest.json`, `output/coverage_dispositions.json` (189 unassigned / 28 deferred / 4 assigned / **0 cleared** → noise-safe)
- `documentation/evals/size-credit-2024-06/{answer_key,final_eval_report,liquidation_health_accounting_research,liquidation_health_promotion,candidate_H-03}.md`

**Ethos** (`audits/ethos-reserve-2023-02-liquidation-health/`):
- `output/coverage_manifest.json`, `output/coverage_dispositions.json` (846 unassigned / 292 deferred / **0 cleared** → noise-safe)
- `documentation/evals/ethos-reserve-2023-02/{answer_key,liquidation_health_validation_report,liquidation_health_patch_retest,liquidation_health_promotion}.md`

## Volatile (behavioral replay, NOT hashed)
`output/liquidation_health_accounting_audit.json` (carries `generated_at`), `output/advisory_escalation_gate.json` (timestamped).
Routes/shapes/confidence/helper-attachments are guarded by `replay/replay_lha.py` + the pytest guard.

## Behavioral replay guard (read-only re-run of the lens + isolated gate check in tmp)
**Size** — assert: 4/4 seeds route high (H-03/H-04 `Liquidate.executeLiquidate`; M-09 `Compensate.executeCompensate` health_factor_after_action; M-11 `LiquidateWithReplacement.executeLiquidateWithReplacement` replacement_swap_fee_accounting); routes high-only; 0 wrong-domain FP (contracts ⊆ {Compensate, Liquidate, LiquidateWithReplacement, SelfLiquidate, Repay}); raw ≤ 12, routed ≤ 6 (now 9/5); isolated gate → every routed id `needs_deep_pass` (assigned_pass=deep, agent=liquidation_health_accounting_review), **never `finding`**; lens never mints.
**Ethos** — assert: H-01 `StabilityPool.offset`+`updateRewardSum` route; M-09 `RedemptionHelper.redeemCollateral` route; M-10 `TroveManager.liquidate`/`liquidateTroves`/`batchLiquidateTroves` route (context/PARTIAL hosts); helper volume control (context_helpers attached on redeemCollateral/offset/liquidateTroves; orphan `_liquidate*` route standalone); routed < raw (now 9 < 19); 0 wrong-domain FP (contracts ⊆ {TroveManager, StabilityPool, RedemptionHelper, BorrowerOperations, ActivePool, CollSurplusPool}); raw ≤ 24, routed ≤ 12; isolated gate → `needs_deep_pass` not `finding`.

## NOT changed
liquidation_health_accounting logic · shipped lenses · advisory_escalation_gate.py · run_pipeline.sh ·
agent_policy.json · prompts · submission/. No Size/Ethos production code touched — only freeze artifacts + 2 guard tests + 2 freeze notes.
