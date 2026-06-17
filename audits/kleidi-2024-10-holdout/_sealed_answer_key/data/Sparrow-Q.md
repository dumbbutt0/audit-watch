# [QA-01] Inconsistent Creation Salt for Single Owner Safe Due to Threshold Variation
## Proof of Concept
The `createSystemInstance` function in `InstanceDeployer.sol` uses the threshold parameter in its creation salt calculation, even when there's only one owner. This can lead to different creation salts (and thus different addresses) for functionally identical configurations.

```
uint256 creationSalt = uint256(
    keccak256(
        abi.encode(
            instance.owners,
            instance.threshold,  // Issue: threshold included in salt for single owner
            instance.timelockParams.minDelay,
            instance.timelockParams.expirationPeriod,
            instance.timelockParams.pauser,
            instance.timelockParams.pauseDuration,
            instance.timelockParams.hotSigners
        )
    )
);
```
When a Safe has only one owner, any threshold value greater than 1 is functionally equivalent to a threshold of 1, as a single owner can only execute transactions alone. However, the current implementation will generate different addresses for the following configurations:
```
// These would create different addresses but are functionally identical
NewInstance {
    owners: [owner1],
    threshold: 1,
    ...
}

NewInstance {
    owners: [owner1],
    threshold: 2,  // Functionally impossible but affects creation salt
    ...
}
```
This violates the contract's key property stated in the comments:

"A key system property is that deployments are deterministic across all chains. The same calldata on any EVM equivalent chain will generate the same safe and timelock address."

Impact
- It affects the deterministic deployment property
- Could lead to confusion when deploying identical configurations across chains
- May cause issues with front-end applications that try to predict Safe addresses
- Wastes blockchain storage by allowing deployment of functionally identical configurations at different addresses

## Recommended Mitigation Steps
Add validation at the start of `createSystemInstance` to normalize the threshold for single-owner cases:
```
function createSystemInstance(NewInstance memory instance)
    external
    returns (SystemInstance memory walletInstance)
{
    // Validate and normalize threshold for single owner case
    if (instance.owners.length == 1) {
        instance.threshold = 1;
    }
    
    // Validate threshold is not greater than number of owners
    require(
        instance.threshold <= instance.owners.length,
        "InstanceDeployer: threshold cannot exceed owner count"
    );

    // Rest of the function remains unchanged
    ...
}
```
# [QA-02] CalldataAdded Event Emits All Datahashes Instead of Only Newly Added Ones

## Proof of Concept
In the `_addCalldataCheck` function, the `CalldataAdded` event emits all datahashes stored in the index, rather than just the newly added ones. This makes it difficult to track which datahashes were actually added in a specific transaction.

```
emit CalldataAdded(
    contractAddress,
    selector,
    startIndex,
    endIndex,
    indexes[targetIndex].dataHashes.values() // Emits all datahashes, not just new ones
);
```
This can lead to:

- Inefficient gas usage by emitting redundant data
- Difficulty in tracking actual changes made in each transaction
- Potential confusion when monitoring contract state changes
## Recommended Mitigation Steps
Modify the `_addCalldataCheck function to track and emit only newly added datahashes

# [QA-03] Missing SPDX License Identifier
## Proof of Concept
All the contracts are missing an SPDX license identifier, which is recommended by the Solidity compiler and considered a best practice in smart contract development.

Direct link to the code: https://github.com/Kleidi-Replicate/2024-10-kleidi/blob/main/src/ConfigurablePause.sol

The absence of an SPDX identifier can lead to:

- Legal ambiguity regarding the terms under which the code can be used, modified, or distributed.
- Persistent compiler warnings, which may obscure other important messages.
- Difficulty for automated tools to process and categorize the contract's licensing information.

## Recommended Mitigation Steps
Add an SPDX license identifier at the very top of the `ConfigurablePause.sol` file. The exact license should be chosen based on the project's requirements, but a common choice for open-source projects is the MIT license.


# [QA-04] Use of Assert Instead of Require for Removal Logic
## Proof of Concept
The Timelock contract uses `assert()` statements in several places to ensure successful removal of calldata hashes. While `assert()` is typically used for invariant checking, using `require()` with descriptive error messages would be more appropriate for these operations, as it would provide better debugging information and consume less gas in case of failure.

Affected locations:

In _removeCalldataCheck(): https://github.com/code-423n4/2024-01-decent/blob/main/src/Timelock.sol#L1215
```
   assert(indexCheck.dataHashes.remove(removedDataHashes[i]));
