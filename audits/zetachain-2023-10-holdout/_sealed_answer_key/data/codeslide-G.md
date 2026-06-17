### <a id="summary-gas-optimizations"></a> Gas Optimizations
There are 335 instances over 20 issues.
|      ID       | Description                                                                        | Count | Gas Per Instance | Gas Savings |
| :-----------: | :--------------------------------------------------------------------------------- | ----: | ---------------: | ----------: |
| [G-01](#g-01) | `<x> += <y>` costs more gas than `<x> = <x> + <y>` for state variables             |     9 |              113 |       1,017 |
| [G-02](#g-02) | `>=` costs less gas than `>`                                                       |    11 |                3 |          33 |
| [G-03](#g-03) | Assembly: Check `msg.sender` using `xor` and the scratch space                     |    21 |                3 |          63 |
| [G-04](#g-04) | Assembly: Use scratch space for building calldata                                  |    14 |              220 |       3,080 |
| [G-05](#g-05) | Avoid contract existence checks by using low level calls                           |    58 |              100 |       5,800 |
| [G-06](#g-06) | Avoid fetching a low-level call's return data by using assembly                    |     3 |              159 |         477 |
| [G-07](#g-07) | Constructors can be marked `payable`                                               |    14 |               21 |         294 |
| [G-08](#g-08) | Functions guaranteed to revert when called by normal users can be marked `payable` |     4 |               21 |          84 |
| [G-09](#g-09) | Gas use can be reduced by using Solidity 0.8.19 or later                           |    27 |                - |           - |
| [G-10](#g-10) | `internal`/`private` functions only called once can be inlined to save gas         |     2 |               20 |          40 |
| [G-11](#g-11) | Nesting `if`-statements is cheaper than using `&&`                                 |     5 |                6 |          30 |
| [G-12](#g-12) | Optimize names to save gas                                                         |    22 |               22 |         484 |
| [G-13](#g-13) | `require()`/`revert()` strings longer than 32 bytes cost extra gas                 |     2 |                3 |           6 |
| [G-14](#g-14) | Simple checks for zero can be done using assembly to save gas                      |    68 |                6 |         408 |
| [G-15](#g-15) | State variables only set in the constructor should be declared `immutable`         |     3 |           22,097 |      66,291 |
| [G-16](#g-16) | Use assembly for small keccak256 hashes, in order to save gas                      |     3 |               80 |         240 |
| [G-17](#g-17) | Use assembly to emit events, in order to save gas                                  |    32 |               38 |       1,216 |
| [G-18](#g-18) | Use `calldata` instead of `memory` for function arguments that do not get mutated  |     6 |              211 |       1,266 |
| [G-19](#g-19) | Use custom errors rather than `revert()`/`require()` strings to save gas           |     5 |                - |           - |
| [G-20](#g-20) | Use predefined address instead of `address(this)`                                  |    26 |               50 |       1,300 |
|               | Total Gas Savings                                                                  |       |                  |      82,129 |

Gas totals use lower bounds of ranges and count two iterations of each `for` loop. Gas savings values are runtime values except for cases where only deployment values are applicable, like for constant declarations.

### <a id="details-gas-optimizations"></a> Gas Optimizations
#### <a id="g-01"></a> \[G-01\] `<x> += <y>` costs more gas than `<x> = <x> + <y>` for state variables
##### Description:
For state variable arithmetic assignments, using syntax like `x = x + y` rather than `x += y` and `x = x - y` rather than `x -= y` will [save 113 gas](https://gist.github.com/ezcodeslide/0d106946dc4143ca8654048c1a9450f8).

##### Instances:
There are 9 instances of this issue.
<details><summary>View 9 Instances</summary>

```solidity
File: contracts/zevm/WZETA.sol

21:         balanceOf[msg.sender] += msg.value;

27:         balanceOf[msg.sender] -= wad;

51:             allowance[src][msg.sender] -= wad;

54:         balanceOf[src] -= wad;

55:         balanceOf[dst] += wad;
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              5 | [21](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L21),[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L27),[51](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L51),[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L54),[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L55) |
___
```solidity
File: contracts/zevm/ZRC20.sol

186:         _balances[recipient] += amount;

194:         _totalSupply += amount;

195:         _balances[account] += amount;

206:         _totalSupply -= amount;
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                              |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              4 | [186](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L186),[194](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L194),[195](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L195),[206](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L206) |
___
</details>

#### <a id="g-02"></a> \[G-02\] `>=` costs less gas than `>`
##### Description:
The compiler uses opcodes `GT` and `ISZERO` for Solidity code that uses `>`, but only requires `LT` for `>=`, which saves 3 gas. If `<` is being used, the condition can be inverted.

##### Instances:
There are 11 instances of this issue.
<details><summary>View 11 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

96:         if (zetaFee_ > zetaMaxFee) {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                      |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              1 | [96](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L96) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

63:         if (message.length > 0) {

89:         if (message.length > 0) {
```

| File Link                                                                                                              | Instance Count | Instance Links                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              2 | [63](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L63),[89](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L89) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);

72:         if (message.length > 0) {

96:         if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)

100:         if (message.length > 0) {
```

| File Link                                                                                                                      | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              4 | [69](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L69),[72](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L72),[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L96),[100](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L100) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

69:         if (token0 < token1) return (token0, token1);
```

| File Link                                                                                                                                                    | Instance Count | Instance Link                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              1 | [69](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L69) |
___
```solidity
File: contracts/zevm/ZRC20.sol

161:         if (currentAllowance < amount) revert LowAllowance();

183:         if (senderBalance < amount) revert LowBalance();

203:         if (accountBalance < amount) revert LowBalance();
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                               |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [161](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L161),[183](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L183),[203](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L203) |
___
</details>

#### <a id="g-03"></a> \[G-03\] Assembly: Check `msg.sender` using `xor` and the scratch space
##### Description:
Assembly can be used to efficiently validate `msg.sender` with the least amount of opcodes necessary. Additionally, `xor()` can be used, saving 3 gas. Potentially more gas can be saved by using scratch space to store the error selector, potentially avoiding memory expansion costs. An example is available for reference in [this prior finding](https://code4rena.com/reports/2023-05-juicebox#g-06-use-assembly-to-validate-msgsender).

##### Instances:
There are 21 instances of this issue.
<details><summary>View 21 Instances</summary>

```solidity
File: contracts/evm/Zeta.non-eth.sol

41:         if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);

41:         if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);

55:         if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

77:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              5 | [41](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L41),[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L41),[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L55),[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L66),[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L77) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);

129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```

| File Link                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                        |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              2 | [129](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L129),[129](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L129) |
___
```solidity
File: contracts/evm/tools/ZetaInteractor.sol

44:         if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                              |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol) |              1 | [44](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol#L44) |
___
```solidity
File: contracts/zevm/SystemContract.sol

52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

| File Link                                                                                                         | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              7 | [52](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L52),[74](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L74),[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L124),[135](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L135),[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L146),[157](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L157),[168](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L168) |
___
```solidity
File: contracts/zevm/WZETA.sol

49:         if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              1 | [49](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L49) |
___
```solidity
File: contracts/zevm/ZRC20.sol

69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                             |
| :---------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [69](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L69),[226](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L226),[226](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L226) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

85:         if (msg.sender != wzeta) revert OnlyWZETA();

115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```

| File Link                                                                                                               | Instance Count | Instance Links                                                                                                                                                                                                      |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              2 | [85](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L85),[115](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L115) |
___
</details>

#### <a id="g-04"></a> \[G-04\] Assembly: Use scratch space for building calldata
##### Description:
If an external call's calldata can fit into two or fewer words (64 bytes), use the scratch space to build the calldata, rather than allowing Solidity to do a memory expansion.

##### Instances:
There are 14 instances of this issue.
<details><summary>View 14 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

180:         uint256 oldBalance = asset.balanceOf(address(this));

184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                            |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              2 | [180](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L180),[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L184) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

24:         return IERC20(zetaToken).balanceOf(address(this));

60:         bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);

86:         bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
```

| File Link                                                                                                              | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                          |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              3 | [24](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L24),[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L60),[86](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L86) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

28:         return ZetaNonEthInterface(zetaToken).balanceOf(address(this));

41:         ZetaNonEthInterface(zetaToken).burnFrom(msg.sender, input.zetaValueAndGas);
```

| File Link                                                                                                                      | Instance Count | Instance Links                                                                                                                                                                                                          |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              2 | [28](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L28),[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L41) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

174:         WETH9(WETH9Address).withdraw(amountOut);
```

| File Link                                                                                                                                                        | Instance Count | Instance Link                                                                                                                     |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              1 | [174](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L174) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

148:         WETH9(WETH9Address).withdraw(amountOut);
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                                 |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              1 | [148](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L148) |
___
```solidity
File: contracts/zevm/SystemContract.sol

77:         IZRC20(zrc20).deposit(target, amount);
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                         |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L77) |
___
```solidity
File: contracts/zevm/WZETA.sol

28:         msg.sender.transfer(wad);
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              1 | [28](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L28) |
___
```solidity
File: contracts/zevm/ZRC20.sol

237:         address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID);

241:         uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID);
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              2 | [237](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L237),[241](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L241) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

95:         WZETA(wzeta).withdraw(input.zetaValueAndGas);
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                            |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [95](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L95) |
___
</details>

#### <a id="g-05"></a> \[G-05\] Avoid contract existence checks by using low level calls
##### Description:
Prior to Solidity 0.8.10, the compiler inserted extra code, including `EXTCODESIZE` (100 gas), to check for contract existence for external function calls. In more recent version of Solidity, the compiler will not insert these checks if the external call has a return value. Similar behavior can be achieved in earlier versions by using low-level calls, since low level calls never check for contract existence.

##### Instances:
There are 58 instances of this issue.
<details><summary>View 58 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

180:         uint256 oldBalance = asset.balanceOf(address(this));

184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                            |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              2 | [180](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L180),[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L184) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

24:         return IERC20(zetaToken).balanceOf(address(this));

32:         bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);

60:         bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);

64:             ZetaReceiver(destinationAddress).onZetaMessage(
65:                 ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:             );

86:         bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);

90:             ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                 ZetaInterfaces.ZetaRevert(
92:                     zetaTxSenderAddress,
93:                     sourceChainId,
94:                     destinationAddress,
95:                     destinationChainId,
96:                     remainingZetaValue,
97:                     message
98:                 )
99:             );
```

| File Link                                                                                                              | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              6 | [24](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L24),[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L32),[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L60),[64](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L64),[86](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L86),[90](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L90) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

28:         return ZetaNonEthInterface(zetaToken).balanceOf(address(this));

41:         ZetaNonEthInterface(zetaToken).burnFrom(msg.sender, input.zetaValueAndGas);

69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);

70:         ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);

73:             ZetaReceiver(destinationAddress).onZetaMessage(
74:                 ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:             );

96:         if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)

98:         ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);

101:             ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                 ZetaInterfaces.ZetaRevert(
103:                     zetaTxSenderAddress,
104:                     sourceChainId,
105:                     destinationAddress,
106:                     destinationChainId,
107:                     remainingZetaValue,
108:                     message
109:                 )
110:             );
```

| File Link                                                                                                                      | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              8 | [28](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L28),[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L41),[69](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L69),[70](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L70),[73](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L73),[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L96),[98](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L98),[101](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L101) |
___
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

207:         Ownable(deploymentAddress).transferOwnership(msg.sender);
```

| File Link                                                                                                                                | Instance Count | Instance Link                                                                                                         |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              1 | [207](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L207) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

120:         uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);

145:         uint256 amountOut = pancakeV3Router.exactInput(params);

172:         uint256 amountOut = pancakeV3Router.exactInputSingle(params);

174:         WETH9(WETH9Address).withdraw(amountOut);

178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");

203:         uint256 amountOut = pancakeV3Router.exactInput(params);

210:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);

218:         return pool.liquidity() > 0;
```

| File Link                                                                                                                                                        | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              8 | [120](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L120),[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L145),[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L172),[174](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L174),[178](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178),[203](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L203),[210](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L210),[218](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L218) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

82:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

93:         uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);

112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

130:         uint256 amountOut = tridentRouter.exactInput(params);

148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

159:         uint256 amountOut = tridentRouter.exactInputSingle(params);

179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

197:         uint256 amountOut = tridentRouter.exactInput(params);
```

| File Link                                                                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |             10 | [82](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L82),[93](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L93),[112](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L112),[115](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L115),[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L130),[148](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L148),[159](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L159),[179](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L179),[182](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L182),[197](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L197) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

31:         wETH = IUniswapV2Router02(uniswapV2Router_).WETH();

45:         uint256[] memory amounts = uniswapV2Router.swapExactETHForTokens{value: msg.value}(
46:             minAmountOut,
47:             path,
48:             destinationAddress,
49:             block.timestamp + MAX_DEADLINE
50:         );

82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );

110:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:             zetaTokenAmount,
112:             minAmountOut,
113:             path,
114:             destinationAddress,
115:             block.timestamp + MAX_DEADLINE
116:         );

148:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:             zetaTokenAmount,
150:             minAmountOut,
151:             path,
152:             destinationAddress,
153:             block.timestamp + MAX_DEADLINE
154:         );

167:         try uniswapV2Router.getAmountsOut(1, path) returns (uint256[] memory amounts) {
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              6 | [31](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L31),[45](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L45),[82](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L82),[110](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L110),[148](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L148),[167](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L167) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

92:         uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);

118:         uint256 amountOut = uniswapV3Router.exactInput(params);

146:         uint256 amountOut = uniswapV3Router.exactInputSingle(params);

148:         WETH9(WETH9Address).withdraw(amountOut);

152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");

178:         uint256 amountOut = uniswapV3Router.exactInput(params);

185:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);

193:         return pool.liquidity() > 0;
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              8 | [92](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L92),[118](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L118),[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L146),[148](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L148),[152](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152),[178](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L178),[185](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L185),[193](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L193) |
___
```solidity
File: contracts/zevm/SystemContract.sol

77:         IZRC20(zrc20).deposit(target, amount);

78:         zContract(target).onCrossChainCall(context, zrc20, amount, message);
```

| File Link                                                                                                         | Instance Count | Instance Links                                                                                                                                                                                              |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              2 | [77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L77),[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L78) |
___
```solidity
File: contracts/zevm/WZETA.sol

28:         msg.sender.transfer(wad);
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              1 | [28](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L28) |
___
```solidity
File: contracts/zevm/ZRC20.sol

237:         address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID);

241:         uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID);

258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                               |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [237](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L237),[241](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L241),[258](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L258) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

94:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();

95:         WZETA(wzeta).withdraw(input.zetaValueAndGas);

96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

| File Link                                                                                                               | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                             |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              3 | [94](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L94),[95](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L95),[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L96) |
___
</details>

#### <a id="g-06"></a> \[G-06\] Avoid fetching a low-level call's return data by using assembly
##### Description:
Even if the `call`'s second return value is not assigned, it still gets copied to memory, using 159 gas.

##### Recommendation:
When the return data is not needed, use assembly as shown in the following example:
```solidity
// Before:
(bool success, ) = payable(receiver).call{gas: gas, value: value}("");

// After:
bool success;
assembly {
  success := call(gas, receiver, value, 0, 0, 0, 0)
}
```

##### Instances:
There are 3 instances of this issue.
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

| File Link                                                                                                                                                        | Instance Count | Instance Link                                                                                                                     |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              1 | [178](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                                 |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              1 | [152](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                            |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [96](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L96) |
___
#### <a id="g-07"></a> \[G-07\] Constructors can be marked `payable`
##### Description:
`payable` functions cost less gas to execute since the compiler does not have to add extra checks to ensure that a payment wasn't provided. A `constructor` can safely be marked as `payable` since only the deployer can pass funds.

##### Instances:
There are 14 instances of this issue.
<details><summary>View 14 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                      |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              1 | [68](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L68) |
___
```solidity
File: contracts/evm/Zeta.eth.sol

10:     constructor(address creator, uint256 initialSupply) {
```

| File Link                                                                                            | Instance Count | Instance Link                                                                                  |
| :--------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------- |
| [Zeta.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.eth.sol) |              1 | [10](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.eth.sol#L10) |
___
```solidity
File: contracts/evm/Zeta.non-eth.sol

33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                      |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              1 | [33](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L33) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
```

| File Link                                                                                                                | Instance Count | Instance Link                                                                                            |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              1 | [74](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L74) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

16:     constructor(
17:         address zetaToken_,
18:         address tssAddress_,
19:         address tssAddressUpdater_,
20:         address pauserAddress_
21:     ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                           |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------ |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              1 | [16](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L16) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

20:     constructor(
21:         address zetaTokenAddress_,
22:         address tssAddress_,
23:         address tssAddressUpdater_,
24:         address pauserAddress_
25:     ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

| File Link                                                                                                                      | Instance Count | Instance Link                                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              1 | [20](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L20) |
___
```solidity
File: contracts/evm/tools/ZetaInteractor.sol

37:     constructor(address zetaConnectorAddress) {
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                              |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol) |              1 | [37](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol#L37) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

71:     constructor(
72:         address zetaToken_,
73:         address pancakeV3Router_,
74:         address uniswapV3Factory_,
75:         address WETH9Address_,
76:         uint24 zetaPoolFee_,
77:         uint24 tokenPoolFee_
78:     ) {
```

| File Link                                                                                                                                                        | Instance Count | Instance Link                                                                                                                   |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              1 | [71](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
```

| File Link                                                                                                                                                    | Instance Count | Instance Link                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              1 | [45](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

26:     constructor(address zetaToken_, address uniswapV2Router_) {
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                               |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              1 | [26](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

42:     constructor(
43:         address zetaToken_,
44:         address uniswapV3Router_,
45:         address uniswapV3Factory_,
46:         address WETH9Address_,
47:         uint24 zetaPoolFee_,
48:         uint24 tokenPoolFee_
49:     ) {
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                               |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              1 | [42](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42) |
___
```solidity
File: contracts/zevm/SystemContract.sol

51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                         |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [51](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L51) |
___
```solidity
File: contracts/zevm/ZRC20.sol

60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              1 | [60](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L60) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

79:     constructor(address wzeta_) {
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                            |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [79](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L79) |
___
</details>

#### <a id="g-08"></a> \[G-08\] Functions guaranteed to revert when called by normal users can be marked `payable`
##### Description:
If a function modifier such as `onlyOwner` is used, the function will revert if a normal user tries to pay the function. Marking the function as `payable` will lower the gas cost for legitimate callers because the compiler will not include checks for whether a payment was provided. The extra opcodes avoided are `CALLVALUE`(2), `DUP1`(3), `ISZERO`(3), `PUSH2`(3), `JUMPI`(10), `PUSH1`(3), `DUP1`(3), `REVERT`(0), `JUMPDEST`(1), and `POP`(2). In addition to the extra deployment cost, on average, approximately 21 gas can be saved per call to the function.

##### Instances:
There are 4 instances of this issue. These are additional instances of an issue listed in the automated findings report.
<details><summary>View 4 Instances</summary>

```solidity
File: contracts/evm/ZetaConnector.eth.sol

52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

77:     function onRevert(
78:         address zetaTxSenderAddress,
79:         uint256 sourceChainId,
80:         bytes calldata destinationAddress,
81:         uint256 destinationChainId,
82:         uint256 remainingZetaValue,
83:         bytes calldata message,
84:         bytes32 internalSendHash
85:     ) external override whenNotPaused onlyTssAddress {
```

| File Link                                                                                                              | Instance Count | Instance Links                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              2 | [52](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L52),[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L77) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

87:     function onRevert(
88:         address zetaTxSenderAddress,
89:         uint256 sourceChainId,
90:         bytes calldata destinationAddress,
91:         uint256 destinationChainId,
92:         uint256 remainingZetaValue,
93:         bytes calldata message,
94:         bytes32 internalSendHash
95:     ) external override whenNotPaused onlyTssAddress {
```

| File Link                                                                                                                      | Instance Count | Instance Links                                                                                                                                                                                                          |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              2 | [61](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L61),[87](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L87) |
___
</details>

#### <a id="g-09"></a> \[G-09\] Gas use can be reduced by using Solidity 0.8.19 or later
##### Description:
See [Preventing Dead Code in Runtime Bytecode](https://blog.soliditylang.org/2023/02/22/solidity-0.8.19-release-announcement/#preventing-dead-code-in-runtime-bytecode) for the full details.

##### Instances:
There are 27 instances of this issue.
<details><summary>View 27 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

3: pragma solidity 0.8.7;
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                    |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              1 | [3](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L3) |
___
```solidity
File: contracts/evm/Zeta.eth.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                            | Instance Count | Instance Link                                                                                |
| :--------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [Zeta.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.eth.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.eth.sol#L2) |
___
```solidity
File: contracts/evm/Zeta.non-eth.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                    |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L2) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                | Instance Count | Instance Link                                                                                          |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L2) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                         |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L2) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                      | Instance Count | Instance Link                                                                                             |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L2) |
___
```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                     | Instance Count | Instance Link                                                                                                  |
| :---------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------- |
| [ConnectorErrors.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ConnectorErrors.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ConnectorErrors.sol#L2) |
___
```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                           | Instance Count | Instance Link                                                                                             |
| :------------------------------------------------------------------------------------------------------------------ | -------------: | :-------------------------------------------------------------------------------------------------------- |
| [ZetaErrors.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaErrors.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaErrors.sol#L2) |
___
```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                               | Instance Count | Instance Link                                                                                                       |
| :-------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------ |
| [ZetaInteractorErrors.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInteractorErrors.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2) |
___
```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                   | Instance Count | Instance Link                                                                                                 |
| :-------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------ |
| [ZetaInterfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInterfaces.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInterfaces.sol#L2) |
___
```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                             | Instance Count | Instance Link                                                                                                      |
| :------------------------------------------------------------------------------------------------------------------------------------ | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [ZetaNonEthInterface.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaNonEthInterface.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2) |
___
```solidity
File: contracts/evm/tools/ZetaInteractor.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                            |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol#L2) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                                                        | Instance Count | Instance Link                                                                                                                 |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                                                    | Instance Count | Instance Link                                                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                             |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                                                | Instance Count | Instance Link                                                                                                             |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2) |
___
```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14: pragma solidity >=0.8.0;
```

| File Link                                                                                                                                                                           | Instance Count | Instance Link                                                                                                                                  |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| [TridentConcentratedLiquidityPoolFactory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol) |              1 | [14](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14) |
___
```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14: pragma solidity >=0.8.0;
```

| File Link                                                                                                                                 | Instance Count | Instance Link                                                                                                             |
| :---------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------ |
| [TridentIPoolRouter.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentIPoolRouter.sol) |              1 | [14](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14) |
___
```solidity
File: contracts/zevm/Interfaces.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                 | Instance Count | Instance Link                                                                                   |
| :-------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------- |
| [Interfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol#L2) |
___
```solidity
File: contracts/zevm/SystemContract.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                       |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L2) |
___
```solidity
File: contracts/zevm/ZRC20.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                       | Instance Count | Instance Link                                                                              |
| :---------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L2) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                          |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L2) |
___
```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                            | Instance Count | Instance Link                                                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [IUniswapV2Router01.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router01.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2) |
___
```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                                            | Instance Count | Instance Link                                                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [IUniswapV2Router02.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router02.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2) |
___
```solidity
File: contracts/zevm/interfaces/IWZETA.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                          |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [IWZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IWZETA.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IWZETA.sol#L2) |
___
```solidity
File: contracts/zevm/interfaces/IZRC20.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                          |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [IZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol#L2) |
___
```solidity
File: contracts/zevm/interfaces/zContract.sol

2: pragma solidity 0.8.7;
```

| File Link                                                                                                          | Instance Count | Instance Link                                                                                             |
| :----------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------- |
| [zContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/zContract.sol) |              1 | [2](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/zContract.sol#L2) |
___
</details>

#### <a id="g-10"></a> \[G-10\] `internal`/`private` functions only called once can be inlined to save gas
##### Description:
The two extra `JUMP` instructions and additional stack operations needed for function calls costs 20 to 40 gas.

##### Recommendation:
For `internal` or `private` functions used just once, move the function logic to the calling function.

##### Instances:
There are 2 instances of this issue.
```solidity
File: contracts/zevm/SystemContract.sol

87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                         |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [87](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L87) |
___
```solidity
File: contracts/zevm/ZRC20.sol

191:     function _mint(address account, uint256 amount) internal virtual {
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                  |
| :---------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              1 | [191](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L191) |
___
#### <a id="g-11"></a> \[G-11\] Nesting `if`-statements is cheaper than using `&&`
##### Description:
Nesting `if`-statements avoids the stack operations of setting up and using an extra `jumpdest`, and saves 6 gas.

##### Instances:
There are 5 instances of this issue.
```solidity
File: contracts/evm/ERC20Custody.sol

177:         if (zetaFee != 0 && address(zeta) != address(0)) {
178:             zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
179:         }
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                        |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              1 | [177](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L177) |
___
```solidity
File: contracts/evm/Zeta.non-eth.sol

41:         if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                      |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              1 | [41](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L41) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```

| File Link                                                                                                                | Instance Count | Instance Link                                                                                              |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              1 | [129](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L129) |
___
```solidity
File: contracts/zevm/WZETA.sol

49:         if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:             require(allowance[src][msg.sender] >= wad);
51:             allowance[src][msg.sender] -= wad;
52:         }
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              1 | [49](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L49) |
___
```solidity
File: contracts/zevm/ZRC20.sol

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                  |
| :---------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              1 | [226](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L226) |
___
#### <a id="g-12"></a> \[G-12\] Optimize names to save gas
##### Description:
`public` and `external` function names and `public` member variable names can be optimized to save gas. The contracts listed below can be optimized so that the most frequently called functions use the least amount of gas possible during the Method ID lookup. Method IDs that have two leading zero bytes can save 128 gas each during deployment. Renaming functions to have lower Method IDs will save 22 gas per call, [per sorted position shifted](https://medium.com/joyso/solidity-how-does-function-name-affect-gas-consumption-in-smart-contract-47d270d8ac92).

##### Recommendation:
Use a tool like [Solidity Optimize Name](https://emn178.github.io/solidity-optimize-name/) to find names that will generate Method IDs that will prioritize the most used functions.

##### Instances:
There are 22 instances of this issue.
<details><summary>View 22 Instances</summary>

```solidity
File: contracts/evm/Zeta.non-eth.sol

/// @audit updateTssAndConnectorAddresses(), renounceTssAddressUpdater()
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                      |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              1 | [10](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L10) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit updatePauserAddress(), updateTssAddress(), renounceTssAddressUpdater(), pause(), unpause(), send(), onReceive(), onRevert()
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

| File Link                                                                                                                | Instance Count | Instance Link                                                                                            |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              1 | [15](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L15) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit getLockedAmount(), setMaxSupply()
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

| File Link                                                                                                                      | Instance Count | Instance Link                                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              1 | [15](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L15) |
___
```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit onZetaMessage(), onZetaRevert()
56: interface ZetaReceiver {

/// @audit getZetaFromEth(), getZetaFromToken(), getEthFromZeta(), getTokenFromZeta(), hasZetaLiquidity()
77: interface ZetaTokenConsumer {
```

| File Link                                                                                                                   | Instance Count | Instance Links                                                                                                                                                                                                                  |
| :-------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaInterfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInterfaces.sol) |              2 | [56](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInterfaces.sol#L56),[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaInterfaces.sol#L77) |
___
```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

/// @audit burnFrom(), mint()
9: interface ZetaNonEthInterface is IERC20 {
```

| File Link                                                                                                                             | Instance Count | Instance Link                                                                                                      |
| :------------------------------------------------------------------------------------------------------------------------------------ | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [ZetaNonEthInterface.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaNonEthInterface.sol) |              1 | [9](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9) |
___
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

/// @audit safeCreate2(), findCreate2Address(), findCreate2AddressViaHash(), hasBeenDeployed(), safeCreate2AndTransfer()
22: contract ImmutableCreate2Factory {
```

| File Link                                                                                                                                | Instance Count | Instance Link                                                                                                       |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------ |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              1 | [22](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L22) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit exactInputSingle(), exactInput()
24: interface ISwapRouterPancake is IUniswapV3SwapCallback {
```

| File Link                                                                                                                                                        | Instance Count | Instance Link                                                                                                                   |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              1 | [24](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit deposit(), withdraw(), depositTo(), withdrawTo()
20: interface WETH9 {
```

| File Link                                                                                                                                                    | Instance Count | Instance Link                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              1 | [20](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) |
___
```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

/// @audit exactInputSingle(), exactInput(), exactOutputSingle(), exactOutput(), sweep()
16: interface IPoolRouter {
```

| File Link                                                                                                                                 | Instance Count | Instance Link                                                                                                             |
| :---------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------ |
| [TridentIPoolRouter.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentIPoolRouter.sol) |              1 | [16](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) |
___
```solidity
File: contracts/zevm/Interfaces.sol

/// @audit FUNGIBLE_MODULE_ADDRESS(), wZetaContractAddress(), uniswapv2FactoryAddress(), gasPriceByChainId(), gasCoinZRC20ByChainId(), gasZetaPoolByChainId()
7: interface ISystem {

/// @audit totalSupply(), balanceOf(), transfer(), allowance(), approve(), transferFrom(), deposit(), withdraw(), withdrawGasFee()
21: interface IZRC20 {

/// @audit name(), symbol(), decimals()
49: interface IZRC20Metadata is IZRC20 {
```

| File Link                                                                                                 | Instance Count | Instance Links                                                                                                                                                                                                                                                                                      |
| :-------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Interfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol) |              3 | [7](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol#L7),[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol#L21),[49](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol#L49) |
___
```solidity
File: contracts/zevm/SystemContract.sol

/// @audit depositAndCall(), uniswapv2PairFor(), setGasPrice(), setGasCoinZRC20(), setGasZetaPool(), setWZETAContractAddress(), setConnectorZEVMAddress()
22: contract SystemContract is SystemContractErrors {
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                         |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [22](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L22) |
___
```solidity
File: contracts/zevm/WZETA.sol

/// @audit deposit(), withdraw(), totalSupply(), approve(), transfer(), transferFrom()
3: contract WETH9 {
```

| File Link                                                                                       | Instance Count | Instance Link                                                                              |
| :---------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              1 | [3](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L3) |
___
```solidity
File: contracts/zevm/ZRC20.sol

/// @audit burn(), updateSystemContractAddress(), updateGasLimit(), updateProtocolFlatFee()
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

| File Link                                                                                       | Instance Count | Instance Link                                                                                |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              1 | [20](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L20) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit transferFrom(), withdraw()
49: interface WZETA {

/// @audit send(), setWzetaAddress()
55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

| File Link                                                                                                               | Instance Count | Instance Links                                                                                                                                                                                                    |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              2 | [49](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L49),[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L55) |
___
```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

/// @audit factory(), WETH(), addLiquidity(), addLiquidityETH(), removeLiquidity(), removeLiquidityETH(), removeLiquidityWithPermit(), removeLiquidityETHWithPermit(), swapExactTokensForTokens(), swapTokensForExactTokens(), swapExactETHForTokens(), swapTokensForExactETH(), swapExactTokensForETH(), swapETHForExactTokens(), quote(), getAmountOut(), getAmountIn(), getAmountsOut(), getAmountsIn()
4: interface IUniswapV2Router01 {
```

| File Link                                                                                                                            | Instance Count | Instance Link                                                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [IUniswapV2Router01.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router01.sol) |              1 | [4](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) |
___
```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

/// @audit removeLiquidityETHSupportingFeeOnTransferTokens(), removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(), swapExactTokensForTokensSupportingFeeOnTransferTokens(), swapExactETHForTokensSupportingFeeOnTransferTokens(), swapExactTokensForETHSupportingFeeOnTransferTokens()
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

| File Link                                                                                                                            | Instance Count | Instance Link                                                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------------------- |
| [IUniswapV2Router02.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router02.sol) |              1 | [6](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) |
___
```solidity
File: contracts/zevm/interfaces/IWZETA.sol

/// @audit totalSupply(), balanceOf(), allowance(), approve(), transfer(), transferFrom(), deposit(), withdraw()
4: interface IWETH9 {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                          |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [IWZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IWZETA.sol) |              1 | [4](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IWZETA.sol#L4) |
___
```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit totalSupply(), balanceOf(), transfer(), allowance(), approve(), decreaseAllowance(), increaseAllowance(), transferFrom(), deposit(), burn(), withdraw(), withdrawGasFee(), PROTOCOL_FEE()
4: interface IZRC20 {
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                          |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :----------------------------------------------------------------------------------------------------- |
| [IZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol) |              1 | [4](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol#L4) |
___
</details>

#### <a id="g-13"></a> \[G-13\] `require()`/`revert()` strings longer than 32 bytes cost extra gas
##### Description:
Shortening revert strings to fit in 32 bytes will decrease deploy-time gas and will decrease runtime gas when the revert condition has been met. Revert strings that are longer than 32 bytes require at least one additional `mstore` (3 gas), along with additional overhead for computing memory offset, etc. (When using Solidity 0.8.4 or later, it is recommended to use custom errors instead.)

##### Instances:
There are 2 instances of this issue. These are additional instances of an issue listed in the automated findings report.
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

67:         require(
68:             deploymentAddress == targetDeploymentAddress,
69:             "Failed to deploy contract using provided salt and initialization code."
70:         );

195:         require(
196:             (address(bytes20(salt)) == msg.sender) || (bytes20(salt) == bytes20(0)),
197:             "Invalid salt - first 20 bytes of the salt must match calling address."
198:         );
```

| File Link                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                            |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              2 | [67](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L67),[195](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L195) |
___
#### <a id="g-14"></a> \[G-14\] Simple checks for zero can be done using assembly to save gas
##### Description:
Example code is at [Solidity Assembly: Checking if an Address is 0 (Efficiently)](https://medium.com/@kalexotsu/solidity-assembly-checking-if-an-address-is-0-efficiently-d2bfe071331).

##### Instances:
There are 68 instances of this issue.
<details><summary>View 68 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

81:         if (TSSAddress_ == address(0)) {

108:         if (TSSAddress == address(0)) {

122:         if (TSSAddress == address(0)) {

177:         if (zetaFee != 0 && address(zeta) != address(0)) {
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                    |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              4 | [81](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L81),[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L108),[122](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L122),[177](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L177) |
___
```solidity
File: contracts/evm/Zeta.non-eth.sol

34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

56:         if (tssAddress == address(0)) revert InvalidAddress();
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              5 | [34](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L34),[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L34),[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L42),[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L42),[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L56) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

76:             zetaToken_ == address(0) ||

77:             tssAddress_ == address(0) ||

78:             tssAddressUpdater_ == address(0) ||

79:             pauserAddress_ == address(0)

118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:         if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

141:         if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

| File Link                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              7 | [76](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L76),[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L77),[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L78),[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L79),[118](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L118),[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L130),[141](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L141) |
___
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

196:             (address(bytes20(salt)) == msg.sender) || (bytes20(salt) == bytes20(0)),
```

| File Link                                                                                                                                | Instance Count | Instance Link                                                                                                         |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              1 | [196](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L196) |
___
```solidity
File: contracts/evm/tools/ZetaInteractor.sol

38:         if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                              |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol) |              1 | [38](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol#L38) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

80:             zetaToken_ == address(0) ||

81:             pancakeV3Router_ == address(0) ||

82:             uniswapV3Factory_ == address(0) ||

83:             WETH9Address_ == address(0)

107:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

212:         if (poolAddress == address(0)) {
```

| File Link                                                                                                                                                        | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |             11 | [80](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L80),[81](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L81),[82](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L82),[83](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L83),[107](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107),[132](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132),[132](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132),[156](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156),[190](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190),[190](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190),[212](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L212) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

47:             zetaToken_ == address(0) ||

48:             uniswapV3Router_ == address(0) ||

49:             WETH9Address_ == address(0) ||

50:             poolFactory_ == address(0)

78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

| File Link                                                                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |             10 | [47](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L47),[48](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L48),[49](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L49),[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L50),[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78),[105](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105),[105](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105),[141](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141),[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172),[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

38:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              8 | [27](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27),[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27),[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38),[64](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64),[64](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64),[100](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100),[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130),[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

51:             zetaToken_ == address(0) ||

52:             uniswapV3Router_ == address(0) ||

53:             uniswapV3Factory_ == address(0) ||

54:             WETH9Address_ == address(0)

78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

187:         if (poolAddress == address(0)) {
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |             11 | [51](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L51),[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L52),[53](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L53),[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L54),[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78),[104](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104),[104](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104),[129](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129),[164](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164),[164](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164),[187](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L187) |
___
```solidity
File: contracts/zevm/SystemContract.sol

90:         if (token0 == address(0)) revert CantBeZeroAddress();

158:         if (addr == address(0)) revert ZeroAddress();

169:         if (addr == address(0)) revert ZeroAddress();
```

| File Link                                                                                                         | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                        |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              3 | [90](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L90),[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L158),[169](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L169) |
___
```solidity
File: contracts/zevm/ZRC20.sol

179:         if (sender == address(0)) revert ZeroAddress();

180:         if (recipient == address(0)) revert ZeroAddress();

192:         if (account == address(0)) revert ZeroAddress();

200:         if (account == address(0)) revert ZeroAddress();

212:         if (owner == address(0)) revert ZeroAddress();

213:         if (spender == address(0)) revert ZeroAddress();

238:         if (gasZRC20 == address(0)) {
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| :---------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              7 | [179](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L179),[180](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L180),[192](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L192),[200](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L200),[212](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L212),[213](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L213),[238](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L238) |
___
</details>

#### <a id="g-15"></a> \[G-15\] State variables only set in the constructor should be declared `immutable`
##### Description:
If a state variable is set only in the constructor, then it should be declared `immutable`. Doing this avoids a `Gsset` (20,000 gas) in the constructor, and replaces the first access in each transaction (`Gcoldsload` 2,100 gas) and each subsequent access (`Gwarmacces` 100 gas) with a `PUSH32` (3 gas).
Although `string`s are not value types and so cannot be `immutable` or `constant` if not hard-coded outside of the constructor, the same behavior can be achieved by making the contract `abstract` with `virtual` functions for the `string` accessors, and having a child contract override the functions with the hard-coded implementation-specific values.

##### Instances:
There are 3 instances of this issue.
```solidity
File: contracts/zevm/ZRC20.sol

37:     string private _name;

38:     string private _symbol;

39:     uint8 private _decimals;
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                         |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [37](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L37),[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L38),[39](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L39) |
___
#### <a id="g-16"></a> \[G-16\] Use assembly for small keccak256 hashes, in order to save gas
##### Description:
If the arguments to the encode call can fit into the scratch space (two words or fewer), then it is more efficient to use assembly to generate the hash (80 gas).

##### Recommendation:
Use assembly as shown in the following example:
```solidity
// Before:
keccak256(abi.encodePacked(x, y));

// After
assembly {
  mstore(0x00, a);
  mstore(0x20, b);
  let hash := keccak256(0x00, 0x40);
}
```

##### Instances:
There are 3 instances of this issue.
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

42:                             keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.

121:                             keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
```

| File Link                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                            |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              2 | [42](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L42),[121](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L121) |
___
```solidity
File: contracts/zevm/SystemContract.sol

109:                             keccak256(abi.encodePacked(token0, token1)),
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                           |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------ |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [109](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L109) |
___
#### <a id="g-17"></a> \[G-17\] Use assembly to emit events, in order to save gas
##### Description:
Using the [scratch space](https://github.com/Vectorized/solady/blob/30558f5402f02351b96eeb6eaf32bcea29773841/src/tokens/ERC1155.sol#L501-L504) for event arguments (two words or fewer) will save gas over needing Solidity's full abi memory expansion used for emitting normally.

##### Instances:
There are 32 instances of this issue.
<details><summary>View 32 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

85:         emit UpdatedTSSAddress(TSSAddress_);

100:         emit UpdatedZetaFee(zetaFee_);

112:         emit RenouncedTSSUpdater(msg.sender);

126:         emit Paused(msg.sender);

137:         emit Unpaused(msg.sender);

146:         emit Whitelisted(asset);

155:         emit Unwhitelisted(asset);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              7 | [85](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L85),[100](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L100),[112](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L112),[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L126),[137](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L137),[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L146),[155](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L155) |
___
```solidity
File: contracts/evm/Zeta.non-eth.sol

47:         emit TSSAddressUpdated(msg.sender, tssAddress_);

48:         emit ConnectorAddressUpdated(msg.sender, connectorAddress_);

59:         emit TSSAddressUpdaterUpdated(msg.sender, tssAddress);

81:         emit Burnt(account, amount);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                              |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol) |              4 | [47](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L47),[48](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L48),[59](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L59),[81](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/Zeta.non-eth.sol#L81) |
___
```solidity
File: contracts/evm/ZetaConnector.base.sol

122:         emit PauserAddressUpdated(msg.sender, pauserAddress_);

134:         emit TSSAddressUpdated(msg.sender, tssAddress_);

144:         emit TSSAddressUpdaterUpdated(msg.sender, tssAddressUpdater);
```

| File Link                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                   |
| :----------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol) |              3 | [122](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L122),[134](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L134),[144](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.base.sol#L144) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

33:         emit MaxSupplyUpdated(msg.sender, maxSupply_);
```

| File Link                                                                                                                      | Instance Count | Instance Link                                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              1 | [33](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L33) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

122:         emit EthExchangedForZeta(msg.value, amountOut);

176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

| File Link                                                                                                                                                        | Instance Count | Instance Links                                                                                                                                                                                                                                                      |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              2 | [122](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L122),[176](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

95:         emit EthExchangedForZeta(msg.value, amountOut);

161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

| File Link                                                                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              2 | [95](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95),[161](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

54:         emit EthExchangedForZeta(msg.value, amountOut);

120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                            |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              2 | [54](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L54),[120](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

94:         emit EthExchangedForZeta(msg.value, amountOut);

150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                            |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              2 | [94](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L94),[150](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150) |
___
```solidity
File: contracts/zevm/SystemContract.sol

126:         emit SetGasPrice(chainID, price);

137:         emit SetGasCoin(chainID, zrc20);

149:         emit SetGasZetaPool(chainID, pool);

160:         emit SetWZeta(wZetaContractAddress);

171:         emit SetConnectorZEVM(zetaConnectorZEVMAddress);
```

| File Link                                                                                                         | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              5 | [126](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L126),[137](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L137),[149](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L149),[160](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L160),[171](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L171) |
___
```solidity
File: contracts/zevm/ZRC20.sol

272:         emit UpdatedSystemContract(addr);

281:         emit UpdatedGasLimit(gasLimit);

290:         emit UpdatedProtocolFlatFee(protocolFlatFee);
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                               |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [272](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L272),[281](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L281),[290](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L290) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

117:         emit SetWZETA(wzeta_);
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                              |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [117](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L117) |
___
</details>

#### <a id="g-18"></a> \[G-18\] Use `calldata` instead of `memory` for function arguments that do not get mutated
##### Description:
Mark data types as `calldata` instead of `memory` where possible. This makes it so that the data is not automatically loaded into memory. If the data passed into the function does not need to be changed (like updating values in an array), it can be passed in as `calldata`. The one exception to this is if the argument must later be passed into another function that takes an argument that specifies `memory` storage.

[Example with gas report](https://gist.github.com/ezcodeslide/d95c73d677bf93f4da21331e7e2c7040).

##### Instances:
There are 6 instances of this issue.
<details><summary>View 6 Instances</summary>

```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

/// @audit initializationCode
87:     function safeCreate2(
88:         bytes32 salt,
89:         bytes memory initializationCode
90:     ) public payable containsCaller(salt) returns (address deploymentAddress) {
```

| File Link                                                                                                                                | Instance Count | Instance Link                                                                                                       |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------ |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              1 | [87](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L87) |
___
```solidity
File: contracts/zevm/Interfaces.sol

/// @audit to
36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

| File Link                                                                                                 | Instance Count | Instance Link                                                                                     |
| :-------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------ |
| [Interfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol) |              1 | [36](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/Interfaces.sol#L36) |
___
```solidity
File: contracts/zevm/ZRC20.sol

/// @audit name_
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {

/// @audit symbol_
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {

/// @audit to
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                           |
| :---------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol) |              3 | [60](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L60),[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L60),[256](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZRC20.sol#L256) |
___
```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit to
25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

| File Link                                                                                                    | Instance Count | Instance Link                                                                                            |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [IZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol) |              1 | [25](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/interfaces/IZRC20.sol#L25) |
___
</details>

#### <a id="g-19"></a> \[G-19\] Use custom errors rather than `revert()`/`require()` strings to save gas
##### Description:
Custom errors are available since Solidity 0.8.4. Custom errors save ~50 gas each time they are hit by [avoiding having to allocate and store the revert string](https://blog.soliditylang.org/2021/04/21/custom-errors/#errors-in-depth). Not defining the strings will also save deployment gas.

##### Instances:
There are 5 instances of this issue. These are additional instances of an issue listed in the automated findings report.
<details><summary>View 5 Instances</summary>

```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

67:         require(
68:             deploymentAddress == targetDeploymentAddress,
69:             "Failed to deploy contract using provided salt and initialization code."
70:         );

195:         require(
196:             (address(bytes20(salt)) == msg.sender) || (bytes20(salt) == bytes20(0)),
197:             "Invalid salt - first 20 bytes of the salt must match calling address."
198:         );
```

| File Link                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                            |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              2 | [67](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L67),[195](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L195) |
___
```solidity
File: contracts/zevm/WZETA.sol

26:         require(balanceOf[msg.sender] >= wad);

47:         require(balanceOf[src] >= wad);

50:             require(allowance[src][msg.sender] >= wad);
```

| File Link                                                                                       | Instance Count | Instance Links                                                                                                                                                                                                                                                                         |
| :---------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol) |              3 | [26](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L26),[47](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L47),[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/WZETA.sol#L50) |
___
</details>

#### <a id="g-20"></a> \[G-20\] Use predefined address instead of `address(this)`
##### Description:
Instead of using `address(this)`, it is more gas-efficient to pre-calculate and use the predefined address. Foundry's `script.sol` and Solmate's `LibRlp.sol` contracts can help pre-determine the address (see [computeCreateAddress](https://book.getfoundry.sh/reference/forge-std/compute-create-address)). The address can be passed in via a constructor argument and assigned to an immutable variable (rather than using a hardcoded constant) so that the code can remain the same across deployments on different networks.

##### Instances:
There are 26 instances of this issue.
<details><summary>View 26 Instances</summary>

```solidity
File: contracts/evm/ERC20Custody.sol

180:         uint256 oldBalance = asset.balanceOf(address(this));

181:         asset.safeTransferFrom(msg.sender, address(this), amount);

184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

| File Link                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol) |              3 | [180](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L180),[181](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L181),[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ERC20Custody.sol#L184) |
___
```solidity
File: contracts/evm/ZetaConnector.eth.sol

24:         return IERC20(zetaToken).balanceOf(address(this));

32:         bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
```

| File Link                                                                                                              | Instance Count | Instance Links                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol) |              2 | [24](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L24),[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.eth.sol#L32) |
___
```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

28:         return ZetaNonEthInterface(zetaToken).balanceOf(address(this));
```

| File Link                                                                                                                      | Instance Count | Instance Link                                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------- |
| [ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol) |              1 | [28](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/ZetaConnector.non-eth.sol#L28) |
___
```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

40:                             address(this), // this contract will be the caller.

119:                             address(this), // this contract will be the caller.

159:                             address(this), // this contract will be the caller.
```

| File Link                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol) |              3 | [40](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L40),[119](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L119),[159](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ImmutableCreate2Factory.sol#L159) |
___
```solidity
File: contracts/evm/tools/ZetaInteractor.sol

32:         if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
```

| File Link                                                                                                              | Instance Count | Instance Link                                                                                              |
| :--------------------------------------------------------------------------------------------------------------------- | -------------: | :--------------------------------------------------------------------------------------------------------- |
| [ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol) |              1 | [32](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaInteractor.sol#L32) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

159:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

166:             recipient: address(this),

193:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

| File Link                                                                                                                                                        | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol) |              4 | [135](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135),[159](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L159),[166](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L166),[193](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L193) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

144:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

175:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

| File Link                                                                                                                                                    | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                  |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol) |              3 | [108](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108),[144](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L144),[175](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L175) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

103:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

133:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                          |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol) |              3 | [67](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67),[103](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L103),[133](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L133) |
___
```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

132:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

140:             recipient: address(this),

167:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

| File Link                                                                                                                                                | Instance Count | Instance Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol) |              4 | [107](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107),[132](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L132),[140](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L140),[167](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L167) |
___
```solidity
File: contracts/zevm/SystemContract.sol

75:         if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
```

| File Link                                                                                                         | Instance Count | Instance Link                                                                                         |
| :---------------------------------------------------------------------------------------------------------------- | -------------: | :---------------------------------------------------------------------------------------------------- |
| [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol) |              1 | [75](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/SystemContract.sol#L75) |
___
```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

94:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
```

| File Link                                                                                                               | Instance Count | Instance Link                                                                                            |
| :---------------------------------------------------------------------------------------------------------------------- | -------------: | :------------------------------------------------------------------------------------------------------- |
| [ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol) |              1 | [94](https://github.com/code-423n4/2023-11-zetachain/blob/main/contracts/zevm/ZetaConnectorZEVM.sol#L94) |
___
</details>
