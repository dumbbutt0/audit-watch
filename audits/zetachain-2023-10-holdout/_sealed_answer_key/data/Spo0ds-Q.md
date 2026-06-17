Title: Potential Token Lock on Withdraw due to Inconsistent Whitelisting

Severity: Low/Not-Critical

Category: Logic

File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193

Function: withdraw

Description:

The withdraw function in the ERC20Custody contract performs a potentially unexpected token lock if the token is whitelisted during deposit but not during withdrawal. This inconsistency might result in users being unable to withdraw their deposited assets unless the token is later whitelisted for withdrawal.