# P251 — Part C: Replay (the 5 P248 state-transition misses)

Ran the manifest-driven checkpoint on munchables/kleidi (4 anchors); the S4 anchor (decent H-04) is in the
`decent-bridge` lib which the decent manifest does not enumerate, so it was replayed via direct
`taxonomy.classify` on the `onOFTReceived` body (a manifest-enumeration / P245-coverage gap, NOT a checkpoint
gap). Outputs: `outputs/<contest>_stcheckpoint.json`. Invariant re-verified everywhere: `emits_findings:false`,
0 records with a conclusion.

## Observation (checkpoint fired at every anchor locus, right family)
| Miss | Sev | Locus | Family observed | Observed? |
|---|---|---|---|---|
| munchables H-01 | High | LockManager.lockOnBehalf / _lock | S1 | ✅ |
| kleidi M-01 | Med | Timelock.pause (loops `_liveProposals`) | S2 | ✅ |
| munchables M-01 | Med | LockManager.approveUSDPrice | S3 | ✅ |
| decent H-04 | High | DecentEthRouter.onOFTReceived (direct taxonomy) | S4 | ✅ |
| kleidi M-03 | Med | Timelock.updateExpirationPeriod | S5 | ✅ |

## Constructed candidates (answer the 8 questions → exploit_hypothesis + chain)
- **munchables H-01 (S1) [High].** Q1 attacker chooses? yes (`lockOnBehalf(victim)`). Q2 repeat? yes. Q3
  overwrite another's critical state? **yes — resets victim's `unlockTime`**. Q8 harmed? the victim.
  **Hypothesis/chain:** attacker repeatedly `lockOnBehalf(victim, dust)` → `unlockTime = now + duration` keeps
  pushing forward → victim can never withdraw. Candidate ✅ Chain ✅ (High).
- **kleidi M-01 (S2).** Q4 unbounded set/loop? **yes — `pause` loops `_liveProposals`, grown by `schedule`**.
  Q1/Q2 attacker (with threshold keys) floods proposals. **Chain:** flood proposals → pause/cancel loop gas
  griefing. Candidate ✅ Chain ✅.
- **munchables M-01 (S3).** Q5 two incompatible states? **yes — `approveUSDPrice` checks `approvals` but not
  `disapprovals`** → a price feed can approve AND disapprove the same proposal. **Chain:** dual-vote skews the
  threshold logic. Candidate ✅ Chain ✅.
- **decent H-04 (S4) [High].** Q6 failure/shortfall branch still updates state? **yes — `if (weth.balanceOf <
  _amount) { dcntEth.transfer(_to,_amount); return; }`**. **Chain:** dst router reserves < amount → user
  receives unbacked dcntEth and loses bridged ETH. Candidate ✅ Chain ✅ (High).
- **kleidi M-03 (S5).** Q7 time-window change affects existing state? **yes — `updateExpirationPeriod` with
  `newPeriod < currentPeriod` vs an in-window proposal**. **Chain:** can't reduce expiration while a proposal
  sits in the old window → update reverts. Candidate ✅ Chain ✅.

## Before → After
| Miss | Before candidate? | Before chain? | After candidate? | After chain? |
|---|---|---|---|---|
| munchables H-01 | partial (P246: flagged setLockDuration, not on-behalf) | ✗ | ✅ | ✅ (High) |
| kleidi M-01 | ✗ (read pause, dismissed) | ✗ | ✅ | ✅ |
| munchables M-01 | ✗ (read, dismissed) | ✗ | ✅ | ✅ |
| decent H-04 | partial (flagged reserve `>` off-by-one) | ✗ | ✅ | ✅ (High) |
| kleidi M-03 | ✗ | ✗ | ✅ | ✅ |
| **Totals** | 0/5 full, 0/5 chains | | **5/5 candidates** | **5/5 chains (2 High)** |

## Result vs success criteria
- ≥4/5 candidates → **5/5** ✅ · ≥3/5 chains → **5/5** ✅ · ≥1 High complete chain → **2** (H-01, H-04) ✅.
- (0 FP / 0 findings in Part D.)

## Honest caveat
Chains reconstructed by the operator answering the checkpoint's questions, confirmed against the P247/P248
ground truth → training-confound stands: the checkpoint guarantees the question is **asked at the locus**, not
that the answer is **found** on unseen code — that is the next forward-blind run's job.
