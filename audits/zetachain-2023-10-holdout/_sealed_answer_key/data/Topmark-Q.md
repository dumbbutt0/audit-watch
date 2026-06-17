###  Report 1:
#### Inconsistent Variable Assignment in SystemContract.sol contract
The functions in the code provided below shows the flexibiliy in setting WZETAContractAddress and setting Zeta Gas Pool, both of this function use "wZetaContractAddress". The problem is each function can be set irrespective of if the other has been updated, which has the risk of creating inconsistencies, whenever setWZETAContractAddress(...) is called it should update the Gas Zeta Pool automatically as edit in the code below.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L159
```solidity
---  function setWZETAContractAddress(address addr) external {
+++  function setWZETAContractAddress(address addr, uint256 chainID, address erc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        if (addr == address(0)) revert ZeroAddress();
        wZetaContractAddress = addr;
+++     updateGasZetaPool(chainID, erc20 );
        emit SetWZeta(wZetaContractAddress);
    }
+++    function updateGasZetaPool(uint256 chainID, address erc20) internal {
+++    address pool = uniswapv2PairFor(uniswapv2FactoryAddress, wZetaContractAddress, erc20);
+++        gasZetaPoolByChainId[chainID] = pool;
+++        emit SetGasZetaPool(chainID, pool);
    }
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L148
```solidity
       function setGasZetaPool(uint256 chainID, address erc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
>>>        address pool = uniswapv2PairFor(uniswapv2FactoryAddress, wZetaContractAddress, erc20);
        gasZetaPoolByChainId[chainID] = pool;
        emit SetGasZetaPool(chainID, pool);
    }
```
### Report 2:
#### No zeta Fee Validation in constructor
As noted from code in the link provide below, no necessary validation was done for zetaFee_ to ensure it is not too low or above maximum allowed before assigning it a value, necessary validation should be done.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L71
```solidity
 constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        TSSAddress = TSSAddress_;
        TSSAddressUpdater = TSSAddressUpdater_;
+++     if (zetaFee_ == 0) {
+++            revert ZeroFee();
+++        }
+++        if (zetaFee_ > zetaMaxFee) {
+++           revert ZetaMaxFeeExceeded();
+++        }
        zetaFee = zetaFee_;
        zeta = zeta_;
        zetaMaxFee = zetaMaxFee_;
    }
```
### Report 3:
#### Double Swap and Swap Fee
Due to absence of validation in the getZetaFromToken(...) function implementation if user intends to swap zeta with weth, the transaction will go through but user will incur excess fees, proper validation should be done to ensure input token is not weth as provided below.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L112
```solidity
  function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();
+++     if (inputToken == WETH9Address) revert ZetaCommonErrors.InvalidAddress();
        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);

        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            deadline: block.timestamp + MAX_DEADLINE,
>>>            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
            recipient: destinationAddress,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut
        });

        uint256 amountOut = uniswapV3Router.exactInput(params);

        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```
###  Report 4:
#### Lack of Range for Gas Fee
Lack of minimum and Maximum price range for gas Price By ChainId would allow setting price too low or two high, a new state should be set and necessary validation done to ensure a price boundary for "gasPriceByChainId" mappings
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L125
```solidity
     function setGasPrice(uint256 chainID, uint256 price) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
+++       require( price > minimumPrice && price < maximumPrice , "Price out of boound" )
>>>        gasPriceByChainId[chainID] = price;
        emit SetGasPrice(chainID, price);
    }
```