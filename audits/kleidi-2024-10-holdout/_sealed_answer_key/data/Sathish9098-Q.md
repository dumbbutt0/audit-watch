# QA Report

| Issue No | Title |
|----------|-------|
| L-1 | ``Dynamic Expiration`` Period Changes Can Invalidate Ready Operations and Revive Expired Ones |
| L-2 | `setGuardian()` function is vulnerable to frontrunning attack |
| L-3 | `setGuardian()` Implementation Does Not Enforce Paused State as Intended |
| L-4 | Automatic `Unpause` After `pauseDuration` Elapsed Could Break Core Functionality |
| L-5 | Accidental `ETH` Transfers to `Timelock` Contract Risk Being Permanently Locked |
| L-6 | Arbitrary Cancellation Risk: Unrestricted `onlySafe` Role May Disrupt `Timelocked Operations` |
| L-7 | No ``Maximum Expiration`` Period Leads to Indefinite ``Timelocked Actions`` |
| L-8 | Risk of ``DoS`` from Large Enumerable Sets in State-Modifying Functions |
| L-9 | Inconsistency between `isOperationReady()` and `isOperationExpired()` Checks |
| L-10 | ``DoS`` Risk Due to Unbounded Enumerable Set Growth in `getAllProposals()` |
| L-11 | Misleading Comment in `isOperation()` Function |
| L-12 | ``Redundant`` Guardian Reassignment and Potential ``Governance Manipulation Risk`` |
| L-13 | Critical ``Immutable`` Variables Assigned Without Validation in Constructor |
| L-14 | Improper ``Memory Alignment`` in Assembly Block |
| L-15 | ``Unsafe`` Assembly Blocks |
| L-16 | Lack of Access Control on Critical ``initialize()`` Function |



##

## [L-1] Dynamic Expiration Period Changes Can Invalidate Ready Operations and Revive Expired Ones

### Impact
Operations that are ready for execution can become immediately expired if the expiration period is shortened.

If the ``expirationPeriod`` increased then the expired Operations become ready.

### POC

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

 /// @dev Returns whether an operation is ready for execution.
    /// Note that a "ready" operation is also "pending".
    /// cannot be executed after the expiry period.
    function isOperationReady(bytes32 id) public view returns (bool) {
        /// cache timestamp, save up to 2 extra SLOADs
        uint256 timestamp = timestamps[id];
        return timestamp > _DONE_TIMESTAMP && timestamp <= block.timestamp
            && timestamp + expirationPeriod > block.timestamp;
    }

/// @dev Returns whether an operation is expired
    /// @notice operations expire on their expiry timestamp, not after
    function isOperationExpired(bytes32 id) public view returns (bool) {
        /// if operation is done, save an extra SLOAD
        uint256 timestamp = timestamps[id];

        /// if timestamp is 0, the operation is not scheduled, revert
        require(timestamp != 0, "Timelock: operation non-existent");
        require(timestamp != 1, "Timelock: operation already executed");

        return block.timestamp >= timestamp + expirationPeriod;
    }

/// @notice update the expiration period for timelocked actions
    /// @param newPeriod the new expiration period
    function updateExpirationPeriod(uint256 newPeriod) external onlyTimelock {
        require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");

        emit ExpirationPeriodChange(expirationPeriod, newPeriod);
        expirationPeriod = newPeriod;
    }

