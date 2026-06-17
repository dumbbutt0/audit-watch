# hybra — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)
3 subtle loci (BASE_BORN_INCOMPLETE; multi-family; not mechanical/access-control). claimMany excluded.

## H-L1 `VotingEscrow.multiSplit`
- why: ve value-conservation across split is core ve(3,3) accounting; high subtle risk.
- base/checkpoint signal: accounting A3/A4 + ST on multiSplit.
- what base knew: proportional split + burn original + permanent flag carried.
- what remained incomplete: permanentLockBalance desync / rounding-dust supply shrink / voting-power inflation.
- why subtle: value-conservation + permanent-balance global invariant (not a typo/access-control).

## H-L2 `VotingEscrow.merge`
- why: permanent-lock global accounting on merge.
- signal: accounting + ST on merge.
- what base knew: permanentLockBalance conditional add; end=max.
- what remained incomplete: permanent/non-permanent edge mis-accounts global balance or voting power.
- why subtle: global invariant accounting.

## H-L3 `GaugeManager._distribute`
- why: reward distribution across gauges/periods.
- signal: accounting A + ST.
- what base knew: distribute + updateForAfterDistribution.
- what remained incomplete: cross-period reward drift / double-distribution.
- why subtle: reward-index accounting.

**FREEZE.**
