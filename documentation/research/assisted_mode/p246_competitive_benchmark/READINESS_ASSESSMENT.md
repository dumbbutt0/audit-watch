# P246 — Readiness Assessment

Measured on 6 fully-sealed, blind-hunted contests (freeze-before-reveal, hashes in each SCORECARD). Only
awarded-finding recovery vs answer keys counts. No optimism adjustments.

## Headline numbers
- **Overall weighted recall: 38.0% credited / 25.0% strict (direct-hit only)** (denom 52).
- **High recall: 44% direct / 61% credited** (4 of 9 Highs caught outright; real Highs found on 3 of 6).
- **Medium recall: 8% direct / 25% credited.**
- **FP rate ≈ 0%** (0 hard false positives in 6 contests).
- **Proof conversion: 0%** (BLOCKED_BY_BUILD everywhere).
- **Advisory-lens contribution: 0** awarded findings (precision-safe, recall-neutral on this corpus).

## Verdict

# B — LIVE_HUNT_READY

**Justification against the rubric:** credited weighted recall 38% falls in B's 30–50% band; the system
**finds real Highs consistently on tractable targets** (decent H-01 setRouter, vultisig H-01 fee-accounting
& H-03 launch-DoS, munchables H-02 early-unlock — all DIRECT), FP rate is ~0, and misses are concentrated
(reasoning depth 45% + coverage 24%). It is **not A**: it does not clear 50% weighted, recall is not
repeatable across architectures (0–65% range; collapses on large/cross-chain/hardened targets), and no
finding was proven with a PoC.

**This B is honestly at the B/C boundary**, for reasons recorded below — a stricter reading lands it in C.

## Why the true number is lower than 38% (no-optimism caveats)
1. **Training-data confound (largest):** all 6 are public Code4rena contests. As an LLM I likely have prior
   exposure to several of these findings (e.g. decent H-01 setRouter is widely cited). On a *genuinely
   unseen* contest, recall would be lower. The 38% is an **upper bound**.
2. **Partial-credit dependence:** strict DIRECT-HIT weighted recall is **25%** (C-range). The 38% relies on
   awarding 0.25–0.5 for same-root/same-area candidates that, in a real contest, would often **not** earn an
   award (judges reward the specific mechanism + impact, not "same area").
3. **Coverage collapse on scale:** fully-readable contests (≤3.3k LOC) averaged **45%**; coverage-incomplete
   contests (centrifuge 9%, badger 0%) averaged **26%** and the P245 gate would BLOCK them entirely. The
   system effectively **cannot compete on large/diamond/multi-contract targets in one pass**.
4. **Depth ceiling on hardened targets:** kleidi (8%) and badger (0%) — mature, formally-reasoned codebases
   where bugs are subtle logic/DoS — are near-misses; the system reads them but does not complete the
   reasoning (reasoning-depth = 45% of misses).
5. **No proof:** 0 PoCs. Modern High/Critical awards increasingly require working PoCs; an unproven High is
   often downgraded or disputed.
6. **n = 6, high variance.**

## Final question — answered with benchmark evidence only
**"If I entered real contests tomorrow with this frozen system, where would I realistically rank vs strong
human competitors?"**

**Mid-pack at best, and only on small, single-domain contests; uncompetitive on large or hardened ones.**
Concretely, the evidence says:
- On a **small, fully-readable** contest (e.g. an ILO, a single-vault, a focused bridge) the system would
  likely **catch the 1–2 most prominent Highs and a couple of Mediums** — enough to **place and earn some
  award**, landing it around a **competent-but-not-elite warden**: it would miss roughly half the Mediums and
  most subtle/depth findings, so it would **rarely finish top-5** and would not consistently take the top
  prize.
- On a **large, diamond/facet, or cross-chain** contest, it would be **non-competitive**: coverage collapses,
  the gate blocks triage, and recall falls toward 0–10% — it would **place poorly or not earn**.
- On a **hardened, multiply-audited** codebase it would **likely earn nothing** (the remaining bugs are the
  subtle depth/DoS findings it misses).
- Across a season it would behave like a **net-positive-but-marginal participant**: occasional awards on
  favorable (small, in-domain) contests, dragged down by the majority of contests that are too large or too
  hardened. It would **not** rank among strong human competitors who sustain high Medium recall and produce
  PoCs.

Adjusting honestly for the training-data confound and the partial-credit inflation, the **realistic
unbiased standing is the B/C border — "assisted hunter that is live-hunt-capable on small in-domain targets,
not a competitive top-tier warden."**
