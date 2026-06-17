# Unbounded loop in Registry.sweep enables a griefing DoS

Severity: Critical

## Root Cause
Registry.sweep() iterates the entire participants array with no pagination.

## Impact
Denial of service / griefing: once participants grows past the block gas limit,
sweep() always reverts.

## Entry Point
Registry.register() is permissionless; an attacker inflates participants until
Registry.sweep() reverts for everyone.

## Preconditions
- Pay gas to register many entries

## Attack Path
- The attacker calls register() many times
- The participants array grows past the block gas limit
- Registry.sweep() reverts on every subsequent call

## Affected Contracts
- contracts/Registry.sol

## Affected Functions
- Registry.sweep()
- Registry.register()

## Code References
- contracts/Registry.sol:80-96

## State Before
participants.length = N (sweep succeeds)

## State After
participants.length = N + K (sweep reverts)

## Asset Delta
No funds are lost or frozen; the sweep maintenance function becomes unavailable.

## Worst Case
sweep() cannot run again until the array is reduced.

## Realistic Case
Requires gas to inflate the array; sweep is a periodic maintenance call, not a
funds path.

## Program Table Mapping
Claimed as Critical "protocol insolvency" — note that no funds are lost or frozen.

## Reproduction
- forge test --match-test test_sweep_gas_dos -vvv
- Register entries until sweep() reverts with out-of-gas
