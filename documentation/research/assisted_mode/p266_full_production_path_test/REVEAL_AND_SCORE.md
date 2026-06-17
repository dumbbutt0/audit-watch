# P266 — REVEAL_AND_SCORE (Phase 8, POST-FREEZE)

## Freeze integrity (recorded BEFORE opening the answer key)
BASE_AND_HARNESS_FREEZE `c7788d7d6d30bb2c` · TRIAGE_AND_POC_QUEUE `447918fc7932afe3` · RANKING_AND_COMPLETION
`c0296f973b6ae28e` · POC_INTENT `9fea23943038fe6b` · POC_RESULTS `fb19372f5a47ceae` · PRE_REVEAL_GATE
`067091c03824ba20` · poc_queue.json `b4e5dec6e0a61f39` · advisory_recall_feed.json `62275f55f70bd675` ·
recall_advisory_candidates.json `18f3d80f2b3c5dfa`.
Reveal source: code4rena.com/reports/2024-08-phi (PUBLIC), opened after the freeze. Awarded: **7 High + 8 Medium**.

## Awarded findings (per-issue chain through my path)
| awarded | area | dashboard-surfaced? | recall-delta/narrow | mechanism generated? | top-2 B/C? | selected? | completed? | PoC? | final match |
|---|---|---|---|---|---|---|---|---|---|
| **H-03** shareBalance bloat → curator-reward distribution gas-DoS | `CuratorRewardsDistributor.distribute` + `Cred` curator enumeration | **YES** | distribute narrow#2; `Cred._updateCuratorShareBalance` delta#7 | **YES** (m1c "unbounded-curator gas DoS", Profile B top-2) | **YES (B)** | **NO** (selected m1a instead) | no | no | **FAMILY_LEVEL, GENERATED-BUT-MISRANKED** |
| H-05 public `_add/_removeCredIdPerAddress` manipulate share tracking → DoS | Cred curator-tracking helpers | partial (adjacent `_updateCuratorShareBalance` #7 surfaced; the public helpers themselves not in top-18) | delta-adjacent | no | — | no | no | no | SUBSYSTEM/AREA only |
| H-01 `signatureClaim` replay (missing chainId) | PhiFactory claim | **YES** (narrow#0) | narrow | no | — | **NO (triage-skipped claim flow)** | no | no | LOCUS-SURFACED, TRIAGE-SKIPPED |
| M-07 attacker DoS from share selling | Cred `_handleTrade` | YES (delta#5) | delta | no | — | no | no | no | SUBSYSTEM/AREA only |
| H-02 createArt replay · H-04 endTime extension · H-06 cred-creation reentrancy · H-07 token-setting changes · M-01..M-06, M-08 | claim/art/factory/fee | mostly not in top-18 | — | no | — | no | no | no | MISSED (out of focused reward-subsystem scope) |

## My queued candidates (final classification)
| id | selected mechanism | awarded? | classification |
|---|---|---|---|
| **C1** | m1a: royalty + dust → arbitrary caller | **NOT awarded** (report explicitly notes no distribute royalty/fee-to-caller finding) | **SAME_AREA_WRONG_MECHANISM** (correct locus = distribute, which carries awarded H-03; selected a real-but-non-awarded value flow). Note: my runner-up **m1c ≈ H-03** (generated-but-misranked). |
| **C2** | m2a: just-in-time spot-share reward capture | **NOT awarded** (report explicitly notes no JIT share-capture finding) | **SAME_AREA_WRONG_MECHANISM** (correct reward-split subsystem, non-awarded mechanism) |
| **C-neg** | (none — predicted benign) | no withdraw award (H-01 is `signatureClaim`, not `withdrawWithSig`) | **BENIGN — CORRECT** (negative control validated by reveal) |

## Mechanism-recovery scoring (strict taxonomy)
- **EXACT_AWARDED_MECHANISM: 0**
- **STRONG_MECHANISM_MATCH: 0**
- **FAMILY_LEVEL_MATCH: 1** — H-03 gas-DoS family generated as m1c, but **mis-ranked (B top-2, not #1) and never selected/completed/PoC'd**.
- **SUBSYSTEM_ONLY_RECALL:** distribute + Cred curator-share subsystem surfaced (carries H-03/H-05/M-07).
- **SAME_AREA_WRONG_MECHANISM: 2** (C1 m1a royalty; C2 m2a JIT).
- **FALSE_POSITIVE (severe concluded/reportable): 0** — nothing was marked concluded/reportable/severity; C1 was
  only a CONDITIONAL pre-reveal candidate, C2 held, C-neg benign. The C1/C2 mechanisms are *real value flows*, just
  non-awarded (by-design / not-found) — surfaced as advisory, never as findings.

## Safety result (clean)
0 severe concluded/reportable FP · advisory feed + all candidates stayed ADVISORY (severity null, 0 promotion flags) ·
dashboard surface advisory-only (no canonical-record/forbidden-file touch) · negative control correctly benign ·
no auto-submission · active audit unchanged.

## Honest headline
The full path **surfaced the exact awarded locus** (`distribute`, H-03) and **enumerated the awarded mechanism
family** (gas-DoS, m1c) into Profile-B top-2 — but **mis-ranked it below a non-awarded mechanism** and PoC'd the
wrong target. **0 exact / 0 strong** mechanism recoveries. Mechanism precision did **not** improve beyond P263/P265;
the gap is now localized to **ranking/selection on the full path**, not discovery and not PoC construction.
