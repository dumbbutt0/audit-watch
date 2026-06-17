# P219 — /candidates PAGE VERIFICATION

Verified via direct loader/handler calls (server flaky); live completion guard PASS in the hook run.

| Check (all 12) | Result |
|---|---|
| candidate card loads | ✅ 12/12 (`funnel:ZETA-xx`) |
| 15 checklist sections render | ✅ 12/12 |
| missing values explicit | ✅ executed-PoC fields show "unknown" for NEEDS_HARNESS; novelty "unknown" |
| evidence_backup links present | ✅ register/merged/confirm/L3/harness/report-package/dry-run-queue |
| L3 status visible | ✅ |
| blocker reason visible | ✅ |
| no submit/promote controls | ✅ (HTML unchanged) |
| no active-audit switch | ✅ (global funnel track) |
| /findings + /funnel still show 12 | ✅ |

## Detailed inspection (ZETA-04 / ZETA-07 / ZETA-11)
- **ZETA-07** (executed): now populated — reachability `uncertain (confirm gate)`; PoC actual `withdraw() succeeds with
  gasFee==0…`, expected/control `control test: GAS_LIMIT=21000 -> fee>0`, value-delta `gasFee=gasPrice*0+0=0…`;
  impact who_loses `protocol foregoes gas-fee revenue`, asset `ZRC20 outbound gas-fee collection`, who_gains unknown.
  **Ready for human analysis** (full PoC verification).
- **ZETA-04** (=H-13, NEEDS_HARNESS): reachability + asset + exploit_steps + defense_map present; PoC actual/expected/
  control **explicit-unknown** (no executed harness); who_loses unknown. **Ready for human analysis** — the only gap is
  an executed PoC, which is explicitly flagged (NEEDS_HARNESS), not hidden.
- **ZETA-11** (≈H-10): reachability + expected/control (planned) + asset present; PoC actual/value-delta unknown.
  **Ready for human analysis**; build harness to fill actual/value-delta.

Remaining-missing (exact): executed-PoC actual/value-delta for the 5 NEEDS_HARNESS candidates without an L3 actual;
who_gains for all (no beneficiary in any artifact); novelty for all (no novelty artifact). All explicit.
