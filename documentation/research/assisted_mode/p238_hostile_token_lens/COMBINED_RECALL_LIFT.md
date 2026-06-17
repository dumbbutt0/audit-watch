# P237 + P238 — Combined recall-lift on reNFT 2024-01

> Projected recall if both research lenses (Safe-management `safe_management_coverage` P237 + hostile-token
> `hostile_token_settlement` P238) were applied to the reNFT hunt. Both un-wired/research-only; this is a
> measurement, not a wiring. Weighting High=3, Medium=1; reNFT awarded ≈ 5 High (H-01..H-05) + ~14 Medium ≈ 29.

## reNFT awarded Highs — recovery by stage
| High | Family | P235 baseline | + P237 (Safe-mgmt) | + P238 (hostile-token) | Combined |
|---|---|---|---|---|---|
| H-01 | hostile-token (malicious consideration tip → settle reverts → lock) | miss | miss | **DIRECT (high)** | **recovered** |
| H-02 | Safe-management (setFallbackHandler uncovered) | miss (partial) | **DIRECT (high)** | — | **recovered** |
| H-03 | create-time reentrancy (ERC1155 onReceived before registration) | miss | miss | miss | **still missed** |
| H-04 | Safe-management (disableModule offset) | hand-found | **DIRECT (high)** | — | **recovered** |
| H-05 | Safe-management (fallback removal + permit) | miss | **PARTIAL (high)** | — | **recovered (partial)** |
| #64/#605 | hostile-token (blacklist freeze, Medium) | miss | — | **covered (same settle path)** | **recovered** |

## Recall numbers
| Stage | Raw High recall | Weighted recall (approx) |
|---|---|---|
| **P235 baseline (actual hunt)** | 1/5 = 20% (H-04, hand-found) | ~10–16% |
| **+ P237 Safe-management lens** | ~3/5 = 60% (H-04, H-02, H-05 partial) | ~26–36% |
| **+ P238 hostile-token lens** | adds H-01 + #64/#605 | adds High=3 + ~2 Med |
| **Combined P237 + P238** | **~4/5 = 80%** (H-01, H-02, H-04, H-05; only H-03 missed) | **~40–45%** |

The two lenses recover **disjoint** families (Safe-management vs hostile-token), so they stack cleanly. Combined,
they lift reNFT High recall from 1/5 to ~4/5 — moving the P235 verdict from **C (RECALL_GAPS_REMAIN) to ~B
(WOULD_HAVE_FOUND_MEANINGFUL_FINDINGS)**.

## What's still missed (honest)
- **H-03** — create-time reentrancy (ERC1155 transferred to the safe before the rental is registered + malicious
  fallback handler reenters). This is P236's **third** family (create-time reentrancy / lifecycle ordering), not
  built. It is the main remaining High gap.
- **#387** — Seaport execution-invariant bypass (MEDIUM-generalization family per P236).
Reaching A (top-tier) would need the create-time-reentrancy lens too; neither lens here targets it (by design).

## Recommendation (combined)
Both lenses are clean on the single reNFT anchor (0 FP each) but unvalidated beyond it →
PROMISING-BUT-NEEDS-REFINEMENT. **Next step: a joint 15–20 target validation campaign of both lenses** (test both
recall lifts together, as the user intended), gated on 0 high-confidence FP retention, before any wiring. A second
shadow contest on a fresh architecture should follow the campaign to confirm the end-to-end lift before live hunting.
A third lens (create-time reentrancy) is the natural follow-on to close H-03.
