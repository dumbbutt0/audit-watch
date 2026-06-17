# payable is not required for FUNGIBLE_MODULE_ADDRESS

Line: https://github.com/code-423n4/2023-11-zetachain/blob/ec0e6141406ac99b7ccd3cc793d1428b7c19a59e/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63

    address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);

FUNGIBLE_MODULE_ADDRESS does not need to have `payable` to receive ZETA through `.call` method.

### Recommendation
```
address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB
```