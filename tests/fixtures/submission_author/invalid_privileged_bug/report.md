# Owner can set the swap fee to 100% and capture all output

Severity: High

## Root Cause
Treasury.setFeeBps() allows the owner to set feeBps up to 10000 (100%). The
function is onlyOwner, so only the trusted owner role can call it.

## Impact
Theft of all swap output (fund loss) when the owner sets the fee to 100%.

## Entry Point
Treasury.setFeeBps(uint256) — onlyOwner; only the trusted owner can call it.

## Attack Path
- The owner calls setFeeBps(10000)
- A user swaps; 100% of the output is routed to the owner

## Affected Contracts
- contracts/Treasury.sol

## Affected Functions
- Treasury.setFeeBps(uint256)
- Treasury.swap()

## Code References
- contracts/Treasury.sol:54-61

## State Before
feeBps = 30

## State After
feeBps = 10000

## Asset Delta
Up to 100% of a user's swap output redirected to the owner.

## Reproduction
- forge test --match-test test_owner_max_fee -vvv
- As owner, call setFeeBps(10000), then assert a user swap routes all output to the owner
