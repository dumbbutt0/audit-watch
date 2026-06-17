
# LOW RISK

| Number | Issue | Instencs |
|--------|-------|----------|
|[L-01]| Missing checks for address(0) when assigning values to address state variables  | 15 |
|[L-02]| onlyOwner functions not accessible if owner renounces ownership  | 1 |
|[L-03]| Setters should have initial value check  | 2 |
|[L-04]| Functions calling contracts/addresses with transfer hooks are missing reentrancy guards  | 9 |
|[L-05]| Unused/empty receive/fallback function  | 3 |
|[L-06]| Consider using descriptive constants when passing zero as a function argument  | 6 |
|[L-07]| External call recipient can consume all remaining gas  | 3 |
|[L-08]| Revert on transfer to the zero address  | 1 |
|[L-09]| unchecked blocks with subtractions may underflow  | 2 |
|[L-10]| Using >/>= without specifying an upper bound in version pragma is unsafe  | 2 |
|[L-11]| Governance operations should be behind a timelock  | 9 |
|[L-12]| Missing checks in constructor  | 14 |
|[L-13]| `decimals()` is not a part of the ERC-20 standard  | 1 |


## [L-01] Missing checks for address(0) when assigning values to address state variables

There are 15 instance(s) of this issue:

```solidity
file: main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

80   wzeta = wzeta_;

116  wzeta = wzeta_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L80

```solidity
file: main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

69    TSSAddress = TSSAddress_;

70    TSSAddressUpdater = TSSAddressUpdater_;

84    TSSAddress = TSSAddress_;

```

https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69


```solidity
file: main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol

36   tssAddress = tssAddress_;

37   tssAddressUpdater = tssAddressUpdater_;

44   tssAddress = tssAddress_;

45   connectorAddress = connectorAddress_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L36


```solidity
file: main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

84     zetaToken = zetaToken_;

85     tssAddress = tssAddress_;

86     tssAddressUpdater = tssAddressUpdater_;

87     pauserAddress = pauserAddress_

120    pauserAddress = pauserAddress_;

132    tssAddress = tssAddress_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L85


## [L-02] onlyOwner functions not accessible if owner renounces ownership

The owner is able to perform certain privileged activities, but it's possible to set the owner to address(0). This can represent a certain risk if the ownership is renounced for any other reason than by design. Renouncing ownership will leave the contract without an owner, therefore limiting any functionality that needs authority.

There are 1 instance(s) of this issue:

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

54   function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54


## [L-03] Setters should have initial value check

Setters should have initial value check to prevent assigning wrong value to the variable. Assginment of wrong value can lead to unexpected behavior of the contract.

There are 2 instance(s) of this issue:

```solidity
file: main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

31    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31


```solidity
file: main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
 
114  function setWzetaAddress(address wzeta_) external {

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114


## [L-04] Functions calling contracts/addresses with transfer hooks are missing reentrancy guards

Even if the function follows the best practice of check-effects-interaction, not using a reentrancy guard when there may be transfer hooks will open the users of this protocol up to read-only reentrancies with no way to protect against it, except by block-listing the whole protocol.

There are 9 instance(s) of this issue:


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

135   IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

159   IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

193   IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135


```solidity
file: main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

32    bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);

60    bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);

86    bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L32

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

108   IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

144   IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

175   IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108


## [L-05] Unused/empty receive/fallback function

If the intention is for the ETH to be used, the function should call another function, otherwise it should revert (e.g. require(msg.sender == address(weth))).

There are 3 instance(s) of this issue:

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101   receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

66   receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72   receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72


## [L-06] Consider using descriptive constants when passing zero as a function argument

Passing zero as a function argument can sometimes result in a security issue (e.g. passing zero as the slippage parameter). Consider using a constant variable with a descriptive name, so it's clear that the argument is intentionally being used, and for the right reasons.

There are 6 instance(s) of this issue:

```solidity
file:  main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

82   address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

112  address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

115  address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

148  address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

179  address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

182  address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L82



## [L‑07] External call recipient can consume all remaining gas

There is no limit specified on the amount of gas used, so the recipient can use up all of the remaining gas(gasleft()), causing it to revert. Therefore, when calling an external contract, it is necessary to specify a limited amount of gas to forward.

There are 3 instances:

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

178   (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

152   (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152

```solidity
file: main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

