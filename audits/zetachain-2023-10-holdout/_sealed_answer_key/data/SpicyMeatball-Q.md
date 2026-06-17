### Withdrawal will be unable if asset is unwhitelisted
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194-L195
Let's assume that  a user deposited assets into the custody contract and after some time this asset was removed from the whitelist.
```
    function unwhitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = false;
        emit Unwhitelisted(asset);
    }
```
Then withdrawals for this asset will be unavailable resulting in funds being stuck in the custody.
### ETH still can be sent to `ZetaConnectorZEVM.sol`
There is a check in `ZetaConnectorZEVM.sol` that allows ETH transfer only from the WETH contract.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L84
```
    /// @dev Receive function to receive ZETA from WETH9.withdraw().
    receive() external payable {
        if (msg.sender != wzeta) revert OnlyWZETA();
    }
```
It is possible to bypass this check and send ETH directly with a `selfdestruct(addr)`.
### Some tokens will be unswappable with the consumer due to immutable `tokenPoolFee`
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L48
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L77

When deploying Uniswap/Pancakeswap V3 consumer contracts we specify a `tokenPoolFee` which is later used in swaps to construct a path for the router.
```
path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
``` 
However not all pools will have a fee similar to that we store in the contract, therefore some token swaps will revert.

The consumer allows swapping user specified tokens for ZETA and back, the swap is executed in two hops. For instance, a user wants to swap X for ZETA, first we swap X for WETH and then WETH is exchanged for ZETA. Path for the router is constructed in Uniswap V3 fashion and consists of an input token, a pool fee and an output tokens. This leaves us with 2 constraints:
- token must be pooled with WETH
- pool fee must be equal to `tokenPoolFee` that was specified in the constructor
Although WETH pools are pretty popular, there is no guarantee that it's fee will be equal to `tokenPoolFee`.