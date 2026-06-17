| S.No | Title                                                                                                      |
|------|------------------------------------------------------------------------------------------------------------|
| **L-01** | Potential Under-Utilization of Return Values in ERC20 Standard Functions                                   |
| **L-02** | Lack of Event Emission in Critical State-Changing Functions                                                |
| **L-03** | Insufficient Validation in the `burn` Function                                                             |
| **L-04** | Redundant Code in `_msgSender` and `_msgData` Functions                                                    |
| **L-05** | Inconsistent Error Handling Strategy                                                                       |
| **L-06** | Unrestricted Access to Update Functions                                                                    |
| **L-07** | Lack of Input Validation in `transfer`, `transferFrom`, and `burn` Functions                               |
| **L-08** | Missing Return Value Documentation in View Functions                                                       |
| **L-09** | Necessity for Zero Address Checks in Multiple Functions                                                    |
| **L-10** | Potential Risk in Token Approval Handling                                                                  |
| **L-11** | Potential Incomplete Error Handling in `getEthFromZeta` Function                                           |
| **L-12** | Unrestricted Ether Receipt via Fallback Function                                                           |
| **L-13** | Redundant Initialization of State Variables                                                                |
| **L-14** | Inadequate Liquidity Check Mechanism                                                                       |
| **L-15** | Potential Miscalculation of Swap Fees in Token Exchanges                                                    |
| **L-16** | Oversight in Handling Price Limits for Swap Transactions                                                   |
| **L-17** | Use of Hardcoded Constant `MAX_DEADLINE`                                                                   |
| **L-18** | Potential Logical Flaw in Reentrancy Guard Implementation                                                  |
| **L-19** | Misuse of `unwrap` Flag in `getEthFromZeta` Function                                                       |
| **L-20** | Absence of Deadline Handling in Token Exchange Functions                                                   |
| **L-21** | Inconsistent Liquidity Check in `hasZetaLiquidity` Method                                                  |
| **L-22** | Potential Rounding Error in Swap Amount Calculations                                                       |
| **L-23** | Potential Discrepancy in Zeta Fee Handling                                                                 |
| **L-24** | Unclear Handling of Token Transfer Fees in `deposit`                                                       |
| **L-25** | Lack of Check Against Zero Asset Amount in `deposit` and `withdraw`                                        |
| **L-26** | Potential for Unintended TSSAddressUpdater Privilege Persistence                                           |
| **L-27** | Lack of Return Value Check for ERC20 `safeTransfer` and `safeTransferFrom`                                 |
| **L-28** | Hardcoded Deadline in Uniswap Transactions May Lead to Unpredictable Behavior                              |
| **L-29** | Reliance on `block.timestamp` for Transaction Timing                                                       |
| **L-30** | Lack of Validation for `destinationAddress` Parameter in Swap Functions                                    |
| **L-31** | Insufficient Validation in `setMaxSupply` Function                                                         |
| **L-32** | Use of `tx.origin` in `send` Function May Lead to Vulnerabilities                                          |




### [L-01]Potential Under-Utilization of Return Values in ERC20 Standard Functions

### File : ZRC20.sol

### Description
In the `approve`, `transfer`, and `transferFrom` functions, the contract correctly executes the required state changes but does not utilize the return values from internal function calls. According to the ERC20 standard, these functions are expected to return a boolean value indicating the success or failure of the operation. While the contract does return `true` at the end of these functions, there could be situations where the internal function calls might fail silently without reverting the transaction, leading to misleading return values.

### Code Snippet
```solidity
function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
    _transfer(_msgSender(), recipient, amount);
    return true;
}

function approve(address spender, uint256 amount) public virtual override returns (bool) {
    _approve(_msgSender(), spender, amount);
    return true;
}

function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
    _transfer(sender, recipient, amount);
    // Missing check for the result of the _transfer and _approve operations
    return true;
}
```

### Expected Behavior
The `transfer`, `approve`, and `transferFrom` functions should return the result of their respective internal function calls. This ensures that the return value accurately reflects the outcome of the operation, as per the ERC20 standard.

### Actual Behavior
The functions always return `true` regardless of the success or failure of the internal operations. This could lead to scenarios where, despite an internal failure, the functions report a successful operation.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)

---

### [L-02]Lack of Event Emission in Critical State-Changing Functions

### File : ZRC20.sol

### Description
The contract lacks event emissions in several critical functions that change the contract's state, notably in the `updateSystemContractAddress`, `updateGasLimit`, and `updateProtocolFlatFee` functions. While these functions do alter important state variables, they do not emit any events to log these changes. In Solidity and blockchain development, events are crucial for tracking state changes, especially for off-chain monitoring and user interfaces.

### Code Snippet
```solidity
function updateSystemContractAddress(address addr) external onlyFungible {
    SYSTEM_CONTRACT_ADDRESS = addr;
    // Missing event emission here
}

function updateGasLimit(uint256 gasLimit) external onlyFungible {
    GAS_LIMIT = gasLimit;
    // Missing event emission here
}

function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
    PROTOCOL_FLAT_FEE = protocolFlatFee;
    // Missing event emission here
}
```

### Expected Behavior
The functions `updateSystemContractAddress`, `updateGasLimit`, and `updateProtocolFlatFee` should emit events whenever they are called and successfully change the contract's state. This is essential for transparency and traceability.

### Actual Behavior
No events are emitted in these functions after the state changes. This lack of event logs can make it difficult to track the changes made to key contract parameters, especially in a decentralized environment where transparency is crucial.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270)
---


### [L-03]Insufficient Validation in the `burn` Function

### File : ZRC20.sol

