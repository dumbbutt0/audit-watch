# P149 — Source Intent Review (local source only; cited)

Files under `audits/centrifuge-2023-09-holdout/contracts/src/`.

## 1. Only the owner can initiate a withdrawal/redemption
`LiquidityPool.sol`:
```solidity
modifier withApproval(address owner) {                       // :97
    require(msg.sender == owner, "LiquidityPool/no-approval"); // :98
    _;
}
function withdraw(uint256 assets, address receiver, address owner) public withApproval(owner) ...  // :176-178
function redeem(uint256 shares, address receiver, address owner) public withApproval(owner) ...    // :200-202
```
`withApproval` = `msg.sender == owner` (no operator / no share-allowance delegation in this 2023-09 version). So a
caller can only withdraw/redeem **their own** position; an external actor cannot act on a victim's `owner`.

## 2. The owner chooses `receiver`; the value path
`LiquidityPool.withdraw/redeem` → `InvestmentManager.processWithdraw/processRedeem` (`auth`, caller = the pool) →
`_redeem(...)`:
```solidity
userEscrow.transferOut(lPool.asset(), user, receiver, currencyAmount);   // InvestmentManager.sol:545
```
`user` = the `owner`; `receiver` = the ERC4626 recipient the owner passed to `withdraw/redeem`. The escrow-in side:
```solidity
userEscrow.transferIn(_currency, address(escrow), recipient, currencyPayout);  // InvestmentManager.sol:272
```
escrows the payout for `recipient` (the owner).

## 3. `transferOut` is ward-only; the allowance check is documented defense-in-depth
`UserEscrow.sol`:
```solidity
function transferOut(address token, address destination, address receiver, uint256 amount) external auth {  // :36
    require(destinations[token][destination] >= amount, "UserEscrow/transfer-failed");
    require(
        /// transferOut can only be initiated by the destination address or an authorized admin.   // :39
        /// The check is just an additional protection to secure destination funds in case of compromized auth.  // :40
        /// Since userEscrow is not able to decrease the allowance for the receiver,                // :41
        /// a transfer is only possible in case receiver has received the full allowance from destination.  // :42
        receiver == destination || (ERC20Like(token).allowance(destination, receiver) == type(uint256).max),  // :43
        "UserEscrow/receiver-has-no-allowance"
    );
    destinations[token][destination] -= amount;
    SafeTransferLib.safeTransfer(token, receiver, amount);
}
```

## Intent classification (method step 3)
The NatSpec frames the allowance as **(a)** — "additional protection … in case of compromized auth" — i.e., a
secondary guard, with the **primary** authorization being `withApproval(owner)` at the LiquidityPool layer + the
`auth` (ward-only) gate on `transferOut`. The `receiver` is the **intended economic recipient** chosen by the
owner (ERC4626 `withdraw(assets, receiver, owner)`). So under intended operation the owner is directing **their
own** escrowed funds to a receiver **they** chose — not a third party redirecting a victim's escrow.

## Allowance consumption (method step 4)
The contract **never reduces** the allowance (NatSpec :41: "userEscrow is not able to decrease the allowance"), so
an infinite allowance is, by design, left unconsumed — confirming the `== type(uint256).max` check is a deliberate
*proxy*, not a spend. This is precisely why it is a **weak** proxy under compromised auth (unrelated infinite
approvals satisfy it, repeatably).

## Roles elsewhere (method step 5)
`destinations[token][destination]` is per-destination escrow accounting (`UserEscrow.sol:17`); `transferIn` credits
a `destination`, `transferOut` debits that `destination` and pays a `receiver`. `destination` is the economic owner
of the escrow; `receiver` is the withdrawal target the owner selects. They are distinct **by ERC4626 design**, not
by an internal delegation role.

## Tests/docs/scripts (method step 6)
No local tests, deployment scripts, or protocol docs for `transferOut` exist in the holdout clone (contracts-only).
No external docs were consulted.
