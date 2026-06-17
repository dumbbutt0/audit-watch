# P150 — Problem Statement

Second non-duplicate runtime holdout (after P147 centrifuge `runtime_confirmed` and P148 velodrome
`runtime_refuted`). Evaluate **one fresh `duplicate_unknown` holdout** with a real-contract harness, **not biased
toward confirmation**, for cross-architecture yield + runtime-panel honesty. Sidecar/runtime-only only; baseline
preserved.

## Selected candidate & result
**`decent-2024-01-holdout` `UTBFeeCollector.collectFees`** — a cross-chain bridge fee collector (a 5th distinct
architecture vs noya/blackhole/centrifuge/velodrome). No local answer key → `duplicate_unknown`.

- **Shape (authorization subject mismatch):** `collectFees(FeeStructure fees, bytes packedInfo, bytes signature)`
  verifies `ecrecover` over `packedInfo`, then transfers `fees.feeAmount` of `fees.feeToken` — but **`fees` is
  never bound to `packedInfo`**. The signer's authorization does not constrain the executed fee.
- **Runtime result: RUNTIME_CONFIRMED (mechanism).** With a valid signer signature over `feeAmount=1e18`, the real
  contract charged the **unsigned `feeAmount=1000e18`**; a corrected reference that binds `fees` to `packedInfo`
  reverts; a matched control shows no divergence.

## Honesty
- `runtime_confirmed` = the **contract-level binding-failure mechanism** is exhibited (clear state delta + control
  comparison). **Reachability/severity is NOT established** and is deferred to human review: `collectFees` is
  `onlyUtb`, so whether an external attacker can supply mismatched `fees` while reusing a signer signature depends
  on the UTB router flow (out of harness); replay / no-nonce / no-chainid are also noted.
- `duplicate_status=duplicate_unknown` = no local record only (not novelty). Not submission-ready
  (`submission_ready=false`, `requires_human_review=true`).

## Panel outcome
Panel now `{rows: 14, runtime_only: 3, by_status: {runtime_confirmed: 4, runtime_refuted: 1, not_run: 9}}` across
5 architectures, with the P138 prompt baseline byte-for-byte unchanged (`prompt_corpus_unchanged: true`). H3 is a
runtime-only row: `runtime_confirmed` / `duplicate_unknown` / `routing_allowed=false` / `submission_ready=false`.
