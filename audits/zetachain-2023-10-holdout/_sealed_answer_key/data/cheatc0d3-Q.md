# Zetachain QA Report

### The constructor does not validate the `systemContractAddress_` parameter passed in. This could allow setting it to the zero address initially.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60

**Recommendation:** Validate `systemContractAddress_` is not zero address in constructor:

```solidity
require(systemContractAddress_ != address(0), "Invalid system contract"); 
```

### Using `uint8` for `_decimals` wastes gas.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99

**Recommendation:** Use `uint32` instead to optimize gas usage.

### Lack of input validation

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256

```diff
- function withdraw(uint amount) external {
+ function withdraw(uint amount) external {
+   require(amount > 0, "Invalid amount");
+   require(balanceOf(msg.sender) >= amount, "Insufficient balance");
   // Transfer tokens 
}
```  
### No events emitted on critical updates shows lack of transparency

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103

```solidity
event ZetaExchanged(
    address indexed from,
    address indexed to,
    uint256 amount
);

function getZetaFromEth(
  // ...
  uint256 amountOut  
) external payable override returns (uint256) {
  
  emit ZetaExchanged(msg.sender, destinationAddress, amountOut);  

  return amountOut;
}
```

### if-statement can be converted to a ternary

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L171

**Summary:** Simplify if-statements to ternary operators for conciseness.

*Code Snippet:*
```solidity
// Before
if (paused) {
    revert IsPaused();
} else {
    // Other logic
}

// After
paused ? revert IsPaused() : otherLogic();
```

### Lack of validation for initialization code length in `safeCreate2`

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87

This could allow extremely long initialization code to be passed in.

**Fix:** Validate initialization code length.

```diff
function safeCreate2(
  bytes32 salt,
  bytes memory initializationCode
) public payable containsCaller(salt) returns (address) {

+ require(initializationCode.length > 0 && initializationCode.length <= 24576, "Invalid init code length");
  
  return safeCreate2Internal(salt, initializationCode); 
}
```

### Multiple calls to `keccak256()`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L42

**Fix:** Call once and store hash in variable ([G-09]).

```diff
- keccak256(abi.encodePacked(//...))
+ bytes32 initCodeHash = keccak256(abi.encodePacked(//...)); 
+ initCodeHash
```

### Missing NatSpec comments on state variables

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L24

**Fix:** Add descriptions for `_deployed`.

```diff
+ /// @dev Mapping to track deployed contract addresses 
mapping(address => bool) private _deployed;
```

### Long parameter list in `onReceive()`

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172

**Fix:** Move parameters into a struct to allow inlining.

```diff
function onReceive(
-   bytes calldata zetaTxSenderAddress, 
-   uint256 sourceChainId,
-   address destinationAddress,
-   uint256 zetaValue,
-   bytes calldata message,
+   ReceiveParams calldata params 
   bytes32 internalSendHash  
 ) external virtual {}

+ struct ReceiveParams {
+    bytes zetaTxSenderAddress;
+    uint256 sourceChainId; 
+    address destinationAddress;
+    uint256 zetaValue;
+    bytes message; 
+ }
```

### Consider adding NatSpec comments

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151

**Fix:** Add `@notice` and `@dev` tags for functions, `@param` and `@return` for arguments.

```diff
+ /// @notice Pause Zeta transfers 
+ /// @dev Only pauser role can call this 
 function pause() external onlyPauser { 
   // ...
 }
```

### Use named imports

**Fix:** Import specific contract names.

```diff
- import "@openzeppelin/contracts/security/Pausable.sol";
+ import { Pausable } from "@openzeppelin/contracts/security/Pausable.sol";
```


### Long parameter list in `depositAndCall()` 

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67

**Fix:** Move parameters into struct to allow inlining.

```diff 
function depositAndCall(
- zContext calldata context,  
- address zrc20,
- uint256 amount,
- address target, 
- bytes calldata message
+ DepositParams calldata params
) external {

+ struct DepositParams {
+   zContext context;
+   address zrc20;
+   uint256 amount;
+   address target;
+   bytes message;  
+ } 
```

### Use named imports

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4

**Fix:** Import specific contract names.

```diff 
- import "./interfaces/zContract.sol";
+ import { zContract } from "./interfaces/zContract.sol"; 
```


### State variable `wzeta` not cached  

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

**Description**: The `wzeta` state variable is read multiple times without being cached in a local storage pointer. This causes unnecessary SLOADs costing additional gas.

**Recommendation:** Cache `wzeta` in a local storage pointer:

```solidity 
address wzeta_ = wzeta;
if (!WZETA(wzeta_).transferFrom(...)) {
  revert WZETATransferFailed(); 
}
WZETA(wzeta_).withdraw(...);
```
### Missing access modifier

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74

The external exchange functions lack access control. This could lead to loss of funds.

```solidity
modifier onlyOwner() {
  require(msg.sender == owner, "Not owner");
  _;
}

function getZetaFromEth(
  // ...
) external payable override onlyOwner returns (uint256) {
  // ...
}
```


### No events emitted on critical updates shows lack of transparency

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74

The contract lacks events for token exchanges.

```solidity
event TokenExchange(
  address indexed from,
  address indexed to, 
  uint256 amount
);

function getZetaFromEth(
  // ...
) external payable override returns (uint256) {

  emit TokenExchange(msg.sender, destinationAddress, amountOut);
  
  return amountOut;
}
```
### Lack of caching for state variables

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L43

**Fix**: Introduce local variables to avoid multiple external calls.

```diff
function _isValidCaller() private view {
+ ZetaConnector connector_ = connector;
+ if (msg.sender != address(connector_)) {
    revert InvalidCaller(msg.sender); 
}
```
### Usage of non-optimized Solidity version

**Fix**: Use Solidity 0.8.19 or newer to enable the latest optimizations.
