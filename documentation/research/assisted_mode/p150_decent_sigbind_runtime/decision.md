# P150 — Decision

## Decision: **RUNTIME_CONFIRMED** (mechanism; reachability/severity → human review)

A Foundry test deploys the **real decent `UTBFeeCollector`** (a holdout, no local answer key) and calls its real
`collectFees`. With a valid signer signature over `feeAmount = 1e18` (encoded in `packedInfo`), the contract
charged the **unsigned `feeAmount = 1000e18`** from `utb`; a corrected reference that binds `fees` to the signed
`packedInfo` reverts; a matched control shows no divergence. The signature does not bind the executed fee
(authorization subject mismatch) — a contract-level binding-failure mechanism with a clear state delta + control
comparison.

### Rubric (not biased toward confirmation)
- **RUNTIME_CONFIRMED** ✅ for the mechanism: real contract exhibits the binding failure with a meaningful state
  delta + corrected reference + matched control.
- **Reachability/severity unproven** (the partial axis): `collectFees` is `onlyUtb`; whether an external attacker
  can supply mismatched `fees` while reusing a signer signature depends on the UTB router flow (out of harness);
  replay/no-nonce noted. → deferred to **human review** (`requires_human_review=true`,
  `requires_poc_review=true`). [Per P147 calibration, mechanism-confirmed + severity-deferred is recorded as
  `runtime_confirmed` with the impact axis flagged, not `runtime_partial`.]
- Not RUNTIME_REFUTED (the binding failure is real); not RUNTIME_BLOCKED (deps compiled, path executed).

## Final response
- **Decision:** RUNTIME_CONFIRMED.
- **Selected candidate & why:** decent `UTBFeeCollector.collectFees` — deploy-light (3 small deps; no oracle/RPC/
  bridge infra), crisp state delta (charges an unsigned fee), clean corrected reference + control, and a 5th
  distinct architecture (cross-chain bridge fee/signature auth). `duplicate_unknown` (no local answer key).
- **Rejected candidates:** vultisig `ILOPool.claim` (heavy UniV3/vesting deps), kelp `LRTDepositPool` (oracle/RSETH
  deps, less crisp); munchables/pooltogether considered.
- **Runtime classification & evidence:** 3/3 pass; signer authorized 1e18, real charged 1000e18; corrected reverts;
  matched control charges 1e18.
- **Panel delta:** +1 runtime-only row `H3-decent-utbfeecollector-sigbind` → panel `{rows: 14, runtime_only: 3,
  by_status: {runtime_confirmed: 4, runtime_refuted: 1, not_run: 9}}` across 5 architectures; prompt baseline
  byte-for-byte unchanged.
- **Integrity:** production source unchanged (`UTBFeeCollector.sol` byte-identical); harness un-wired; no
  detector/gate/severity/submission/routing/prompt change; corpus + prompt baseline unchanged; active `output/`
  symlink unchanged; all rows `routing_allowed=false` + `submission_ready=false`.
- **Tests:** 31 research tests pass (29 + 2); full suite 1668 passed / 2 pre-existing snapshot fails / 4 skipped.
- **submission_ready = false** (explicit end-state unless a human overrides outside this phase).

## Next recommended phase (P151)
Either a human reachability/severity review of H3 (is the UTB router flow attacker-influenceable? is replay in
scope?) — analogous to P149 — or a third non-duplicate runtime holdout to keep growing cross-architecture yield;
or roll the runtime panel's 5-architecture / full-vocabulary state into a brief cross-architecture yield summary.
