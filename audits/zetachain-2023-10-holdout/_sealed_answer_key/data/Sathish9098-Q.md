# QA Report

## LOW FINDINGS

##

## [L-1] Contradiction between documentation and implementation in ``deposit()`` Function

### Impact

The comment suggests exclusive access for the Fungible module, but the implementation allows both the Fungible module and the System contract to call the function. This broader access control could be intentional (for added flexibility) or an oversight.

The comment describes the function as handling deposits from an external chain, but the implementation does not show any direct mechanism for interacting with external chains. Instead, it mints tokens on the current chain.

### POC
```solidity
FILE: Breadcrumbs2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

 /**
     * @dev Deposits corresponding tokens from external chain, only callable by Fungible module.
     * @param to, recipient address.
     * @param amount, amount to deposit.
     * @return true/false if succeeded/failed.
     */
    function deposit(address to, uint256 amount) external override returns (bool) {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
        _mint(to, amount);
        emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);
        return true;
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L219-L230

### Recommended Mitigation

```solidity
/**
 * @dev Mints tokens to a specific address, callable by either Fungible module or System contract.
 * This function does not handle external chain deposits directly but mints new tokens on the current chain.
 * Access is restricted to ensure controlled minting operations.
 * @param to The recipient address to receive the minted tokens.
 * @param amount The amount of tokens to be minted and deposited to the 'to' address.
 * @return true Indicates successful execution of the function.
 */

```
##

## [L-2] Hardcoded ChainId

### Impact
In systems where signatures are used for authentication or transaction verification, a hardcoded CHAIN_ID can cause issues if the network’s chain ID changes. This could invalidate existing signatures or compromise the integrity of new ones.

For protocols designed to operate across multiple chains, a hardcoded CHAIN_ID can limit functionality. It may prevent the protocol from correctly identifying and interacting with different networks, thereby reducing its cross-chain operability.

Hardcoding CHAIN_ID can create hurdles when moving a contract from a testnet to the mainnet or vice versa, as these environments typically have different chain IDs.

### POC

```solidity

FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm
/ZRC20.sol

24:  uint256 public immutable CHAIN_ID;

