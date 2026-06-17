# P167 Part C — hygiene-filtered selection + H11–H13 (reject-first, P166)

**Demonstration run; the hygiene tooling (Parts A/B) stands independently.** All three candidates were
generated from **`protocol_src`-only** signals (`scan_signals`, lib/test/mock excluded). Each: prediction
logged first → `sandbox_check` → Step-1 refutation → bucket → recorded. **0 harnesses built** (guardrail).

## Selection (hygiene-filtered)
The strict converting shape (`claim_many`/`onBehalfOf`/`claimFor`) returned **0 protocol_src hits** across
spectra / dittoeth / silo / predy — confirming the converting shape is genuinely depleted, not just buried in
vendored noise. Widening to recipient-parameterized value functions surfaced real protocol_src candidates.

## H11 — silo `BaseIncentivesController.claimRewards(_to)` → NO_ATTACKER_PROFIT
- Predicted: `static_false_positive`.
- Step 1: `claimRewards(_to)` does `_accrueRewards(msg.sender)` then `_claimRewards(msg.sender, msg.sender,
  _to, …)` — the recipient is caller-chosen but the value is the **caller's own** accrued rewards. The
  on-behalf path `claimRewardsOnBehalf` is `onlyAuthorizedClaimers` (owner-set). No foreign value.
- Bucket **NO_ATTACKER_PROFIT** (first failed gate G3); `SOURCE_REFUTED_NO_HARNESS`. Outcome matched prediction.

## H12 — zaros `CreditDelegationBranch._convertAssetsToUsdc(..recipient..)` → NO_RECIPIENT_CONTROL
- Predicted: `static_false_positive`.
- Step 1: the `recipient` signal is a parameter of an **internal** function (under `INTERNAL FUNCTIONS`,
  DEX-swap output plumbing) — not an attacker-callable external entrypoint; the recipient is not
  caller-controlled from outside.
- Bucket **NO_RECIPIENT_CONTROL** (first failed gate G2); `SOURCE_REFUTED_NO_HARNESS`. Outcome matched prediction.

## H13 — predy `PredyPool.updateRecepient(vaultId, recipient)` → PRIVILEGED_ONLY
- Predicted: `static_false_positive`.
- Step 1: `function updateRecepient(uint256 vaultId, address recipient) external onlyVaultOwner(vaultId)`
  (PredyPool.sol:286) — only the vault owner sets its recipient; an attacker cannot redirect another vault's
  margin.
- Bucket **PRIVILEGED_ONLY** (first failed gate G2); `SOURCE_REFUTED_NO_HARNESS`. Outcome matched prediction.

## Result vs the P167 success metric
- **Refutation quality up:** H11–H13 are real protocol_src refutations (NO_ATTACKER_PROFIT / NO_RECIPIENT_CONTROL
  / PRIVILEGED_ONLY) — *meaningful* reasons, not the lib-noise that produced H10.
- **Junk eliminated at generation:** 0 of the 3 candidates were vendored/mock noise (hygiene filter held).
- **harnesses_avoided preserved/grown:** 5 → 8. **reportables_per_harness 1/1** unchanged.
- **prediction_accuracy 4/4** — the reject-first prior is well-calibrated on this corpus.
- **0 reportables** — honest: the converting shape is depleted in the scanned fresh corpora (a real
  measurement, not a tooling failure).

## Scorecard after H11–H13
candidates 9 · reportable 1 · runtime_confirmed 1 · harnesses_built 1 · harnesses_avoided 8 ·
source_refutations 3 · gate_refutations 5 · reportables_per_harness 1/1 · prediction_accuracy 4/4 ·
fabrication_rate 0/9.