### Description
The `burn` function in the contract allows users to destroy (burn) their tokens, reducing the total supply. However, this function lacks explicit validation to ensure that the amount to be burned is greater than zero. While burning zero tokens technically doesn't affect balances or total supply, allowing such a transaction is inefficient and could lead to unnecessary network congestion or confusion for users.

### Code Snippet
```solidity
function burn(uint256 amount) external returns (bool) {
    _burn(msg.sender, amount);
    return true;
}
```

### Expected Behavior
The `burn` function should include a check to ensure that the `amount` to be burned is greater than zero. This is a standard practice to avoid pointless transactions and to make the function's intent and effects clearer to users.

### Actual Behavior
Currently, the `burn` function allows burning of zero tokens. Although this does not pose a security risk or a functional issue in the contract, it can be seen as an unnecessary operation that could be easily prevented.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173)
---


### [L-04]Redundant Code in `_msgSender` and `_msgData` Functions

### File : ZRC20.sol

### Description
The contract includes custom internal functions `_msgSender` and `_msgData` that simply return the `msg.sender` and `msg.data` respectively. However, these functions don't add any additional logic or checks beyond what is already provided by Solidity's native `msg.sender` and `msg.data`. This redundancy might lead to confusion and slightly increased bytecode size without any practical benefit.

### Code Snippet
```solidity
function _msgSender() internal view virtual returns (address) {
    return msg.sender;
}

function _msgData() internal view virtual returns (bytes calldata) {
    return msg.data;
}
```

### Expected Behavior
Normally, custom functions like `_msgSender` and `_msgData` are used when there's a need to add extra logic (e.g., for meta-transactions or to modify the standard behavior of `msg.sender` and `msg.data`). If no such custom logic is required, directly using `msg.sender` and `msg.data` in the contract would be more straightforward and efficient.

### Actual Behavior
The contract defines `_msgSender` and `_msgData` without providing additional functionality beyond the standard `msg.sender` and `msg.data`. This can be seen as unnecessary code, which ideally should be avoided to keep the contract clean and efficient.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41)
---


### [L-05]Inconsistent Error Handling Strategy

### File : ZRC20.sol

### Description
The contract employs custom errors for various checks and conditions, which is a good practice for gas efficiency and readability. However, there is an inconsistency in the error handling strategy. While most functions use custom errors, some critical checks rely on inline require statements with string messages. This inconsistency can lead to a less uniform and potentially more confusing codebase, especially for future maintainers or auditors of the contract.

### Code Snippet
In the constructor, the contract uses a custom error for a specific check:
```solidity
if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```
In contrast, other parts of the contract might use `require` statements with string error messages for similar checks, which is not shown in the provided snippet but is a common practice in many contracts.

### Expected Behavior
The contract should employ a consistent error handling strategy throughout. If custom errors are used, they should be used uniformly across the contract for all revert conditions. This approach enhances readability and maintainability, making it easier to understand and manage the contract's error handling logic.

### Actual Behavior
The provided code snippet indicates the use of custom errors, but there may be other parts of the contract (or in commonly associated patterns) that use `require` statements with string messages. This inconsistency can make the contract less coherent in terms of error handling.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53)

---


### [L-06]Unrestricted Access to Update Functions

### File : ZRC20.sol

### Description
The contract includes several functions (`updateSystemContractAddress`, `updateGasLimit`, and `updateProtocolFlatFee`) that allow updating critical contract parameters. These functions use the `onlyFungible` modifier for access control, which restricts access to the `FUNGIBLE_MODULE_ADDRESS`. However, there seems to be no mechanism in place to change the `FUNGIBLE_MODULE_ADDRESS` itself if needed, for instance, in case of a security issue with the current address or a protocol upgrade. This could lead to a situation where the contract's critical settings become unmodifiable if the `FUNGIBLE_MODULE_ADDRESS` is compromised or needs to be changed for any reason.

### Code Snippet
```solidity
modifier onlyFungible() {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    _;
}

function updateSystemContractAddress(address addr) external onlyFungible {
    SYSTEM_CONTRACT_ADDRESS = addr;
    // ...
}

function updateGasLimit(uint256 gasLimit) external onlyFungible {
    GAS_LIMIT = gasLimit;
    // ...
}

function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
    PROTOCOL_FLAT_FEE = protocolFlatFee;
    // ...
}
```

### Expected Behavior
Ideally, the contract should include a mechanism to update the `FUNGIBLE_MODULE_ADDRESS` itself in a secure and controlled manner. This could be through a multi-signature process, a timelock, or any other governance mechanism that suits the protocol's security needs.

### Actual Behavior
The contract has functions that are only accessible by `FUNGIBLE_MODULE_ADDRESS`, but there is no way to update this address. This could potentially lead to administrative challenges or security risks if the address needs to be changed in the future.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270)

---


### [L-07]Lack of Input Validation in `transfer`, `transferFrom`, and `burn` Functions

### File : ZRC20.sol

### Description
The contract's `transfer`, `transferFrom`, and `burn` functions do not perform explicit checks on the `amount` parameter to ensure it is greater than zero. While transferring or burning zero tokens does not pose a security risk or functional issue, it can result in unnecessary transactions that waste network resources and could be misleading for users.

### Code Snippet
```solidity
function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
    _transfer(_msgSender(), recipient, amount);
    return true;
}

function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
    _transfer(sender, recipient, amount);
    // ...
    return true;
}

function burn(uint256 amount) external returns (bool) {
    _burn(msg.sender, amount);
    return true;
}
```

### Expected Behavior
These functions should include checks to ensure that the `amount` being transferred or burned is greater than zero. This is a standard practice to prevent pointless transactions and can also serve as a safeguard against potential errors in dApp interfaces or smart contract interactions.