96   (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96

## [L-08] Revert on transfer to the zero address

It's good practice to revert a token transfer transaction if the recipient's address is the zero address. This can prevent unintentional transfers to the zero address due to accidental operations or programming errors. Many token contracts implement such a safeguard, such as OpenZeppelin - ERC20, OpenZeppelin - ERC721.

```solidity
file: main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

181   asset.safeTransferFrom(msg.sender, address(this), amount);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L181

## [L‑09] unchecked blocks with subtractions may underflow

There aren't any checks to avoid an underflow which can happen inside an unchecked block, so the following subtractions may underflow silently.

There are 2 instances:

```solidity
file: main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

185   _balances[sender] = senderBalance - amount;

205   _balances[account] = accountBalance - amount;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L185

## [L‑10] Using >/>= without specifying an upper bound in version pragma is unsafe

There will be breaking changes in future versions of solidity, and at that point your code will no longer be compatible. While you may have the specific version to use in a configuration file, others that include your source files may not.

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14   pragma solidity >=0.8.0;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14   pragma solidity >=0.8.0;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14

## [L-11] Governance operations should be behind a timelock

All critical and governance operations should be protected by a timelock. For example from the point of view of a user, the changing of the owner of a contract is a high risk operation that may have outcomes ranging from an attacker gaining control over the protocol, to the function no longer functioning due to a typo in the destination address. To give users plenty of warning so that they can validate any ownership changes, changes of ownership should be behind a timelock.

There are 9 instance(s) of this issue:

```solidity
file: main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

80    function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
        if (TSSAddress_ == address(0)) {
            revert ZeroAddress();
        }
        TSSAddress = TSSAddress_;
        emit UpdatedTSSAddress(TSSAddress_);
    }

92  function updateZetaFee(uint256 zetaFee_) external onlyTSS {
        if (zetaFee_ == 0) {
            revert ZeroFee();
        }
        if (zetaFee_ > zetaMaxFee) {
            revert ZetaMaxFeeExceeded();
        }
        zetaFee = zetaFee_;
        emit UpdatedZetaFee(zetaFee_);
    }

107  function renounceTSSAddressUpdater() external onlyTSSUpdater {
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
        TSSAddressUpdater = TSSAddress;
        emit RenouncedTSSUpdater(msg.sender);
    }

118  function pause() external onlyTSS {
        if (paused) {
            revert IsPaused();
        }
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
        paused = true;
        emit Paused(msg.sender);
    }

144  function whitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = true;
        emit Whitelisted(asset);
    }

153  function unwhitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = false;
        emit Unwhitelisted(asset);
    }
    
193  function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
        IERC20(asset).safeTransfer(recipient, amount);
        emit Withdrawn(recipient, asset, amount);
    }

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80-L86

```solidity
file: main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

117  function updatePauserAddress(address pauserAddress_) external onlyPauser {
        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

        pauserAddress = pauserAddress_;

        emit PauserAddressUpdated(msg.sender, pauserAddress_);
    }

140  function renounceTssAddressUpdater() external onlyTssUpdater {
        if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

        tssAddressUpdater = tssAddress;
        emit TSSAddressUpdaterUpdated(msg.sender, tssAddressUpdater);
    }

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L123



## [L-12] Missing checks in constructor

There are some missing checks in these functions, and this could lead to unexpected scenarios. Consider always adding a sanity check for state variables.

There are 14 instance(s) of this issue:


```solidity
file: main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

73   zetaMaxFee = zetaMaxFee_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L71


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

86   zetaToken = zetaToken_;

89   WETH9Address = WETH9Address_;

90   zetaPoolFee = zetaPoolFee_;

91   tokenPoolFee = tokenPoolFee_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L86


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

53    zetaToken = zetaToken_;

56    WETH9Address = WETH9Address_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L53

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
 
29    zetaToken = zetaToken_;

```

https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L29


```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

57   zetaToken = zetaToken_;

60   WETH9Address = WETH9Address_;

61   zetaPoolFee = zetaPoolFee_;

62   tokenPoolFee = tokenPoolFee_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L57


```solidity
file: main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

54    uniswapv2FactoryAddress = uniswapv2Factory_;

55    uniswapv2Router02Address = uniswapv2Router02_;

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L54



```solidity
file:  main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

136    IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);

160    IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);

194    IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L136

```solidity
file: main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

109   IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);

145   IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);

176   IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L109


## [L-13] `decimals()` is not a part of the ERC-20 standard

The `decimals()` function is not a part of the [ERC-20 standard](https://eips.ethereum.org/EIPS/eip-20), and was added later as an [optional extension](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/IERC20Metadata.sol). As such, some valid ERC20 tokens do not support this interface, so it is unsafe to blindly cast all tokens to this interface, and then call this function.

```solidity
file: main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

11  _mint(creator, initialSupply * (10 ** uint256(decimals())));

```
https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L11