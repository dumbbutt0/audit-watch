# [QA-01] Setters in `SystemContract.sol` does not verify if the value was really changed

[File: SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134)
```
 function setGasCoinZRC20(uint256 chainID, address zrc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasCoinZRC20ByChainId[chainID] = zrc20;
        emit SetGasCoin(chainID, zrc20);
    }
```

Whenever we update/set a new value of some state variable, it's a good practice to make sure that, that value is being indeed updated.
In the current implementation of `setGasCoinZRC20()`, even when the `gasCoinZRC20ByChainId[chainID]` won't be changed, function will still emit an `SetGasCoin()` event - which might be misleading to the end-user.
E.g. let's assume that `gasCoinZRC20ByChainId[1] = 0x123`. Calling `setGasCoinZRC20(1, 0x123)` won't update/set anything new, but `SetGasCoin()` will still be emitted.

Our recommendation is to add additional `require` check, to verify, that provided values are indeed different than the current ones:

```
require(gasCoinZRC20ByChainId[chainID] != zrc20, "Nothing to update");
```

The same issue occurs in `setGasPrice()`, `setGasZetaPool()`, `setWZETAContractAddress()`, `setConnectorZEVMAddress()` too.

# [QA-02] Setters in `SystemContract.sol` can set values for non-existing chain IDs.

[File: SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134)
```
 function setGasCoinZRC20(uint256 chainID, address zrc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasCoinZRC20ByChainId[chainID] = zrc20;
        emit SetGasCoin(chainID, zrc20);
    }
```

There's no verification if `chainID` already exist. This implies, that it's possible to set `gasCoinZRC20` for non-yet-existing chainIDs. Whenever those chain IDs will be created later - `gasCoinZRC20` will be already set for it - which might lead to some incorrect behavior and/or assumptions about chain ID. When new chain ID starts to exist, `GasCoinZRC20` should not exist for it. However, nothing stops the caller from calling `setGasCoinZRC20()` before chain ID is defined. When chain ID becomes available, setGasCoinZRC20, will already be set.

Make sure to verify that `chainID` exist, before calling `setGasCoinZRC20()`.

The same issue occurs in `setGasPrice()`, `setGasZetaPool()`, `setWZETAContractAddress()`, `setConnectorZEVMAddress()` too.


# [QA-03] Lack of address(0x0) check in `setGasCoinZRC20()` in `SystemContract.sol`.
While most of the functions, e.g. `setWZETAContractAddress()`, `setConnectorZEVMAddress()` checks if provided parameter is not `address(0)`, there's no such a check in `setGasCoinZRC20()`.
This implies that it's possible to set `gasCoinZRC20ByChainId[chainID]` to `address(0)`.


[File: SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134)
```
 function setGasCoinZRC20(uint256 chainID, address zrc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasCoinZRC20ByChainId[chainID] = zrc20;
        emit SetGasCoin(chainID, zrc20);
    }
```

Add additional check:

```
if (zrc20 == address(0)) revert ZeroAddress();
```


# [QA-04] Events that mark critical parameter changes should contain both the old and the new value

This should especially be done if the new value is not required to be different from the old value

[File: SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134)
```
 function setGasCoinZRC20(uint256 chainID, address zrc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasCoinZRC20ByChainId[chainID] = zrc20;
        emit SetGasCoin(chainID, zrc20);
    }
```

The same issue occurs in `setGasPrice()`, `setGasZetaPool()`, `setWZETAContractAddress()`, `setConnectorZEVMAddress()` too.


# [QA-05] Critical Address Changes Should Use Two-step Procedure

[File: ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117)
```
    function updatePauserAddress(address pauserAddress_) external onlyPauser {
        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

        pauserAddress = pauserAddress_;

        emit PauserAddressUpdated(msg.sender, pauserAddress_);
    }

```

Function `updatePauserAddress()` can be called only by the current pauser. Whenever invalid address (e.g. by mistake) will be provided as a parameter to the `updatePauserAddress()` function - the protocol will loose the pauser privilege. Lack of two-step procedure for critical operations leaves them error-prone. Consider adding a two-step procedure on the critical functions.


# [QA-06] Incorrect function descriptions in `ZRC20.sol`

* `transfer()`

[File: ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L120-L128)
```
/**
     * @dev Returns ZRC20 balance of an account.
     * @param recipient, recipiuent address to which transfer is done.
     * @return true/false if transfer succeeded/failed.
     */
    function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
        _transfer(_msgSender(), recipient, amount);
        return true;
    }
```

According to NatSpec, function `transfer()` returns `true/false if transfer succeeded/failed`. When we look at `_transfer()` implementation which is called in function `transfer()`, we can see, that this function either reverts or does not return anything. This implies that `transfer()` will never return false. It will either return true on success or revert on fail. The comment should be changed to `@return true/reverts if transfer succeeded/failed.`


* `approve()`

[File: ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L139-L148)
```
 /**
     * @dev Approves amount transferFrom for spender.
     * @param spender, spender address.
     * @param amount, amount to approve.
     * @return true/false if succeeded/failed.
     */
    function approve(address spender, uint256 amount) public virtual override returns (bool) {
        _approve(_msgSender(), spender, amount);
        return true;
    }

```