```
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L24

### Recommended Mitigation
Make chain id configurable 

```diff
- 24:  uint256 public immutable CHAIN_ID;
+ 24:  uint256 public CHAIN_ID;
```

##

## [L-3] Lack of sanity checks for ``address`` and ``uint256`` when assigning to state variable

### Impact
The absence of sanity checks for address and uint256 types in the provided smart contract constructor can lead to several potential issues and vulnerabilities.

Add checks to ensure that no critical addresses are set to the zero address. Additionally, verify the type of address if necessary (e.g., smart contract vs. EOA).

Implement range checks and logical consistency validations for uint256 parameters. Ensure that values like ``gasLimit_`` are within sensible limits.

### POC
```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 chainid_,
        CoinType coinType_,
        uint256 gasLimit_,
        address systemContractAddress_
    ) {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        _name = name_;
        _symbol = symbol_;
        _decimals = decimals_;
        CHAIN_ID = chainid_;
        COIN_TYPE = coinType_;
        GAS_LIMIT = gasLimit_;
        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77

### Recommended Mitigations

```solidity

require(systemContractAddress_ != address(0), "System contract address cannot be zero");

    // uint256 sanity checks
    require(chainid_ > 0, "Invalid Chain ID");
    require(gasLimit_ >= minGasLimit && gasLimit_ <= maxGasLimit, "Gas limit out of range");

```

## 

## [L-4] receive()/payable fallback() function does not authorize requests

### Impact
Having no access control on the function (e.g. require(msg.sender == address(weth))) means that someone may send Ether to the contract, and have no way to get anything back out, which is a loss of funds. If the concern is having to spend a small amount of gas to check the sender against an immutable address, the code should at least have a function to rescue mistakenly-sent Ether.

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101: receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerTrident.strategy.sol

66: receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72: receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72

### Recommended Mitigation
Add rescue functions

```solidity

function rescueEther() external {
        require(msg.sender == owner, "Only the owner can rescue Ether");
        payable(owner).transfer(address(this).balance);
    }

``` 

##

## [L-5] Implementing Dual-Phase Protocol address updates for enhanced security 

### Impact

A copy-paste error or a typo may end up bricking protocol functionality, or sending tokens to an address with no known private key. Consider implementing a two-step procedure for updating protocol addresses, where the recipient is set as pending, and must 'accept' the assignment by making an affirmative call. A straight forward way of doing this would be to have the target contracts implement [EIP-165](https://eips.ethereum.org/EIPS/eip-165), and to have the 'set' functions ensure that the recipient is of the right interface type.

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

function updateSystemContractAddress(address addr) external onlyFungible {
        SYSTEM_CONTRACT_ADDRESS = addr;
        emit UpdatedSystemContract(addr);
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270-L273

##

## [L-6] External call recipient may consume all transaction gas

### Impact

There is no limit specified on the amount of gas used, so the recipient can use up all of the transaction's gas, causing it to revert. Use addr.call{gas: <amount>}("") or [this]() library instead.

### POC

```solidity
FILE: Breadcrumbs2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerPancakeV3.strategy.sol

178: (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerUniV3.strategy.sol

152: (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm
/ZetaConnectorZEVM.sol


96: (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96

##

## [L-7] Lack of address(0) in important SYSTEM_CONTRACT_ADDRESS update 

### Impact
Without a check for address(0), there's a risk that the SYSTEM_CONTRACT_ADDRESS could be set to this null address. This could happen either accidentally (due to a programming error) or maliciously (if an attacker gains control)

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

   function updateSystemContractAddress(address addr) external onlyFungible {
        SYSTEM_CONTRACT_ADDRESS = addr;
        emit UpdatedSystemContract(addr);
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270-L273

### Recommended Mitigation

```diff

function updateSystemContractAddress(address addr) external onlyFungible {
+    require(addr != address(0), "Address cannot be zero");

    SYSTEM_CONTRACT_ADDRESS = addr;
    emit UpdatedSystemContract(addr);
}

```

##

## [L-8] Missing contract-existence checks before low-level calls

### Impact

Low-level calls return success if there is no code present at the specified address. In addition to the zero-address checks, add a check to verify that <address>.code.length > 0


### POC

```solidity
FILE: Breadcrumbs2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerPancakeV3.strategy.sol

178: (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerUniV3.strategy.sol

152: (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152

##

## [L-9] Numbers downcast to addresses may result in collisions

### Impact
If a number is downcast to an address the upper bytes are truncated, which may mean that more than one value will map to the address

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

34: // determine the target address for contract deployment.
        address targetDeploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );

113: deploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L33-L47

##

## [L-10] State variables not capped at reasonable values

### Impact
Consider adding minimum/maximum value checks to ensure that the state variables below can never be used to excessively harm users, including via griefing

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

 function updateGasLimit(uint256 gasLimit) external onlyFungible {
        GAS_LIMIT = gasLimit;
        emit UpdatedGasLimit(gasLimit);
    }

function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
        PROTOCOL_FLAT_FEE = protocolFlatFee;
        emit UpdatedProtocolFlatFee(protocolFlatFee);
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279-L291

##

## [L-11] Unsafe downcast

### Impact
When a type is downcast to a smaller type, the higher order bits are truncated, effectively applying a modulo to the original value. Without any other checks, this wrapping will lead to unexpected behavior and bugs

### POC

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

35:            uint160( // downcast to match the address type.
36                uint256( // convert to uint to truncate upper digits.

154: uint160( // downcast to match the address type.
155:                uint256( // convert to uint to truncate upper digits.

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L114-L115

##

## [L-12] Follow Check-Effect-Interaction pattern 

``Check``: Validate all conditions and states before making any state changes. This involves ensuring that the inputs are valid, the sender is authorized, and any other preconditions are met.

``Effects``: Update the state of your contract. This typically involves changing balances, updating storage variables, or in your case, burning tokens.

``Interaction``: Interact with external contracts or addresses. This is where you send funds or call functions of other contracts.

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm
/ZRC20.sol

function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
        (address gasZRC20, uint256 gasFee) = withdrawGasFee();
        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
            revert GasFeeTransferFailed();
        }
        _burn(msg.sender, amount);
        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
        return true;
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L264


##

## [L-13] Use of a single-step ownership transfer

### Impact
The existing transferOwnership function immediately transfers ownership to the new addres. Consider implementing a two-step variant, where the 'acceptor' of the ownership must call a separate function in order for the transfer to take effect. This can help to prevent mistakes where the wrong address is used, and ownership is irrecoverably lost.

### POC
```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

207: Ownable(deploymentAddress).transferOwnership(msg.sender);

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L207

## NON CRITICAL FINDINGS

##

## [NC-1] addresses shouldn't be hard-coded

It is often better to declare addresses as immutable, and assign them via constructor arguments. This allows the code to remain the same across deployments on different networks, and avoids recompilation when addresses need to change.

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm
/ZRC20.sol

22: address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22

##

## [NC-2] Add inline comments for unnamed variables

function foo(address x, address) -> function foo(address x, address /* y */)

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerTrident.strategy.sol

81: (address token0, address token1) = getPair(WETH9Address, zetaToken);

111: (address token0, address token1) = getPair(inputToken, WETH9Address);

147: (address token0, address token1) = getPair(zetaToken, WETH9Address);

178: (address token0, address token1) = getPair(zetaToken, WETH9Address);

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L81

##

## [NC-3] Array indices should be referenced via enums rather than via numeric literals

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerTrident.strategy.sol

185: path[0] = pairPools1[0];
186: path[1] = pairPools2[0];

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185-L186

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L73-L74

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L77-L79

##

## [NC-4] Assembly block creates dirty bits

Writing data to the free memory pointer without later updating the free memory pointer will cause there to be dirty bits at that memory location. Not updating the free memory pointer will make it [harder](https://docs.soliditylang.org/en/latest/ir-breaking-changes.html#cleanup) for the optimizer to reason about whether the memory needs to be cleaned, which may lead to worse optimizations. Annotate the block with assembly ("memory-safe") { ... } if the memory's value can be discarded. If the memory needs to be saved, update the free memory pointer in addtion to using the annotation. See this [link](https://docs.soliditylang.org/en/latest/assembly.html#memory-safety) for other cases where the annotation can be used.

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

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
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L53-L64

##

## [NC-5] Assembly blocks should have extensive comments

Assembly blocks take a lot more time to audit than normal Solidity code, and often have gotchas and side-effects that the Solidity versions of the same code do not. Consider adding more comments explaining what is being done in every step of the assembly code, and describe why assembly is being used instead of Solidity.


```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

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
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L53-L64

##

## [NC-6] Cast to bytes or bytes32 for clearer semantic meaning

Using a [cast](https://ethereum.stackexchange.com/questions/30912/how-to-compare-strings-in-solidity#answer-82739) on a single argument, rather than abi.encodePacked() makes the intended operation more clear, leading to less reviewer confusion.

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

10:  bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10

##

## [NC-7] Complex casting

Consider whether the number of casts is really necessary, or whether using a different type would be more appropriate. Alternatively, add comments to explain in detail why the casts are necessary, and any implicit reasons why the cast does not introduce an overflow.


```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ImmutableCreate2Factory.sol

34: // determine the target address for contract deployment.
        address targetDeploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );

113: deploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L33-L47

##

## [NC-8] Consider adding a block/deny-list

Doing so will significantly increase centralization, but will help to prevent hackers from using stolen tokens

```solidity
FILE: Breadcrumbs2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20

## 

##[NC-9] Consider adding emergency-stop functionality

Adding a way to quickly halt protocol functionality in an emergency, rather than having to pause individual contracts one-by-one, will make in-progress hack mitigation faster and much less stressful.

##

## [NC-10] Consider disallowing transfers to address(this)

```solidity
FILE : 2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools
/ZetaTokenConsumerPancakeV3.strategy.sol

135: IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

159: IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

193: IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135

##

## [NC-11] Consider moving msg.sender checks to a common authorization modifier

```solidity
FILE: 2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol

53: if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
69: if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
226: if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();


```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53













