# [L-01]: Redundant State changes.

##### Context. 
1. [ERC20Custody.sol#L144-L147](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144-L147) 

```Solidity
function whitelist(IERC20 asset) external onlyTSS {
    whitelisted[asset] = true;
    emit Whitelisted(asset);
}
```
`whitelist()` function does not check that the asset in question isn’t already whitelisted.

2. [ERC20Custody.sol#L153-L156](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153-L156) 

```Solidity
function unwhitelist(IERC20 asset) external onlyTSS {
    whitelisted[asset] = false;
    emit Unwhitelisted(asset);
}
```
`unwhitelist()` function does not check whether the asset in question isn't already unwhitelisted.

## Description
This would result to unnecessary Redundant State changes that might lead to  confusion as the state of the contract does not accurately represent the intended logic.

## Recommendation
> Any function that is involved in the changing of state in a contract should first ensure that the change for which it is designed to effect isn't already satisfied to to avoid redundant state changes

# [L-02]: Use a two-step transfer function for updating the `TSSAddress` privilege in the `ERC20Custody` contract. 

## Description 
The `ERC20Custody` has a very important `TSSAddress` privilege which can be updated via a `updateTSSAddress()` function.
In order to prevent the role from mistakenly being transferred to an address that cannot handle it (e.g. due to a typo in the address), require that the recipient of the new `TSSAddress` privilege actively accepts via a `contract call` of its own.

```Solidity
function updateTSSAddress (address TSSAddress_) external onlyTSSUpdater {

if (TSSAddress_ == address(0)) {

revert ZeroAddress();

}

TSSAddress = TSSAddress_

emit UpdatedTSSAddress (TSSAddress_);

}
```

# [NC-01]: Failed event firing due to omission of `emit` keyword. 

Example: [deposit() function](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/WZETA.sol#L20-L23)
```Solidity
function deposit() public payable {
    balanceOf[msg.sender] += msg.value;
    Deposit(msg.sender, msg.value);
}
```

## Description
If the `emit` keyword is omitted, the events will not actually be emitted and this means that the listeners will not receive it and this will break integrations that rely on events.

##### Context.
- [WZETA.sol#L25-L30](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25-L30) 
- [WZETA.sol#L36-L39](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L39) 

## Recommendation
> Use the `emit` keyword to fire the events. 

```Solidity
function deposit() public payable {
    balanceOf[msg.sender] += msg.value;
    emit Deposit(msg.sender, msg.value);
}
```

# [NC-02]: Inaccurate use of `virtual` and `override` specifiers. 
## Impact
Using `virtual` and `override` specifiers   in the same function  is invalid syntax and will result in compiler error. 
Example:
```Solidity
function name() public view virtual override returns (string memory) {
    return _name;
}
```

##### Context.
- [ZRC20.sol#L91-L93](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91-L93) 
- [ZRC20.sol#L99-L101](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99-L101) 
- [ZRC20.sol#L107-L109](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107-L109) 

## Recommendation
> Use `virtual` keyword when declaring a function in a base contract to indicate that it may be overridden by derived contracts.
>Use the `override` keyword when implementing a function in a derived contract that is intended to override a virtual function in the base contract.

# [NC-03]: Older Version Pragma

##### Context. 
```Solidity
pragma solidity ^0.4.18; 
```

##### Description
Using very old versions of Solidity prevents benefits of bug fixes and newer security checks. Using the latest versions might make contracts susceptible to undiscovered compiler bugs.

## Recommendation
> Consider using the most recent version.

# [NC-04]: Missing or Incomplete NatSpec

##### Context
[All Contracts]() 

## Description
Some functions are missing @notice/@dev NatSpec comments for the function, @param for all/some of their parameters and @return for return values. Given that NatSpec is an important part of code documentation, this affects code comprehension, auditability and usability.

## Recommendation
> Consider adding in full NatSpec comments for all functions to have complete code documentation for future use.

# [NC-05]: Missing Visibility

##### Context


## Description
It’s best practice to explicitly mark visibility of state variables.

## Recommendation
> Consider adding the missing visibility to the state variables.