# P247 — Verdict

## Success-criterion check
> Explain ≥80% of reasoning-bound misses with a small recurring failure set AND identify interventions that
> plausibly recover the majority of lost weighted recall without increasing false positives.

- **Explained:** top-5 clusters explain **95% by count / 97% by weighted** (top-3 already 71% / 74%). ✅ (≤5
  clusters, ≥80%).
- **Recovery plausible:** expected interventions recover ~55% of the 24.75 reasoning-recoverable weighted
  (~majority); confound-adjusted overall weighted recall ~50–58% (expected). ✅ plausible, not guaranteed.
- **No FP increase:** interventions are examine-time checkpoints feeding the existing precision gates (not
  auto-submitters) → FP ≈ 0 preserved. ✅ by design (conditional on that wiring).

**Success criterion: MET** (clustering decisively; recovery plausibly, with stated uncertainty).

## Verdict (exactly one)

# A — REASONING_FIXES_LIKELY_SUFFICIENT

Reasoning interventions plausibly move benchmark performance toward competitive levels.

### Why A (not B/C/D)
- **Not B (coverage still dominates):** P246 measured reasoning = 45% of misses vs coverage = 24%, and the
  coverage misses concentrate entirely in oversized targets (centrifuge unread layers, badger) that the P245
  gate already BLOCKS. On the tractable, fully-readable contests — the regime where the system can actually
  compete — the misses are almost purely reasoning. Coverage is no longer the primary bottleneck there.
- **Not C (depth overstated):** the attribution is not inflated — 21 concrete read-but-missed findings, each
  with a reconstructed system-vs-ground-truth divergence, clustering into 3–5 recurring failure modes (clean,
  not diffuse).
- **Not D (insufficient evidence):** n=21 across 6 diverse contests with sealed-key ground truth is enough
  for a directional verdict; the uncertainty is in the *magnitude* of lift (quantified as a band), not in the
  *direction*.

### The honest qualifier
"Likely sufficient" means **the lever is correct and plausibly reaches competitive (~50–58% expected,
confound-adjusted)** — it is **not a guarantee of 60–70%+**. Three caveats bound the claim:
1. **Magnitude is estimated, training-confounded, and unverified** — only a forward blind run with the
   interventions live can confirm it.
2. **Oversized targets stay coverage-capped** — reasoning fixes do nothing for badger/centrifuge-scale
   surfaces; the ceiling there remains the P245 coverage regime.
3. **FP-safety is conditional** — the interventions must produce gated candidates, not auto-submissions, or
   the Economic checkpoint in particular could reintroduce false positives and erode the net gain.

### What this implies (no implementation here)
The concrete path is **examine-time reasoning checkpoints** (cross-contract terminal-state trace ·
adversarial state-transition walk · conservation/rounding/index check · entrypoint-principal map · economic
actor model), sequenced cheapest-FP-tightest first (accounting + permission → state-machine → cross-contract
→ economic), inserted at hypothesis-generation time (distinct from P245's rejection-time depth gate) and
routed through existing precision gates. **Building any of this is a separate, explicitly-approved phase** —
P247 ends at this forensic verdict.
