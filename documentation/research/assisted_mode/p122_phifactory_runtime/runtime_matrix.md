# P122 — Runtime matrix

Command: `forge test --use 0.8.25 --match-contract PhiFactoryClaimRuntime -vvv`
Project: `/tmp/p122-phifactory-harness` (standalone; phi `PhiFactory.sol` unmutated via remapping; solady + OZ-upgradeable from phi lib).
Art config: `verificationType=SIGNATURE`, `mintFee=1e15`, `mintProtocolFee=1e14`, `maxSupply=5`. `getArtMintFee(1,1) = 1.1e15`.

| Case | Scenario (attacker = permissionless caller) | Result | Evidence |
|---|---|---|---|
| **A** | claim payload with an INVALID signer signature (wrong key) | **PASS** | reverts (`AddressNotSigned`) — minter cannot be claimed-for without a valid `phiSignerAddress` signature |
| **B** | valid signed claim, `msg.value == mintFee` | **PASS** | `claimFromFactory` called once; `protocolFeeDest += 1e14`; `artAddr += 1e15`; `factory.balance == 0` (no excess) |
| **C** | valid signed claim, `msg.value == fee + 0.5e18` (overpay) | **PASS** | `factory.balance == 0.5e18` — **excess STUCK** (no refund on the wrapper path); caller lost `fee + 0.5e18` |
| **D** | underpay (`msg.value == 0`) | **PASS** | D1 empty factory balance → **reverts** (can't fund inner `{value: mintFee}`); D2 factory pre-funded 1e18 → claim **succeeds**, `factory.balance` drops by exactly `fee` — **mintFee drawn from standing balance** |
| **E** | mint 5 (== maxSupply) then a 6th | **PASS** | the 6th reverts (`OverMaxAllowedToMint`) — cap enforced |

All 5 tests pass (executed). Full log: `execution_output.txt`.

## Reading
- **A / E** the high-impact guards hold: the signer-signature entitlement cannot be forged (no minter spoof / no
  unauthorized mint) and the supply cap is enforced. The trusted `phiSignerAddress` gates who can mint.
- **B** the normal flow with exact payment is clean (correct fee split, no excess).
- **C / D** confirm the **fee-binding gap** at runtime: the `claim` wrapper forwards a computed `mintFee` (not
  `msg.value`), so overpayment is stuck (no refund — inconsistent with the direct `signatureClaim`/`merkleClaim`
  refund) and underpayment is subsidized by the contract's standing balance. This is real but bounded/conditional:
  it requires standing funds (themselves from a prior overpayer) and a VALID signer entitlement; the mintFee still
  flows to the protocol/art. It is not an unconditional fund-theft and not an unauthorized mint.
