# Research Judge Layer — Evaluation Methodology (Paper Design)

> **Status: DESIGN ONLY. The judge is NOT built; this corpus is NOT collected.** This is the **evaluation-design**
> artifact that resolves the "Evaluation method" open question in
> `research_judge_layer_design.md` §10, written *before* any prototype so the future judge is built against a
> success definition rather than a vibe. No code, schema, config, routing, gate, or answer key exists or is changed
> by this document.

```
Research Stage
Status:     Evaluation Methodology — Design Only
Judge:      Not Built
Corpus:     Not Collected
Routing:    Disabled
```

---

## 1. Why a Judge Resists Detector-Style Evaluation

Detector validation is clean because a detector has an **answer key**: a frozen anchor finding it must recover and a
set of negatives it must stay quiet on → HIT / MISS / false-positive / precision (see
`../architecture/research_methodology.md`, stages Ground-Truth and Validation).

The judge has **no ground-truth verdict by construction**. Per `research_judge_layer_design.md` it refuses to emit
`is_bug` / `valid` / `severity` / `exploitability_score` / `verdict`. It outputs only a *plausibility estimate over
assembled evidence*, supporting/counter signals (each grounded in bundle fields), and an `information_needed[]`
list. Therefore:

> **Scoring the judge's output against a bug answer-key is category-inappropriate — and actively harmful.**

It is harmful because "reward the judge when it agrees with the real bug outcome" silently trains/selects the judge
toward predicting bug validity and severity — exactly the adjudication the **"assess, don't prove"** invariant
exists to forbid. The evaluation method must refuse HIT/MISS bug scoring as firmly as the judge refuses `is_bug`.

---

## 2. The Goodhart Trap  *(the most important section)*

If we evaluate the judge against any of the following targets, we corrupt it into an exploitability/severity
predictor and re-create the engine the platform deliberately kept separate:

```
┌──────────────────── FORBIDDEN EVALUATION TARGETS ────────────────────┐
│  • agreement with final bug validity   (was it "really" a bug?)       │
│  • agreement with final severity        (critical/high/…)             │
│  • agreement with "submitted / accepted / paid" outcomes              │
│  • PoC pass/fail used as a CORRECTNESS oracle for the judge           │
│  • any metric that rewards calling more bugs "real"                   │
└────────────────────────────────────────────────────────────────────────┘
```

The discipline mirrors the judge's own forbidden-field list:

> **The evaluation must not reward the judge for things the judge is forbidden to output.**

