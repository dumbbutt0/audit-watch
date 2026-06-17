# P151 — Problem Statement

P150 RUNTIME_CONFIRMED a **contract-level** mechanism in `decent UTBFeeCollector.collectFees`: the signature is
verified over `packedInfo`, but the executed transfer uses the unbound `fees`. `collectFees` is `onlyUtb`. P151 is
a **reject-first** human reachability/severity review (judgment-record; like P149): can an **unprivileged
attacker** make the executed `fees` differ from the signed subject via the **real Decent UTB/router flow**,
converting the mismatch into user/protocol loss?

## Decision: DESIGN / PRIVILEGED-ONLY — NOT externally reachable (+ separate replay side finding)
The sole production caller (the UTB router) constructs `packedInfo = abi.encode(instructions, fees)` from the
**same** user `fees` at both entrypoints (`swapAndExecute` UTB.sol:115, `bridgeAndExecute` :266), via the
`retrieveAndCollectFees` modifier (:228-251 → `collectFees` :248). Those entrypoints take **no user `packedInfo`
parameter** — so the executed `fees` is always a member of the signed `packedInfo`, and an unprivileged attacker
**cannot** make them diverge. Only a direct `onlyUtb` call (privileged/compromised UTB, owner-set) could pass a
mismatched `packedInfo`. ⇒ The missing re-bind in `collectFees` is **defense-in-depth only**, not an externally
reachable value-movement bug. A **separate** replay/domain-binding weakness exists (the signed blob omits
nonce/chainid/contract/deadline) and is recorded as a side finding. `submission_ready=false`.

## Mechanism vs exploitability (kept separate)
- **Mechanism (P150, unchanged):** `collectFees` does not re-bind `fees` to `packedInfo` — `runtime_confirmed`.
- **Exploitability (P151):** not externally reachable through the router; privileged/design-only.

This is the intended "stop at the right boundary": a confirmed mechanism is **not** promoted to bounty-grade
exploitability when the only reachable caller binds the data. `duplicate_unknown` (no novelty inference); no
production/detector/gate/severity/submission/routing/prompt change; H3 panel row stays `runtime_confirmed` with
`routing_allowed=false`/`submission_ready=false`.
