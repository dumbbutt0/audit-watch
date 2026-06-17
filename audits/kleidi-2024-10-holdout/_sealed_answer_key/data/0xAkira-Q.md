# [Low-01] TYPO 

### Description 
In the `Timelock` contract, there is a typo on [L947](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L947).
```solidity 
function removeAllCalldataChecks(
        address[] memory contractAddresses,
        bytes4[] memory selectors
    ) external onlyTimelock {
        require(
            contractAddresses.length == selectors.length,
            "Timelock: arity mismatch" //@audit typo 
        );
        for (uint256 i = 0; i < contractAddresses.length; i++) {
            _removeAllCalldataChecks(contractAddresses[i], selectors[i]);
        }
    }
```
### Recommendation
Consider solving the typo by changing the `arity` to `length`

# [Low-02] Inconsistency between reality and NatSpec documentation  

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L799-L804
### Description 
 NatSpec's comments imply that the function below can be called by either the address `safe` or the `Timelock` contract. But if we talk about **this** function only, then it can be called **only by safe**, because the `onlySafe` modifier is present. This comment by NatSpec may be misleading.

```solidity 
/// @notice function to revoke the hot signer role from an address
/// can only be called by the timelock or the safe
/// @param deprecatedHotSigner the address of the hot signer to revoke

function revokeHotSigner(address deprecatedHotSigner) external onlySafe {

_revokeRole(HOT_SIGNER_ROLE, deprecatedHotSigner);

}
```

### Recommendation
You should remove the comments in natspec that this function can be called by `timelock` or create a new modifier `onlySafeAndTimelock` to simplify entry
```solidity 
modifier `onlySafeAndTimelock`() {
require(msg.sender == address(this) || msg.sender == safe,
"Timelock: caller is not the timelock and is not the safe"
);
_;
}
```

# [Low-03] Code duplication  

### Description 

There is duplicated code in the [_addCalldataCheck](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1034-L1155) function.
Specifically on the [1058](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1058-L1060)
and on the [1089](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1089-L1090)
Duplicate code, make the code base more difficult to read. They also make it more error-prone, harder to fix, and complicate maintainability and updateability.
### Recommendation
Consider refactoring the code for the above cases. This will lower gas consumption and increase the codebase's overall readability and quality.

# [Low-04] With the expiration period update, the proposals will become expired

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L972-L977
### Description 
Proposals become expired if no one has executed them during the expiration period. After that we will have to delete the proposal, add it again and wait for the delay.  Suppose that the expiration period is set to 5 days, an proposal is added, and we have to wait for the set delay to execute it. If at this moment the `updateExpirationPeriod` function is called and changes the `expirationPeriod` variable to a smaller one than the current period, many proposals will become expired.
```solidity 
function updateExpirationPeriod(uint256 newPeriod) external onlyTimelock {

require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");

emit ExpirationPeriodChange(expirationPeriod, newPeriod);

expirationPeriod = newPeriod;

}
```

#### PoC
copy this code and paste it into the test file `Timelock.t.sol` 

```solidity 
function testEspirationPeriod() public {
bytes memory data = abi.encodeWithSelector(
timelock.updateDelay.selector,
MINIMUM_DELAY
);

bytes32 id = timelock.hashOperation(
address(timelock),
0,
data,
bytes32(0)
);

_schedule({
caller: address(safe),
timelock: address(timelock),
target: address(timelock),
value: 0,
data: abi.encodeWithSelector(
timelock.updateDelay.selector,
MINIMUM_DELAY
),
salt: bytes32(0),
delay: MINIMUM_DELAY
});

assertEq(timelock.expirationPeriod(), 5 days);
assertFalse(timelock.isOperationExpired(id));
vm.warp(block.timestamp + 2 days);
assertFalse(timelock.isOperationExpired(id));
vm.prank(address(timelock));
timelock.updateExpirationPeriod(1 days);
assertTrue(timelock.isOperationExpired(id));
}
```

```bash 
forge test --mt testEspirationPeriod

Ran 1 test for test/unit/Timelock.t.sol:TimelockUnitTest
[PASS] testEspirationPeriod() (gas: 134723)
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 9.33ms (1.47ms CPU time)

Ran 1 test suite in 242.82ms (9.33ms CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)
```
### Recommendation
Consider making a static expirationPeriod for the proposals 