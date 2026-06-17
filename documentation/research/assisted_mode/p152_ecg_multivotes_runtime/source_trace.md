# P152 — Source Trace

File: `audits/ecg-2023-12-holdout/contracts/src/tokens/ERC20MultiVotes.sol` (solc 0.8.13; `abstract … is
ERC20Permit`).

## The accounting invariant
```solidity
function freeVotes(address account) public view returns (uint256) {
    return balanceOf(account) - userDelegatedVotes[account];      // :71-72
}
function getVotes(address account) public view returns (uint256) {  // delegatee's checkpointed votes :80-83
    ...
}
```

## The guarded transfer (the reason the suspicion refutes)
```solidity
function transfer(address to, uint256 amount) public override returns (bool) {   // :408
    _decrementVotesUntilFree(msg.sender, amount);                                // :412
    return super.transfer(to, amount);                                           // :413
}
function transferFrom(address from, address to, uint256 amount) public override returns (bool) {  // :416
    _decrementVotesUntilFree(from, amount);                                      // :421
    return super.transferFrom(from, to, amount);                                 // :422
}
function _decrementVotesUntilFree(address user, uint256 votes) internal {        // :427
    uint256 userFreeVotes = freeVotes(user);
    if (userFreeVotes >= votes) return;                                          // :431
    ... greedily free whole delegates until (userFreeVotes + totalFreed) >= votes // :441-458
        _writeCheckpoint(delegatee, _subtract, delegateVotes);                   // :455 (delegatee getVotes drops)
    userDelegatedVotes[user] -= totalFreed;                                      // :460
}
```

## Why the suspicion refutes (invariant proof)
On a transfer of `amount`, the post-transfer balance is `balance - amount`. The contract frees `totalFreed` such
that `userFreeVotes + totalFreed >= amount`, i.e. `totalFreed >= amount - freeVotes = amount - (balance -
userDelegatedVotes)`. Hence `userDelegatedVotes_after = userDelegatedVotes - totalFreed <= balance - amount =
balance_after`. So delegated votes can never exceed the post-transfer balance ⇒ **no retention/inflation**; the
delegatee's `getVotes` is decremented (`_writeCheckpoint _subtract`). The canonical "retain votes after transfer"
attack is structurally prevented.

## Reachability
`delegate`/`incrementDelegation`/`transfer` are all public & unprivileged (any holder). `_setMaxDelegates` is
internal (parent adds a public setter; here only to enable delegation in the test). So the surface is
unprivileged — and the runtime shows the mechanism is **absent** there.
