# P186 — Firewall-sealed fresh-model blind mechanism-selection run

**Goal:** remove the same-model contamination caveat from P184/P185 by measuring mechanism SELECTION with a
**different Claude model (Sonnet)** doing the blind deep-trace, then scoring answer-aware only after outputs are
frozen. **Residual caveat (unavoidable, disclosed): Sonnet is still Claude/same-vendor — a different-vendor model
would be needed to remove vendor-level priors entirely.** Measurement only; no prompt/checker/code edits.

## Firewall (verified)
- 5 exact blind prompts frozen to `blind_prompts/` BEFORE the run (production `deep_trace.md` + verbatim source).
- Token-scan of prompts: **zero** finding-IDs / `answer key` / `P18x` / specific awarded descriptions. (The only
  `awarded`/`recall` hits are the production prompt's own generic header — same text the deployed pipeline uses.)
- 5 Sonnet subagents, each given ONLY its frozen prompt; raw outputs preserved verbatim in `raw_outputs/`.
- Token-scan of outputs: **zero** answer-key IDs cited → blind confirmed.
- Scorer (answer-aware) ran only after all raw outputs were written. No backfill.

## Result
```
awarded_mechanism_enumerated : 9/9
awarded_mechanism_SELECTED   : 7/9   (EXACT+LOOSE)     ← matches P184 Opus (7/9)
conservative_selected        : 5/9   (EXACT only)
demoted_unresolved_mechanism : 0     avg_selected/surface: 1.80 (Opus P184: 2.80 → no spam)
```

## Selection-stability matrix (the headline view)
| finding | P184 Opus | P185 Opus | P186 Sonnet | stable? |
|---|---|---|---|---|
| H-07 | ✓ | ✓ | ✓ | **stable** |
| M-03 | ✓ | (not re-run) | ✓ | **stable** |
| M-10 | ✓ | (not re-run) | ✓ (loose) | **stable** |
| L-01 | ✓ | (not re-run) | ✓ | **stable** |
| L-02 | ✓ | (not re-run) | ✓ | **stable** |
| H-03 | ✓ (loose) | ✓ (loose) | ✓ (loose) | **stable (loose)** |
| M-17 | ✗ not enum | ✓ carried | ✓ | improved & held |
| **M-02** | ✗ folded | **✓ carried** | **✗ rejected** | **MODEL-DEPENDENT** (P185✓→P186✗) |
| **M-06** | ✓ | (not re-run) | **✗ rejected** | **MODEL-DEPENDENT** (P184✓→P186✗) |

## Interpretation
- **Aggregate selection is STABLE across models (7/9 Opus → 7/9 Sonnet).** Per the decision rule, this
  **promotes confidence in P183 enumeration**: the mechanism-enumeration gain is real and **not primarily a
  same-model artifact** — a different model independently selects the awarded 2nd/3rd mechanisms.
- **6 selections are fully model-independent** (H-07, M-03, M-10, L-01, L-02, H-03-loose) — these are the
  high-confidence, stable wins (exactly the "stable selections matter more than the aggregate" lens).
- **The two flips are the honest, important part:**
  - **M-02** — the *specific P185 ranking fix* did NOT hold on Sonnet. Sonnet's stronger reject-first judged the
    `lpTokenDepositValueChange` division "dimensionally consistent, floors favour the LP" and **rejected it with a
    confident source-backed reason**. So the P185 carry-forward fix for M-02 is **model-dependent** — a more
    skeptical model treats M-02 as not-a-bug. → **qualified confidence in the P185 M-02 fix.**
  - **M-06** — Sonnet rejected the unhandled-Chainlink-revert DoS as "liveness-only / view function, not
    fund-loss," whereas Opus (P184) selected it. Also a model-dependent reject-first severity judgment.
  - **M-17 improved** (Sonnet carried the >100% fee-bound mechanism Opus P184 missed) — the inventory-menu line
    generalizes.
- **No mechanism spam.** Sonnet's avg selected/surface is 1.80 (< Opus 2.80); it pushed more mechanisms into
  `unresolved`/`rejected`. The selected lists stayed tight and source-grounded; checker = 5/5 complete, 0 demoted.

## Checker limitation surfaced (flag, not fixed)
Sonnet's rejections of M-02 and M-06 carry confident source-backed `rejecting_source_fact` +
`leans_on_unproven_guard=false`, so the P185 `demoted_unresolved_mechanism` detector does **not** flag them. The
checker prevents *unresolved* demotion, **not a confident mis-rejection of a real bug**. Closing that gap is a
ranking/severity-calibration problem (a future phase), not a checker-format fix.

## Decision
- **PROMOTE confidence in P183 enumeration** — model-robust (7/9 holds cross-model; 6 stable selections).
- **QUALIFIED confidence in the P185 M-02 ranking fix** — works on Opus, rejected by Sonnet; model-sensitive.
- Not a contamination collapse (selection held); not spam (Sonnet more conservative).
- No production change (measurement). No recall claimed beyond this blind cross-model n=9.

## Honesty / residual
Same vendor (Claude) — vendor-level priors remain; n=9 single run per model. The genuinely model-dependent
cells (M-02, M-06) are reject-first *validity/severity judgments*, not enumeration failures — i.e. both models
SEE the mechanism; they disagree on whether it's a real, in-severity bug. That is now the frontier: not "can the
deep-pass enumerate the mechanism" (yes, robustly) but "can it consistently *adjudicate* a plausible mechanism's
validity/severity" — which P186 shows is model-sensitive.
