## Table of Contents

| Finding   | Heading                                                 |
|:-------|:-----------------------------------------------------------|
| L-01  | `calculateAddress()` function is vulnerable to frontrunning |
| L-02  | Safe calling itself with empty calldata is potentially dangerous if a fallback handler is configured |
| L-03  | Insufficient validation for owners in `RecoverySpellFactory.sol` |
| L-04  | Consider restricting unbounded loops to protect against user error |
| L-05  | Bad proposal timestamp cleanup leads to inconsistent behavior |
| Q-01  | Arbitrum and Optimism chainIds missing in `SystemDeploy.s.sol` |
| Q-02  | InstanceDeployer immutable variable verification missing in `SystemDeploy.s.sol` |
| Q-03  | Consider making RecoverySpell deployment permissioned |
| Q-04  | Wrong comment in `ConfigurablePause.sol` |
| Q-05  | Unused Code |
| Q-06  | Unnecessary `salt` in `InstanceDeployer.sol` |
| Q-07  | Reachable `assert()` functions in `InstanceDeployer.sol` will consume all of the remaining gas |
| Q-08  | `s` parameter in signature can be non-zero due to corrupted memory |
| Q-09  | Rename `newRecoveryThreshold` to `recoveryThreshold` |
| Q-10  | Add recovery spell owners to the recovery spell signature |
| Q-11  | Comment that safe owners can call `executeWhitelistedBatch()` is wrong |
| Q-12  | Comment that safe owners can execute whitelisted calldatas is wrong |
| Q-13  | Comment that `require()` can not be reached is wrong |
| Q-14  | `indexes` variable is redundant |
| Q-15  | Delete `_calldataList[contractAddress][selector]` is redundant |
| Q-16  | `_setPauseTime()` in `setGuardian()` is redundant |
| Q-17  | `checkCalldata()` does not support calls with zero calldata |
| Q-18  | `Index` copying logic can be shortcut |




# L-01 `calculateAddress()` function is vulnerable to frontrunning

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/views/AddressCalculation.sol#L48-L51
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L186-L204

## Description

When calling `calculateAddress(NewInstance memory instance)` after the safe has been deployed, it reverts.

In other words, even though the InstanceDeployer core contract is resistant to frontrunning, AddressCalculation can be made to revert.

Even though it is ok to fail due to the try-catch block in `InstanceDeployer.sol`, it should be documented that when the safe is deployed, `AddressCalculation` should not be used, or that it may revert.


# L-02 Safe calling itself with empty calldata is potentially dangerous if a fallback handler is configured

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Guard.sol#L43-L69

## Description

