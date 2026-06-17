|no |issue|number of issue|
|------|-----|---------------|
|[G-01]|Using the ‘onlyTssUpdater’ modifier can save gas fees|1|

## [G01]Using the ‘onlyTssUpdater’ modifier can save gas fees

```solidity
109    modifier onlyTssUpdater() {
110        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
111        _;
112    }
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L109-L112

128    function updateTssAddress(address tssAddress_) external {
129        if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128-L129
```