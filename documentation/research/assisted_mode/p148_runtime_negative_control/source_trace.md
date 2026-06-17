# P148 — Source Trace

File: `audits/velodrome-2022-05-bench/contracts/contracts/RewardsDistributor.sol` (solc 0.8.13).

## claim (282-292)
```solidity
function claim(uint _tokenId) external returns (uint) {
    if (block.timestamp >= time_cursor) _checkpoint_total_supply();
    uint _last_token_time = last_token_time / WEEK * WEEK;
    uint amount = _claim(_tokenId, voting_escrow, _last_token_time);
    if (amount != 0) {
        IVotingEscrow(voting_escrow).deposit_for(_tokenId, amount);   // <-- only routing action
        token_last_balance -= amount;
    }
    return amount;
}
```

## claim_many (294-313)
```solidity
for (uint i = 0; i < _tokenIds.length; i++) {
    uint _tokenId = _tokenIds[i];
    if (_tokenId == 0) break;
    uint amount = _claim(_tokenId, _voting_escrow, _last_token_time);
    if (amount != 0) {
        IVotingEscrow(_voting_escrow).deposit_for(_tokenId, amount);  // <-- SAME only routing action
        total += amount;
    }
}
```

## Comparison vs blackhole (where B5 lives)
| | velodrome (this) | blackhole (B5) |
|---|---|---|
| post-`_claim` action | `deposit_for(_tokenId, amount)` only | `if (locked expired && !permanent) { _nftOwner = ownerOf; [claim: + AVM correction] transfer(_nftOwner) } else deposit_for` |
| `ownerOf` recipient resolution | **absent** | present |
| AVM `getOriginalOwner` correction | **absent** | present in `claim`, **omitted** in `claim_many` (= B5) |
| recipient divergence possible? | **no** (both deposit_for same `_tokenId`) | yes (claim_many → ownerOf/AVM manager) |

## Conclusion
velodrome has **no recipient-resolution branch at all** — both siblings credit the claimed `_tokenId` via
`deposit_for`. The B5 divergence is architecturally absent ⇒ the suspicion is **refuted** at the source level, and
the runtime PoC confirms it (both `deposit_for` the same subject; no external-recipient transfer).

## Driving a nonzero `_claim` (for a faithful runtime check)
`_claim` (169-224) uses bias/slope point math + `ve_supply[]` (seeded by `_checkpoint_total_supply`, 142-163) +
`tokens_per_week[]` (seeded by `checkpoint_token`, 64-100). A flat point (`slope 0`, `bias` constant) makes
`balance_of` constant; `claim` auto-calls `_checkpoint_total_supply` (line 283). Setting `USER_BIAS < SUPPLY_BIAS`
yields a fractional per-claim payout so two claims don't underflow `token_last_balance`.
