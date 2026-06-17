# Gas optimization for the constructor https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L86
## Replacing the multiple if statements with a single require statement
### require(zetaToken_ != address(0) && pancakeV3Router_ != address(0) && uniswapV3Factory_ != address(0) && WETH9Address_ != address(0), "InvalidAddress");

# Gas optimization for the nonReentrant modifier at https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95
## Replacing revert with require
### require(!_locked, "ReentrancyError");

# Gas optimization for getZetaFromEth function at https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107C3-L107C3
## Replacing multiple if statements with require
### require(destinationAddress != address(0) && msg.value > 0, "InvalidAddress or InputCantBeZero");

# Gas optimizations for getZetaFromToken function at https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132 
## Replacing multiple if statements with a single require statement
### require(destinationAddress != address(0) && inputToken != address(0) && inputTokenAmount > 0, "InvalidAddress or InputCantBeZero");

# Gas optimizations for getEthFromZeta function at https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156
## Replacing multiple if statements with a single require statement
### require(destinationAddress != address(0) && zetaTokenAmount > 0, "InvalidAddress or InputCantBeZero");

# Gas optimization for getTokenFromZeta function at https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190
## Replacing multiple if statements with a single require statement 




