## L-01:  Zero withdraw amounts should be reverted cause withdraw charges gas amount to user . 

`withdraw` function  Withraws ZRC20 tokens to external chains,  causes cctx module to send out outbound tx to the outbound chain. 
`withdraw ` functionality in ZRC20.sol charges calculated gas Fee to the user and burns the token amount . If an user mistakenly inputs zero as amount it still charges gas fee from the user . Which should not be the case . 
 

```solidity 
function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
        (address gasZRC20, uint256 gasFee) = withdrawGasFee();
        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
            revert GasFeeTransferFailed();
        }
        _burn(msg.sender, amount);//@ci low zero amounts needs to be restricted here . 
        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
        return true;
    }
```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256

#### Recommendation : 
Zero withdraw amounts should be reverted . 
```diff
 function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
+       require(amount > 0 , "Amount should be larger than zero ");
        (address gasZRC20, uint256 gasFee) = withdrawGasFee();

        //...
    }
```

## L-02 : `transferFrom` not  following CEI 
the  `transferFrom` function in ZRC20.sol doesnot follow CEI pattern . It is standard to follow CEI when there is a fund transfer to prevent unwanted scenarios like re-entrancy , erc777 re-entrancy etc.  


```solidity 
 function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
        _transfer(sender, recipient, amount);//@ci low not following CEI ..! 

        uint256 currentAllowance = _allowances[sender][_msgSender()];
        if (currentAllowance < amount) revert LowAllowance();

        _approve(sender, _msgSender(), currentAllowance - amount);

        return true;
    }

```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157

#### Recommendation : 
rewrite the function as follows to follow CEI : 
```diff
  function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
-       _transfer(sender, recipient, amount);//@ci low not following CEI ..! 

        uint256 currentAllowance = _allowances[sender][_msgSender()];
        if (currentAllowance < amount) revert LowAllowance();

        _approve(sender, _msgSender(), currentAllowance - amount);
+       _transfer(sender, recipient, amount);
        return true;
    }
```

## L-03: WZETA#approve is vulnerable to approval frontrunning 
Exploit scenario : 
1. Alice gives allowance of 100 tokens to Bob.
2. Later, Alice rethinks her choice, changing it to 50. When this happens, Bob watches the chain, transfers his 100 tokens immediately with a higher gas price.
3. As a result, Bob gains 150 tokens overall instead of 50.

```solidity 
  function approve(address guy, uint wad) public returns (bool) {
        allowance[msg.sender][guy] = wad; //@ci low vulnerable to approval frontrunning.  
        Approval(msg.sender, guy, wad);
        return true;
    }
```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36

#### Recommendation : 
Mitigating approval frontrunning is not easy . Its up to the developers . 
But here's a [proposal](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt) to a probable solution . 



## L-04: `ZetaFee <= ZetaMaxFee` check is missing . 
`ZetaFee ` should always be less than `ZetaMaxFee` . But this check is not imposed inside the constructor .In this scenario , Logically  Wrong inputs can be provided and executed without issue . This should be considered . 

```solidity 
  constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        ...
        zetaFee = zetaFee_; //@ci low zetaFee < zetaMaxFee is not checked ! 
        zetaMaxFee = zetaMaxFee_; 
    }

```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68

#### Recommendation : 
Implement this check inside the constructor :
`require(ZetaFee <= ZetaMaxFee, "Fee cannot exceed Max Fee!")`



## NC-01: Unnecessary line of code :
The function is only callable by the `TSSAddress ` . It is only possible to call the function by `TSSAddress ` if `TSSAddress != address(0))`  . So the `TSSAddress == address(0)` check is not necessary . 

```solidity 

   function pause() external onlyTSS {
        if (paused) {
            revert IsPaused();
        }
        if (TSSAddress == address(0)) { //@ci low unnnecessary line of code . theres a modifier !! 
            revert ZeroAddress();
        }
        paused = true;
        emit Paused(msg.sender);
    }
```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118

#### Recommendation : 
Remove the unnecessary check and revert . 


## NC-02: Follow the best practices  
Name it recieve() function to follow the best practices to make code more consistent, readable, and understandable for developers and others.  Also to avoid common errors and bugs that result from poor coding practices. 
```solidity 

function() public payable {
        deposit();
    }
```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L16

#### Recommendation : 
Name as `receive()` function . 
```diff
recieve() public payable {
        deposit();
    }
```


## NC-03: No error msg in `WZETA::withdraw` 
Withdraw function in WZETA.sol does not throw any error message while reverting . The below require statement should throw an error message explaining the  reason of error . 
```solidity 
 function withdraw(uint wad) public {
        require(balanceOf[msg.sender] >= wad);//@ci low doesnot throw any error message !
        balanceOf[msg.sender] -= wad;
        msg.sender.transfer(wad);
        Withdrawal(msg.sender, wad);
    }

```

code link : https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25

#### Recommendation : 
Add error msg to the code as follows : 
```diff
 function withdraw(uint wad) public {
-       require(balanceOf[msg.sender] >= wad);
+       require(balanceOf[msg.sender] >= wad , " Withdraw Amount can't be larger than balance" );
        balanceOf[msg.sender] -= wad;
        msg.sender.transfer(wad);
        Withdrawal(msg.sender, wad);
    }
```



