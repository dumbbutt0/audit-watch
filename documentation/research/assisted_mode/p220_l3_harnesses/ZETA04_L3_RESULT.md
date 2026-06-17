# ZETA-04 — L3 result: PASS (pause bypass executed)

**Harness.** `pocs/p220/test/ZETA04_pauseBypass.t.sol` · real unmodified `ZetaConnectorNonEth` (+ base) ·
mock: `MintableZetaToken` (standard mint/burn ERC20, does not create the vuln).
**Command.** `forge test --match-contract ZETA04 -vv` → **3/3 PASS** (`pocs/p220/logs/ZETA04_run.log`).

## What was proven
- **PoC (L1/L2/L3).** Pauser calls `pause()`; with `paused()==true`, TSS calls `onReceive(...,100 ether, EMPTY,...)`.
  - L2 state flip: `totalSupply += 100e18`, `balanceOf(DEST) += 100e18`.
  - L3 outcome: inbound minting **succeeds during an active pause** — the emergency pause does not halt inbound delivery.
- **Control.** The guarded sibling `onRevert` (`whenNotPaused`) **reverts** while paused, then mints `50e18` after
  `unpause()` → the pause modifier is precisely the gate `onReceive` omits. (`test_control_onRevert_blockedByPause_thenWorks`.)
- **Sanity.** `onReceive` also works unpaused — the defect is the missing pause gate, not a broken path.

## Classification & calibration
- **l3_status = PASS**, `poc_tier = L3_REAL_CONTRACT_POC`, `impact_class = auth_only`, `dependency_mocks = external_only`.
- `decide()` → **calibrated_severity = medium**, `high_promotion_allowed = false`,
  blocker = `attacker_model=privileged_only (need permissionless/program_accepted)`: `onReceive` requires the TSS
  caller, so High-promotion is correctly withheld pending human judgment. The mechanism (pause ineffective for
  inbound) is confirmed; severity is an availability/incident-response question.
- **Scorecard P220 category: `L3_PASS_MEDIUM`.**

## Post-score note (answer key, not used to shape the harness)
Official Sherlock severity for this issue (H-13) was High; P215 also flagged this as the system's recurring
under-rating of TSS-gated availability issues. Recorded only in `scoring_note`/`last_reviewer_note`; the harness and
calibration above were derived solely from source + run artifacts.