### Actual Behavior
Currently, these functions allow the transfer or burning of zero tokens. Although this does not directly impact the contract's functionality or security, it can be seen as an unnecessary operation that could be easily prevented.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)

---


### [L-08]Missing Return Value Documentation in View Functions


### File : ZRC20.sol

### Description
The contract includes several view functions (`name`, `symbol`, `decimals`, `totalSupply`, `balanceOf`, and `allowance`) that return important token information. However, the contract does not provide explicit documentation in the form of comments for the return values of these functions. While Solidity's syntax makes it clear what type of value is being returned, the purpose and significance of these values might not be immediately clear, especially to someone less familiar with ERC20 tokens or the specific intentions of this contract.

### Code Snippet
```solidity
function name() public view virtual override returns (string memory) {
    return _name;
}

function symbol() public view virtual override returns (string memory) {
    return _symbol;
}

// ... Similar for other view functions ...
```

### Expected Behavior
These view functions should include comments that explain what each return value represents. For example, a comment for `name` could explain that it returns the token's name, and for `totalSupply`, that it returns the current total supply of the token. This documentation helps in understanding the contract's functionality and makes the codebase more accessible to developers and auditors.

### Actual Behavior
Currently, these functions lack comments explaining the return values. While experienced Solidity developers and those familiar with ERC20 standards might understand these functions intuitively, the lack of documentation could pose a barrier to understanding for others.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83)
---

### [L-09]Necessity for Zero Address Checks in Multiple Functions

### File : ZRC20.sol

### Description
In the `ZRC20` smart contract, several functions interact with address parameters. These functions should include checks to ensure that these addresses are not the zero address (`0x0`). Interactions with the zero address in the context of transfers, approvals, minting, burning, and administrative actions can lead to undesired behavior and potential loss of tokens. The functions needing such checks are identified below.

### Code Snippet
The following functions in the contract require zero address validations:

1. **`transfer`** (for `recipient`):
   ```solidity
   function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
       _transfer(_msgSender(), recipient, amount);
       return true;
   }
   ```

2. **`approve`** (for `spender`):
   ```solidity
   function approve(address spender, uint256 amount) public virtual override returns (bool) {
       _approve(_msgSender(), spender, amount);
       return true;
   }
   ```

3. **`transferFrom`** (for `recipient`):
   ```solidity
   function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
       _transfer(sender, recipient, amount);
       ...
   }
   ```

4. **`_transfer`** (for `sender` and `recipient`):
   ```solidity
   function _transfer(address sender, address recipient, uint256 amount) internal virtual {
       ...
   }
   ```

5. **`_burn`** (for `account`):
   ```solidity
   function _burn(address account, uint256 amount) internal virtual {
       ...
   }
   ```

6. **`_mint`** (for `account`):
   ```solidity
   function _mint(address account, uint256 amount) internal virtual {
       ...
   }
   ```

7. **`deposit`** (for `to`):
   ```solidity
   function deposit(address to, uint256 amount) external override returns (bool) {
       ...
   }
   ```

8. **`updateSystemContractAddress`** (for new `addr`):
   ```solidity
   function updateSystemContractAddress(address addr) external onlyFungible {
       ...
   }
   ```

9. **`_approve`** (for `owner` and `spender`):
   ```solidity
   function _approve(address owner, address spender, uint256 amount) internal virtual {
       ...
   }
   ```

### Expected Behavior
Each of these functions should include a validation step to ensure that the relevant address parameters are not the zero address. This validation is crucial for preventing accidental loss of tokens and maintaining the integrity of the token's operations.

### Actual Behavior
Currently, the functions listed do not explicitly include checks to prevent interaction with the zero address. This omission could lead to inadvertent token transfers to or approvals for the zero address, potentially resulting in unrecoverable token loss or other unintended effects.

### Github : [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)
---


_____________________________________________________________________________________________________________________________________________________




### [L-10]Potential Risk in Token Approval Handling

### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The contract uses `safeApprove` from OpenZeppelin's SafeERC20 library to set allowances for the PancakeSwap V3 Router. However, the contract does not reset the allowance to zero before setting a new allowance. This practice can potentially lead to an issue known as the "approve/transferFrom attack vector" if the user is not aware of the existing allowance. Although this risk is more theoretical than practical, especially with reputable entities like PancakeSwap, it is considered a best practice to first set the allowance to zero before setting a new value.

### Code Snippet
```solidity
IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
// and
IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
```

### Expected Behavior
The expected best practice is to first reset the token allowance to zero and then set the new allowance. This mitigates any risks associated with the ERC20 `approve` function.

### Actual Behavior
The current implementation directly sets a new allowance without resetting it to zero first. This could potentially expose the contract to the mentioned risk, albeit very minimal and theoretical in this context.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L136)

---

### [L-11]Potential Incomplete Error Handling in `getEthFromZeta` Function

### File : ZetaTokenConsumerPancakeV3.strategy.sol


### Description
The `getEthFromZeta` function involves an ETH transfer using a low-level `call` method. While it does correctly check for the success of the call and reverts in case of failure, the contract does not log the reason for this failure. This lack of detailed error reporting can make it difficult to diagnose issues in the case of failed transactions.

### Code Snippet
```solidity
(bool sent, ) = destinationAddress.call{value: amountOut}("");
if (!sent) revert ErrorSendingETH();
```

### Expected Behavior
When a call to transfer ETH fails, the contract should ideally provide more information about the failure. This can be achieved by using a custom error that includes the returned data from the failed call, giving more context about the failure.

### Actual Behavior
The contract simply reverts with `ErrorSendingETH()` without any additional information about why the transfer failed. While this does not pose a direct security risk, it can obscure underlying issues and make troubleshooting more challenging.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178)