```

### Problem Scenario: Sudden Expiration Period Change

#### Scenario Example
- Initial State:
 - Operation timestamp: 10,000 (block timestamp when scheduled).
 - Initial expiration period: 7 days (equivalent to 604,800 seconds).
 - The operation will expire at- expiration = 10,000 + 604,800 = 614,800
 - If block.timestamp = 610,000, the operation is still valid and can be executed since (610,000 < 614,800)

- Scenario: Sudden Decrease of Expiration Period:
 - The expiration period is changed from 7 days to 2 days (172,800 seconds).
 - The new expiration becomes:new expiration = 10,000 + 172,800 = 182,800
- Impact:
 - Now, block.timestamp = 610,000, which is greater than the new expiration (182,800).
 - As a result, the operation immediately expires and can no longer be executed, even though it was originally valid for 7 days.

### Recommended Mitigation
Lock Expiration Period for Existing Operations
Introduce a Cooldown for Expiration Period Updates

##

## [L-2] ``setGuardian()`` function is vulnerable to frontrunning attack

### Impact
The old guardian can cancel all pending proposals by pausing the contract just before the setGuardian() transaction completes. This vulnerability allows the old guardian to disrupt the governance process by clearing pending operations during a guardian transition, resulting in lost proposals, delays, governance manipulation, and loss of trust in the system.

### POC

### Step-by-Step Attack Scenario

State: Contract is Not Paused.

- There are pending proposals in the system.
``setGuardian(newGuardian)`` Transaction is Sent. Because the ``onlyTimelock ``decided to change the ``oldGuardian`` .

This transaction is visible in the ``mempool``.
- Old Guardian ``Frontruns`` the Transaction:
The old guardian sees the transaction and sends a ``pause()`` transaction first.
- Impact of the pause() Call:
The contract is paused, all pending proposals are deleted, and the old guardian is revoked.
Since the proposals are now removed, governance actions are disrupted.
- ``setGuardian()`` Still Executes:
The new guardian is granted, but the damage is done — all pending operations are lost.

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

/// @notice cancel all outstanding pending and non executed operations
    /// pauses the contract, revokes the guardian
    function pause() public override {
        /// check that msg.sender is the pause guardian, pause the contract
        super.pause();

        bytes32[] memory proposals = _liveProposals.values();
        for (uint256 i = 0; i < proposals.length; i++) {
            bytes32 id = proposals[i];

            delete timestamps[id];
            assert(_liveProposals.remove(id));

            emit Cancelled(id);
        }
    }

 /// @notice function to grant the guardian to a new address
    /// resets the pauseStartTime to 0, which unpauses the contract
    /// @param newGuardian the address of the new guardian
    function setGuardian(address newGuardian) public onlyTimelock {
        /// if a new guardian is granted, the contract is automatically unpaused
        _setPauseTime(0);

        _grantGuardian(newGuardian);
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L815-L820

### Recommended Mitigation
Use a two-step process with a time delay to introduce the new guardian. This prevents the old guardian from immediately pausing the contract during the transition window.


## [L-3] ``setGuardian()`` Implementation Does Not Enforce Paused State as Intended

Even if the contract is already unpaused, the pause timer is reset unnecessarily, which could create inconsistencies in the governance logic.

The ``setGuardian()`` function contains a logic inconsistency where it ``unpauses`` the contract by setting ``pauseStartTime`` to 0. However, the function can be invoked even when the contract is not paused, which deviates from the intended behavior implied by the function’s comment. This allows a guardian transition to occur during normal operations, bypassing the pause mechanism’s constraints.

#### What the Comment Says:
The comment implies that granting a new guardian resets the pause timer (i.e., unpauses the contract).

#### What the Code Does:

- setGuardian() can be called regardless of whether the contract is paused or not.
- Even if the contract is already ``unpaused``, calling ``setGuardian()`` will still reset the pause timer, allowing the operation to proceed without any constraint on the current state.


```solidity
FILE: 2024-10-kleidi/src/Timelock.sol

 /// @notice function to grant the guardian to a new address
    /// resets the pauseStartTime to 0, which unpauses the contract
    /// @param newGuardian the address of the new guardian
    function setGuardian(address newGuardian) public onlyTimelock {
        /// if a new guardian is granted, the contract is automatically unpaused
        _setPauseTime(0);

        _grantGuardian(newGuardian);
    }

```

### Recommended Mitigation
If the intention newGuardian is only changed after contract paused then implement ``whenPaused`` Modifier or check ``pauseStartTime`` is already not ``0``.

Or update the comment as per implementation


##

## [L-4] Automatic ``Unpause`` After ``pauseDuration`` elapsed Could Break Core Functionality

``pauseStartTime`` remains non-zero even after the contract is automatically unpaused.The contract ``unpauses`` itself once ``pauseDuration`` elapses without resetting or clearing ``pauseStartTime``. This creates a situation where the contract resumes operation after the pause window, even if there was a critical reason to keep it paused.

If automatically ``unpause`` can create the unintended consequences and contract become unpaused without guardian. If any sudden problem its not possible to pause without setting new guardian.

### Scenario Where the Issue Might Occur

- Lets assume a security vulnerability is detected, and the contract is paused by setting pauseStartTime = block.timestamp and the ``pauseGuardian`` is set to address(0).
- Assume pauseDuration = 2 days.
- After 2 days, the contract automatically unpauses even the setGuardian function not called and set pauseStartTime to 0 and without newGuardian address.

After 2 days elapsed when check ``whenNotPaused()`` modifier this will return true because ``block.timestamp <= pauseStartTime + pauseDuration `` check return false. Since pauseStartTime + pauseDuration (today + 2 days).

### POC

```solidity

