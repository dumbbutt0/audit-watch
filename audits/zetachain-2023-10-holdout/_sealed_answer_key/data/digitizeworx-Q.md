# [NC-1] MISSING UNDERSCORE IN NAMING VARIABLES

## Impact

Not following Solidity naming conventions for internal functions and variables reduces code clarity and readability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L72
```solidity
    function getPair(address token0, address token1) internal pure returns (address, address) {
        if (token0 < token1) return (token0, token1);


        return (token1, token0);
    }
```

## Recommended Mitigation

Prefix internal functions and variables with an underscore `_` to improve code quality.

# [NC-2] MISSING UNDERSCORE IN NAMING VARIABLES  

## Impact

Not following Solidity naming conventions for internal variables reduces code clarity and readability.


```solidity

```

## Recommended Mitigation

Prefix internal variable with an underscore to improve code quality.

# [NC-3] MISSING UNDERSCORE IN NAMING VARIABLES

## Impact 

Not following Solidity naming conventions for internal functions reduces code clarity and readability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/testing/SystemContractMock.sol#L56-L60
```solidity
    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        if (token0 == address(0)) revert CantBeZeroAddress();
    }
```

## Recommended Mitigation

Prefix internal function with an underscore _ to improve code quality.

# [NC-4] REQUIRE WITH EMPTY MESSAGE

## Impact

Empty require message provides no details on failure reason to facilitate debugging.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26-L26
```solidity
require(balanceOf[msg.sender] >= wad);
```

## Recommended Mitigation 

Add a descriptive message to require statement to improve debuggability. 

# [NC-5] REQUIRE WITH EMPTY MESSAGE

## Impact

Empty require message provides no details on failure reason to facilitate debugging.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47-L47
```solidity
require(balanceOf[src] >= wad);
```

## Recommended Mitigation

Add a descriptive message to require statement to improve debuggability.

# [NC-6] REQUIRE WITH EMPTY MESSAGE 

## Impact

Empty require message provides no details on failure reason to facilitate debugging.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L50-L50
```solidity
require(allowance[src][msg.sender] >= wad);
```

## Recommended Mitigation

Add a descriptive message to require statement to improve debuggability.

# [NC-7] IN-LINE ASSEMBLY DETECTED  

## Impact

Inline assembly bypasses Solidity safety checks and can introduce vulnerabilities if used improperly.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L53-L64
```solidity
        assembly {
            // solhint-disable-line
            let encoded_data := add(0x20, initCode) // load initialization code.
            let encoded_size := mload(initCode) // load the init code's length.
            deploymentAddress := create2(
                // call CREATE2 with 4 arguments.
                callvalue, // forward any attached value.
                encoded_data, // pass in initialization code.
                encoded_size, // pass in init code's length.
                salt // pass in the salt value.
            )
        }
```

## Recommended Mitigation

Avoid using inline assembly instructions if possible because it might introduce certain issues in the code if not dealt with properly because it bypasses several safety features that are already implemented in Solidity.

# [NC-8] HARD-CODED GAS LIMITS   

## Impact

Hardcoded gas limits may break contract if future Ethereum hard forks adjust gas costs.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L30-L30
```solidity
uint256 public GAS_LIMIT;
```

## Recommended Mitigation  

Make gas limit variable settable by admin.

# [NC-9] UNUSED RECEIVE FALLBACK

## Impact

An unused receive function may indicate logic missing or not fully implemented.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L101
```solidity
receive() external payable {}
```

## Recommended Mitigation

Check the receive function implementation for completeness.

# [NC-10] UNUSED RECEIVE FALLBACK

## Impact  

Unused receive function may indicate logic missing or not fully implemented. 

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L66
```solidity
receive() external payable {}
```

## Recommended Mitigation

check receive function implementation for completeness.

# [NC-11] UNUSED RECEIVE FALLBACK

## Impact

Unused receive function may indicate logic missing or not fully implemented.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72
```solidity
receive() external payable {}
```

## Recommended Mitigation 

make sure these functions are properly implemented and are not missing any validations in the definition.

# [NC-12] HARD-CODED ADDRESS DETECTED

## Impact