---

### [L-12]Unrestricted Ether Receipt via Fallback Function


### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The contract includes a fallback function to receive Ether (ETH). This function is empty and lacks any access control, meaning that anyone can send ETH to the contract without any restriction or logging. While this might be intentional to allow the contract to receive ETH from various sources, it can lead to untracked Ether deposits. Unrestricted and unlogged Ether receipts might complicate the contract's financial tracking and could potentially be exploited in specific scenarios (e.g., to inflate the contract's balance artificially).

### Code Snippet
```solidity
receive() external payable {}
```

### Expected Behavior
Ideally, the receipt of Ether should be accompanied by event logging, or there should be some form of access control to restrict who can send Ether to the contract. This would ensure better tracking and management of funds sent to the contract.

### Actual Behavior
Currently, the contract can receive Ether from any address without any restrictions or logging. This lack of control and visibility over incoming funds may not align with the best practices for financial management in smart contracts.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101)


---

### [L-13]Redundant Initialization of State Variables


### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The contract declares several state variables as `immutable`, meaning they can only be set once during contract construction and cannot be changed afterward. However, the constructor includes explicit checks to ensure that these `immutable` variables are not set to the zero address. Since `immutable` variables are uninitialized before the constructor runs, these checks are redundant. The nature of `immutable` variables in Solidity ensures that they must be set during contract deployment, and they cannot hold their default values after the constructor execution completes.

### Code Snippet
```solidity
if (
    zetaToken_ == address(0) ||
    pancakeV3Router_ == address(0) ||
    uniswapV3Factory_ == address(0) ||
    WETH9Address_ == address(0)
) revert ZetaCommonErrors.InvalidAddress();
```

### Expected Behavior
Typically, checks for zero addresses are implemented to prevent incorrect initialization of state variables. However, for `immutable` variables, this check is implicit since these variables must be initialized during contract creation, and the constructor will not execute successfully if they are not properly set.

### Actual Behavior
The constructor includes checks to prevent `immutable` variables from being set to the zero address. While this does not pose a security risk or functional issue, it adds unnecessary code and gas overhead during contract deployment.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L79)



---



### [L-14]Inadequate Liquidity Check Mechanism

### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The function `hasZetaLiquidity` is designed to check for the presence of liquidity in the Uniswap V3 pool between WETH and the Zeta token. However, the function only checks for the existence of the pool and whether its liquidity is greater than zero. This approach may not be sufficient to accurately determine the health or usability of the pool. In practice, a pool might exist and have non-zero liquidity, but the amount of liquidity could still be too low to facilitate meaningful transactions without causing significant slippage.

### Code Snippet
```solidity
function hasZetaLiquidity() external view override returns (bool) {
    address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
    if (poolAddress == address(0)) {
        return false;
    }
    IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
    return pool.liquidity() > 0;
}
```

### Expected Behavior
A more robust liquidity check would consider not only the existence of liquidity but also its depth relative to the size of the transactions the contract expects to handle. This could involve setting a minimum liquidity threshold that is considered sufficient for the contract's operational needs.

### Actual Behavior
The current implementation only checks for the existence of the pool and whether its liquidity is non-zero. This simplistic approach might not provide a reliable indication of the pool's effectiveness for the contract's purposes, especially for larger transactions.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209)

---


### [L-15]Potential Miscalculation of Swap Fees in Token Exchanges

### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The contract facilitates token swaps using Uniswap V3, which involves dynamic fees. However, the contract does not appear to account for these variable fees in its calculations when determining the output amounts in functions like `getZetaFromEth`, `getEthFromZeta`, etc. While the contract correctly uses `minAmountOut` to protect against slippage, it does not calculate or consider the actual swap fees which might be higher or lower than expected, especially in highly volatile market conditions or pools with different fee tiers.

### Code Snippet
```solidity
// Example from getZetaFromEth function
uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
```

### Expected Behavior
In an ideal scenario, the contract should account for the dynamic nature of swap fees. This could involve fetching the current fee rate from the Uniswap pool and using it in the calculation to estimate the actual amount out more accurately. For example, if the fee rate is 0.3%, and the input amount is `X`, the actual amount used for the swap should be `X - (0.003 * X)`.

### Actual Behavior
The current implementation does not explicitly account for varying swap fees in its calculations. It relies on the `minAmountOut` parameter to guard against excessive slippage but does not adjust the input amount for the actual fees charged by the pool.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L120)
---


### [L-16]Oversight in Handling Price Limits for Swap Transactions

### File : ZetaTokenConsumerPancakeV3.strategy.sol

### Description
The contract's functions `getZetaFromEth`, `getEthFromZeta`, `getZetaFromToken`, and `getTokenFromZeta` facilitate token swap operations. In these functions, the `sqrtPriceLimitX96` parameter for the Uniswap V3 swap function is set to zero. This parameter sets a limit on the minimum or maximum price at which the trade will execute, effectively acting as a slippage protection mechanism. However, setting it to zero means that the trade has no price limit, potentially exposing users to unfavorable execution prices in volatile market conditions.

### Code Snippet
```solidity
sqrtPriceLimitX96: 0
// Used in the swap parameters
```

### Expected Behavior
The expected behavior would be to calculate an appropriate `sqrtPriceLimitX96` value that provides a reasonable price range for executing the trade. This value should be derived based on the current pool price and an acceptable slippage percentage. For instance, if the acceptable slippage is 1%, the price limit should be set to the current mid-price ± 1%.

### Actual Behavior
Currently, the contract sets `sqrtPriceLimitX96` to zero, which effectively removes any price limit protection from the swap. This means the swaps could be executed at any price, which might not be favorable to the user, especially in highly volatile market conditions.

