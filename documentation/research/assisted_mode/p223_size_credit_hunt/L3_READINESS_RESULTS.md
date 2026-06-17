# P223 — L3 readiness + harness results (Step 7)

Run with `AUDITWATCH_L3_READINESS=1` (in-process). Records: `output_research/l3_readiness/SC-0{1,3,4}.json`
(schema PASS). `decide()` is the severity authority (forbidden file, byte-identical START==END).

## SC-01 — EXECUTED L3 PASS (the clean reportable)
- **Harness:** `pocs/p223/` (forge 1.5.1 / solc 0.8.23). `realsrc/` = real, unmodified Size `@src` (collateral
  subset; `Size.sol`/`SizeView*`/`Multicall.sol` excluded — none on the deposit path). Vendor: authentic OZ v5,
  minimal authentic-shape Aave v3 interface types (never executed), solady `FixedPointMathLib`. `MockWETH` is a
  faithful WETH9 wrapper that does **not** contain the bug.
- **Result: 3/3 PASS** on real source:
  - `test_L1_entry_permissionless` — unprivileged EOA enters `deposit` permissionlessly.
  - `test_L2_state_flip` — with 1 ETH trapped, attacker's 1-wei `deposit` credits `collateralToken` 1e18+1
    (not msg.value) and the contract ETH balance flips 1e18→0 (swept into WETH).
  - `test_L3_outcome_theft` — attacker paid 1 wei, holds 1e18+1 collateral; control asserts a msg.value-correct
    deposit would credit 1; net theft = 1e18 (the victim's trapped ETH).
- **decide() (flag on): `high_promotion_allowed=true`, `calibrated_severity=high`,
  `submission_state=ready_for_submission_package`.** All gates clear: L3 PASS · material delta · control · clean
  mocks (`external_only`) · `production_source_modified=false` · `attacker_model=permissionless`.
- **Severity-calibration caveat (recorded, drives conservative queue routing):** the attacker action is
  permissionless, but the *magnitude* is conditional on ETH being resident in the contract (a user mis-sending
  to one of the ~12 payable non-deposit functions, faithfully modeled by `nonDepositPayable`, or residual). The
  mechanism + theft are proven; whether real-world severity is Medium or High is a human calibration call.
  Therefore SC-01 is routed to the **dry-run queue as human-review (P222 priority lane)** rather than auto-High,
  honoring the 0-false-High invariant — the L3-PASS High is advisory, never auto-submitted.

## SC-03 / SC-04 — NEEDS_HARNESS (honest, not High-gated)
Both Medium-ceiling; not harnessed (PoC cap=3 spent on the SC-01 flagship; each needs the full offer/lending
deployment — Initialize + price feed + Aave pool + offer/position setup). `decide()` →
`high_promotion_allowed=false`, `calibrated_severity=needs_harness_for_severity`, `blocked_by_missing_poc`.
Source-confirmed mechanisms recorded; the over-rating guard correctly keeps them un-promoted. As Mediums they
carry no High-promotion dependency — the NEEDS_HARNESS state is the honest outcome, not a gate failure.

## Safety
- 0 false-Highs auto-promoted: only SC-01 reaches `high_allowed=true`, backed by an **executed** L3 PoC, and is
  still routed to human-review (not auto-submitted). SC-03/04 fail-closed.
- `decide()` severity authority unchanged; `validate_p208_l3_readiness.py` byte-identical START==END.
- All 9 downgraded candidates (SC-02/05/06/07/08/09/10/11/12) carry no L3 record (Low; not High-attempting).
