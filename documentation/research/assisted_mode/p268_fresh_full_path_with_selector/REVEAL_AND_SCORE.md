# P268 — REVEAL_AND_SCORE (Phase 11, POST-FREEZE)

## Freeze integrity (recorded BEFORE opening the answer key)
BASE_AND_HARNESS_FREEZE `981190e8928a451c` · TRIAGE_AND_POC_QUEUE `fa4d1913073f49eb` · RANKING_OUTPUTS
`5803fc9b445a9af8` · SELECTOR_OUTPUTS `ad2bdc5b783f020f` · COMPLETION_OUTPUTS `3d1c23d4854d6f18` · POC_INTENT
`cc862c6535a4fe76` · POC_RESULTS `52fcd55a34eddb0b` · PRE_REVEAL_GATE `5c3ea8aac6bfbab3` · selector_decisions
`68497ab2ad0362cd` · poc_queue `7e26d0cbeefc9a4a` · P268_Vault.t.sol `ed7fb79345dfa0be`.
Reveal source: code4rena.com/reports/2024-07-karak (PUBLIC), opened after the freeze. Awarded: **4 High + 5 Medium**.

## Awarded findings — all 9 cluster in NativeVault / slashing / snapshot
| awarded | subsystem | harness-surfaced? | triaged to PoC? | selector? | final |
|---|---|---|---|---|---|
| H-01 slashing NativeVault double-reduction → locked ETH | NativeVault/snapshot | **YES** (`_startSnapshot` narrow#2, `validateSnapshotProofs` delta#7) | **NO (de-scoped)** | — | MISSED-AT-TRIAGE |
| H-02 operator can create unslashable NativeVault (extraData) | NativeVault init | partial | NO | — | MISSED |
| H-03 ERC4626 rounding DoS on snapshots (`convertToAssets` > totalRestakedETH) | NativeVault | YES (`validateSnapshotProofs`) | NO | — | MISSED-AT-TRIAGE |
| H-04 DSS can slash unregistered operators (time gap) | SlasherLib/Core | **YES** (`finalizeSlashing` delta#11, `cancelSlashing` #12) | NO (treated slashing as gated control) | — | MISSED-AT-TRIAGE |
| M-01 slashingHandler change DoSes slashing | SlashingHandler/Core | partial | NO | — | MISSED |
| M-02 snapshot DoS share-burn | NativeVault | YES (area) | NO | — | MISSED |
| M-03 slash miscalc with queued withdrawals | SlasherLib + Withdraw | YES (`finalizeSlashing`) | NO | — | MISSED-AT-TRIAGE |
| M-04 pending-slash deposit-loss / first-depositor in fully-slashed vaults | Vault/Core | YES (Vault area) | partially (C2 area) | — | ADJACENT (different mechanism) |
| M-05 slashing fails when vault assets zero | SlashingHandler | partial | NO | — | MISSED |

## My queued mechanisms (final classification)
| id | mechanism | PoC | awarded? | classification |
|---|---|---|---|---|
| **C2-M1** | Vault first-depositor donation inflation (victim → 0 shares) | **PASS (real loss)** | **NO** — report states "No distinct first-depositor / decimalsOffset finding was independently awarded" | **NOT_AWARDED real issue** (true-positive, not awarded; adjacent to M-04) |
| C1-M1 | finishRedeem accounting | refuted (by-design) | no | BENIGN |
| C1-M2 | startRedeem approval revert | UX/griefing | no | BENIGN |
| C-neg | slashing | REFUTE_FIRST | (H-04/M-03 live here) | the gated-control assumption MISSED the awarded slashing bugs |

## Mechanism-recovery scoring (strict)
- **EXACT_AWARDED_MECHANISM: 0** · **STRONG_MECHANISM_MATCH: 0** · FAMILY_LEVEL_MATCH: 0.
- **SUBSYSTEM_ONLY_RECALL: YES** — the harness's narrow+recall-delta surfaced the award-dense NativeVault/slashing/
  snapshot subsystem (H-01/H-03/H-04/M-02/M-03 loci), but **triage de-scoped it** (recorded pre-reveal in
  `poc_queue.json` `skipped_high_ranked`: "needs beacon fixtures → heavy PoC harness").
- **NOT_AWARDED real issue: 1** (C2-M1 inflation — PoC-confirmed victim loss, but not an awarded finding).
- **FALSE_POSITIVE (severe concluded/reportable): 0** — C2-M1 stayed an advisory PRE_REVEAL candidate (never
  concluded/reportable); it is a real issue, not a fabricated FP.

## The selector verdict (the P268 question)
**Did P267 fix the P266 drop? YES — mechanically, on fresh data.** The selector returned KEEP_BOTH on C1 and C2
(anti-easy-PoC), preserving the high-impact mechanisms the raw pre-P267 path would have dropped for the easy rivals
(dust-rounding / approval-revert); the preserved C2-M1 was carried to completion + PoC and **confirmed real**.
**But it did NOT convert to an AWARDED exact recovery**, because (1) the confirmed mechanism (Vault first-depositor)
was not awarded, and (2) the award-dense NativeVault/slashing subsystem was **skipped upstream at TRIAGE** — the
selector can only choose among mechanisms triage routes to it. The binding constraint moved upstream of the selector,
to triage/candidate-selection-for-PoC.