### Github : [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L117)


---

_________________________________________________________________________________________________________


### [L-17]Use of Hardcoded Constant `MAX_DEADLINE`

### File : ZetaTokenConsumerTrident.strategy.sol

### Description
The contract defines a constant `MAX_DEADLINE` but does not use it in any of the functions. Hardcoding values, especially when they are not used, can lead to misunderstandings about the contract's logic and intentions. It can also lead to potential future bugs if the constant is later used without a proper understanding of its context or purpose.

### Code Snippet
```solidity
uint256 internal constant MAX_DEADLINE = 200;
```

### Expected Behavior
The contract should either use the defined constants in a meaningful way or avoid declaring unused constants. If `MAX_DEADLINE` is intended for future use, it should be documented clearly to indicate its purpose and how it should be integrated into the contract's functions.

### Actual Behavior
The contract declares a constant `MAX_DEADLINE` with a value of 200 but does not utilize this constant in any of its functions. This leads to unnecessary code bloat and potential confusion.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35)

---


### [L-18]Potential Logical Flaw in Reentrancy Guard Implementation

### File : ZetaTokenConsumerTrident.strategy.sol


### Description
The `nonReentrant` modifier is designed to prevent reentrant calls to certain functions, using the `_locked` state variable. However, this implementation could lead to potential logical issues. If a reentrant call occurs and the contract's state is somehow reverted (for example, due to an exception in an external call), the `_locked` variable would remain set to `true`. This would lock the contract in a state where all functions protected by the `nonReentrant` modifier become inaccessible, even though the reentrancy attempt failed.

### Code Snippet
```solidity
bool internal _locked;

modifier nonReentrant() {
    if (_locked) revert ReentrancyError();
    _locked = true;
    _;
    _locked = false;
}
```