Hardcoded address could lead to loss of funds if address is incorrect or changes.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L63
```solidity
    address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

## Recommended Mitigation

It is required to check the address. Also, it is required to check the code of the called contract for vulnerabilities.
Ensure that the contract validates if there's an address or a code change or test cases to validate if the address is correct.

# [NC-13] HARD-CODED ADDRESS DETECTED

## Impact

Hardcoded address could lead to loss of funds if address is incorrect or changes. 

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31-L31
```solidity
    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

## Recommended Mitigation

Validate hardcoded address and handle potential address changes.

# [NC-14] HARD-CODED ADDRESS DETECTED  

## Impact

Hardcoded address could lead to loss of funds if address is incorrect or changes.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22
```solidity
    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

## Recommended Mitigation

Validate hardcoded address and handle potential address changes.

# [NC-15] USE CALL INSTEAD OF TRANSFER OR SEND

## Impact  

`Transfer` and `send` have fixed gas limits and can fail for non-EOA recipients.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L28-L28
```solidity
msg.sender.transfer(wad);
```

## Recommended Mitigation

Use `call` instead to forward exact gas needed.

# [NC-16] BLOCK VALUES AS A PROXY FOR TIME

## Impact 

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L49-L49
```solidity
block.timestamp + MAX_DEADLINE
```

## Recommended Mitigation  

Use external time sources or multiple redundant sources.

# [NC-17] BLOCK VALUES AS A PROXY FOR TIME

## Impact

Block values are unpredictable proxies for timing that can fail or be manipulated.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L87-L87
```solidity
block.timestamp + MAX_DEADLINE
```

## Recommended Mitigation

Use external time sources or multiple redundant sources.

# [NC-18] BLOCK VALUES AS A PROXY FOR TIME

## Impact  

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L115-L115
```solidity
block.timestamp + MAX_DEADLINE
```

## Recommended Mitigation

Use external time sources or multiple redundant sources.

# [NC-19] BLOCK VALUES AS A PROXY FOR TIME   

## Impact

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L153-L153
```solidity
block.timestamp + MAX_DEADLINE
```

## Recommended Mitigation 

Use external time sources or multiple redundant sources.

# [NC-20] BLOCK VALUES AS A PROXY FOR TIME

## Impact

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L82-L82
```solidity
            deadline: block.timestamp + MAX_DEADLINE,
```

## Recommended Mitigation

Use external time sources or multiple redundant sources. 

# [NC-21] BLOCK VALUES AS A PROXY FOR TIME

## Impact  

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L111-L111
```solidity
            deadline: block.timestamp + MAX_DEADLINE,
```

## Recommended Mitigation

Use external time sources or multiple redundant sources.

# [NC-22] BLOCK VALUES AS A PROXY FOR TIME

## Impact

Block values are unpredictable proxies for timing that can fail or be manipulated.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L136-L136
```solidity
deadline: block.timestamp + MAX_DEADLINE,
```

## Recommended Mitigation

Use external time sources or multiple redundant sources.

# [NC-23] BLOCK VALUES AS A PROXY FOR TIME  

## Impact

Block values are unpredictable proxies for timing that can fail or be manipulated.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L171-L171
```solidity
            deadline: block.timestamp + MAX_DEADLINE,
```

## Recommended Mitigation

Use external time sources or multiple redundant sources.

# [NC-24] MISSING INDEXED KEYWORDS IN EVENTS

## Impact   

Lack of indexed event parameters reduces filtering and searchability.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L81
```solidity
    event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
    event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
    event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
    event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

## Recommended Mitigation

Add indexed keyword to key event parameters.

# [NC-25] MISSING INDEXED KEYWORDS IN EVENTS

## Impact

Lack of indexed event parameters reduces filtering and searchability. 

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42-L44
```solidity
    event SetGasPrice(uint256, uint256);
    event SetGasCoin(uint256, address);
    event SetGasZetaPool(uint256, address);
```

## Recommended Mitigation  

Add indexed keyword to key event parameters.

# [NC-26] MISSING INDEXED KEYWORDS IN EVENTS 

## Impact

Lack of indexed event parameters reduces filtering and searchability.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L68
```solidity
    event TSSAddressUpdated(address callerAddress, address newTssAddress);
    event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
    event PauserAddressUpdated(address callerAddress, address newTssAddress);
```

## Recommended Mitigation

Add indexed keyword to key event parameters.