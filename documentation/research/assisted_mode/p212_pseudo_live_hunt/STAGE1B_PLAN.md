# P212 Stage 1B — Harness verification of SOPH-01/02/03 (firewall intact, answer key SEALED)

## Context
P212 Stage 1 ended `READY_FOR_HUMAN_REVIEW` with 0 candidates High-submission-ready (all `blocked_by_missing_l3_poc`,
no executed PoC). Stage 1B builds real Foundry harnesses for the top 3 permissionless candidates to determine
source-valid executable impact and produce human-reviewable packages. **The sealed Sherlock report is NOT opened.**

## Recon (read-only) — harness is feasible
- `SophonFarming` (solc 0.8.25) inherits `Upgradeable2Step` → `Ownable(msg.sender)`, so a **directly-deployed** instance
  makes the deployer (test) the owner → can `initialize`/`add`/setters. Constructor takes `address[8]` token mocks.
- `initialize` only needs the 8 token mocks to support `approve()` (no conversions at init); it `add()`s 3 predefined
  pools. For SOPH-01/02 use a **generic `add()`'d MockERC20 pool** via `deposit(pid,amount,boost)`/`withdraw`/
  `increaseBoost`/`pendingPoints` — no LST mocks needed.
- SOPH-03: `depositStEth`→`_stEthTOwstEth`→`IwstETH(wstETH).wrap(_amount)` pulls `_amount` stETH from the contract;
  with stETH share-rounding delivering `_amount-1/2`, `wrap` reverts (DoS). Needs MockStETH (rounding) + MockWstETH.
- Deps: OZ **v5** locally available (`recall-2025-02/.../node_modules/@openzeppelin`) for remap; solc 0.8.25 via forge.
- Reuse the P204/P205/P207 forge-std-free harness pattern (inline `Vm` + `HarnessBase`); target source is the cloned
  `targets/` tree (never edited) referenced via remapping — not re-copied.

## Strict scope
Do NOT open the sealed report / read finding titles/bodies/judging/issue-IDs/dup discussions. No submit/route/promote/
demote. No production-source edit. Harnesses isolated under `pocs/p212/`. L3 flag in-process only (readiness checks).
Human review mandatory. Production prompt/gate/ledger byte-identical START==END (none modified). Active quantamm audit
untouched. Target source under `targets/` never edited.

## Execution (deliverables under `documentation/research/assisted_mode/p212_pseudo_live_hunt/`)
1. **STAGE1B_INTEGRITY_PRECHECK.md** — confirm sealed key unopened; START hashes (`deep_trace ef93a6c2`, gates,
   `submission_readiness_review 7c4b563d`, `dashboard 857d593a`, `validate_p208 7e148e18`, ledger `fc446040`) + target
   source tree hash; L3 flag not persisted; quantamm untouched.
2. **STAGE1B_HARNESS_TARGET_MATRIX.md** — per candidate: hypothesis · exploit sequence · affected state vars · loss
   model · pass/fail conditions · required mocks · source-validity assumptions.
3. **pocs/p212/** foundry project: `foundry.toml` (solc 0.8.25; remap `@openzeppelin/=<recall OZ v5>`, `vult/=<targets
   contracts>`); `test/Harness.sol` (inline Vm incl. `roll`/`prank`/`warp` + assert base); `test/Mocks.sol`
   (MockERC20; MockStETH delivering amount-1 on transfer to model share-rounding; MockWstETH.wrap pulling stETH).
4. **SOPH-01 harness** (`test/SOPH01_withdraw_boost.t.sol`): deploy+initialize+add generic pool; userA deposits with
   boost, userB deposits plain; userA `withdraw`s full depositAmount; roll blocks; compare userA `pendingPoints` vs
   expected-on-real-remaining-stake; check boostAmount stale, conservation, dilution of userB. Record before/after
   amount+boostAmount, pool totals, pending points, scalability. → PASS/MEDIUM/FAIL per L3.
5. **SOPH-02 harness** (`test/SOPH02_accPointsPerShare.t.sol`): single + multi-user accrual; compare contract
   `pendingPoints` vs independently computed expected; vary deposit sizes/elapsed blocks; classify overpay/underpay/
   view-only-rounding; record delta magnitude + who gains/loses. → PASS only if material scalable misallocation.
6. **SOPH-03 harness** (`test/SOPH03_stEth_wrap.t.sol`): depositStEth with MockStETH delivering `amount-1` → expect
   revert (DoS) at wrap; control with honest stETH (exact) → succeeds. Record requested/received/wrapped, revert
   condition, attacker-gain vs DoS-only. → MEDIUM (DoS) unless material theft.
7. **L3 readiness records** — update `output_research/l3_readiness/SOPH-0{1,2,3}.json` with measured l3_status/poc_tier
   (L3_REAL_CONTRACT_POC if executed)/poc_path/poc_command/poc_result/actual_delta/expected_delta_or_control/
   magnitude_basis/source_validity_notes/dependency_mocks/production_source_modified:false; re-run `l3_evaluate` overlay.
8. **UPDATED_REPORT_PACKAGES/** for SOPH-01/02/03 — PoC command, actual vs control result, revised severity, L3 status,
   missing evidence, human-review checklist.
9. **STAGE1B_RECOMMENDATION.md** + **stage1b_metrics.json** + **stage1b_integrity_checks.md** + copy plan →
   **STAGE1B_PLAN.md** + memory update.

## Decision space (Stage 1B)
`READY_FOR_SCORING` (≥1 candidate human-reviewable as Medium/High; every High rec has L3 PASS or written override;
key sealed; hashes unchanged; JSON valid) · `NEEDS_MORE_HARNESS_WORK` · `NO_REPORTABLE_CANDIDATES` ·
`FIREWALL_CONTAMINATED` · `INVALID_RUN`. **Expected:** `READY_FOR_SCORING` (likely ≥1 executable Medium; clean High
PASS uncertain — if none, candidates stand as Mediums, still scoreable).

## Acceptance criteria
Only SOPH-01/02/03 harnessed; sealed report unopened; harnesses under `pocs/p212/`; no production-source edit; L3
records updated + overlay re-run; High requires PASS/override; production hashes byte-identical START==END; JSON valid.

## Verification
`cd pocs/p212 && forge test -vvv` runs the 3 harnesses with measured deltas; `output_research/l3_readiness/SOPH-0{1,2,3}.json`
updated; `l3_evaluate` overlay reflects measured status; sealed `_sealed/judging` still unread; prod hashes unchanged;
`stage1b_metrics.json` valid. Then await user "ready for scoring" for Stage 2 (answer key) — NOT in this phase.
