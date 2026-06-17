- Function `updateZetaFee()` should be behind timelock to avoid centralization control.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L92-L101

- In `renounceTssAddressUpdater`, the logic never reaches this condition:

`if (tssAddress == address(0)) revert InvalidAddress();`

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L108

- The `transferFrom` allows self transfer (src == dst) which emits unnecessary Transfer event which could results unwanted behaviour specially for bots.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46C1-L60C6

- No param from this constructor is checked for address(0) unlike other places:

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74

- Recipient param is never used in logical flow, instead `msg.sender` is used in transfer and same `msg.sender` is not emitted in event, but recipient is.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165C1-L185C6