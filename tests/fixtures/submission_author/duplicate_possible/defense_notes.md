### Defense: minimum-claim threshold
Blocks: no
Why it fails: claim() has no minimum-claim threshold; the truncating division
runs unconditionally (contracts/StakingRewards.sol:128).

### Defense: reward index checkpointing
Blocks: no
Why it fails: the index is updated after the truncating division, so it cannot
recover the dropped remainder.
