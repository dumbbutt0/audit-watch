# P290 — POC_RESULTS (pre-reveal)

## Pools.deposit — Tier-C, claimed mechanism PASS_REFUTED (not lens-driven)
The pipeline's one READY claimed an EXTERNAL_INTEGRATION "crafted callback" mechanism. The Tier-C reproduction
(verbatim nonReentrant deposit + a malicious-callback token) shows:
| test | result |
|---|---|
| `test_standard_deposit_credits_correctly` (control) | ✔ standard token credits `amount` |
| `test_callback_reentrancy_is_refuted_PASS_REFUTED` | ✔ malicious-callback re-entry is reverted by `nonReentrant`; state uncorrupted |
`Suite result: ok. 2 passed.` → **classification PASS_REFUTED**: the claimed callback/reentrancy mechanism does NOT hold
(deposit is `nonReentrant`; only a standard `safeTransferFrom`; no DEX callback). The READY was a P279
EXTERNAL_INTEGRATION-template over-claim, not a source-backed deviation and not a P289-lens result.

## P289 lens PoCs: none (0 lens firings → no lens-driven READY to PoC).
## Fabricated passes: 0. severe FP: 0.