### Expected Behavior
The `nonReentrant` modifier should be resilient to potential state reverts. A more robust pattern is to set the `_locked` variable back to `false` in a `finally`-like block or use built-in mechanisms that automatically handle such cases (e.g., using OpenZeppelin's `ReentrancyGuard`).

### Actual Behavior
The current implementation of `nonReentrant` could potentially leave the contract in a permanently locked state if a reentrant call is made and the contract's state is reverted for any reason after `_locked` is set to `true`.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59)
---


### [L-19]Misuse of `unwrap` Flag in `getEthFromZeta` Function

### File : ZetaTokenConsumerTrident.strategy.sol


### Description
In the `getEthFromZeta` function, there is an `unwrap` parameter set in the `ExactInputSingleParams` struct passed to the `tridentRouter.exactInputSingle` function. The `unwrap` flag is set to `true`, indicating the intention to unwrap WETH into ETH. However, this function deals with the conversion of Zeta tokens into ETH, and the `unwrap` flag's usage here seems misplaced or unnecessary, as the input token is not WETH but Zeta.

### Code Snippet
```solidity
function getEthFromZeta(
    // ...
) external override returns (uint256) {
    // ...

    IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
        // ...
        unwrap: true
    });

    // ...
}
```

### Expected Behavior
The `unwrap` flag is typically used when dealing with WETH (Wrapped ETH) tokens, where you'd want to convert WETH back into ETH. In a function converting Zeta tokens into ETH, the use of this flag should be critically evaluated. If the intermediate step involves converting Zeta to WETH and then unwrapping WETH to ETH, this usage is justified. Otherwise, the flag might be redundant or misleading.

### Actual Behavior
The function uses the `unwrap` flag in a context where its purpose is not clear. This could potentially lead to confusion about the function's behavior or, depending on the implementation details of the `tridentRouter`, might result in incorrect or inefficient execution of the token swap.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136)

---


### [L-20]Absence of Deadline Handling in Token Exchange Functions

### File : ZetaTokenConsumerTrident.strategy.sol


### Description
The contract functions for token exchanges (`getZetaFromEth`, `getZetaFromToken`, `getEthFromZeta`, and `getTokenFromZeta`) involve interactions with a decentralized exchange through `tridentRouter`. Typically, such interactions include a deadline parameter to ensure that the transaction is executed within a certain timeframe, protecting against market volatility and potential front-running attacks. However, there's no apparent handling or inclusion of a deadline parameter in these functions, which could lead to potential risks in highly volatile market conditions.

### Code Snippet
```solidity
function getZetaFromEth(
    // ...
) external payable override returns (uint256) {
    // ...
    IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
        // ...
        // No deadline parameter is being set or used
        // ...
    });
    // ...
}
```

### Expected Behavior
The functions should ideally include a deadline parameter, allowing users to specify the latest block timestamp by which the transaction must be executed. This parameter should be used in the call to the `tridentRouter` to ensure that the trade is executed within a safe timeframe relative to market conditions.

### Actual Behavior
There's no deadline parameter in the token exchange functions, which means these functions do not account for time-based conditions in executing trades. This omission could expose users to risks associated with prolonged execution times, such as price slippage or front-running in volatile markets.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74)

---



### [L-21]Inconsistent Liquidity Check in `hasZetaLiquidity` Method

### File : ZetaTokenConsumerTrident.strategy.sol

### Description
The `hasZetaLiquidity` method is designed to check if there is liquidity for the Zeta token in the Uniswap V3 pool. However, it only checks the liquidity of the WETH9/ZetaToken pool. If the contract is also dealing with other tokens (as seen in the `getZetaFromToken` and `getTokenFromZeta` methods), the liquidity check might not be comprehensive enough. This could lead to scenarios where the contract assumes liquidity is available for operations involving other tokens, but in reality, it might not be, potentially causing failed transactions.

### Code Snippet
```solidity
function hasZetaLiquidity() external view override returns (bool) {
    address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);

    if (poolAddress == address(0)) {
        return false;
    }

    IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
    return pool.liquidity() > 0;
}
```

### Expected Behavior
The expected behavior for a comprehensive liquidity check should account for all token pairs that the contract interacts with. In other words, if the contract is designed to swap Zeta tokens with other ERC20 tokens, the liquidity check method should verify the availability of liquidity for all relevant token pairs.

### Actual Behavior
Currently, the `hasZetaLiquidity` method only checks the liquidity of the WETH9/ZetaToken pool. This might not reflect the actual liquidity situation for other token pairs that the contract might need to interact with.

### Suggested Improvement
Consider enhancing the `hasZetaLiquidity` method to check the liquidity of all token pairs that are relevant to the contract's operations. This could involve iterating over a list of supported tokens or dynamically checking liquidity based on the tokens involved in a specific transaction. This approach will provide a more accurate picture of the available liquidity and reduce the risk of transaction failures due to liquidity issues.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203)

---


### [L-22]Potential Rounding Error in Swap Amount Calculations

### File : ZetaTokenConsumerTrident.strategy.sol


### Description
The functions `getZetaFromEth`, `getZetaFromToken`, `getEthFromZeta`, and `getTokenFromZeta` involve calculations for token swap amounts. These calculations are integral to determining the amount of tokens to send or receive. However, the contract does not explicitly handle potential rounding errors that can occur during these calculations. In token swaps, especially when dealing with tokens having different decimal places or in cases of small transaction amounts, rounding errors can lead to discrepancies between the expected and actual amounts of tokens exchanged. This is more of a concern in the functions that involve intermediate token conversions (like ETH to WETH or Zeta to another token).

### Code Snippet
```solidity
// Example from getZetaFromEth function
uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
```

### Expected Behavior
The expected behavior in token exchange functions is to accurately calculate the amount of tokens to be exchanged, taking into consideration the decimal places and potential rounding errors, to ensure the precision of transactions.

### Actual Behavior
The current implementation does not explicitly address rounding errors in token amount calculations. While the Uniswap V3 Router itself handles some aspects of precision, the contract does not have additional checks or mechanisms to deal with potential discrepancies caused by rounding.

### Suggested Improvement
Implement a mechanism to account for and mitigate rounding errors in token swap calculations. This could include:
- Implementing buffer margins in `minAmountOut` calculations to accommodate potential rounding errors.
- Providing clear documentation or user guidance on how rounding might affect transaction outputs, especially for tokens with different decimal places.
- Conducting thorough testing with various token types and amounts to understand how the contract behaves in scenarios prone to rounding errors, and adjust the logic accordingly.

### Github : [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L93C76-L93C76)

---


### [L-23]Potential Discrepancy in Zeta Fee Handling

### File :ERC20Custody.sol


### Description
In the `deposit` function, the contract allows for the collection of a zeta fee. However, the logic checks if `zetaFee` is non-zero and if `address(zeta)` is not zero before transferring the fee. This logic assumes that if `zetaFee` is non-zero, there is a valid Zeta token address to transfer from. But there is no direct check to ensure that the Zeta token address (`address(zeta)`) is indeed a valid, non-zero address when the fee is set or updated. There's a possibility that `zetaFee` could be set to a non-zero value while the Zeta token address is inadvertently zero or invalid, leading to a failed transaction or an unexpected state when attempting to collect fees.

### Code Snippet
```solidity
if (zetaFee != 0 && address(zeta) != address(0)) {
    zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
}
```

### Expected Behavior
The expected behavior is to have robust checks that ensure the integrity of fee collection logic. This includes verifying that both the fee amount and the token address used for fee collection are valid and non-zero whenever fees are set or updated.

### Actual Behavior
Currently, the contract only checks the validity of the Zeta token address during fee collection in the `deposit` function, but not when `zetaFee` is updated or initially set. This could lead to scenarios where an invalid or zero Zeta token address might be used for fee collection.

### Suggested Improvement
Enhance the logic for setting and updating `zetaFee` to include a check ensuring that the Zeta token address is valid and non-zero. This could be done in the `updateZetaFee` function or any other function that may affect the fee amount or the Zeta token address. Implementing this change will make the fee collection logic more robust and less prone to failures or unexpected behaviors.

### Github : [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177)

---


### [L-24]Unclear Handling of Token Transfer Fees in `deposit`

### File :ERC20Custody.sol


### Description
In the `deposit` function, there is a mechanism to handle potential transfer fees for ERC20 tokens. The contract assumes that if there is a fee on token transfer, the actual amount received might be less than the amount sent. To account for this, the contract calculates the received amount by subtracting the old balance from the new balance of the contract. While this approach accommodates tokens with transfer fees, it may not account for scenarios where the fee is charged to the sender rather than being deducted from the transfer amount. In such cases, the logic might inaccurately reflect the amount deposited.

### Code Snippet
```solidity
uint256 oldBalance = asset.balanceOf(address(this));
asset.safeTransferFrom(msg.sender, address(this), amount);
emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

### Expected Behavior
The expected behavior in handling token deposits is to accurately reflect the amount of tokens deposited in the contract, regardless of the token's fee model (whether the fee is deducted from the transfer amount or charged to the sender).

### Actual Behavior
Currently, the contract assumes that fees are deducted from the transfer amount, which may not be accurate for all ERC20 tokens, especially those that charge the fee to the sender instead. This could lead to discrepancies in the recorded deposit amounts for such tokens.

### Suggested Improvement
Enhance the logic in the `deposit` function to handle different token fee models more accurately. This might involve checking the token's fee model (if possible) or implementing a more flexible approach to account for both types of fee deductions. Alternatively, consider restricting the whitelist to tokens without transfer fees or with a known, consistent fee model to simplify the accounting.

### Github : [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L180)

---



### [L-25]Lack of Check Against Zero Asset Amount in `deposit` and `withdraw`

### File :ERC20Custody.sol

### Description
In the `deposit` and `withdraw` functions of the contract, there is no explicit check to ensure that the `amount` parameter (representing the quantity of the ERC20 asset to be deposited or withdrawn) is greater than zero. While depositing or withdrawing zero assets may not directly cause a functional issue, it could lead to unnecessary transactions, which in turn results in wastage of network resources and user funds (in the form of transaction fees), without any meaningful state change in the contract.

### Code Snippet
```solidity
function deposit(
    bytes calldata recipient,
    IERC20 asset,
    uint256 amount,
    bytes calldata message
) external nonReentrant {
    ...
    asset.safeTransferFrom(msg.sender, address(this), amount);
    ...
}

function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
    ...
    IERC20(asset).safeTransfer(recipient, amount);
    ...
}
```

### Expected Behavior
Ideally, these functions should have a safeguard to prevent zero-amount transactions. This would involve checking if the `amount` is greater than zero and reverting the transaction if it isn't.

### Actual Behavior
Currently, the contract allows depositing and withdrawing of zero assets. While this won't disrupt the contract's functionality, it can cause unnecessary network transactions and user confusion.

### Suggested Improvement
Implement a check at the beginning of the `deposit` and `withdraw` functions to ensure that the `amount` is greater than zero. If the amount is zero, the function should revert with an appropriate error message. This change would prevent pointless transactions and make the contract's behavior more intuitive.

### Github : [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165)
---


### [L-26]Potential for Unintended TSSAddressUpdater Privilege Persistence

### File :ERC20Custody.sol

### Description
The contract includes a function `renounceTSSAddressUpdater` intended to transfer the privilege of updating the TSSAddress to the current TSSAddress itself. This is designed as a security feature to centralize control. However, the function checks if `TSSAddress` is zero but does not verify if `TSSAddress` is different from `TSSAddressUpdater`. If `TSSAddress` and `TSSAddressUpdater` are already the same, calling this function will emit the `RenouncedTSSUpdater` event without actually changing any state. This could mislead administrators or users into believing that a change in privileges has occurred when, in fact, it has not.

### Code Snippet
```solidity
function renounceTSSAddressUpdater() external onlyTSSUpdater {
    if (TSSAddress == address(0)) {
        revert ZeroAddress();
    }
    TSSAddressUpdater = TSSAddress;
    emit RenouncedTSSUpdater(msg.sender);
}
```

### Expected Behavior
The expected behavior in `renounceTSSAddressUpdater` is to ensure that a meaningful change of state occurs - specifically, that the `TSSAddressUpdater` privilege is transferred to the current `TSSAddress` only if they are different.

### Actual Behavior
Currently, the function does not check if `TSSAddress` and `TSSAddressUpdater` are already the same. As a result, it may emit a misleading event without changing any state.

### Suggested Improvement
Add a check in `renounceTSSAddressUpdater` to verify if `TSSAddress` and `TSSAddressUpdater` are different before proceeding with the update. If they are the same, the function should revert or simply return without emitting the `RenouncedTSSUpdater` event. This would ensure that the function reflects a true change of privilege and avoids confusion.

### Github : [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L107)

---


### [L-27]Lack of Return Value Check for ERC20 `safeTransfer` and `safeTransferFrom`

### File :ERC20Custody.sol

### Description
In the contract's `deposit` and `withdraw` functions, the ERC20 `safeTransfer` and `safeTransferFrom` methods from OpenZeppelin's SafeERC20 library are used to transfer tokens. While these methods are designed to be safer than their raw counterparts, they do not always revert on failure, especially for non-standard ERC20 tokens that return a boolean instead of using the standard `revert` on failure. The current implementation assumes these methods always revert on failure, potentially leading to inconsistent contract state if a token transfer fails but doesn't cause a revert.

### Code Snippet
```solidity
// From the deposit function
asset.safeTransferFrom(msg.sender, address(this), amount);

