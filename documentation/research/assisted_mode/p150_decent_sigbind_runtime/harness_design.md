# P150 — Harness Design

**harness_type: real_contract** — the real `UTBFeeCollector` is deployed; its real `collectFees`/`setUtb`/
`setSigner` are called.

Location: `audits/decent-2024-01-holdout/pocs/p150/` (Foundry, local to the holdout). solc 0.8.21, evm paris;
remaps `dc/` → real decent `src/`, `solmate/` → cloned solmate, `forge-std/`; `allow_paths` for the decent tree;
`lib/forge-std` + `lib/solmate` cloned then removed post-run.

## Contracts in the test
- **`UTBFeeCollector` (REAL, `dc/UTBFeeCollector.sol`)** — subject; unmodified production source (via `UTBOwned` →
  `solmate/Owned`).
- **`MockERC20`** — fee token (`transferFrom`/`transfer`/`balanceOf`/`approve`/`allowance`).
- **`CorrectedFeeCollector`** (control) — the real `collectFees` body with **one** added check:
  `require(keccak256(packedInfo) == keccak256(abi.encode(fees)))` (binds the executed `fees` to the signed
  `packedInfo`).
- Actors: `signer = vm.addr(0xA11CE)`, `utb = 0x07B` (the privileged `onlyUtb` caller).

## Signature
`digest = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", keccak256(packedInfo)))`,
`(v,r,s) = vm.sign(signerPk, digest)`, `signature = abi.encodePacked(r, s, v)` (matches `splitSignature`'s
`r=mload(+32), s=mload(+64), v=byte(0,mload(+96))`).

## Tests
1. `test_executed_fee_not_bound_to_signed_packedinfo` — sign `packedInfo = abi.encode(fees(SMALL=1e18))`; call
   `collectFees(fees(LARGE=1000e18), packedInfo, sig)` as `utb` → succeeds; collector holds LARGE; `utb` debited
   LARGE (signer only authorized SMALL).
2. `test_corrected_reference_binds_fees` — corrected reverts (`fees-not-bound-to-signature`).
3. `test_control_matched_fees` — `feesExecuted == feesAuthorized` → real and corrected both charge SMALL.

No production contract edited; all mocks/control live in the test.

## Why real-contract was achievable
`UTBFeeCollector` has only three light deps (`solmate/Owned`, `forge-std/IERC20`, `FeeStructure`); no oracle, RPC,
or bridge infra is needed to exercise `collectFees`. The signature path executes unmodified; only the ERC20 + a
corrected reference + a control are added.
