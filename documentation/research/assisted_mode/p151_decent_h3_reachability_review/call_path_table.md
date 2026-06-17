# P151 — Gate 1: Call-Path Table (every production caller of `collectFees`)

`UTBFeeCollector.collectFees` is `onlyUtb` (`UTBFeeCollector.sol:36`). The **only** production caller is the UTB
router's `retrieveAndCollectFees` modifier, which forwards its `packedInfo` argument to `collectFees`
(`UTB.sol:248`). The modifier (`UTB.sol:228-251`) is used at exactly two entrypoints; `receiveFromBridge`
(`UTB.sol:311-319`) does not collect fees.

| caller (entrypoint) | file:line | who can trigger | origin of `fees` | origin of `packedInfo` | `fees`/`packedInfo` same bytes? | user supply one while sig covers other? | recompute/validate fees? |
|---|---|---|---|---|---|---|---|
| `swapAndExecute` | `UTB.sol:108-115` | anyone (public) | user calldata | **router-built** `abi.encode(instructions, fees)` | **yes** (embeds `fees`) | **no** (no user packedInfo param) | bound by construction |
| `bridgeAndExecute` | `UTB.sol:259-266` | anyone (public) | user calldata | **router-built** `abi.encode(instructions, fees)` | **yes** (embeds `fees`) | **no** | bound by construction |
| `receiveFromBridge` | `UTB.sol:311-319` | anyone (public) | — (no fee collection) | — | n/a | n/a | n/a |
| direct `collectFees` | `UTBFeeCollector.sol:36` | **onlyUtb** | caller-supplied | caller-supplied | independent | **yes — but only the privileged UTB can call** | no |

## Conclusion
There is **no public entrypoint that accepts a user-supplied `packedInfo`**. The router derives `packedInfo` from
the user's `fees`, so executed `fees` ≡ a member of the signed `packedInfo`. The only actor that could pass a
`packedInfo` not containing the executed `fees` is the privileged UTB itself (a direct `onlyUtb` call). ⇒
fee-mismatch is **trusted-router-only / not externally reachable**.
