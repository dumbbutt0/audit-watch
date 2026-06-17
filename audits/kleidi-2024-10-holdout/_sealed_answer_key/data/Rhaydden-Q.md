# QA for Kleidi

| Issue ID | Description |
| -------- | ----------- |
| [QA-01](#qa-01-potential-transaction-revert-in-timelocksolcleanup-due-to-the-assert-being-used) | Potential transaction revert in `Timelock.sol::Cleanup` due to the `assert` being used |
| [QA-02](#qa-02-misleading-comment-in-isoperationexpired-function-could-cause-incorrect-implementation) | Misleading comment in `isOperationExpired` function could cause incorrect implementation |
| [QA-03](#qa-03-recovery-spells-is-excluded-from-safe-proxy-address-calculation) | Recovery spells is excluded from safe proxy address calculation |
| [QA-04](#qa-04-wildcard-and-specific-checks-coexistence) | Wildcard and specific checks coexistence |
| [QA-05](#qa-05-the-arrays-could-underflow-in-removecalldatacheckdatahash-function) | The arrays could underflow in `removeCalldataCheckDatahash` function |
| [QA-06](#qa-06-inefficient-and-redundant-data-removal-in-_removeallcalldatachecks) | Inefficient and redundant data removal in `_removeAllCalldataChecks` |
| [QA-07](#qa-07-no-way-to-manually-unpause-the-contract-before-pauseduration-elapses) | No way to manually unpause the contract before `pauseDuration` elapses |

## [QA-01] Potential transaction revert in `Timelock.sol::Cleanup` due to the `assert` being used


https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L674-L680
```solidity
function cleanup(bytes32 id) external whenNotPaused {
    require(isOperationExpired(id), "Timelock: operation not expired");
    /// unreachable state assert statement
    assert(_liveProposals.remove(id));

    emit Cleanup(id);
}
```

The problem heres in the assertion `assert(_liveProposals.remove(id))`. Contrary to the [comment](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L676), this state is not "unreachable" and could cause the transaction to revert unnecessarily. Here's why:

1. The [`isOperationExpired` function](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L405-L415) only checks if the operation has expired based on its timestamp. It doesn't verify if the operation is still in the `_liveProposals` set:

```solidity
function isOperationExpired(bytes32 id) public view returns (bool) {
    uint256 timestamp = timestamps[id];
    require(timestamp != 0, "Timelock: operation non-existent");
    require(timestamp != 1, "Timelock: operation already executed");
    return block.timestamp >= timestamp + expirationPeriod;
}
```

2. It's possible for an operation to be expired (based on its timestamp) but already removed from the `_liveProposals` set. This could happen if:
   - The operation was executed after its expiration but before cleanup.
   - The operation was cancelled after its expiration but before cleanup.

3. In such cases, `isOperationExpired(id)` would return true, passing the require check, but `_liveProposals.remove(id)` would return false, causing the assert to fail and the transaction to revert.

Using `assert` this way could lead to unnecessary transaction reversions and gas wastagge.

### Recommendations

Consider replacing the assert statement with a require statement cos it'll allow the function to complete successfully even if the proposal has already been removed from `_liveProposals`, while still ensuring that only expired operations can be cleaned up. Something like this:

```diff
function cleanup(bytes32 id) external whenNotPaused {
    require(isOperationExpired(id), "Timelock: operation not expired");
-    assert(_liveProposals.remove(id));
+    require(_liveProposals.remove(id), "Timelock: operation not in live proposals");

    emit Cleanup(id);
}
```


## [QA-02] Misleading comment in `isOperationExpired` function could cause incorrect implementation

The misleading comment in the `isOperationExpired` function gives a false info which could cause the function to be modified incorrectly resulting in a narrow expiration window that could cause operations to be incorrectly classified as unexpired when they should be considered expired. This could potentially allow expired operations to be executed when they shouldn't be.


https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L403-L416

```solidity
/// @dev Returns whether an operation is expired
/// @notice operations expire on their expiry timestamp, not after
function isOperationExpired(bytes32 id) public view returns (bool) {
    uint256 timestamp = timestamps[id];

    require(timestamp != 0, "Timelock: operation non-existent");
    require(timestamp != 1, "Timelock: operation already executed");

    return block.timestamp >= timestamp + expirationPeriod;
}
```

The comment suggests that operations expire exactly on their expiry timestamp and not after. However, the actual implementation correctly considers an operation expired if the current time is greater than or equal to the expiration time.
 
If we were to tweak this function to match the comment, we could change it to:

```solidity
return block.timestamp == timestamp + expirationPeriod;
```

This would create a problem where:
1. Operations are only considered expired for a single block.
2. Operations could be executed after their intended expiration time if that exact block is missed.
3. The function would not accurately reflect whether an operation should be considered expired for practical purposes.

### Recommended Mitigation Steps
Consider updating the comment to accurately reflect the intended behavior of the function. The comment should indicate that operations are considered expired starting from their expiry timestamp and remain expired thereafter. 



## [QA-03] Recovery spells is excluded from safe proxy address calculation

`calculateAddressUnsafe` function in the `AddressCalculation` contract does not include `recoverySpells` in the salt calculation for the Safe proxy address. This could lead to address collisions for instances with different recovery spells but identical in all other aspects. As a result, two distinct wallet instances might end up with the same Safe proxy address, 

>Although, the protocol hinted and I quote: "only use this if you know what you are doing and are an advanced user" and the function is meant to calculate address without safety checks, we included this in QA

### Proof of Concept
Take a look at the `calculateAddressUnsafe` function: 

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/views/AddressCalculation.sol#L62-L103

```solidity
function calculateAddressUnsafe(NewInstance memory instance)
    public
    view
    returns (SystemInstance memory walletInstance)
{
    // ... SNIP

    uint256 creationSalt = uint256(
        keccak256(
            abi.encode(
                instance.owners,
                instance.threshold,
                instance.timelockParams.minDelay,
                instance.timelockParams.expirationPeriod,
                instance.timelockParams.pauser,
                instance.timelockParams.pauseDuration,
                instance.timelockParams.hotSigners
            )
        )
    );

    // ... SNIP
}
```

The `creationSalt` calculation includes various parameters from the `instance` struct, but it doesnt `instance.recoverySpells`. This means that two `NewInstance` structs with different `recoverySpells` but identical in all other aspects would generate the same `creationSalt`, and consequently, the same Safe proxy address.

This salt is [then used to calculate the final salt](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/views/AddressCalculation.sol#L109-L111) for the Safe proxy:

```solidity
bytes32 salt = keccak256(
    abi.encodePacked(keccak256(safeInitdata), creationSalt)
);
```

As a result, the Safe proxy address calculation doesn't take into account the `recoverySpells`, which should be a distinguishing factor between different instances.

### Recommended Mitigation Steps
Include `instance.recoverySpells` in the `creationSalt` calculation to ensure that different recovery spells result in different Safe proxy addresses.

```diff
function calculateAddressUnsafe(NewInstance memory instance)
    public
    view
    returns (SystemInstance memory walletInstance)
{
    // ... SNIP

    uint256 creationSalt = uint256(
        keccak256(
            abi.encode(
                instance.owners,
                instance.threshold,
                instance.timelockParams.minDelay,
                instance.timelockParams.expirationPeriod,
                instance.timelockParams.pauser,
                instance.timelockParams.pauseDuration,
                instance.timelockParams.hotSigners,
+               instance.recoverySpells
            )
        )
    );
```




## [QA-04] Wildcard and specific checks coexistence


`_addCalldataCheck` function allows adding a "wildcard" check (where `startIndex == endIndex == 4`) only if there are no existing checks for that contract address and selector. Albeit, it doesn't prevent adding specific checks after a wildcard has been added. We could end up in a situation where both a wildcard and specific checks exist for the same contract and selector.

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1099-L1117

```solidity
if (startIndex == endIndex) {
    require(
        startIndex == 4,
        "CalldataList: End index equals start index only when 4"
    );
    require(
        listLength == 0,
        "CalldataList: Add wildcard only if no existing check"
    );
    require(data.length == 0, "CalldataList: Data must be empty");
} else {
    require(
        endIndex > startIndex,
        "CalldataList: End index must be greater than start index"
    );
    require(data.length != 0, "CalldataList: Data empty");
}
```

The issue here's that while this function prevents adding a wildcard when specific checks exist, it doesn't prevent the opposite scenario. This means we could add a wildcard check first, and then later add specific checks for the same contract and selector.

This is confusing as it's not clear which check should take precedence - the wildcard or the specific checks.


### Recommendations
Consider adding a check at the beginning of the function to ensure that if a wildcard check exists, no new checks (wildcard or specific) can be added for that contract and selector. Something like this:

```solidity
Index[] storage calldataChecks = _calldataList[contractAddress][selector];
require(
    calldataChecks.length == 0 || calldataChecks[0].startIndex != calldataChecks[0].endIndex,
    "CalldataList: Cannot add check when wildcard exists"
);
```




## [QA-05] The arrays could underflow in `removeCalldataCheckDatahash` function


`removeCalldataCheckDatahash` function handles the case where all data hashes for a particular index check are removed. 

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L924-L941

```solidity
if (indexCheck.dataHashes.length() == 0) {
    /// index check to overwrite the specified index check with
    Index storage lastIndexCheck = calldataChecks[
        calldataChecks.length - 1
    ];

    indexCheck.startIndex = lastIndexCheck.startIndex;
    indexCheck.endIndex = lastIndexCheck.endIndex;
    bytes32[] memory dataHashes = lastIndexCheck.dataHashes.values();

    for (uint256 i = 0; i < dataHashes.length; i++) {
        assert(indexCheck.dataHashes.add(dataHashes[i]));
        assert(lastIndexCheck.dataHashes.remove(dataHashes[i]));
    }

    /// remove the last index check for the specified function
    calldataChecks.pop();
}
```

The issue is that the function attempts to replace the empty index check with the last index check in the array, but it doesn't handle the case where the empty index check is the last one in the array. 

If the empty index check is the last one in the array, it will try to copy data from itself to itself, which is I dont think is necessary. More critically, it will always attempt to remove the last element with `calldataChecks.pop()`, even if there's only one element left. This could lead to an underflow if the array becomes empty.


### Recommendation 
The function should probably check if the index being removed is the last one in the array. If it is, it should simply remove it without trying to copy data from the "last" element. 




## [QA-06] Inefficient and redundant data removal in `_removeAllCalldataChecks`


Take a look at `_removeAllCalldataChecks` function especially in the loop that removes the calldata checks.
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1297-L1322

```solidity
while (checksLength != 0) {
    Index storage removedCalldataCheck = calldataChecks[
        checksLength - 1
    ];

    bytes32[] memory dataHashes = removedCalldataCheck
        .dataHashes
        .values();

    emit CalldataRemoved(
        contractAddress,
        selector,
        removedCalldataCheck.startIndex,
        removedCalldataCheck.endIndex,
        dataHashes
    );
    for (uint256 i = 0; i < dataHashes.length; i++) {
        assert(removedCalldataCheck.dataHashes.remove(dataHashes[i]));
    }
    calldataChecks.pop();
    checksLength--;
}
    /// delete the calldata list for the given contract and selector
        delete _calldataList[contractAddress][selector];
    }
```

We see the function is unnecessarily removing individual data hashes from the `removedCalldataCheck.dataHashes` set before popping the entire `Index` struct from the `calldataChecks` array. This is wasteful in terms of gas consumption and doesn't provide any benefit, as the entire `Index` struct is being removed anyway.

Removing each data hash individually is an expensive operation, especially if there are many hashes.

### Recommendation
A more efficient and cleaner approach would be to simply emit the event and then pop the `Index` struct from the array without even bothering to remove individual data hashes. The storage slot for that `Index` struct will be cleared when it's popped from the array anyway.

Something like this:

```solidity
function _removeAllCalldataChecks(
    address contractAddress,
    bytes4 selector
) private {
    Index[] storage calldataChecks = _calldataList[contractAddress][selector];

    uint256 checksLength = calldataChecks.length;

    require(checksLength > 0, "CalldataList: No calldata checks to remove");

    while (checksLength != 0) {
        Index storage removedCalldataCheck = calldataChecks[checksLength - 1];

        emit CalldataRemoved(
            contractAddress,
            selector,
            removedCalldataCheck.startIndex,
            removedCalldataCheck.endIndex,
            removedCalldataCheck.dataHashes.values()
        );

        calldataChecks.pop();
        checksLength--;
    }

    delete _calldataList[contractAddress][selector];
}
```






## [QA-07] No way to manually unpause the contract before `pauseDuration` elapses


The `ConfigurablePause` contract allows pausing by setting the `pauseStartTime` to the current block timestamp and removing the `pauseGuardian`. The contract remains paused until the current block timestamp exceeds `pauseStartTime + pauseDuration`. However, there is no way to manually unpause the contract before the `pauseDuration` elapses, which can lead to extended downtime.

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L78-L98
```solidity
function pause() public virtual whenNotPaused {
    require(
        msg.sender == pauseGuardian,
        "ConfigurablePauseGuardian: only pause guardian"
    );

    _setPauseTime(uint128(block.timestamp));

    address previousPauseGuardian = pauseGuardian;
    pauseGuardian = address(0);

    emit PauseGuardianUpdated(previousPauseGuardian, address(0));
    emit Paused(msg.sender);
}

function paused() public view returns (bool) {
    return block.timestamp <= pauseStartTime + pauseDuration;
}
```

Here, once the `pause()` function is called, the contract remains paused for the entire `pauseDuration` without any way to manually unpause it.

If the `pauseDuration` is set to a very long duration (e.g., close to `MAX_PAUSE_DURATION`), the contract will remain paused for that entire duration without any way to unpause it manually.


### Recommendation

Consider introducing a manual unpause function that allows a specific role (e.g., the contract owner) to reset the `pauseStartTime` to zero, effectively unpausing the contract. 

