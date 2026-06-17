# P145 — Source Trace

File: `audits/blackhole-2025-05-eval/contracts/2025-05-blackhole/contracts/RewardsDistributor.sol` (solc 0.8.13).

## `claim` — has the AVM correction (197-217)
```solidity
uint amount = _claim(_tokenId, voting_escrow, _last_token_time);
if (amount != 0) {
    IVotingEscrow.LockedBalance memory _locked = IVotingEscrow(voting_escrow).locked(_tokenId);
    if (_locked.end < block.timestamp && !_locked.isPermanent) {
        address _nftOwner = IVotingEscrow(voting_escrow).ownerOf(_tokenId);
        if (address(avm) != address(0) && avm.tokenIdToAVMId(_tokenId) != 0) {
            _nftOwner = avm.getOriginalOwner(_tokenId);          // <-- AVM correction (207-208)
        }
        IERC20(token).transfer(_nftOwner, amount);
    } else { IVotingEscrow(voting_escrow).deposit_for(_tokenId, amount); }
    token_last_balance -= amount;
}
```

## `claim_many` — OMITS the AVM correction (219-246)
```solidity
uint amount = _claim(_tokenId, _voting_escrow, _last_token_time);
if (amount != 0) {
    IVotingEscrow.LockedBalance memory _locked = IVotingEscrow(_voting_escrow).locked(_tokenId);
    if (_locked.end < block.timestamp && !_locked.isPermanent) {
        address _nftOwner = IVotingEscrow(_voting_escrow).ownerOf(_tokenId);   // <-- ownerOf only (233)
        IERC20(token).transfer(_nftOwner, amount);                            // no getOriginalOwner (234)
    } else { IVotingEscrow(_voting_escrow).deposit_for(_tokenId, amount); }
    total += amount;
}
```

## Divergence
For an **AVM-managed** tokenId (`avm.tokenIdToAVMId(id) != 0`), `ownerOf(id)` is the AVM manager and the entitled
party is `avm.getOriginalOwner(id)`. `claim` resolves to the original owner; `claim_many` resolves to the AVM
manager. Trigger conditions (both functions share them): nonzero `_claim` amount **and** an **expired**,
**non-permanent** lock (`_locked.end < block.timestamp && !_locked.isPermanent`) — the direct-transfer branch.
Non-AVM tokenIds are unaffected (`ownerOf == original owner`).

## Reaching it in a test
- `_claim` amount is driven nonzero by funding the distributor with the reward `token` then `checkpoint_token()`
  after a ≥1-WEEK warp (WEEK=1800), with a mock VE returning `user_point_epoch=1`,
  `user_point_history(.,1).ts=start`, `balanceOfNFTAt=S`, `totalSupplyAtT=SUP` (S<SUP → fractional, no
  double-spend).
- `locked` returns an expired non-permanent lock → the transfer branch.
- `ownerOf(avmId)` = AVM manager; `avm.tokenIdToAVMId/​getOriginalOwner` mark it AVM-managed → user.
- `claim` is consumed via the public entrypoint (real corrected behavior); `claim_many` via the public batch
  entrypoint (the vulnerable behavior).
