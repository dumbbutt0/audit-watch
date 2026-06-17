# P198 — generalization scorecard (answer-aware, post-freeze)

Awarded key built from `report.md` (read only **after** the 12 blind outputs were frozen). 8 Medium / 0 High.

## Awarded findings × blind outcome
| awarded | surface | in bounded sample? | blind | score |
|---|---|---|---|---|
| **M-08** RestrictionManager only checks receiver, not sender | RestrictionManager.detectTransferRestriction | ✅ | RM-12 | **HIT (exact fn + exact mechanism)** |
| **M-07** trancheTokenAmount rounded DOWN (should be UP on withdrawal) | InvestmentManager._calculateTrancheTokenAmount (L591) | ✅ | IM-06 | **HIT (exact fn + rounding-direction mechanism)** |
| **M-05** claiming via deposit() starves Escrow shares for other claimers | LiquidityPool.deposit → Escrow/processDeposit | ✅ | IM-04 | **PARTIAL (Escrow-share conservation family; related framing)** |
| **M-04** deposit small amount for other users → DoS | LiquidityPool.deposit/mint (public, no access control) | ✅(callee only) | IM-04 | **MISS / WRONG_MECHANISM** |
| M-01 onlyCentrifugeChainOrigin ≠ axelarGateway | Gateway/axelar Router | ❌ | — | OUT_OF_SAMPLE |
| M-02 requestRedeemWithPermit front-run (wrong pool) | LiquidityPool.requestRedeemWithPermit | ❌ | — | OUT_OF_SAMPLE |
| M-03 cached DOMAIN_SEPARATOR wrong for tranche tokens | ERC20/Tranche permit | ❌ | — | OUT_OF_SAMPLE |
| M-06 DelayedAdmin cannot PauseAdmin.removePauser | PauseAdmin/DelayedAdmin | ❌ | — | OUT_OF_SAMPLE |

## Totals
- **In bounded sample (4):** HIT 2 · PARTIAL 1 · MISS/WRONG_MECHANISM 1.
- **Out of bounded sample (4):** not reachable by the 12-surface invariant-core sample (peripheral surfaces:
  gateway/permit/admin) — a **coverage/sampling** outcome, not an adjudication failure.
- **False positives / over-enumeration:** the blind run carried 24+ selected mechanisms across 12 surfaces; only
  ~3 correspond to awarded findings. The remainder (recipient-spoof, replay, escrow allowance-drain, _toUint128
  truncation, price-update ordering) are mostly hedged on "compromised Gateway/auth" or routed to NEEDS_HARNESS —
  **unconfirmed; low precision on this clean corpus** (not counted as awarded hits).
- **Wrong-mechanism (1):** M-04 — IM-04 traced the auth-gated callee `processDeposit`, **rejected** the
  access-control mechanism citing `auth`, and missed that the **public `LiquidityPool.deposit` wrapper** lacks
  access control (the awarded griefing). A non-responsive rejection on the wrong layer.

## The two exact hits (core generalization evidence)
- **M-08 / RM-12** — blind, with no answer key, stated: *"detectTransferRestriction checks hasMember(to) but NOT
  hasMember(from) → a revoked/non-member sender can transfer."* The awarded M-08 is verbatim this.
- **M-07 / IM-06** — blind selected *"_calculateTrancheTokenAmount rounds DOWN … disadvantaging the user vs the
  vault"* on the exact function (L591). The awarded M-07 is the rounding-direction defect in that function.

## Verdict-calibration lens
11/12 blind verdicts = HIGH_THREAD; awarded reality = **0 High / 8 Medium**. Severity is **over-calibrated** on a
clean codebase. Recall of awarded *mechanisms* generalized; severity *grading* and *precision* did not.