[This](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Guard.sol#L59) `require()` function allows calls to the fallback handler with empty calldata.

It is possible to use the `nonce` in Safe by doing some transaction to another address.

You should not take the risk of allowing self calls to the fallback handler and therefore make sure that `to` does never equal `msg.sender`.


# L-03 Insufficient validation for owners in `RecoverySpellFactory.sol`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpellFactory.sol#L135-L137
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L276-L280
https://github.com/safe-global/safe-smart-account/blob/bf943f80fec5ac647159d26161446ac5d716a294/contracts/base/OwnerManager.sol#L58-L69

## Description

When a user creates a new `RecoverySpell`, `_paramChecks()` is executed to verify the parameters provided by the user. This function ensures that no owner is set to `address(0)`:

```solidity
for (uint256 i = 0; i < owners.length; i++) {
	require(owners[i] != address(0), "RecoverySpell: Owner cannot be 0");
}
```

However, it should also validate that no owner is set to `address(0x1)`, which represents `SENTINEL_OWNERS` and would cause `executeRecoverySpell()` to revert. Additionally, it should ensure that no owner is the safe itself, as this would also trigger a revert.

Consider adding additional checks in `_paramChecks()` to prevent setting any provided owner to `address(0x1)` or the address of the safe.


# L-04 Consider restricting unbounded loops to protect against user error

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L245-L280
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L461-L468
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L488-L489
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L572-L575
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L639-L644
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L743-L754
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L913-L916
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L949-L951
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1093-L1101
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1133-L1138
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1178-L1186
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1214-L1216
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1228-L1231
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1277-L1279
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L214-L221
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L291-L294
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/BytesHelper.sol#L53-L55


## Description

When `executeRecovery()` is called, the contract loops over the existing owners of the safe to remove them. 
Additionally, it loops over the number of owners, which were provided as inputs during the creation of the recovery spell, to add them as the new owners of the safe.

Both of these loops are unbounded. First of all the safe could have an unlimited amount of owners, depending user's specifications.
Furthermore, there is no limit to the number of owners provided as input.

However, this is not a severe issue because: 
1. A user should not add a recovery spell to the system without knowing its inputs, as he should be aware of who and how many owners the safe will have.

and:

2. The loops running out of gas means that the timelock has already been compromised and all funds are lost

These arguments hold true for all loops (including data hashes and calldata checks).
The only unbounded loop that is dangerous, regardless of user error, is the one in `Timelock.pause()` which is reported seperately as a high severity finding.

There is no need to restrict the loops, but a limit should still be considered to protect against mistakes.


# L-05 Bad proposal timestamp cleanup leads to inconsistent behavior

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L392-L394
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L413-L422
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L671-L677

## Description

When `cleanup(bytes32 id)` is called, the `_liveProposal` of the id gets removed but the timestamp is not.

Even though this behavior is documented, the timestamp should also be removed, as not removing prevents the same proposal id from being scheduled again.
Furthermore, this is inconsistent with the behaviour of `pause()`, as it does delete the timestamp and the `_liveProposal`, and so an expired proposal that is deleted via `pause()` has its timestamp removed.

Additionally, the `assert()` function in `cleanup()` is reachable and will consume all remaining gas if the same id is cleaned up twice.
The comment is misleading, as "not reachable" implies that the timestamp should be deleted, since the `require()` function above would revert.

This bad cleanup does also affect `isOperation()` and `isOperationExpired()`.

Consider deleting the timestamp of the id as well.







# Q-01 Arbitrum and Optimism chainIds missing in `SystemDeploy.s.sol`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/deploy/SystemDeploy.s.sol#L21-L28

## Description

The Arbitrum and Optimism chainIds are missing and should also be added in the constructor.
This means that the deployment script can not be used with Arbitrum and Optimism, even though the documentation states that they should be supported.


# Q-02 InstanceDeployer immutable variable verification missing in `SystemDeploy.s.sol`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/deploy/SystemDeploy.s.sol#L76-L132

## Description

The InstanceDeployer immutable variable for the AddressCalculation contract should also be verified to be consistent with the validation that is performed for the InstanceDeployer.


# Q-03 Consider making RecoverySpell deployment permissioned

## Description

[This](https://github.com/GalloDaSballo/kleidi-notes?tab=readme-ov-file#q-12-once-a-recoveryspell-is-deployed-all-spells-on-all-chains-may-be-deployed:~:text=compromised%20hot%20signer-,Q%2D12%20Once%20a%20RecoverySpell%20is%20deployed%2C%20all%20spells%20on%20all,happens%20on%20one%20chain%2C%20it%20should%20probably%20happen%20on%20all%20chains,-Q%2D13%20InstanceDeployer) finding in the old security review by Alex The Entreprenerd mentions that a frontrun of a RecoverySpell on another chain will cause the RecoverySpell to have a reduced delay.

As a mitigation, it should be considered whether it would be better if only one of the recovery signers is able to deploy the RecoverySpell.


# Q-04 Wrong comment in `ConfigurablePause.sol`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L8

## Description

The comment does not reflect what is happening in the code.

It should be changed to:

```solidity
///     3. unpaused, pauseStartTime < block.timestamp - pauseDuration, guardian == address(0)
```


# Q-05 Unused Code

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/TimelockFactory.sol#L4
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Guard.sol#L7
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Guard.sol#L33


## Description

The following Import in `TimelockFactory.sol` is unused.

```solidity
import {calculateCreate2Address} from "src/utils/Create2Helper.sol";
```

Similarly, the following import in `Guard.sol` is also unused.

```solidity
import {BytesHelper} from "src/BytesHelper.sol";
```

Additionally, the following statement in `Guard.sol` is unnecessary and should be removed:

```solidity
using BytesHelper for bytes;
```

Removing unused code can improve readability.


# Q-06 Unnecessary `salt` in `InstanceDeployer.sol`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L179-L182
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/TimelockFactory.sol#L6-L18

## Description

It is not necessary to create a timelock with a `salt`, as the safe is a construction parameter for a timelock. This means we have a seperate timelock for every safe without a `salt`.

Consider removing the `salt` when creating a timelock. It should also be removed from the `DeploymentParams` struct.


# Q-07 Reachable `assert()` functions in `InstanceDeployer.sol` will consume all of the remaining gas

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L218-L219

## Description

When a different hot signer calls `createSystemInstance(NewInstance memory instance)` for a system which has already been created, the two assert functions will be reachable.

This means that they will consume all of the remaining gas.

Consider changing them to `require()`.


# Q-08 `s` parameter in signature can be non-zero due to corrupted memory

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L342-L380

## Description

It is bad practice to pass potentially corrupted memory even though the parameter is not used by the safe.

You should add the following line:

```diff
-/// no need to store s, this should be 0 bytes
+mstore(add(ptr, 0x40), 0)
```


# Q-09 Rename `newRecoveryThreshold` to `recoveryThreshold`

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L76-L78

## Description

To improve clarity, `newRecoveryThreshold` should be renamed to `recoveryThreshold`, as it is not the new `recoveryThreshold` but the only `recoveryThreshold` that is determined at construction.


# Q-10 Add recovery spell owners to the recovery spell signature

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L76-L78
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/RecoverySpell.sol#L136-L152

## Description

`RECOVERY_TYPEHASH` should include `address[] memory owners` for the sake of completeness.


# Q-11 Comment that safe owners can call `executeWhitelistedBatch()` is wrong

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L728-L729

## Description

The comment states that any safe owner can call the `executeWhitelistedBatch()` function.

However, this is not true, as only hot signers can call it.

The comment should therefore be changed.


# Q-12 Comment that safe owners can execute whitelisted calldatas is wrong

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L52

## Description

The comment states that only safe owners can execute whitelisted calldatas, but this is not true as only hot signers can.

It should therefore be changed.

# Q-13 Comment that `require()` can not be reached is wrong

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L999-L1001

## Description

The comment is incorrect, as this line can be reached by simply scheduling a proposal again that has been executed as it has `_DONE_TIMESTAMP`.


# Q-14 `indexes` variable is redundant

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1089

## Description

The `indexes` variable is not needed as it is a duplicate of `calldataChecks`.

Therefore, it should be removed and `calldataChecks` should be used instead.


# Q-15 Delete `_calldataList[contractAddress][selector]` is redundant

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1284-L1285

## Description

When `_removeAllCalldataChecks(address contractAddress, bytes4 selector)` is called, `_calldataList[contractAddress][selector]` gets deleted.

However, this line is redundant and can be removed, as all the individual array elements have been deleted by that point, so there is no effect in deleting the overall array.


# Q-16 `_setPauseTime()` in `setGuardian()` is redundant

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L815-L820

## Description

The `setGuardian(address newGuardian)` function has the `onlyTimelock` modifier, which means that only the Timelock can call this function. For this to happen, the proposal must go through the contract's scheduling and execution flow.

However, this is only possible if the contract is unpaused.
This means that using `_setPauseTime()` in this function has no effect.

Consider removing it.


# Q-17 `checkCalldata()` does not support calls with zero calldata

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L475-L504
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/BytesHelper.sol#L7-L14

## Description

When a `HOT_SIGNER` calls `executeWhitelisted()` or `executeWhitelistedBatch()`, the provided payload gets checked by `checkCalldata()`. However, `checkCalldate()` currently does not allow a `data` length of `0`, as `getFunctionSignature()` in `BytesHelper.sol` would cause a revert. This means that `fallback()` and `receive()` functions are not supported.

Consider adding a case distinction for when the `data` length is `0`.


# Q-18 `Index` copying logic can be shortcut

## Links to affected code

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L903-L920
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1219-L1234

## Description

A check should be added that

```diff
/// remove the index check if the dataHashes are empty
if (indexCheck.dataHashes.length() == 0) {
+   if (calldataChecks.length > 1 && index != calldataChecks.length - 1) {
    	/// index check to overwrite the specified index check with
    	Index storage lastIndexCheck =
        	calldataChecks[calldataChecks.length - 1];

    	indexCheck.startIndex = lastIndexCheck.startIndex;
    	indexCheck.endIndex = lastIndexCheck.endIndex;
    	bytes32[] memory dataHashes = lastIndexCheck.dataHashes.values();

    	for (uint256 i = 0; i < dataHashes.length; i++) {
        	assert(indexCheck.dataHashes.add(dataHashes[i]));
        	assert(lastIndexCheck.dataHashes.remove(dataHashes[i]));
    	}
+    }
    /// remove the last index check for the specified function
    calldataChecks.pop();
}



/// pop the index without swap if index is same as last index
-if (calldataChecks.length > 1) {
+if (calldataChecks.length > 1 && index != calldataChecks.length - 1) {
    /// index check to overwrite the specified index check with
    Index storage lastIndexCheck =
        calldataChecks[calldataChecks.length - 1];

    indexCheck.startIndex = lastIndexCheck.startIndex;
    indexCheck.endIndex = lastIndexCheck.endIndex;
    bytes32[] memory dataHashes = lastIndexCheck.dataHashes.values();

    for (uint256 i = 0; i < dataHashes.length; i++) {
        assert(indexCheck.dataHashes.add(dataHashes[i]));
        assert(lastIndexCheck.dataHashes.remove(dataHashes[i]));
    }
}

calldataChecks.pop();
```

Even just `index != calldataChecks.length - 1` should be enough because it implies that `calldataChecks.length > 1`.