```
Also in _removeCalldataCheck(): https://github.com/code-423n4/2024-01-decent/blob/main/src/Timelock.sol#L1229-L1230
```
   assert(indexCheck.dataHashes.add(dataHashes[i]));
   assert(lastIndexCheck.dataHashes.remove(dataHashes[i]));
```
In _removeAllCalldataChecks(): https://github.com/code-423n4/2024-01-decent/blob/main/src/Timelock.sol#L1278
```
   assert(removedCalldataCheck.dataHashes.remove(dataHashes[i]));
```
Impact:

- Using `assert()` can result in hard-to-debug errors in production environments since it does not provide a descriptive error message.
- If the assertion fails, it will consume all remaining gas, which is more costly than a require() statement.
- The lack of specific error messages makes it harder to identify the exact cause of a failure during contract execution or testing.

## Recommended Mitigation Steps
Replace the `assert()` statements with `require()` statements that include descriptive error messages. This will improve debuggability and provide more informative errors if unexpected conditions occur

# [QA-05] Pause State Ambiguity Due to Non-Reset pauseStartTime After Expiry
## Proof of Concept
In `ConfigurablePause.sol`, the `pauseStartTime` variable is not reset to zero when a pause expires naturally, leading to state ambiguity.

Current implementation:
```
function paused() public view returns (bool) {
    return block.timestamp <= pauseStartTime + pauseDuration;
}
```
The contract can be in an unpaused state in two different ways:

- `pauseStartTime == 0` (explicit unpaused state)
- `pauseStartTime != 0 && block.timestamp > pauseStartTime + pauseDuration` (implicit unpaused state)
Example scenario:
```
// Initial state
pauseStartTime = 0;
pauseDuration = 1 days;
pauseGuardian = guardianAddress;

// Guardian calls pause() at t=1000
pauseStartTime = 1000;
pauseDuration = 1 days;
pauseGuardian = address(0);

// At t=2000 (after pause expires)
// pauseStartTime remains 1000 instead of resetting to 0
// Contract is unpaused but state is ambiguous
```
This ambiguity can affect:

- External contract integrations that rely on pauseStartTime checks
- Monitoring tools tracking contract state
- Audit trail clarity
- State interpretation in UI/frontend applications

## Recommended Mitigation Steps
- Add an explicit pause expiry handler


# [QA-06] Late Authorization Check in `createSystemInstance` Wastes Gas and Creates Unnecessary Deployments
## Proof of Concept
In `InstanceDeployer.sol`, the `createSystemInstance` function performs authorization checks after deploying contracts:
```
// First deploys Safe (lines 186-213)
try SafeProxyFactory(safeProxyFactory).createProxyWithNonce(
    safeProxyLogic, safeInitdata, creationSalt
) returns (SafeProxy safeProxy) {
    walletInstance.safe = safeProxy;
} catch {
    // ...
}

// Then deploys Timelock (lines 223-229)
walletInstance.timelock = Timelock(
    payable(
        TimelockFactory(timelockFactory).createTimelock(
            address(walletInstance.safe), instance.timelockParams
        )
    )
);

// Only then checks authorization (lines 231-236)
require(
    walletInstance.timelock.hasRole(
        walletInstance.timelock.HOT_SIGNER_ROLE(), 
        msg.sender
    ),
    "InstanceDeployer: sender must be hot signer"
);
```
This creates several issues:

- Unauthorized users waste gas deploying contracts before the transaction reverts
- Unnecessary contract deployments occur even if the caller isn't authorized
- Creates potential security risks by deploying contracts before verifying authorization

## Recommended Mitigation Steps
Move the authorization check to the beginning of the function