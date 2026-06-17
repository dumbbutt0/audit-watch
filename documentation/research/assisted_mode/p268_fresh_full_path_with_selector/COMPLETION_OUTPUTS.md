# P268 — COMPLETION_OUTPUTS (Phase 7)

Five-op completion (STS/AAS/TSE/IDC/CCIT) on the mechanisms the P267 selector **preserved** (KEEP_BOTH carries BOTH
M1 and M2 on C1 and C2; REFUTE_FIRST on C-neg). Pre-reveal; source-grounded.

## C2-M1 — first-depositor share-inflation (selector-preserved high-impact)
- **STS:** attacker `deposit(1 wei)` → 1 share (totalSupply 1, assets 1); donate `D` assets (totalAssets=balanceOf);
  victim `deposit(V)` → `convertToShares(V)=floor(V·(supply+1)/(assets+1))=floor(V·2/(D+2))=0` when `D≳2V`.
- **AAS:** attacker is a fresh EOA, no privilege; `deposit` is permissionless.
- **TSE:** victim's `V` assets are now in the pool backing the attacker's 1 share (+ the +1 virtual share); victim
  holds 0 shares → cannot recover anything. Terminal: victim loss.
- **IDC:** invariant "a depositor receives shares proportional to assets" violated — victim Δassets = 5000e18,
  Δshares = 0.
- **CCIT:** attacker/victim distinct EOAs; the attacker's seed share captures the victim's deposit value.
- **Status: COMPLETED_CHAIN** (victim loss). Attacker-profit is **PARTIAL** — solady's +1 virtual share (offset 0,
  not overridden by Karak) absorbs ~half, so it is a victim-loss/griefing with capped attacker profit rather than a
  clean drain. The **loss to the victim is unconditional**; the root cause is the missing `_decimalsOffset` override.

## C1-M1 — permissionless finishRedeem + finish-time spot conversion (selector-preserved)
- **STS/AAS/TSE:** quiet-path `deposit → startRedeem → (delay) → finishRedeem` returns ~deposit; `finishRedeem` is
  permissionless but pays the fixed `beneficiary` (the finisher gains nothing). Slashing during the queue reduces a
  queued withdrawer's payout — but the NatSpec states this is **intended** ("DSS shouldn't consider stakes queued in
  withdrawals … to prevent front-running a slashing").
- **Status: NO_CHAIN / by-design** — no standalone loss beyond the intended queued-withdrawal-bears-slashing.
  (The selector preserving it was still correct: by-design is only knowable after completion; the falsifier resolved
  it.)

## C1-M2 — startRedeem self-approval (the easy rival)
- Confirmed: `startRedeem` reverts without `allowance[staker][vault]` (the `this.transferFrom` self-approval). **Status:
  NO_CHAIN** — a UX/griefing revert, low impact. This is exactly the easy mechanism the raw pre-P267 path would have
  PoC'd instead of C2-M1.

## C-neg — SlasherLib.requestSlashing
- Core/operator-gated → no permissionless path. **Status: REFUTED / benign** (selector said REFUTE_M1_FIRST).

## Summary
| mechanism | selector | completion |
|---|---|---|
| C2-M1 inflation | KEEP_BOTH (preserved) | **COMPLETED_CHAIN** (victim loss; profit PARTIAL) |
| C1-M1 finishRedeem | KEEP_BOTH (preserved) | NO_CHAIN / by-design |
| C1-M2 approval-revert | KEEP_BOTH (rival) | NO_CHAIN (UX/griefing) |
| C-neg slashing | REFUTE_FIRST | REFUTED / benign |
Frozen before PoC code.
