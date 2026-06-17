# P250 — Reveal & Score (post-freeze)

Freeze hashes (recorded before reveal): base `5ab782d3…`, checkpoint `107db6ef…`. Answer key WEB-FETCHED from
the Code4rena Spectra report AFTER both freezes (sources below).

## Awarded findings (spectra-2024-02): 0 High + 2 Medium
- **M-01 — PrincipalToken not ERC-5095 compliant:** `redeem`/`withdraw` don't support EIP-20 allowance flows
  (msg.sender allowance over owner); `maxWithdraw`/`maxRedeem` revert when paused instead of returning 0.
  → **PERMISSION / spec-compliance** family (not accounting).
- **M-02 — flashLoan vault-deflation drains yield:** borrow the entire IBT balance, redeem all shares from
  the IBT 4626, re-mint at default price → drains accumulated yield, PT users lose. → **CROSS-CONTRACT**
  (external IBT-vault pricing interaction via `flashLoan`).

## Scoring (weights H=3/M=1; denom = 2)
| Awarded | Base candidate | Base class | +Checkpoint | Checkpoint class |
|---|---|---|---|---|
| M-01 (ERC-5095 / paused / allowance) | — (read `_owner!=msg.sender` revert + `whenNotPaused`, not flagged) | MISSED (0) | — (out of accounting domain) | MISSED (0) |
| M-02 (flashLoan vault-deflation) | B-3 (flashLoan lends entire IBT + reentrancy framing) | PARTIAL_HIT (0.5) | reinforced B-3 locus (A3/A4) but did not construct the cross-contract deflation chain | PARTIAL_HIT (0.5) |

- **Base recall:** 0.5 / 2 = **25% credited** (strict 0%).
- **+Checkpoint recall:** 0.5 / 2 = **25% credited** (strict 0%).
- **Recall lift (checkpoint-attributable): 0.0** — the checkpoint recovered **no** awarded finding the base
  hunt missed.

## Why the lift is zero (honest, informative)
Spectra's two awarded findings are **not accounting-family**: M-01 is a permission/ERC-5095 compliance issue
and M-02 is a cross-contract flashLoan/IBT-vault deflation. The accounting checkpoint:
- **correctly stayed silent on M-01** (out of its domain → no false candidate; this is good precision, not a
  miss of its job), and
- **reinforced the M-02 locus** (`flashLoan` A3/A4, Q4 "deprive others") but could not complete M-02's
  specific deflation chain, which requires **cross-contract** reasoning about the external IBT vault's pricing
  — the job of the not-yet-built cross-contract checkpoint, not the accounting one.

So the zero lift is a property of *this contest's bug mix* (no accounting-family award), not a checkpoint
failure. It also independently corroborates P247/P248: the high-value recall lives in the **state-transition +
cross-contract** checkpoints (M-02 is cross-contract), while accounting was chosen first to validate the
architecture cheaply and FP-safely — which it did.

Sources: [Code4rena Spectra report](https://code4rena.com/reports/2024-02-spectra) ·
[finding #210 (M-01)](https://github.com/code-423n4/2024-02-spectra-findings/issues/210)
