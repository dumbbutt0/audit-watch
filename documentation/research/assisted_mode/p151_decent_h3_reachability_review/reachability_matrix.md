# P151 — Gate 4: Reachability Matrix

| actor | can cause executed `fees` ≠ signed subject (fee-mismatch)? | can cause replay/domain reuse? |
|---|---|---|
| unprivileged external attacker | **NO** — `swapAndExecute`/`bridgeAndExecute` build `packedInfo` from the user's own `fees`; no entrypoint accepts an independent `packedInfo` | possibly (a signer-issued blob lacks nonce/chainid/contract/deadline) — **separate** axis |
| user (the payer / `msg.sender`) | NO — same as above; the user can only supply `fees`, which is what gets signed-over and executed | possibly (replay of own/obtained signature) |
| trusted UTB router (the `onlyUtb` caller) | only the privileged UTB could pass a mismatched `packedInfo` via a direct `collectFees` call | n/a |
| signer (backend) | issues signatures over `(instructions, fees)` | issues replayable blobs (no nonce/chainid/contract/deadline) |
| owner | sets `utb`/`signer`/`feeCollector` (config) | — |

## Verdict
- **Fee-binding mismatch (P150 mechanism): UNREACHABLE by unprivileged/user actors** → `trusted_router_only`.
- **Replay/domain weakness: user-influenced but a distinct issue** (does not amplify the bound fee).

The confirmed mechanism therefore does **not** convert into attacker-driven user/protocol loss under intended
operation. It is a **defense-in-depth gap** (collectFees ideally should re-bind `fees` regardless of caller) plus a
**separate replay concern** — both for human review, neither submission-ready.
