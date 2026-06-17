# P150 — Runtime Result

| field | value |
|---|---|
| harness_type | **real_contract** (real `UTBFeeCollector`; real `collectFees` called) |
| tests | 3 passed / 0 failed / 0 skipped |
| suspected mechanism | signature verified over `packedInfo` but executed transfer uses unbound `fees` |
| signer authorized | feeAmount = 1e18 (encoded in `packedInfo`) |
| actually charged | feeAmount = **1000e18** (the unsigned `fees.feeAmount`) |
| corrected reference | bind `fees` ↔ `packedInfo` → **reverts** |
| control (matched fees) | both charge 1e18; no divergence |
| runtime_status | **runtime_confirmed** (mechanism) |
| runtime_confidence | high |
| duplicate_status | duplicate_unknown |

## What this proves
The real `UTBFeeCollector.collectFees` charges a fee amount the signer never authorized: the `ecrecover` covers
only `packedInfo`, while the executed `transferFrom` uses the separate, unbound `fees` struct. The corrected
reference (which binds `fees` to the signed `packedInfo`) reverts, and the matched control shows no divergence —
isolating the defect to the unbound-fees path. This is a contract-level **authorization subject mismatch**
(signed subject ≠ executed subject) with a clear state delta.

## What it does NOT prove (kept honest; not biased)
- **Reachability/severity.** `collectFees` is `onlyUtb`; whether an external attacker can supply mismatched `fees`
  while reusing a signer signature depends on the UTB router flow (out of harness). The in-test caller is the
  privileged `utb` (analogous to P147's ward / P149's owner-vs-ward analysis). → **human review**.
- **Replay.** No nonce / chainid / contract binding in the signed message is noted but not the tested axis.
- **Severity / novelty.** No severity assigned; `duplicate_unknown` = no local record only.
- Not submission-ready.
