# Reentrancy in Vault.withdraw drains the WETH backing

Severity: High

## Root Cause
Vault.withdraw() sends ETH via a low-level call before decrementing the caller's
balance, allowing a malicious receiver to re-enter.

## Impact
Theft of vault funds (fund loss / drain).

## Entry Point
Vault.withdraw(uint256) from an attacker contract with a receive() hook.

## Preconditions
- One legitimate deposit to seed the attacker balance

## Attack Path
- The attacker calls withdraw()
- receive() re-enters withdraw() before the balance update
- The vault is drained beyond the attacker's recorded deposit

## Affected Contracts
- contracts/Vault.sol

## Affected Functions
- Vault.withdraw(uint256)

## Code References
- contracts/Vault.sol:138-150

## State Before
vault ETH balance = 1000e18

## State After
vault ETH balance = 800e18

## Asset Delta
Net +100e18 stolen against a recorded 100e18 deposit.

## Reproduction
- forge test --match-test test_reentrancy_drain -vvv
