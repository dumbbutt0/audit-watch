# Use of bool in modifier nonReentrant is gas expensive

## Summary
Use of bool variable in nonReentrant modifier adds 22,100+ gas to each function that uses the modifier

## Details
The following modifier is defined in [ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65), [ZetaTokenConsumerPancakeV3.strategy.sol
](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94) and [ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59):

    bool internal _locked;
    modifier nonReentrant() {
        if (_locked) revert ReentrancyError();
        _locked = true;
        _;
        _locked = false;
    }

Each time this modifier is called, `_locked` sets the storage slot from zero to non-zero (i.e. from false to true). Setting storage slot from zero to non-zero consumes 22,100 gas while setting slot from non-zero to non-zero takes only 5000 gas. As a result, all the functions that use this modifier are atleast 22,100 more gas expensive.

## Recommendation
Change type from `bool` to `uint256` for `_locked` and use a non-zero initial value of `_locked` to for it. Inside modifier, change its value to another non-zero integer.

    uint256 internal _locked = 1;
    modifier nonReentrant() {
        if (_locked != 1) revert ReentrancyError();
        _locked = 2;
        _;
        _locked = 1;
    }