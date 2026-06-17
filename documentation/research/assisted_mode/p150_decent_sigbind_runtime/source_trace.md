# P150 — Source Trace

File: `audits/decent-2024-01-holdout/contracts/src/UTBFeeCollector.sol` (solc ^0.8.0, 80 lines).

## The signature check vs the executed transfer
```solidity
function collectFees(FeeStructure calldata fees, bytes memory packedInfo, bytes memory signature)
    public payable onlyUtb
{
    bytes32 constructedHash = keccak256(abi.encodePacked(BANNER, keccak256(packedInfo)));   // signs packedInfo
    (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
    address recovered = ecrecover(constructedHash, v, r, s);
    require(recovered == signer, "Wrong signature");                                        // signer over packedInfo
    if (fees.feeToken != address(0)) {
        IERC20(fees.feeToken).transferFrom(utb, address(this), fees.feeAmount);             // executes `fees` (UNBOUND)
    }
}
```
- `signer` is set by `setSigner` (`onlyOwner`); `utb` by `setUtb` (`onlyOwner`); `collectFees` is `onlyUtb`.
- **`fees` is never compared to `packedInfo`.** The signature proves only that `signer` signed *some* `packedInfo`;
  it places **no constraint** on `fees.feeToken` / `fees.feeAmount`, which drive the actual transfer. NatSpec says
  the signature is "to verify the fee structure," but the code does not bind it.

## Subject mismatch
- `validated/signed subject`: `packedInfo` (hashed + ecrecover'd against `signer`).
- `executed subject`: `fees` (the struct used for `transferFrom`).
- `divergence_point`: the `transferFrom(utb, this, fees.feeAmount)` uses `fees`, which is unauthenticated relative
  to the signed `packedInfo`.

## Secondary observations (noted, not the primary axis)
- No nonce / no `chainid` / no contract-address binding in the signed message → replay potential (cross-call /
  cross-chain). Recorded for human review; the PoC targets the binding-failure axis.

## Reaching it in a test
Deploy real `UTBFeeCollector`; `setUtb`, `setSigner(vm.addr(pk))`; a mock ERC20 funded to `utb` + approved; sign
`packedInfo = abi.encode(feesAuthorized)` and call `collectFees(feesExecuted, packedInfo, sig)` as `utb` with
`feesExecuted != feesAuthorized`. Deps: `solmate/Owned` (via `UTBOwned`), `forge-std/IERC20`, `FeeStructure`
(`CommonTypes.sol`).
