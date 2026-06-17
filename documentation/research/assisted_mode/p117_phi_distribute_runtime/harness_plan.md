# P117 — Harness plan

**Classification: HARNESS_MODERATE.** phi ships a full Foundry env (lib/forge-std, solady, OZ-upgradeable;
remappings; solc 0.8.25; evm paris). No fork needed. The existing test suite needs `@prb/test` from a missing
`node_modules`, so the harness is built in a SEPARATE project that references phi's `src` + `lib` (avoiding the
broken PRBTest tests) and uses `forge-std/Test`.

## Required contracts
- REAL `CuratorRewardsDistributor` (the function under test), compiled from phi `src` via remapping `phi/=.../src/`.
- `MockCred` — minimal, selector-compatible: `isExist(uint256)→true`, `getShareNumber(uint256,address)→1`,
  `getCuratorAddresses(uint256,uint256,uint256)→ N addresses` (N settable). (Distributor casts `ICred(addr)`; a
  selector-compatible mock suffices.) The mock is intentionally CHEAP (no per-curator storage reads), so measured
  gas is a CONSERVATIVE LOWER BOUND on the real Cred (which does `EnumerableMap.at` + `isShareHolder` per element).
- `MockPhiRewards` — `depositBatch(address[],uint256[],bytes4[],string) payable` no-op sink.

## Actors
- deployer/owner (test contract); the "attacker / organic growth" is modelled by the curator count N the mock
  returns (source already establishes N is permissionlessly growable).

## Setup steps
1. deploy MockCred + MockPhiRewards; deploy `CuratorRewardsDistributor(mockPhiRewards, mockCred)`.
2. `deposit{value:1 ether}(credId, 1 ether)` to seed `balanceOf` (re-seed before each measurement; distribute zeroes it).
3. set N on the mock; call `distribute(credId)`; measure gas via `gasleft()` deltas.
4. also call `distribute` under a 30M gas cap at large N to demonstrate un-includability (revert).

## Missing dependencies
None — phi's lib provides forge-std/solady/OZ. (Project-level `@prb/test` from node_modules is avoided by the
standalone harness; the real distributor + its imports compile.)

## Project location
`/tmp/p117-phi-harness/` (foundry.toml + remappings.txt + test/CuratorDistributeDoS.t.sol). phi `src/` is unmutated.
