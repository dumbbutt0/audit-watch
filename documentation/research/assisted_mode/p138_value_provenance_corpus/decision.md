# P138 — Decision

## Decision: **CORPUS_VALIDATES_PROMPT**

On a blind, labeled value-provenance corpus (10 items, 3 architectures, 5 buggy / 5 clean), the
`deep_pass_value_provenance` prompt — run by fresh uncontaminated subagents from source only — achieved
**useful recall 4/5 (80%)**, **finding precision 3/3 (100%)**, and **zero false positives on all 5 clean
controls** (incl. the HIGH-confidence clean). The 0% clean-FP (the key safety signal for advisory surfacing)
plus broad useful recall support promoting the H-03-class deep-pass routing from a manual recommendation to an
**automatic advisory** (human_review_queue, advisory_only) — never confirmed/submission.

### Rubric
- **CORPUS_VALIDATES_PROMPT** ✅ — high useful recall (80%) + low (0%) clean FP.
- Not CORPUS_PARTIALLY_VALIDATES: FP is zero, not "some"; recall is high.
- Not PROMPT_TOO_NOISY: 0/5 clean FP, including the HIGH-confidence clean.
- Not INSUFFICIENT_CORPUS: 10 labeled items across 3 architectures, balanced.

### Honest caveats (do not over-read)
- **n is small (10)**; promotion is to *advisory* (human-gated), not automation of confirmation.
- **2 positives were context-aided** (B5 needed the AVM ownerOf-vs-getOriginalOwner fact; B2 mildly) — recall is
  "with adequate bundle context" (callees/interfaces/domain facts that `deep_pass_prepare` supplies), not pure
  source-only. Unaided strict recall is ~2–3/5.
- **1 MISS (B3 / H-13)**: the subtle "÷weight twice" weighted-pool case — the blind agent produced sound math and
  cleared (the noya answer key itself predicted this as MISS-expected). Subtle arithmetic/units bugs remain a gap
  (covered separately by arithmetic_conservation / units_invariant, per P134).
- Result is **research evidence**: even a blind `finding` requires human + PoC before any severity/submission.

## Final response

**What this phase tested** — the `deep_pass_value_provenance` prompt's precision/recall/FP on a blind, labeled
value-provenance corpus (≥3 architectures, buggy + clean), to decide whether to promote the H-03-class routing
from manual recommendation to auto-advisory.

**Corpus** — 10 items, noya/size-credit/blackhole, 5 buggy (H-03 loop-var, H-19 debt-sign, H-13 ÷weight, Size
M-02 wrong-basis, Blackhole M-04 wrong-recipient) + 5 clean (1 HIGH + 4 MEDIUM confidence). Neutral packets, no
answer-key/role hints.

**Blind results** — buggy: HIT, HIT, MISS, PARTIAL(needs_human), HIT; clean: all 5 strong_clear.

**Precision / recall / FP** — useful recall **80% (4/5)**, strict **60% (3/5)**, finding precision **100% (3/3)**,
**strict_clean_fp_rate 0/5**, **high_confidence_clean_fp_rate 0/1**, needs_human-on-cleans 0.

**Per-architecture** — useful detection on all 3 archs; 0 clean FP on all 3.

**Safety** — no code changed; research evidence only; nothing confirmed/submission-ready; the clean controls and
the answer key stayed out of the blind packets; the 0% clean-FP is the safety basis for advisory promotion.

**Decision** — CORPUS_VALIDATES_PROMPT.

**Tests / integrity** — no code changed; active audit unchanged (`quantamm-2024-12-eval`); `rank_signal_probe
--self-test` OK; full `pytest -q` 1607 passed / 2 pre-existing snapshot fails / 4 skipped.

**Deliverables** — `documentation/research/assisted_mode/p138_value_provenance_corpus/` (corpus_design,
blind_packets, blind_outputs, grading, per_architecture, decision .md + metrics.json + runtime_output.txt).

**Next recommended phase (P139)** — implement the validated promotion: have the P135/P136 surfacing layer
**auto-run the `deep_pass_value_provenance` prompt** on the deep_pass_router's H-03-class recommendations and
attach the structured output to `human_review_queue` as advisory_only (config-gated, capped, human+PoC still
required) — with an A/B that it adds the value-provenance recall without raising clean FP. Keep the subtle-math
class (H-13) on arithmetic_conservation/units_invariant. Optionally expand the corpus (more protocols, fewer
aided items) to tighten the recall estimate before defaulting the auto-run on for production.
