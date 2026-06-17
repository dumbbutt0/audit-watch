### Defense: minimum-claim threshold
Blocks: no
Why it fails: claim() enforces no minimum-claim threshold, so the truncating
division runs unconditionally (contracts/StakingRewards.sol:128).

### Defense: reward index checkpointing
Blocks: no
Why it fails: the reward index is updated after the truncating division, so
checkpointing does not recover the dropped remainder.
