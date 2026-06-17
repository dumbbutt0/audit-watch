## Unused contracts should be removed
These unused contracts should be removed, it can be misleading to developers and gas if accidentally deployed
```
repos/protocol-contracts/contracts/zevm/Uniswap.sol
repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```

## Zero Address Check

Apparently ** 3/4 OF THE CONTRACT IN SCOPE ** has no zero address check as well as 0 input value which means that you can accidentally transfer to zero address or deploy contracts with null address. Do include zero address and value checks in ALL contracts in scope. I did not add code lines here as there is too much.

## Ancient Pragma Version
The contract `repos/protocol-contracts/contracts/zevm/WZETA.sol` uses Ancient Complier Version `pragma solidity ^0.4.18;` which has integer overflow and underflow. Do use the latest version and use it consistently throughout the contracts.

## Missing Receive() function
The contract `repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol` receives ether to swap for tokens, it is great practice to have a receive or fallback function for contracts that receives ether.