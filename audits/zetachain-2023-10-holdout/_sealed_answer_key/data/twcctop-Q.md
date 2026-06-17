## L-1  ERC20Custody  `withdraw` , comparing to `depoit`,don't have similar logic to process fee-on-transfer token.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193-L199
 
In function deposit, there is logic to compete with fee-on-transfer token, but in `withdraw`, there is no related logic. 



## L-2 `totoalSupply()` possible return higher value.
 
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L32-L34

In `WZEZA.sol`,  `totoalSupply()` is designed to return the current supply `wzeta`, every time user `deposit` or transfer native token will trigger the `deposit`  logic. The issue is self-destruct contract can force send eth to `WZETA`,  and bypass the `function() public payable `  logic.
The result is , `totoalSupply()` may return a higher value than actually supply.