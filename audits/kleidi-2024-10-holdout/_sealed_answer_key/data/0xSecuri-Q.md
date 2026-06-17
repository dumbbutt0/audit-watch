## Low Severity Findings

|            | Issue                                        |
| ---------- | :------------------------------------------- |
| [L-1](#L1) | Use of `assert` Statements in Production Code |
| [L-2](#L2) | Embedding Modifier in Private Function Reduces Contract Size |

## Non-Critical Findings

|            | Issue                                         |
| ---------- | :-------------------------------------------- |
| [NC-1](#NC1) | Incorrect Inline Documentation in `Timelock::atIndex` Function |
| [NC-2](#NC2) | Inefficient Gas Usage in `getCalldataChecks` Function |
| [NC-3](#NC3) | Redundant `require` Check in `Timelock` Contract |
| [NC-4](#NC4) | Unnecessary Type Casting in `Constants.sol` |
| [NC-5](#NC5) | Unused Imports in `TimelockFactory` |
| [NC-6](#NC6) | Unnecessary `eq` Usage in Inline Assembly in `RecoverySpell.sol` |
| [NC-7](#NC7) | Unnecessary Loading of State Variable in `Timelock.sol` |
| [NC-8](#NC8) | Solidity Naming Convention Violation |


## Low Severity Findings

---

### [L-1] **Use of `assert` Statements in Production Code**

#### Summary
The protocol utilizes the `assert` statement in multiple locations within the production code, which is intended only for testing purposes. Unlike `require`, `assert` statements do not provide clear error messages, nor do they refund gas, potentially increasing transaction costs. For additional information, please see this article: [Assert vs. Require in Solidity](https://codeforgeek.com/assert-vs-require-in-solidity/).

#### Affected Code Snippets

- `InstanceDeployer.sol`: Lines [218-219](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L218-L219), [247-248](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L247-L248), [332](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/InstanceDeployer.sol#L332
)
- `Timelock.sol`: Lines [674](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L674), [696](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L696), [914-915](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L914-L915), [1215](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1215
), [1229-1230](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1229-L1230
), and [1278](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1278)


#### Recommended Mitigation Steps
Replace all `assert` statements with `require` statements or `if-else` constructs combined with `revert` and custom error messages. Using `require` provides clarity on failure points and allows for gas refunds, making code reliability easier and helping with debugging.

---

### [L-2] Embedding Modifier in Private Function Reduces Contract Size

Consider consolidating the logic of a modifier within a private function to optimize contract size. Employing a private visibility, which is more efficient for function calls compared to internal visibility, is advisable since the modifier will exclusively invoke this function internally within the contract.

For example, the modifier referenced below could be refactored as demonstrated:
https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L338-L341

```diff
-    modifier onlySafe() {
+    function _onlySafe() private view {
       require(msg.sender == safe, "Timelock: caller is not the safe");
+    }
+    modifier onlySafe() {
+        _onlySafe();
       _;
   }

```

---

## Non-Critical Findings

---

### [NC-1] **Incorrect Inline Documentation in `Timelock::atIndex` Function**

#### Summary
The inline documentation for the `Timelock::atIndex` function incorrectly states that it returns the proposal ID at the specified index, whereas the function actually returns the proposal itself. 

```solidity
@>  /// @notice returns the proposal id at the specified index in the set
    function atIndex(uint256 index) external view returns (bytes32) {
@>       return _liveProposals.at(index);
    }
```

#### Recommended Mitigation Steps
Update the inline documentation to reflect the actual return value of the function accurately.

---

### [NC-2] **Inefficient Gas Usage in `getCalldataChecks` Function**

#### Summary
The `getCalldataChecks` function iterates over the `indexes` array, a state variable, resulting in multiple `SLOAD` operations (~100 gas per load). Given that `indexDatas.length` is equal to `indexes.length`, a memory variable can store the length to reduce redundant gas usage.

```solidity
function getCalldataChecks(address contractAddress, bytes4 selector)
    public
    view
    returns (IndexData[] memory indexDatas)
{
@>  Index[] storage indexes = _calldataList[contractAddress][selector];
    indexDatas = new IndexData[](indexes.length);

@>   for (uint256 i = 0; i < indexes.length; i++) {
        indexDatas[i] = IndexData(
            indexes[i].startIndex,
            indexes[i].endIndex,
            indexes[i].dataHashes.values()
        );
    }
}
```

#### NOTE 
I know this is a gas optimization but I noticed that the protocol team cares about gas usage, I know that there isn't a gas pot, however I still wanted to add more value for the protocol team.

#### Recommended Mitigation Steps
Optimize gas usage by creating a local memory variable to store `indexes.length` instead of repeatedly accessing the state variable.

---

### [NC-3] **Redundant `require` Check in `Timelock` Contract**

#### Summary
The `Timelock::schedule` function includes a redundant `require` statement that checks for duplicate IDs, which is already handled within the `_schedule` method as mentioned with the comment.

```solidity
function schedule(
    address target,
    uint256 value,
    bytes calldata data,
    bytes32 salt,
    uint256 delay
) external onlySafe whenNotPaused {
    bytes32 id = hashOperation(target, value, data, salt);

@>  // Redundant check as _schedule also performs this check.
@>  require(_liveProposals.add(id), "Timelock: duplicate id");
}
```

#### Recommended Mitigation Steps
Remove the redundant `require` statement to avoid unnecessary computation. This can also be applied to the `scheduleBatch` function.

---

### [NC-4] **Unnecessary Type Casting in `Constants.sol`**

#### Summary
A type casting in `Constants.sol` (`uint256 constant _DONE_TIMESTAMP = uint256(1);`) is unnecessary and may confuse developers. It is unclear if this casting is intended for a specific purpose or if it was meant to represent another value (e.g `uint256(-1)`).

#### Recommended Mitigation Steps
Simplify by removing the explicit casting and setting `_DONE_TIMESTAMP` to `1` directly. 

---

### [NC-5] **Unused Imports in `TimelockFactory`**

#### Summary
The import `import {calculateCreate2Address} from "src/utils/Create2Helper.sol";` in the `TimelockFactory` file is not utilized.

#### Recommended Mitigation Steps
Remove the unused import.

---

### [NC-6] **Unnecessary `eq` Usage in Inline Assembly in `RecoverySpell.sol`**

#### Summary
In `RecoverySpell.sol`, `eq(valid, 1)` is used in inline assembly, which could be simplified to `if (valid)` since `valid` is a boolean. Simplifying the code would make it more readable.

```solidity
bool valid;
assembly ("memory-safe") {
    valid := tload(recoveredAddress)
    if eq(valid, 1) { tstore(recoveredAddress, 0) }
}
```

#### Recommended Mitigation Steps
Replace `if eq(valid, 1)` with `if (valid)` for readability and simplicity.

---

### [NC-7] **Unnecessary Loading of State Variable in `Timelock.sol`**

#### Summary
In `Timelock.sol`, the code loads the `indexes` state variable multiple times, which is redundant since it has already been loaded once.

[Timelock.sol#L1089](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1089)
```solidity
@>      Index[] storage calldataChecks = _calldataList[contractAddress][selector];

        uint256 listLength = calldataChecks.length;

        if (listLength == 1) {
            require(
                calldataChecks[0].startIndex != calldataChecks[0].endIndex,
                "CalldataList: Cannot add check with wildcard"
            );
        }
        if (startIndex == endIndex) {
            require(startIndex == 4, "CalldataList: End index equals start index only when 4");
            require(listLength == 0, "CalldataList: Add wildcard only if no existing check");
            require(data.length == 0, "CalldataList: Data must be empty");
        } else {
            require(endIndex > startIndex, "CalldataList: End index must be greater than start index");
            /// if we are adding a concrete check and not a wildcard, then the
            /// calldata must not be empty
            require(data.length != 0, "CalldataList: Data empty");
        }

@>      Index[] storage indexes = _calldataList[contractAddress][selector]; // @audit-issue Unnecessary load, as we already have the indexes loaded above.
```

#### Recommended Mitigation Steps
Use the initially loaded variable and avoid duplicate loading.

---

### [NC-8] **Solidity Naming Convention Violation**

#### Summary
A variable name (`safeInitdata`) does not adhere to Solidity naming conventions, which recommend camelCase. In the following snippet, `safeInitdata` should be renamed to `safeInitData`.

[AddressCalculation.sol#L70](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/views/AddressCalculation.sol#L70)
```solidity
@> bytes memory safeInitdata = abi.encodeWithSignature(
      "setup(address[],uint256,address,bytes,address,address,uint256,address)",
      factoryOwner, 1, address(0), "", address(0), address(0), 0, address(0)
);
```

#### Recommended Mitigation Steps
Rename `safeInitdata` to `safeInitData` to align with Solidity conventions.