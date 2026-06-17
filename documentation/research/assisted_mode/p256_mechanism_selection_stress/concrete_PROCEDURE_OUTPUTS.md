# concrete — Phase 3: Five-operation completion on SELECTED + RUNNER-UP (PRE-REVEAL, FROZEN)

Ops unchanged; labels + chain status.

## C-L1 — SELECTED M1 (finalization-direction inversion → claim unfinalized)
- STS PASS (requestId > lastFinalizedRequestId passes the guard). AAS PASS (requester controls their own requestId; claims before finalize). TSE CANDIDATE_STRENGTHENED (funds released for an unbacked/unfinalized request → terminal loss). IDC PASS (vault pays out assets not yet finalized). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN** (depends on whether the vault gates the caller; flagged in falsifier). Runner-up M2 (off-by-one strand): STS PASS / TSE PARTIAL → PARTIAL_CHAIN (griefing/strand).

## C-L2 — SELECTED M1 (protocol fee on totalAssets via share-mint dilution)
- STS PASS (every deposit/withdraw triggers takeFees → time-based fee minted). AAS NO_EFFECT (affects all depositors). TSE PARTIAL. IDC CANDIDATE_STRENGTHENED (continuous dilution delta vs depositors, independent of gains). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN.** Runner-up M2 (HWM pre-mint timing): IDC PARTIAL → PARTIAL_CHAIN.

## C-L3 — SELECTED M1 (diff-vs-amount_ basis mismatch → over-withdraw when float>0)
- STS PASS (else-branch: amount_>float; withdraws amount_*allocation from strategies while float stays). AAS PARTIAL. TSE PARTIAL (leftover float / over-withdrawal). IDC CANDIDATE_STRENGTHENED (receiver gets ~amount_ from strategies + float unspent ⇒ accounting drift). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN.** Runner-up M2 (Ceil dust): IDC PARTIAL → PARTIAL_CHAIN.

## Summary (frozen)
| locus | selected | runner-up | selected chain |
|---|---|---|---|
| C-L1 | M1 finalize inversion | M2 off-by-one strand | PARTIAL |
| C-L2 | M1 protocol-fee dilution | M2 HWM timing | PARTIAL |
| C-L3 | M1 diff-vs-amount_ | M2 Ceil dust | PARTIAL |

**FREEZE** before key opened; hashes in concrete_REVEAL_AND_SCORE.md.
