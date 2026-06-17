## Impact
Checks and event do not match

## Proof of Concept
The function 'deposit(address to, uint256 amount) external override returns (bool)' on the following link:
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225

- This functions accepts interaction from 2 addresses: FUNGIBLE_MODULE_ADDRESS and SYSTEM_CONTRACT_ADDRESS, but the event is only being emitted on the FUNGIBLE_MODULE_ADDRESS address

## Tools Used

Manual verification

## Recommended Mitigation Steps

Updates the event 'emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);' for the following code 'emit Deposit(abi.encodePacked(msg.sender), to, amount);'