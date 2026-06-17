# P151 — Replay / Domain-Binding (separate side finding)

Kept **separate** from the fee-binding mismatch (per reject-first discipline: do not mix replay with the confirmed
mismatch unless replay directly enables the fee exploit — it does not, because the fee is bound by the router).

## Observation
The signed message `keccak256("\x19Ethereum Signed Message:\n32", keccak256(abi.encode(instructions, fees)))`
(`UTBFeeCollector.sol:46-47`; `packedInfo` from `UTB.sol:115/266`) binds `instructions` + `fees` but omits:
- **nonce** — no single-use enforcement; `UTBFeeCollector` has no nonce mapping (confirmed: no `nonce` in source).
- **chainid / domain separator** — no EIP-712 domain; same signature valid across chains.
- **verifying-contract address** — not bound; same signature valid across UTB/FeeCollector deployments.
- **deadline** — no expiry.

## Why it does NOT amplify the fee mismatch
The executed `fees` is part of the signed blob (router-derived), so replay reuses the **same** `(instructions,
fees)` the signer authorized — it does not let an attacker substitute a different fee. Replay's impact (if any) is
about reusing an authorized operation, not about charging an unsigned fee.

## Disposition
- Severity: undetermined (depends on backend signing policy: are signatures one-shot quotes? do `instructions`
  encode a unique op? is the same signer/feeCollector deployed multi-chain?).
- Human review required; `submission_ready=false`; recorded in the H3 sidecar row `replay_side_finding` field.
- Not pursued with a PoC in this phase (reachability review, not exploit-build).
