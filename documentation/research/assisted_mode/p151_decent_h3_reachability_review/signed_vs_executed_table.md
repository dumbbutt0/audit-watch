# P151 — Gate 2: Signed-vs-Executed Field Table

Signed digest (`UTBFeeCollector.sol:46-47` over `packedInfo`, with `packedInfo = abi.encode(instructions, fees)`
built by the router at `UTB.sol:115/266`):
`keccak256("\x19Ethereum Signed Message:\n32", keccak256(abi.encode(instructions, fees)))`.

| field | signed? | executed by collectFees? | notes |
|---|---|---|---|
| `fees.feeToken` | **yes** (inside `fees` in `packedInfo`) | yes (`transferFrom(utb, this, fees.feeAmount)` of `fees.feeToken`) | bound via router |
| `fees.feeAmount` | **yes** | yes | bound via router |
| `fees.bridgeFee` | **yes** | used by `bridgeAndExecute` (`fees.bridgeFee`) | bound via router |
| `instructions` (swap/bridge payload) | **yes** | drives the swap/bridge | bound via router |
| nonce | **no** | n/a | → replay (side finding) |
| `chainid` / domain | **no** | n/a | → cross-chain replay (side finding) |
| FeeCollector / UTB contract address | **no** | n/a | → cross-deployment replay (side finding) |
| deadline | **no** | n/a | → unbounded validity (side finding) |
| payer (`msg.sender`) | **no** | the `utb`/`msg.sender` pays | not part of the fee-binding question |

## Reading
The executed fee fields (`feeToken`, `feeAmount`) **are** signed (via `fees` ⊂ `packedInfo`), so the P150
"signature not bound to executed fee" mismatch does **not** manifest through the router. The genuinely-unsigned
fields are replay/domain-binding metadata — a **separate** issue (see replay_side_finding.md), not an amplifier of
the (already-bound) fee.
