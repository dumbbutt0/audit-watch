# Allbridge Core (EVM) — audit findings (HackenProof)

Date: 2026-06-13 · Real hunt, local/fork-only, **nothing submitted**, no finding manufactured.
Repo: `allbridge-io/allbridge-core-evm-contracts` (HEAD `8f91165`; Hardhat solc 0.8.20 / Foundry 0.8.18).
Scope = deployed Allbridge Core EVM contracts. Focus = fund loss / unauthorized-tx / price-balance manipulation
/ rounding / replay / signature malleability / composability. **OOS:** anything requiring privileged addresses
(owner / stopAuthority / validator keys), incorrect 3rd-party oracle data, self-exploits, leaked keys.

## VERDICT: HONEST NEGATIVE — no permissionless fund-loss bug found in the EVM contracts.

Mature, post-incident-hardened protocol (Hacken-audited; relaunched after the Apr-2023 flash-loan hack with
`validateBalanceRatio` + invariant tests). Independent conservation fuzzing and a full consensus/replay trace
hold. EVM is the audited surface (non-EVM chains — Solana/Tron/Stellar/Sui/Algorand/Stacks — are out of the
Solidity toolkit).

## Deployed-version pin
- Core (Pool/Bridge/Messenger/Router/RewardManager) is unchanged since "Pre-release" + a zero-address fix; HEAD's
  "Feature/x reserve #27" only **adds** `XReserveBridge` — which has **no deployed address** in the bounty list →
  not live → out of scope.
- Live Ethereum USDC Pool `0xa7062bbA…57C4d` read on-fork: `a=20, decimals=3, feeShareBP=15, balanceRatioMinBP=
  1000 (10%), adminFeeShareBP=2000`, all source functions present → **deployed Pool == repo source**. Etherscan
  keyless API is blocked, but the live-ABI/param match + stable git history pin the version.

## Pool — custom cubic-invariant AMM (highest-EV; the 2023 exploit's locus) → SOUND
Invariant `4AD−D = 4A(x+y) − D³/4xy`; `SYSTEM_PRECISION=3`; `reserves` = real-token backing (SP); LP = ΔD; withdraw
pays par (`_fromSystemPrecision(amountLp)`, capped by reserves); `getY` `+1` offset and floor `_sqrt`/`_cbrt` round
**toward the pool**. Conservation fuzzed two ways with the **balance guard disabled (`balanceRatioMinBP=0`) and
zero fee** — the hardest setting and the exact LP-and-swapper attack shape of the 2023 hack:
- Repo's own `test/foundry/BasicInvariants.t.sol` (18-dec): **3 invariants × 200,000 calls, 0 failures**.
- New `test/foundry/Pool6DecConservation.t.sol` (6-dec, real USDC/USDT config, coarsest SP truncation):
  **3 invariants × 200,000 calls, 0 failures**.
- Invariants held: (1) `reserves ≤ real token balance` (solvency); (2) `totalSupply(LP) ≤ d (+≤2 dust)`;
  (3) a combined LP+swapper (`alice`) can never end with more raw tokens than they started (no extraction).
- Manual: every rounding site (`getY +1`, floor sqrt/cbrt, `_toSystemPrecision` truncation→dust folded into fee,
  proportional deposit split, par withdraw) favors the pool. `getPrice` is view-only (not used in settlement).
  The 2023 root cause (LP+swap price manipulation) is mitigated by `validateBalanceRatio`; the fuzz shows the math
  is conservative **even without** that guard.

## Bridge + Messenger — consensus / replay / hashing → SOUND
- **Binding traced end-to-end**: source `Messenger.sendMessage` stores `messageWithSender =
  hashWithSenderAddress(message, BridgeSrc)`; validators sign that; dest `Messenger.receiveMessage` stores
  `receivedMessages[messageWithSender]`; dest `Bridge.receiveTokens` recomputes `hashMessage(...,destChainId=this)
  .hashWithSender(otherBridges[src])` and checks both `processedMessages` (0→1) and `hasReceivedMessage`. The two
  hashings coincide because `otherBridges[src] == bytes32(uint160(sourceBridge))`. No path verifies a message the
  validators didn't attest for the specific (source-bridge, dest-chain, token, amount, nonce).
- **hashMessage / replaceChainBytes**: dst is a 1-byte overlay not in the keccak preimage, but `receiveTokens`
  fixes `destinationChainId = chainId` (immutable) and dest `Messenger` checks `message[1]==chainId`, so a relayer
  can't redirect; Allbridge chain-ids are small (≤255) so no uint8 aliasing. `receiveToken`/`recipient`/`nonce`
  are all in the preimage → no cross-token/cross-amount collision.
- **Signature malleability** (explicitly in-scope): `ecrecover` has no `s<n/2` guard, but the replay maps are keyed
  by the **message**, not the signature — a malleated signature marks the *same* message received; forging a *new*
  message needs the validator key (privileged, OOS). `ecrecover→address(0)` fails (validators are nonzero). Benign.
- **Receive flow**: the extra-gas `recipient.call{value:msg.value}` runs **after** `processedMessages` is set and
  the swap completes; re-entering hits the replay guard (same message) or requires a separately-attested message →
  no reentrancy benefit. `receiveAmountMin` enforces slippage. `MessengerGateway.hasReceivedMessage` **reverts**
  ("Not implemented") for any protocol other than Allbridge/Wormhole → no bogus-enum bypass.
- **RewardManager**: standard non-transferable-LP MasterChef accumulator (`accRewardPerShareP`, `P=52`); LP
  `_transfer`/`_approve` revert → no reward-debt transfer games; admin-fee split conserves.

## Composability adapters (CCTP v1/v2, OFT) → SOUND thin wrappers
- `CctpBridge`/`CctpV2Bridge.receiveTokens` delegate minting to Circle's `cctpTransmitter.receiveMessage(message,
  signature)`; tokens mint to the recipient **encoded in Circle's attested burn message**, not chosen by the
  caller. The `recipient` arg only forwards the caller's own `msg.value` extra gas → no fund redirection.
  `changeRecipient` is gated to the original `senders[nonce]`.
- `OftBridge` has only the send side + admin config; cross-chain delivery/mint is the LayerZero OFT token's
  `lzReceive` (DVN-attested). Security delegated to LZ.
- Trust in Circle/LZ attestation = 3rd-party (OOS for "incorrect data supplied by third party oracles"); the
  Allbridge binding logic around it is correct.

## Out-of-scope confirmed (not reported)
GasOracle owner-set prices; owner/stopAuthority/rebalancer/validator-key powers; 3rd-party attestation trust.

## External audits (disclosed issues non-payable; nothing to exclude — no finding)
Hacken (Sept 2021 score 10; Feb 2022 score 9.8) + post-incident review (PeckShield/Hacken/HAPI). The Apr-2023
flash-loan hack ($570–650K, LP+swapper price manipulation) was fixed in the relaunch — current code is hardened
and independently fuzz-confirmed conservative here.

## Bottom line
The deployed Allbridge Core EVM stack is conservation-sound (Pool fuzzed 18-dec + 6-dec, 200k calls each, 0 fails,
guard off), the bridge consensus/replay binding holds end-to-end, signature malleability is benign, and the
CCTP/OFT adapters correctly delegate to Circle/LayerZero. No permissionless soundness/fund-loss bug.
Correct outcome = **honest negative**, not submitted.
Evidence: `test/foundry/BasicInvariants.t.sol` (repo, 18-dec), `test/foundry/Pool6DecConservation.t.sol` (added, 6-dec).