According to NatSPec, function `approve()` returns `true/false if succeeded/failed`. When we look at `_approve()` implementation which is called in function `approve()`, we can see, that this function either reverts or does not return anything. This implies that `approve()` will never return false. It will either return true on success or revert on fail. The comment should be changed to `@return true/reverts if  succeeded/failed.`

The same issue occurs for other functions: `transferFrom()`, `burn()`, `deposit()`, `withdraw()`. Those function also reverts on fail (instead of returning `false`). This implies that their NatSpec comment should be changed to:  `@return true/reverts if  succeeded/failed`.


# [R-01] Use tautology in `WZETA.sol` to avoid double negation

Due to the De Morgan's laws: `(not A) and (not B) == not (A or B)`, we can get rid of double negation in `transferFrom()` in `WZETA.sol`

[File: WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L49)
```
 if (src != msg.sender && allowance[src][msg.sender] != uint(-1))
```

can be changed to:

```
 if (  !(src == msg.sender || allowance[src][msg.sender] == uint(-1))  )
```

# [R-02] Implement modifier for checking if `msg.sender != FUNGIBLE_MODULE_ADDRESS` in `SystemContract.sol`

There are multiple of functions in `SystemContract.sol` which performs below check:

```
if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

We can spot them in `setGasPrice()`, `setGasCoinZRC20()`, `setGasZetaPool()`, `setWZETAContractAddress()`, `setConnectorZEVMAddress()`.

It will improve the code readability, when this check will be implemented as a modifier.
Implement additional modifier which performs above check and use it in above functions.


# [R-03] Improve code readability by divining multiple-OR condition in `ZeraConnector.base.sol`

[File: ZeraConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L75)
```
 if (
            zetaToken_ == address(0) ||
            tssAddress_ == address(0) ||
            tssAddressUpdater_ == address(0) ||
            pauserAddress_ == address(0)
        ) {
            revert ZetaCommonErrors.InvalidAddress();
        }
