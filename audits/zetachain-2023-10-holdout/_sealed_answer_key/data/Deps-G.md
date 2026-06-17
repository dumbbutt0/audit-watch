## Impact
Double external contract calls

## Proof of Concept
The function 'd withdrawGasFee() public view override returns (address, uint256)' on the following link:
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236

- This functions interacts with the same address 2 times: 
' address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID); '
' uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID); '

The functions on the ISYSTEM contract could be efficient is a way that a single call returns both address gasZRC20 and uint256 gasPrice

## Tools Used

Manual verification
