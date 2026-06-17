# P217 — P215 ZetaChain RE-SYNC RESULTS

Command:
```
python scripts/sync_hunt_findings.py --phase P215 --audit zetachain-2023-10-holdout \
  --workspace documentation/research/assisted_mode/p215_full_funnel_rehearsal --write
```
(`scripts/build_synced_findings.py` is now a thin shim that runs exactly this.)

- **Dry-run first** → printed plan + 90% completeness + safety PASS; mirror hash UNCHANGED (wrote nothing).
- **Write** → emitted **12** records (12 updated / 0 new), 0 duplicates, **same record_ids** as P216
  (`zetachain-2023-10:P215:ZETA-xx:...`). Mirror `eb359941 → d578cd87`.
- **Idempotent**: re-running `--write` → byte-identical mirror (`d578cd87…`). The shim produces the identical file.
- **Safety**: 12/12 records pass `validate_synced` + `safety_ok` (`research_only/review_only:true`,
  `routes_in_production/routing_allowed/submission_ready:false`, `no_submit_controls:true`,
  `browser_computes_severity:false`, `canonical_submission_ready_source` present, `human_review_required:true`).
- **Completeness**: 57% → 90% (see COMPLETENESS_SCORECARD.md).

## ZETA-04 / ZETA-07 / ZETA-11 (checked in detail)
- **ZETA-04** (=H-13): mechanism="onReceive is onlyTssAddress but NOT whenNotPaused, while onRevert IS…";
  exploit_steps=["Operator pauses after incident","TSS … still calls onReceive", …]; defense_map="Add whenNotPaused to
  onReceive (both eth/non-eth connectors)"; attacker="conditional…"; severity=Medium (recorded); l3=NEEDS_HARNESS;
  blocker=blocked_by_missing_l3_poc; post-score note = HIT == H-13.
- **ZETA-07**: mechanism="gasFee = gasPrice*GAS_LIMIT + …"; exploit_steps=["FUNGIBLE_MODULE sets GAS_LIMIT=0","any user
  withdraws paying zero gas fee"]; defense_map="Add GAS_LIMIT!=0 / gasFee!=0 guard"; **poc_verification REPRODUCED**
  (forge test --match-contract ZETA07); severity=Low.
- **ZETA-11** (≈H-10): mechanism="pairPools[0] used directly … no check…"; exploit_steps=["Attacker pre-registers a
  pool…","victim swaps route through it"]; severity=Medium; post-score note = PARTIAL ~ H-10.

All three render 15/15 verifier sections; `submission_ready/routing_allowed:false`; severity recorded (never a
conversion token); dry-run-queue state + L3 status + blockers visible.