A judge optimized for "agrees with the eventual bug verdict" would learn to *assert* validity to score well —
maximizing exactly the behavior `assess, don't prove` prohibits. Any of the targets above turns the judge into a
shadow `judge_simulate.py` (production's wired judge, which *is* allowed to predict outcomes — see §7). We refuse
them at the evaluation layer.

---

## 3. What "Useful" Actually Means Here

Usefulness is defined as **triage value over evidence bundles**, not bug-calling accuracy:

> *Does the judge's assessment help a human (or the next research layer) spend effort where it pays off — without
> suppressing real signal?*

Three usefulness lenses, **none requiring a bug answer-key**:

1. **Reviewer agreement (coherence, not validity).** Does the judge's `plausibility_estimate` and its
   `counter_signals` agree with an expert's *independent read of the same bundle* — agreement on "is this evidence
   coherent / worth a closer look," **not** on "is this a bug"? Measured as inter-rater agreement between judge and
   human on the ordinal coherence scale.
2. **Effort allocation / triage lift (ranking quality).** If a reviewer's scarce attention were allocated in the
   judge's `plausibility_estimate` order, would the bundles the reviewer independently deemed worth investigating
   appear *earlier*, and the dismissed ones *later*? This is a ranking-quality measure (the reviewer's own
   "worth-effort" label is the comparison, not a bug outcome).
3. **Grounding fidelity (mechanical, no humans).** Every `supporting_signal` / `counter_signal` must cite a real
   bundle field via `evidence_refs[]` (per the judge design's Grounding Requirements). Metric = rate of
   uncited / dangling-ref / hallucinated-field signals. This is the **only fully automatic metric**, requires no
   corpus and no humans, and is the **first gate any prototype must pass** — a judge that invents field references
   fails here before reviewer studies are even worth running.

---

## 4. Proposed Evaluation Protocol  *(paper)*

- **Corpus.** A small **frozen set of `READY_FOR_REVIEW` evidence bundles** drawn from existing research-track
  output — the demo bundles already on disk (`_evidence_demo/evidence_bundles.json`, 6 READY bundles over
  `multicall_invariant` + `permit_asset_binding`) plus additional bundles produced by re-running the two
  RESEARCH-STABLE detectors → normalization → evidence gate on already-examined targets. Size band: enough for a
  meaningful agreement statistic without over-claiming (a few dozen bundles, not thousands); frozen by content hash
  like every other research corpus.
- **Only READY bundles.** Consistent with the judge's input contract — INSUFFICIENT bundles are an *evidence-layer*
  problem and are out of scope for judge evaluation.
- **Blind expert annotation.** Independent human reviewer(s) annotate each bundle, *blind to the judge's output*,
  with: (a) a coherence rating on the same ordinal scale the judge uses; (b) a "worth PoC effort?" yes/no/maybe;
  (c) the reviewer's own counter-arguments. **These labels are coherence / effort judgments — never a bug
  answer-key.** They are **human-authored**: consistent with the non-negotiable that `data/evaluation/
  ground_truth.jsonl` is human-only, the AI must not fabricate, infer, or pre-fill these labels (and this corpus is
  separate from `ground_truth.jsonl` entirely — see §7).
- **Comparison.** Judge vs human on lens 1 (agreement) and lens 2 (ranking); lens 3 computed automatically over the
  judge output alone. Candidate statistics (named, **not** mandated): weighted Cohen's κ or an ordinal rank
  correlation for the ordinal coherence scale; a rank-overlap measure (e.g. top-k overlap) for triage lift. The
  exact statistic is itself a sub-decision to settle before running.
- **What a pass looks like.** Grounding fidelity at/near 100%; reviewer agreement clearly above chance; triage
  ranking clearly better than random ordering of the same bundles. None of these references a bug outcome.

---

## 5. Calibration & Drift  *(secondary; explicitly not a training loop)*

A longitudinal *observation* is permissible: over time, do bundles the judge rated `coherent_signal` tend to be the
ones a human / the separate PoC path *later* found worth the effort? This is recorded as a **calibration
observation**, not optimized against.

> **Hard line:** this observation is **never** fed back as a training/selection signal that tunes the judge toward
> bug-calling. Doing so would re-open the Goodhart trap of §2.

This is the one place the platform's Self-Calibration principle (`CLAUDE.md`: "a system that cannot measure its own
FP/recall cannot be tuned") interacts with the judge — and the resolution is deliberate: **we measure, we do not
auto-tune the judge toward validity.** Calibration informs humans deciding whether the layer is worth promoting; it
does not close a loop onto the judge's outputs.

---

## 6. Negative Results & Failure Modes

A *failed* judge is a valid, documentable outcome — never something to patch toward agreement:

- **Low grounding fidelity** (uncited / hallucinated `evidence_refs`) ⇒ the judge invents — fails the first gate;
  fix is design/constraint, not metric-chasing.
- **Reviewer agreement near chance** ⇒ the `plausibility_estimate` carries no signal a human shares.
- **Triage lift ≈ random** ⇒ ranking by the judge saves no effort.
- **Suppressed real signal** ⇒ the judge consistently rates `weak_signal` on bundles reviewers found worth effort
  (a recall-style harm, measured against *reviewer* effort labels, not bug outcomes).

Per `research_methodology.md`, such a judge is classified **PROMISING-BUT-NEEDS-REFINEMENT** or **NOT-A-LAYER** and
documented honestly. It is **never** patched to chase reviewer agreement, just as a detector is never patched to
chase answer-key HITs.

---

## 7. Relationship to Production  *(separate, un-wired)*

The production pipeline already has a feedback loop — `scripts/record_outcome.py`, `compute_metrics.py`,
`derive_learning.py` (staged) + human-run `promote_learning.py`, over a provenance-gated, human-only
`data/evaluation/ground_truth.jsonl` — and a wired `judge_simulate.py` that *is* allowed to predict
outcome/severity/submit. This research evaluation is **separate and un-wired**:

- It never writes `ground_truth.jsonl` or any production outcome record.
- It never feeds `derive_learning.py` / production calibration.
- It never sets severity, exploitability, or submission readiness.
- Its corpus and labels live under the research track, not the production evaluation store.

Cross-link, do not reuse. Bridging this research evaluation (or the judge it would evaluate) into production is a
future, explicit, human decision.

---

## 8. Lifecycle & Next Steps

This resolves the `research_judge_layer_design.md` §10 "Evaluation method" open question and **pre-defines the
Ground-Truth and Validation stages** (`../architecture/research_methodology.md`) for the future judge. Deferred
until a judge prototype exists: collecting the frozen bundle corpus, the blind human annotation pass, fixing the
exact agreement statistic, and a first run of lens-3 grounding fidelity (the only part runnable the moment a
prototype emits output). Prototype itself remains **not built** — by design, and by the user's "more cautious, not
faster" direction.