// From the withdraw function
IERC20(asset).safeTransfer(recipient, amount);
```

### Expected Behavior
The expected behavior when transferring tokens is to ensure the transfer was successful. This can be achieved by checking the return value of the `safeTransfer` and `safeTransferFrom` methods and handling cases where the transfer fails but does not revert.

### Actual Behavior
Currently, the contract does not check the return values of these transfer methods. While `safeTransfer` and `safeTransferFrom` are generally reliable, their behavior can vary with non-standard ERC20 tokens, potentially leading to unhandled transfer failures.

### Suggested Improvement
Enhance the `deposit` and `withdraw` functions to explicitly check the return values of the `safeTransfer` and `safeTransferFrom` methods. If a transfer fails (indicated by a `false` return value), the contract should revert or handle this case appropriately to maintain a consistent state.

### Github : [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197)

---



### [L-28]Hardcoded Deadline in Uniswap Transactions May Lead to Unpredictable Behavior

### File : `ZetaTokenConsumerUniV2.strategy.sol`

### Description
The contract utilizes a constant named `MAX_DEADLINE` with a value of `200` in its functions (`getZetaFromEth`, `getZetaFromToken`, `getEthFromZeta`, `getTokenFromZeta`) when interacting with UniswapV2Router for swapping tokens. This deadline is added to the `block.timestamp` to specify the time until which the transaction is valid. Using a hardcoded deadline poses a risk in scenarios where network congestion or other unforeseen delays occur. If the transaction is not mined within this timeframe, it will fail, which might not be an ideal behavior for the users.

### Code Snippet
```solidity
block.timestamp + MAX_DEADLINE
```

### Expected Behavior
Ideally, the deadline for a transaction should be flexible and determined based on current network conditions or user preference. This could be achieved by either allowing users to specify their own deadline or by calculating a more dynamic deadline based on current block times and network congestion.

### Actual Behavior
The contract uses a hardcoded value for the deadline, which may not be suitable in all network conditions, leading to a higher risk of transaction failures in certain scenarios.

### Recommendation
Consider implementing a mechanism to allow users to specify their own deadline or dynamically calculate an appropriate deadline based on the current network conditions. This will make the contract more adaptable to varying network situations and potentially improve the user experience by reducing the likelihood of failed transactions due to deadline issues.

### Github : [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L49)



---

### [L-29]Reliance on `block.timestamp` for Transaction Timing

### File : `ZetaTokenConsumerUniV2.strategy.sol`

### Description
The contract uses `block.timestamp` in the functions `getZetaFromEth`, `getZetaFromToken`, `getEthFromZeta`, and `getTokenFromZeta` to calculate the deadline for Uniswap transactions. While `block.timestamp` is generally reliable, it is manipulable by miners to a certain degree (up to around 900 seconds from the actual time). This reliance could lead to potential issues in scenarios where precise timing is crucial, such as in specific financial transactions or time-sensitive swaps. The use of `block.timestamp` can be especially problematic if combined with other contract functionalities that rely on precise time measurements.

### Code Snippet
```solidity
block.timestamp + MAX_DEADLINE
```

### Expected Behavior
In an ideal scenario, smart contracts that rely on time for critical functionalities should use mechanisms that are less vulnerable to manipulation. This might include using block numbers for timing, or incorporating external time-checking services for critical functionalities, although these approaches have their own trade-offs.

### Actual Behavior
The contract relies on `block.timestamp` to set deadlines for token swaps, which introduces a minor risk due to the manipulability of `block.timestamp` by miners.

### Recommendation
While the current use of `block.timestamp` is generally acceptable for many applications, it's important to be aware of its limitations. For contracts requiring precise timing or for higher-value transactions, consider alternative methods such as using block numbers for time-dependent actions or introducing additional checks to mitigate the risks associated with `block.timestamp` manipulation. Ensure that the potential impact of time manipulation is understood and appropriately mitigated, especially in contracts dealing with financial transactions.

### Github : [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L49)

----

### [L-30]Lack of Validation for `destinationAddress` Parameter in Swap Functions

### File : `ZetaTokenConsumerUniV2.strategy.sol`

### Description
The contract functions `getZetaFromEth`, `getZetaFromToken`, `getEthFromZeta`, and `getTokenFromZeta` include a parameter `destinationAddress` to specify where the output tokens should be sent. While there is a check to ensure that `destinationAddress` is not the zero address, there are no checks to prevent self-transfers or transfers to the contract itself. Transferring tokens to the contract address or allowing self-transfers can lead to unintended consequences, such as tokens getting locked in the contract.

### Code Snippet
```solidity
if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
// Proceed to perform swap operation
```

### Expected Behavior
The contract should include checks to prevent sending tokens to the contract's address or facilitate self-transfers, as these scenarios can lead to operational issues or token mismanagement.

### Actual Behavior
The contract currently only checks for the zero address, leaving scenarios open where tokens might be transferred to the contract address itself or involve unnecessary self-transfers.

### Recommendation
Implement additional validation to ensure that the `destinationAddress` is neither the contract’s address nor the address of the sender. This will prevent tokens from being unintentionally locked in the contract and avoid redundant self-transfers, thus ensuring smoother operational functionality and better token management.

### Github : [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100)


---



### [L-31]Insufficient Validation in `setMaxSupply` Function

### File: ZetaConnector.non-eth.sol

### Description
The `setMaxSupply` function in the ZetaConnectorNonEth contract lacks essential validation checks for its input parameter `maxSupply_`. This function is responsible for updating the maximum supply of tokens and can be externally called by the TSS address. Without proper validation, this function could set an illogical or harmful maximum supply value, like zero or a value lower than the current total supply.

### Code Snippet
```solidity
function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
    maxSupply = maxSupply_;
    emit MaxSupplyUpdated(msg.sender, maxSupply_);
}
```

### Expected Behavior
The function should include validation checks to ensure the new maximum supply is logical, such as being non-zero and not less than the current total supply of tokens.

### Actual Behavior
The function sets the new maximum supply directly from the input parameter without any validation checks, potentially leading to scenarios where the maximum supply is set to an inappropriate value.

### Github : [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31)
---

### [L-32]Use of `tx.origin` in `send` Function May Lead to Vulnerabilities

### File: ZetaConnector.non-eth.sol

### Description
The `send` function in the ZetaConnectorNonEth contract uses `tx.origin` to identify the original sender of the transaction. The usage of `tx.origin` is generally discouraged in Solidity programming due to its vulnerability to phishing attacks and other security issues, especially in contracts that interact with multiple addresses or contracts.

### Code Snippet
```solidity
function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
    ...
    emit ZetaSent(
        tx.origin,
        ...
    );
}
```

### Expected Behavior
Best practices in Solidity suggest using `msg.sender` instead of `tx.origin`. `msg.sender` accurately reflects the immediate sender of the message, providing a more secure and predictable way to handle sender information.

### Actual Behavior
The contract uses `tx.origin` for logging the transaction sender, which can potentially lead to security vulnerabilities, especially in complex transactions involving multiple contracts.

### Github : [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31)
---




