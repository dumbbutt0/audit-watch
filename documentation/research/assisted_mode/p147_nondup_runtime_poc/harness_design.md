# P147 — Harness Design

**harness_type: real_contract** — the real `UserEscrow` is deployed and its real `transferIn`/`transferOut` are
called.

Location: `audits/centrifuge-2023-09-holdout/pocs/p147/` (Foundry, local to the holdout — constraint 11).
- `foundry.toml` — solc 0.8.21, evm paris; remap `cf/` → the real centrifuge `src/` + `allow_paths`;
  `lib/forge-std` (cloned, removed post-run). **No OZ** — `UserEscrow` imports only local `Auth` + `SafeTransferLib`.
- `test/UserEscrowRecipientProvenance.t.sol`.

## Contracts in the test
- **`UserEscrow` (REAL, `cf/UserEscrow.sol`)** — subject; unmodified production source. Deployer (the test) is a
  ward (constructor `wards[msg.sender]=1`), so the real `auth` setters run.
- **`MockERC20`** — `balanceOf`/`allowance`/`approve`/`transfer`/`transferFrom`; `transferFrom` decrements
  allowance unless it is `type(uint).max` (matching real ERC20s, so the "never reduces max allowance" property is
  faithful).
- **`CorrectedUserEscrow`** (control) — mirrors `transferIn`/`transferOut` with the single fix
  `require(receiver == destination)` (escrow strictly pays the destination it holds funds for).

## Test functions (neutral names — constraint 15)
1. `test_escrow_funds_redirected_to_unrelated_receiver_with_max_allowance` — real escrow pays receiver (≠ destination).
2. `test_corrected_reference_requires_receiver_equals_destination` — corrected reverts.
3. `test_control_receiver_equals_destination_matches` — real escrow pays destination (no divergence).
4. `test_allowance_not_reduced_enables_repeated_redirect` — repeated redirect (allowance never reduced).

## Why real-contract was achievable
`UserEscrow` has no heavyweight base (no OZ); deps are two tiny local utils. The recipient-resolution divergence
executes unmodified; only the ERC20 + a corrected reference + a control are added (test-only). No production
contract edited (constraint 2).