```

Multiple OR conditions decreases the code readability and waste gas (it's better for gas to divide one single `if` with multiple `OR`s to multiple `if`s statements instead). This implies, that above condition can be rewritten to:

```
if (zetaToken_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
if (tssAddressUpdater_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

# [R-04] Checking if `tssAddress == address(0)` in `renounceTssAddressUpdater()` is redundant

[File: ZeraConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140-L144)
```
function renounceTssAddressUpdater() external onlyTssUpdater {
        if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

        tssAddressUpdater = tssAddress;
        emit TSSAddressUpdaterUpdated(msg.sender, tssAddressUpdater);
    }
```

`tssAddress` is being set either in constructor or in `updateTssAddress()`. In both function there's additional check which verifies that `tssAddress` cannot be address(0). This implies that whenever `renounceTssAddressUpdater()` will be called,  `tssAddress` will never be `address(0)`. This implies that `if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();` is redundant.


# [R-05] `MAX_DEADLINE` is not used in some strategies

Every strategy: `ZetaTokenConsumerPancakeV3.strategy.sol`, `ZetaTokenConsumerTrident.strategy.sol`, `ZetaTokenConsumerUniV3.strategy.sol`, `ZetaTokenConsumerUniV2.strategy.sol` defines constant `MAX_DEADLINE`: `uint256 internal constant MAX_DEADLINE = 200;`.
However, when we take a deeper look at each of these strategies' codebase, we can notice, that only `ZetaTokenConsumerUniV3.strategy.sol` and `ZetaTokenConsumerUniV2.strategy.sol` use this constant to calculate deadline.

In `ZetaTokenConsumerPancakeV3.strategy.sol` and `ZetaTokenConsumerTrident.strategy.sol`, constant `MAX_DEADLINE` is only defined, but nowhere used, which implies, that this constant in redundant in those two strategies and can be removed.


# [R-06] Redundant casting to `uint256` in `Zeta.eth.sol`

[File: Zeta.eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L11)
```
 _mint(creator, initialSupply * (10 ** uint256(decimals())));
```

While `decimals()` returns `uint8` value, there's no need to cast that value when using it as an exponent.


# [R-07] `setInteractorByChainId()` does not emit an event

[File: ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54)
```
    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
        interactorsByChainId[destinationChainId] = contractAddress;
    }
```

Since `setInteractorByChainId()` modifies the state variable (it adds new value to `interactorsByChainId` mapping), it should emit an event. The current implementation of `interactorsByChainId()` does not emit an event.




# [R-08] Use tautology in `updateTssAndConnectorAddresses()` to reduce number of negations

Due to De Morgans Law: `(NOT A) AND (NOT B) == NOT (A OR B)`

This implies that below code:

[File: Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41)
```
if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
```

can be rewritten to:

```
if (!(msg.sender == tssAddressUpdater || msg.sender == tssAddress)) revert CallerIsNotTssOrUpdater(msg.sender);
```

to reduce the number of NOT operators.


# [R-09] `TODO` comment suggests that code is not finished

[File: ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203)
```
 function hasZetaLiquidity() external view override returns (bool) {
        //@TODO: Implement
        return false;
    }
```
According to `TODO` comment, function `hasZetaLiquidity()` is not yet implemented. This function always return false.


# [N-01] Do not use upper-case in function names

According to Solidity naming convention, upper-case (e.g. `TEST`) is reserved for constants. Function names should be represented in camel-case (e.g. `functionName`).

In `IZRC20.sol` there's a deviation from this convention:

[File: IZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29)
```
function PROTOCOL_FEE() external view returns (uint256);
```

[File: Interfaces.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8)
```
function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
```

# [N-02] Use more descriptive parameter names

[File: ZetaNonEthInterface.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12)
```
function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```

Word `mintee` does not exist in the English dictionary. It supposed to be an address where the tokens will be mint. Since `ZetaNonEthInterface.sol` implements also `burnFrom()` function with parameter `account`, it will be much clear to use `account` (instead of `mintee`) in function `mint()` too.


# [N-03] Typos

[File: ZetaInteractorErrors.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8)
```
 // @dev Thrown when try to send a message or tokens to a non whitelisted chain
```

`non whitelisted` should be changed to `non-whitelisted`.

[File: ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183)
```
// and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount
```

`o we subtract` should be changed to `so we subtract`.

[File: ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L122)
```
* @param recipient, recipiuent address to which transfer is done.
```

`recipiuent` should be changed to `recipient`.

# [N-04] Do not use contractions in error names

[File: SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13-L14)
```
    error CantBeIdenticalAddresses();
    error CantBeZeroAddress();
```

Do not use contraction-forms in error names. It's better to use full name: `CanNot` instead of `Cant`, since it improves readability of the code.
Change `error CantBeIdenticalAddresses()` to `error CanNotBeIdenticalAddresses()`.
Change `error CantBeZeroAddress();` to `error CanNotBeZeroAddress();`


# [N-05] Use shorted `require` messages

There is no need to use excessively long strings in `require` statements, since `require()` strings longer than 32 bytes cost extra gas. Above strings can be made shorter and still enough descriptive:

[File: ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L197)
```
require(
            (address(bytes20(salt)) == msg.sender) || (bytes20(salt) == bytes20(0)),
            "Invalid salt - first 20 bytes of the salt must match calling address."
        );
```

[File: ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L67)
```
 require(
            deploymentAddress == targetDeploymentAddress,
            "Failed to deploy contract using provided salt and initialization code."
        );
```

[File: ImmutableCreate2Factory.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L50)
```
require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
```

E.g., above `require` string can be shorten to: `Contract already deployed`.


# [N-06] Change the name of `setMaxSupply` to `updateMaxSupply`

[File: ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31)
```
 function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
        maxSupply = maxSupply_;
        emit MaxSupplyUpdated(msg.sender, maxSupply_);
    }
```

`maxSupply` is already set to `2 ** 256 - 1` (line 16: ` uint256 public maxSupply = 2 ** 256 - 1;`), which implies, that calling `setMaxSupply()` will only update this value. We recommend to change the name of this function which will better describe its purpose. `setMaxSupply()` is responsible for updating the current `maxSupply`, thus it should be named to `updateMaxSupply()`.


# [N-07] `@dev` should be used inside NatSpec in `Zeta.non-eth.sol`

[File: Zeta.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62)
```
function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
        /**
         * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
         */
        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
        [...]
```

NatSpec should be defined above the function, instead of inside the function. E.g.:
```
 /**
 * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
*/
function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
       
        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
        [...]
```

The same issue occurs in `burnFrom()`.


# [N-08] Use `uint256` instead of `uint`
While `uint` is a shorter form of `uint256`, using `uint256` improves code readability.
The problem occurs across the whole `WZETA.sol` contract, where every `uint256` is represented by `uint`. Our recommendation is to change `uint` to `uint256`.


# [N-09] `WZETA.sol` does not implement increasing/decreasing approvals, which implies, that it's prone to front-running

Accorgind to [Code4rena Severity Categorization](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization#approve-race-condition-nc-or-invalid) this issue has been reported as NC.

`WZETA.sol` implements only `approve` function. This function is prone to front-running attack,

1. Alice approves Bob to spend 100 of her tokens. She calls `approve(0xB0B, 100)`.
2. After some time, see changes her mind and decides that Bob should spend only 10 of her tokens. She calls approve again: `approve(0xB0B, 10)`.
3. Bob sees that 2nd transaction in the mem-pool and decides to front-run her. Firstly, he spends 100 tokens (because of the first approve). Then, 2nd approve comes. After that approval, he spends another 10 tokens.
4. Bob front-runned Alice and was able to spend 100 + 10 = 110 tokens, instead of 10.

Our recommendation is to implement additional functions: `increaseAllowance`, `decreaseAllowance`.

It's worth to notice, that `increaseAllowance` and `decreaseAllowance` was removed from OpenZeppelin's ERC-20 standard: `https://github.com/OpenZeppelin/openzeppelin-contracts/issues/4583`
Since this attack is not practical (likelihood is very low) - we've decided to describe it only in QA section.
