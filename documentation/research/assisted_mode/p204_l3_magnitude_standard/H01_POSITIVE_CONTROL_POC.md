# P204 — H-01 positive-control PoC

Harness: `pocs/test/H01_setRouter.t.sol` (real `DcntEth.sol`; only the external `OFTV2` base mocked). Run log:
`pocs/run_log.txt`.

## Setup (source-valid)
- `DcntEth` deployed by a legitimate `deployer` (becomes owner via the OFTV2 base).
- A legitimate router is set by the deployer (honest config).
- `attacker` = unprivileged EOA: NOT owner, NOT router (asserted as preconditions).

## Exploit tx sequence (permissionless)
1. `attacker` calls `setRouter(attacker)` — **public, no access modifier** → attacker becomes `router`.
2. `attacker` calls `mint(attacker, 1_000_000 ether)` — `onlyRouter` now passes → arbitrary unbacked mint.

## Measured realized impact
- `balanceOf(attacker)` increased by exactly `1,000,000 ether`; `totalSupply` inflated by the same (unbacked).
- **PASS** `test_H01_permissionless_arbitrary_mint`.
- Control: `test_H01_control_mint_blocked_without_hijack` — `mint` reverts for a non-router, proving the public
  `setRouter` hijack is the required (and source-valid) lever.

## L3 verdict: **HIGH_CONFIRMED**
All L3 conditions met by an executed tx: attacker-controlled entry · executable · source-valid config · concrete
asset (DcntEth supply/balance) · material+scalable magnitude (arbitrary amount) · unauthorized privileged-value
control · no trusted prerequisite · no hypothetical custody (the value created is the token supply itself, controlled
inside the contract under trace). H-01 is a genuine High and L3 confirms it.
