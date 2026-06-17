# P286 — POC_EVIDENCE_AUDIT

Honest audit of the claim_many PoC: faithful to source? AVM branch the only difference? entry permissionless? any
fabricated pass / over-claim? L3 outcome real?

## Faithful to source?
Yes. The repro's `claim` / `claim_many` are the **verbatim recipient control-flow** of RewardsDistributor.sol lines
197–246: same `if (_locked.end < block.timestamp && !_locked.isPermanent)` direct-transfer branch, same
`ve.ownerOf(tokenId)`, same AVM-correction guard `if (address(avm)!=0 && avm.tokenIdToAVMId(tokenId)!=0)` in `claim`,
and the same OMISSION of that guard in `claim_many`. Only the reward computation `_claim(...)` is mocked to a fixed
amount — Tier-C reproduces the RECIPIENT logic, not the reward math, which is the locus of the bug.

## Is the AVM branch the only difference?
Yes, and the control test proves it: `test_control_non_avm_token_routes_same` uses a non-AVM tokenId
(`tokenIdToAVMId==0`) where `ownerOf == originalOwner`; there `claim` and `claim_many` pay the SAME recipient. The
divergence appears ONLY when the AVM correction would change the recipient — i.e. exactly the omitted `getOriginalOwner`.

## Permissionless entry (L1)?
Yes. All three tests call via `vm.prank(attacker)` from an unprivileged EOA with no setup; `claim_many` has no caller
guard (confirmed by P285: its only auth-ish token `ownerOf` is a RECIPIENT_READ, not an execution gate).

## State-flip named (L2)?
Yes. Before/after `balanceOf` of BOTH `avmHolder` and `originalOwner` are asserted; the reward moves to the wrong
recipient under `claim_many` and the right one under `claim`.

## Fabricated pass / over-claim?
None. The bug test asserts the MISROUTE (reward to `ownerOf`, original owner denied) — it does not assert a contrived
condition. The reference and control tests bound the claim (claim is correct; non-AVM is unaffected). Tier-C is
explicitly labelled; the result is a faithful-reproduction proof of the recipient divergence, not a live-chain exploit.

## L3 outcome real?
Yes — within the documented M-04 scope: for AVM-managed locks (the AVM holds the NFT while the original locker is a
different address), `claim_many` sends accrued rewards to the AVM/current holder, permanently denying the original owner.
This is a fund-misdirection / reward-loss outcome, permissionlessly triggerable.

## Verdict on the audit
Faithful, permissionless, named state-flip, controlled, no fabrication. The claim_many READY converts to a
PoC-supported finding. Consistent with verdict **A**.