/// @notice function to grant the guardian to a new address
    /// resets the pauseStartTime to 0, which unpauses the contract
    /// @param newGuardian the address of the new guardian
    function setGuardian(address newGuardian) public onlyTimelock {
        /// if a new guardian is granted, the contract is automatically unpaused
        _setPauseTime(0); //@audit possible to frontrun the setGuardian transaction frontrun by old guardian the puposefully pause the contract and remove all pending proposals 

        _grantGuardian(newGuardian);
    }

```

```solidity
FILE: 2024-10-kleidi/src/ConfigurablePause.sol

 /// @dev Modifier to make a function callable only when the contract is not paused.
    modifier whenNotPaused() {
        require(!paused(), "Pausable: paused");
        _;
    }

/// @notice return the current pause status
    /// if pauseStartTime is 0, contract is not paused
    /// if pauseStartTime is not 0, contract could be paused in the pauseDuration window
    function paused() public view returns (bool) {
        return block.timestamp <= pauseStartTime + pauseDuration;
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/ConfigurablePause.sol#L66-L71

### Recommended Mitigation
Change the core pause logic only unpause the contract after setGuardian() function called.

##

## [L-5] Accidental ``ETH`` Transfers to ``Timelock`` Contract Risk Being permanently Locked

In its current design, the ``Timelock`` contract can receive and store ``ETH`` via the ``receive()`` function. However, there is no built-in mechanism to automatically refund ETH sent by mistake. This can lead to operational challenges, as retrieving the mistakenly sent ETH would require manual intervention through the contract’s governance process. If a user accidentally sends ETH to the Timelock contract, there is no automated refund mechanism to return the funds.


```solidity
FILE:2024-10-kleidi/src/Timelock.sol

  /// @dev Timelock can receive/hold ETH, emit an event when this happens for
    /// offchain tracking
    receive() external payable {
        emit NativeTokensReceived(msg.sender, msg.value);
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1339-L1343

### Recommended Mitigation
Add Governance-Managed (onlyTimelock) Refund Function 

```solidity

function refundAccidentallySentETH(address recipient, uint256 amount) external onlyTimelock {
    require(address(this).balance >= amount, "Insufficient balance");
    (bool success, ) = recipient.call{value: amount}("");
    require(success, "Refund failed");
}

```

##

## [L-6] Arbitrary Cancellation Risk Unrestricted ``onlySafe`` Role May Disrupt ``Timelocked Operations``

Any operation in the ``timelock``, whether it is critical or already ready for execution, can be canceled without any specific reason or justification by the ``onlySafe`` role.

The ``require()`` condition only checks if the operation exists ``isOperation(id)`` and if it is successfully removed from ``_liveProposals``.Since there is no requirement to justify cancellations, a user with onlySafe access can cancel governance-approved proposals arbitrarily, disrupting the governance process.

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

 /// @notice cancel a timelocked operation
    /// cannot cancel an already executed operation.
    /// not callable while paused, because while paused there should not be any
    /// proposals in the _liveProposal set.
    /// @param id the identifier of the operation to cancel
    function cancel(bytes32 id) external onlySafe whenNotPaused {
        require(
            isOperation(id) && _liveProposals.remove(id),
            "Timelock: operation does not exist"
        );

        delete timestamps[id];
        emit Cancelled(id);
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L652-L665

### Recommended Mitigation
N/A 

##

## [L-7] No Maximum Expiration Period Leads to Indefinite Timelocked Actions

In the current implementation, the ``_expirationPeriod`` only has a minimum limit check, with no upper bound. This allows extremely large values (even years or infinite periods) to be set resulting in:

- Timelocked actions might never expire, staying in the system indefinitely.

### POC

```solidity
FILE:2024-10-kleidi/src/Timelock.sol 

 require(
            _expirationPeriod >= MIN_DELAY,
            "Timelock: expiration period too short"
        );
        expirationPeriod = _expirationPeriod;

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L289-L292

### Recommended Mitigation
Incorporate maximum value check to avoid unintended consequences 

```solidity
require(
            _expirationPeriod >= MIN_DELAY && ,_expirationPeriod <= MAX_EXPIRATION_DELAY,
            "Timelock: expiration period too short or too long "
        );

```

##

## [L-8] Risk of DoS from Large Enumerable Sets in State-Modifying Functions

The protocol uses OpenZeppelin's EnumerableSet for managing [_liveProposals](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L107)

### Impact

- As the sets grow larger, operations become increasingly gas-intensive.

- EnumerableSet is primarily designed for efficient membership checks, not for maintaining ordered lists

>> Also, using an Enumerable set can cause a Dos in the contract if the set grows large enough and it’s used in a function that modifies the state of the contract, this is commented in the openzeppelin documentation and it’s something to keep in mind for future iterations of the contracts

```Solidity
FILE: 2024-10-kleidi/src/Timelock.sol

/// @notice store list of all live proposals, remove from set once executed or cancelled
    EnumerableSet.Bytes32Set private _liveProposals;

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L106-L107

##

## [L-9] Inconsistency between ``isOperationReady()`` and ``isOperationExpired()`` checks 

The expiration logic considers ``>=`` (inclusive), meaning the operation expires the moment the expiration timestamp is reached.

But the ready logic uses ``>`` (exclusive), meaning the operation is not ready right when it’s at the expiration timestamp.

This creates an inconsistency: At the exact expiration timestamp, the operation will not be ready but won’t be marked expired until the next block.

The inconsistence checks are  ``timestamp + expirationPeriod > block.timestamp`` and ``block.timestamp >= timestamp + expirationPeriod``


```solidity
FILE:2024-10-kleidi/src/Timelock.sol

 function isOperationReady(bytes32 id) public view returns (bool) {
        /// cache timestamp, save up to 2 extra SLOADs
        uint256 timestamp = timestamps[id];
        return timestamp > _DONE_TIMESTAMP && timestamp <= block.timestamp
            && timestamp + expirationPeriod > block.timestamp;
    }

 function isOperationExpired(bytes32 id) public view returns (bool) {
        /// if operation is done, save an extra SLOAD
        uint256 timestamp = timestamps[id];

        /// if timestamp is 0, the operation is not scheduled, revert
        require(timestamp != 0, "Timelock: operation non-existent");
        require(timestamp != 1, "Timelock: operation already executed");

        return block.timestamp >= timestamp + expirationPeriod;
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L421

### Recommended Mitigation
isOperationExpired() only expire after ``timestamp + expirationPeriod`` passed instead of of expire in equal value 

##

## [L-10] DoS Risk Due to Unbounded Enumerable Set Growth in ``getAllProposals()``

If the number of proposals grows indefinitely, calling this function could exceed the block gas limit, resulting in a Denial of Service (DoS).

EnumerableSet's values() function returns the entire set in a single call, which means the more proposals in the set, the higher the gas consumption.

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

function getAllProposals() external view returns (bytes32[] memory) {
        return _liveProposals.values();
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L360-L362

##

## [L-11] Misleading Comment in ``isOperation`` Function

The comment states: "Cancelled operations will return false."
However, this function only checks if the timestamp for the given id is greater than 0. If the contract is paused (or the relevant state is modified to make it temporarily inactive), this might also cause the operation to appear invalid (returning false), even though it wasn’t necessarily cancelled.

If the contract is paused then the timestamp[id] value cleared and become 0.

```diff
FILE: 2024-10-kleidi/src/Timelock.sol

    /// @dev Returns whether an id corresponds to a registered operation. This
    /// includes Pending, Ready, Done and Expired operations.
-    /// Cancelled operations will return false.
+    /// Operations will return false if they are cancelled or if the contract is paused.
    function isOperation(bytes32 id) public view returns (bool) {
        return timestamps[id] > 0;
    }

```

##

## [L-12] Redundant Guardian Reassignment and Potential Governance Manipulation Risk

In the current implementation, the setGuardian function allows reassigning the same old guardian address as the new guardian, which could lead to unintended behavior or governance inefficiencies. There is no validation to prevent assigning the old guardian as the new one.

Allowing the same guardian to be assigned might defeat the purpose of role transitions intended to rotate power or responsibility between different addresses. There is no point to revoke ``oldguardian`` to ``address(0)`` then assigning same guardian as ``newGuardian``. 

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

/// @notice function to grant the guardian to a new address
    /// resets the pauseStartTime to 0, which unpauses the contract
    /// @param newGuardian the address of the new guardian
    function setGuardian(address newGuardian) public onlyTimelock {
        /// if a new guardian is granted, the contract is automatically unpaused
        _setPauseTime(0);

        _grantGuardian(newGuardian);
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L812-L820

### Recommended Mitigation

Store oldGuardian to any state variable and check newGuardian with old guardian

```solidity

require(oldGuardian != newGuardian , ``Can't be old guardian``);

```

##

## [L-13] Critical Immutable Variables Assigned Without Validation in Constructor

The constructor of this contract is responsible for initializing several critical immutable variables, such as the addresses for key components like factories, guards, and proxy logic. However, there are no validation checks on these addresses, which introduces risks.

The constructor assigns values directly to important variables such as ``safeProxyFactory``, ``timelockFactory``, and ``guard`` without validating that these addresses are correct (e.g.address(0)).Since these variables are marked as ``immutable``, they cannot be changed after the constructor completes execution.Any error during initialization will make the contract permanently misconfigured or only redeploy the contract.

```solidity
FILE: 2024-10-kleidi/src/InstanceDeployer.sol

 /// @notice initialize with all immutable variables
    constructor(
        address _safeProxyFactory,
        address _safeProxyLogic,
        address _timelockFactory,
        address _guard,
        address _multicall3
    ) {
        safeProxyFactory = _safeProxyFactory;
        safeProxyLogic = _safeProxyLogic;
        timelockFactory = _timelockFactory;
        guard = _guard;
        multicall3 = _multicall3;
    }

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L108-L120

### Recommended Mitigation
Add address(0) check 

##

## [L-14] Improper Memory Alignment in Assembly Block

The issue arises because the free memory pointer is updated to [mstore(0x40, add ptr, 97](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L350) ptr + 97, which is not a multiple of 32, violating Solidity’s memory alignment expectations. 


```solidity
FILE:2024-10-kleidi/src/InstanceDeployer.sol

 mstore(0x40, add(ptr, 97))

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L350

### Recommended Mitigation
Align Memory Allocations to 32-Byte Boundaries

##

## [L-15] Unsafe Assembly Blocks

Some assembly blocks that are marked as safe do not follow the Solidity memory model outlined in the [Memory Safety section](https://docs.soliditylang.org/en/v0.8.26/assembly.html#memory-safety) of the Solidity documentation. This might lead to incorrect and undefined behavior.

The original code with assembly ("memory-safe") was not memory-safe because it updated the free memory pointer to a non-aligned address. The corrected version aligns memory to the nearest 32-byte boundary, ensuring safe and predictable memory operations. By following this pattern, you prevent potential data corruption, alignment issues, and ABI decoding errors, making the assembly block truly memory-safe.


```solidity
FILE: 2024-10-kleidi/src/InstanceDeployer.sol


  assembly ("memory-safe") {

```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L342

### Recommended Mitigation
Consider removing the `memory-safe` annotations from assembly blocks that do not follow the Solidity memory model.

##

## [L-16] Lack of Access Control on Critical ``initialize()`` Function

The ``initialize()`` function is a critical setup function that allows the caller to initialize important parameters, including calldata checks. However, there is no access control restricting who can call this function. This creates a security risk since any unauthorized user can call the ``initialize()`` function and potentially set malicious or incorrect data.

If any one adds Calldata unintented way there is no way to resetting the call data again after setting initialized to ``true``.This is crucial function must be called only through access control.

```solidity
FILE:2024-10-kleidi/src/Timelock.sol

/// @param contractAddresses the address of the contract that the calldata check is added to
    /// @param selectors the function selector of the function that the calldata check is added to
    /// @param startIndexes the start indexes of the calldata
    /// @param endIndexes the end indexes of the calldata
    /// @param datas the calldata that is stored
    function initialize(
        address[] memory contractAddresses,
        bytes4[] memory selectors,
        uint16[] memory startIndexes,
        uint16[] memory endIndexes,
        bytes[][] memory datas
    ) external {
        require(!initialized, "Timelock: already initialized");
        initialized = true;

        _addCalldataChecks(
            contractAddresses, selectors, startIndexes, endIndexes, datas
        );
    }


```
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L311-L329

### Recommended Mitigation
Add the access control like ``onlyTimelock``




















