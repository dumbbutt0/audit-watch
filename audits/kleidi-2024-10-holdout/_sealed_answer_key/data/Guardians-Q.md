## Table of Contents

| Issue ID                                                                           | Description                                                        |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| [QA-01](#qa-01-kleidis-_timelock_-can-easily-be-broken-via-mev)                    | Kleidi's _Timelock_ can easily be broken via MEV                   |
| [QA-02](#qa-02-wrong-event-scope-when-adding-new-call-data)                        | Wrong event scope when adding new call data                        |
| [QA-03](#qa-03-pausing-functionality-is-not-implemented-as-documented)             | Pausing functionality is not implemented as documented             |
| [QA-04](&lt;#qa-04-make-timelock#isoperationexpired()-more-efficient&gt;)                | Make `Timelock#isOperationExpired()` more efficient                |
| [QA-05](#qa-05-configuration-changes-should-be-behind-a-timelock-from-loop-update) | configuration changes should be behind a timelock from loop update |
| [QA-07](&lt;#qa-07-_addcalldatacheck()-is-too-strenuous&gt;)                             | `_addCalldataCheck()` is too strenuous                             |
| [QA-08](#qa-08-subtle-invariant-about-not-holding-funds-can-be-broken)             | Subtle invariant about not holding funds can be broken             |
| [QA-09](#qa-09-setters-should-always-have-equality-checkers)                       | Setters should always have equality checkers                       |

## QA-01 Kleidi's _Timelock_ can easily be broken via MEV

### Proof of Concept

Protocol integrates a simple logic of how proposals are proposed, waited on to be ready and then this is executed via:
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L589-L610

```solidity
    function execute(
        address target,
        uint256 value,
        bytes calldata payload,
        bytes32 salt
    ) external payable whenNotPaused {
        bytes32 id = hashOperation(target, value, payload, salt);

        /// first reentrancy check, impossible to reenter and execute the same
        /// proposal twice
        require(_liveProposals.remove(id), "Timelock: proposal does not exist");
        require(isOperationReady(id), "Timelock: operation is not ready");

        _execute(target, value, payload);
        emit CallExecuted(id, 0, target, value, payload);

        /// second reentrancy check, second check that operation is ready,
        /// operation will be not ready if already executed as timestamp will
        /// be set to 1
        _afterCall(id);
    }

```

Issue however is that there are no access control to this, which allows for a simple case like the below to be met:

- Multiple proposals are to be ready around the same time.
- There should be an order for this operation to be submitted.
- Since anyone can execute the proposal including the attacker they can just execute the one that gives them the most MEV opportunity.
- And backrun the tx with their intended attack.

### Impact

Borderline low/medium since one can argue this to be the intended behaviour.

### Recommended Mitigation Steps

Consider attaching some sort of access control to `execute()`.

## QA-02 Wrong event scope when adding new call data

### Proof of Concept

The below ends up being called in order to add a calldata check:
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1034-L1155

```solidity
    function _addCalldataCheck(
        address contractAddress,
        bytes4 selector,
        uint16 startIndex,
        uint16 endIndex,
        bytes[] memory data
    ) private {
        require(
            contractAddress != address(0),
            "CalldataList: Address cannot be zero"
        );
        require(selector != bytes4(0), "CalldataList: Selector cannot be empty");
        require(
            startIndex &gt;= 4, "CalldataList: Start index must be greater than 3"
        );

        /// prevent misconfiguration where a hot signer could change timelock
        /// or safe parameters
        require(
            contractAddress != address(this),
            "CalldataList: Address cannot be this"
        );
        require(contractAddress != safe, "CalldataList: Address cannot be safe");

        Index[] storage calldataChecks =
            _calldataList[contractAddress][selector];
        uint256 listLength = calldataChecks.length;

        if (listLength == 1) {
            require(
                calldataChecks[0].startIndex != calldataChecks[0].endIndex,
                "CalldataList: Cannot add check with wildcard"
            );
        }

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
                endIndex &gt; startIndex,
                "CalldataList: End index must be greater than start index"
            );
            /// if we are adding a concrete check and not a wildcard, then the
            /// calldata must not be empty
            require(data.length != 0, "CalldataList: Data empty");
        }

        Index[] storage indexes = _calldataList[contractAddress][selector];
        uint256 targetIndex = indexes.length;
        {
            bool found;
            for (uint256 i = 0; i &lt; indexes.length; i++) {
                if (
                    indexes[i].startIndex == startIndex
                        &amp;&amp; indexes[i].endIndex == endIndex
                ) {
                    targetIndex = i;
                    found = true;
                    break;
                }
                /// all calldata checks must be isolated to predefined calldata segments
                /// for example given calldata with three parameters:

                ///                    1.                              2.                             3.
                ///       000000000000000112818929111111
                ///                                     000000000000000112818929111111
                ///                                                                   000000000000000112818929111111

                /// checks must be applied in a way such that they do not overlap with each other.
                /// having checks that check 1 and 2 together as a single parameter would be valid,
                /// but having checks that check 1 and 2 together, and then check one separately
                /// would be invalid.
                /// checking 1, 2, and 3 separately is valid
                /// checking 1, 2, and 3 as a single check is valid
                /// checking 1, 2, and 3 separately, and then the last half of 2 and the first half
                /// of 3 is invalid

                require(
                    startIndex &gt; indexes[i].endIndex
                        || endIndex &lt; indexes[i].startIndex,
                    "CalldataList: Partial check overlap"
                );
            }

            if (!found) {
                indexes.push();
                indexes[targetIndex].startIndex = startIndex;
                indexes[targetIndex].endIndex = endIndex;
            }
        }

        for (uint256 i = 0; i &lt; data.length; i++) {
            /// data length must equal delta index
            require(
                data[i].length == endIndex - startIndex,
                "CalldataList: Data length mismatch"
            );
            bytes32 dataHash = keccak256(data[i]);

            /// make require instead of assert to have clear error messages
            require(
                indexes[targetIndex].dataHashes.add(dataHash),
                "CalldataList: Duplicate data"
            );
        }

        emit CalldataAdded(
            contractAddress,
            selector,
            startIndex,
            endIndex,
            indexes[targetIndex].dataHashes.values()
        );
    }
```

Issue hwoever is that the event is expecting the calldata to be emitted for offcahin services, however their hashes get emitted instead: `            indexes[targetIndex].dataHashes.values()`

### Impact

QA

&gt; Broken functionality for off chain parties that expect the call datas to be emitted and not the hashes.

### Recommended Mitigation Steps

Emit the calldata instead.

## QA-03 Pausing functionality is not implemented as documented

### Proof of Concept

First, would be key to note that the protocol integrates with a pausing logic for contracts, this is done by the `whenNotPaused` modifier that only queries the `paused` functionality to ensure the protocol is not paused, i.e

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L59-L62

```solidity
    modifier whenNotPaused() {
        require(!paused(), "Pausable: paused");
        _;
    }
```

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L69-L71

```solidity
    function paused() public view returns (bool) {
        return block.timestamp &lt;= pauseStartTime + pauseDuration;
    }
```

Now per the documentation these are the cases as to which we should consider the protocol paused, quote on quote:

https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L67-L68

&gt; /// if pauseStartTime is 0, contract is not paused

&gt; /// if pauseStartTime is not 0, contract could be paused in the pauseDuration window

Issue however is that there are no checks on whether the `pauseStartTime` is indeed `0`, which would mean that when we have the `pauseStartTime` as `0` the modifier erroneously executes.

### Impact

QA

### Recommended Mitigation Steps

Correctly implement the functionality.

## QA-04 Make `Timelock#isOperationExpired()` more efficient

### Proof of Concept

See https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L413-L422

```solidity
    function isOperationExpired(bytes32 id) public view returns (bool) {
        /// if operation is done, save an extra SLOAD
        uint256 timestamp = timestamps[id];

        /// if timestamp is 0, the operation is not scheduled, revert
        require(timestamp != 0, "Timelock: operation non-existent");
        require(timestamp != 1, "Timelock: operation already executed");

        return block.timestamp &gt;= timestamp + expirationPeriod;
    }
```

The above is used to know if an operation is expired or not.

Now not only is this not really gas efficient it also doesn't use intended code, this is because protocol includes the `DONE_TIMESTAMP` logic however it's not used above:

```rust
    uint256 internal constant _DONE_TIMESTAMP = uint256(1);

    mapping(bytes32 id =&gt; uint256) private _timestamps;
    uint256 private _minDelay;
```

### Impact

QA

### Recommended Mitigation Steps

Apply these changes:

```diff
    function isOperationExpired(bytes32 id) public view returns (bool) {
        /// if operation is done, save an extra SLOAD
        uint256 timestamp = timestamps[id];

        /// if timestamp is 0, the operation is not scheduled, revert
        require(timestamp != 0, "Timelock: operation non-existent");
-        require(timestamp != 1, "Timelock: operation already executed");
+        require(timestamp != _DONE_TIMESTAMP, "Timelock: operation already executed");

        return block.timestamp &gt;= timestamp + expirationPeriod;
    }
```

## QA-05 configuration changes should be behind a timelock from loop update

### Proof of Concept

Take a look at https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L104-L127

```solidity
    function _updatePauseDuration(uint128 newPauseDuration) internal {
        require(
            newPauseDuration &gt;= MIN_PAUSE_DURATION
                &amp;&amp; newPauseDuration &lt;= MAX_PAUSE_DURATION,
            "ConfigurablePause: pause duration out of bounds"
        );

        /// if the contract was already paused, reset the pauseStartTime to 0
        /// so that this function cannot pause the contract again
        _setPauseTime(0);

        uint256 oldPauseDuration = pauseDuration;
        pauseDuration = newPauseDuration;

        emit PauseDurationUpdated(oldPauseDuration, pauseDuration);
    }

    /// @notice helper function to update the pause start time. used to pause the contract
    /// @param newPauseStartTime new pause start time
    function _setPauseTime(uint128 newPauseStartTime) internal {
        pauseStartTime = newPauseStartTime;

        emit PauseTimeUpdated(newPauseStartTime);
    }
```

### Impact

QA

### Recommended Mitigation Steps

Put it behind a timelock.

## QA-06 Kleidi does not protect itself against birthday attacks

Bug case is very similar to: https://github.com/code-423n4/2024-08-axelar-network-findings/issues/49

Kleidi integrates a lot with deterministic addresses, now a keccak is truncated down to a uint160 (20 bytes), the likelihood that a clash is found is around 2^80

This makes brute-forcing a clash plausible, albeit heavily expensive

### Impact

Whereas this is possible, impact here can't be higher than QA considering it's very expensive to actualise, also the attack here might not be feasible for any specific Safe in the system.

See this for more info: https://github.com/code-423n4/2024-08-axelar-network-findings/issues/49 and the comment [here](https://github.com/code-423n4/2024-08-axelar-network-findings/issues/49#issuecomment-2362510401).

### Recommended Mitigation Steps

Protect against the birthday attack.

### Proof of Concept

Take a look at

### Impact

### Recommended Mitigation Steps

## QA-07 `_addCalldataCheck()` is too strenuous

### Proof of Concept

The below ends up being called in order to add a calldata check:
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1034-L1155

```solidity
    function _addCalldataCheck(
        address contractAddress,
        bytes4 selector,
        uint16 startIndex,
        uint16 endIndex,
        bytes[] memory data
    ) private {
        require(
            contractAddress != address(0),
            "CalldataList: Address cannot be zero"
        );
        require(selector != bytes4(0), "CalldataList: Selector cannot be empty");
        require(
            startIndex &gt;= 4, "CalldataList: Start index must be greater than 3"
        );

        /// prevent misconfiguration where a hot signer could change timelock
        /// or safe parameters
        require(
            contractAddress != address(this),
            "CalldataList: Address cannot be this"
        );
        require(contractAddress != safe, "CalldataList: Address cannot be safe");

        Index[] storage calldataChecks =
            _calldataList[contractAddress][selector];
        uint256 listLength = calldataChecks.length;

        if (listLength == 1) {
            require(
                calldataChecks[0].startIndex != calldataChecks[0].endIndex,
                "CalldataList: Cannot add check with wildcard"
            );
        }

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
                endIndex &gt; startIndex,
                "CalldataList: End index must be greater than start index"
            );
            /// if we are adding a concrete check and not a wildcard, then the
            /// calldata must not be empty
            require(data.length != 0, "CalldataList: Data empty");
        }

        Index[] storage indexes = _calldataList[contractAddress][selector];
        uint256 targetIndex = indexes.length;
        {
            bool found;
            for (uint256 i = 0; i &lt; indexes.length; i++) {
                if (
                    indexes[i].startIndex == startIndex
                        &amp;&amp; indexes[i].endIndex == endIndex
                ) {
                    targetIndex = i;
                    found = true;
                    break;
                }
                /// all calldata checks must be isolated to predefined calldata segments
                /// for example given calldata with three parameters:

                ///                    1.                              2.                             3.
                ///       000000000000000112818929111111
                ///                                     000000000000000112818929111111
                ///                                                                   000000000000000112818929111111

                /// checks must be applied in a way such that they do not overlap with each other.
                /// having checks that check 1 and 2 together as a single parameter would be valid,
                /// but having checks that check 1 and 2 together, and then check one separately
                /// would be invalid.
                /// checking 1, 2, and 3 separately is valid
                /// checking 1, 2, and 3 as a single check is valid
                /// checking 1, 2, and 3 separately, and then the last half of 2 and the first half
                /// of 3 is invalid

                require(
                    startIndex &gt; indexes[i].endIndex
                        || endIndex &lt; indexes[i].startIndex,
                    "CalldataList: Partial check overlap"
                );
            }

            if (!found) {
                indexes.push();
                indexes[targetIndex].startIndex = startIndex;
                indexes[targetIndex].endIndex = endIndex;
            }
        }

        for (uint256 i = 0; i &lt; data.length; i++) {
            /// data length must equal delta index
            require(
                data[i].length == endIndex - startIndex,
                "CalldataList: Data length mismatch"
            );
            bytes32 dataHash = keccak256(data[i]);

            /// make require instead of assert to have clear error messages
            require(
                indexes[targetIndex].dataHashes.add(dataHash),
                "CalldataList: Duplicate data"
            );
        }

        emit CalldataAdded(
            contractAddress,
            selector,
            startIndex,
            endIndex,
            indexes[targetIndex].dataHashes.values()
        );
    }
```

Issue however is that when emiting the event for the new calldata added we instead emit all the values of the target index's datahashes instead of the current one being added.

### Impact

QA

&gt; Broken functionality for off chain parties that expect only the call data being added to be emitted and not everything.

### Recommended Mitigation Steps

Emit the correct calldata.

## QA-08 Subtle invariant about not holding funds can be broken

### Proof of Concept

Protocol makes integration with Safe, however it makes an erroneous assumption that [the Safe cannot hold any funds](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Guard.sol#L29-L30) prior to the integration, this is inaccurate however, considering this can be broken as one can just set the contract as the block rewards collector or even selfdestruct and send funds to the contract.

### Impact

QA

### Recommended Mitigation Steps

Do not make a blind assumption and instead prepare for the scenario where there is some funds in the Safe.

## QA-09 Setters should always have equality checkers

### Proof of Concept

See https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L104-L120

```solidity
    function _updatePauseDuration(uint128 newPauseDuration) internal {
        require(
            newPauseDuration &gt;= MIN_PAUSE_DURATION
                &amp;&amp; newPauseDuration &lt;= MAX_PAUSE_DURATION,
            "ConfigurablePause: pause duration out of bounds"
        );

        /// if the contract was already paused, reset the pauseStartTime to 0
        /// so that this function cannot pause the contract again
        _setPauseTime(0);

        uint256 oldPauseDuration = pauseDuration;
        pauseDuration = newPauseDuration;

        emit PauseDurationUpdated(oldPauseDuration, pauseDuration);
    }

```

This is a helper function to update the pause duration, issue however is that it does not include any check to ensure that the new value being set is not `==` the previous value.

### Impact

QA

### Recommended Mitigation Steps

Setters should always have equality checkers this helps with having non unnecessary executions taking place
