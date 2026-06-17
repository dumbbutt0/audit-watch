# P286 — SETUP

**Phase:** P286 — READY-Set PoC Sweep (narrow; not a repair, not blind; production authority WITHHELD).
**Status:** RESEARCH-ONLY · ADVISORY · default-off.

## What this phase is
P285 carried the awarded Blackhole **M-04** bug (`RewardsDistributor.claim_many`) to READY_FOR_POC_INTENT. P286 answers
the next question: **does READY convert into a PoC-supported finding?** It builds a runnable PoC for the `claim_many`
recipient divergence and re-confirms the L2Governor.execute regression. No new candidates, no tuning, no repair.

## The bug (verbatim source — RewardsDistributor.sol)
- `claim(tokenId)` applies the AVM correction: `if (avm!=0 && avm.tokenIdToAVMId(tokenId)!=0) _nftOwner =
  avm.getOriginalOwner(tokenId);` before `token.transfer(_nftOwner, amount)`.
- `claim_many([tokenId])` omits it: `_nftOwner = ve.ownerOf(tokenId); token.transfer(_nftOwner, amount)`.
For an AVM-managed lock (NFT held by the AVM, original owner is someone else) the two pay different recipients →
`claim_many` strands the reward at `ownerOf`; the original owner is denied.

## Components
- `pocs/p286/` — foundry project (solc 0.8.21, forge-std reused from `pocs/p281`).
- `pocs/p286/test/P286_ClaimManyRecipient.t.sol` — Tier-C faithful reproduction (verbatim recipient control-flow +
  MockERC20/MockVotingEscrow/MockAVM), 3 tests (claim reference · claim_many misroute (the bug) · non-AVM control).
- `pocs/p281` — L2Governor regression (re-run only).

## Reproduce
`cd pocs/p286 && forge test -vv` (3 passed); `cd pocs/p281 && forge test --match-path test/P281_GovernorStateMachine.t.sol`
(2 passed). Results: `outputs/{poc_results.json, p286_run_output.txt, l2governor_regression_log.txt}`.

## Standing constraints (in force)
Research-only; no production authority / submission / final severity. **No contest source edits** — Tier-C reproduces
the verbatim control-flow into a new repro contract under `pocs/`, never editing `audits/blackhole-…/contracts`. Active
audit `size-credit-2024-06-blind` symlink unchanged. Frozen P260–P273 + P283/P284/P285 modules + reused detector platform
+ forbidden 5 byte-identical.
