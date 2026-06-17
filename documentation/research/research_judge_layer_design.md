# Research Judge Layer — Paper Design

> **Status: DESIGN ONLY. Nothing in this document is built.** It is the **Research**-stage artifact (per
> `../architecture/research_methodology.md`) for a *future* research-track layer. No code, schema, config, routing,
> or gate exists or is changed by this document. It defines what a research-track judge would be **allowed to do** —
> and, more importantly, what it must **refuse** to do.

```
Research Stage
Status:     Design Only
Prototype:  Not Built
Validation: Not Started
Routing:    Disabled
```

---

## 1. Type & Invariant

A read-only, **research-only**, **un-wired** stage that would sit one step past the Evidence Bundle Gate:

```
detectors → normalization → evidence-bundle gate → [Judge Layer]  ← this document
```

It would carry the same four research flags on every output (`is_gate:false`, `research_only:true`,
`routes_in_production:false`, `routed_manifest_ids:[]`) and remain disconnected from production routing/gates.

Its one-line invariant continues the platform pattern (`../architecture/platform_invariants.md`):

```
Detector    signal,   don't submit
Normalizer  rank,     don't relabel
Evidence    assemble, don't adjudicate
Judge       assess,   don't prove
```

- **Assess** = estimate whether the *assembled evidence* coheres into a plausible issue, and name what is missing.
- **Don't prove** = never claim a validated bug, never assign final severity, never declare exploitability proven,
  never recommend submission.

The dangerous alternative the invariant exists to forbid is `Judge → determine validity`, which would immediately
recreate a second exploitability/severity engine and leak into triage and submission decisions.

### Not the production judge
This is **NOT** the production `scripts/judge_simulate.py` (the 5-persona adversarial judge wired into the
production triage flow, schema `schemas/judge_simulation.schema.json`). That production judge legitimately emits
verdict fields — `predicted_outcome` (`accepted`/`rejected`/…), `predicted_severity` (`critical`…`invalid`), and
`final_submit_recommendation` (`submit`/`revise`/`poc_first`/`drop`). The **research-track** judge described here
consumes research-only *evidence bundles* and emits **none** of those fields. The two are separate tracks; bridging
the research track into production is an explicit, later, human decision and is out of scope here.

---

## 2. The Single Question

> **"Does the assembled evidence cohere into a plausible issue worth PoC effort — and what information would a
> reviewer need to confirm or refute it?"**

Not "is this a real bug." Not "what severity." Just: is this coherent enough to be worth a human's (or a future
PoC-feasibility layer's) time, and what is the gap.

---

## 3. Input Contract

- **Sole input:** `evidence_bundles.json` (the Evidence Bundle Gate's output) — composable, single upstream.
- **Only `READY_FOR_REVIEW` bundles are judged.** `INSUFFICIENT_EVIDENCE` bundles are **not** passed to the judge;
  they return to the evidence stage for more material. This is the strongest architectural decision in the design:
  it means the judge **never reasons about missing code, missing traceability, missing rationale, or an empty
  evidence payload** — which is precisely where a model would otherwise invent facts to fill gaps. The completeness
  question is already settled before the judge sees anything.
- **Refuses routed input:** if the bundle file's `routing_allowed` is not `false`, the judge refuses (same
  defensive guard as the normalization layer and evidence gate).
- **Reasons only over fields already in the bundle:** `location`, `code_snippet`, `evidence_signals`, `rationale`,
  `confidence`, `declared_severity_potential`, `candidate_surface`, traceability. See §6 (Grounding Requirements).

---

## 4. Output Contract (proposed `research_judge_assessments.json`)

Per judged bundle:

**Carried verbatim** (never recomputed — continues "don't relabel"/"carry verbatim" up the stack):
`candidate_id`, `detector`, `detector_version`, `candidate_surface`, `confidence`, `declared_severity_potential`,
`source_audit_path`.

**Assessed (the judge's only added content):**
- `plausibility_estimate` — an **ordinal over the coherence of the assembled evidence**, deliberately worded so it
  can never be mistaken for a severity or a validity verdict. Proposed scale:
  `coherent_signal` / `partial_signal` / `weak_signal`.
- `assessment_rationale` — prose grounded in named bundle fields (no free assertion).
- `supporting_signals[]` — concrete reasons the evidence coheres; **each cites bundle fields** (see §6).
- `counter_signals[]` — the adversarial half: concrete reasons it may be benign / a non-issue / a known-safe
  pattern; **each cites bundle fields** (see §6).
- `information_needed[]` — what a human or a future PoC-feasibility layer would need to confirm or refute the signal
  (e.g. "trace the `asset()` value", "check caller authorization", "confirm reachable from an EOA with no
  privileged setup").

**Flags:** `routing_allowed:false`, `research_only:true` on every record and at top level.

---

## 5. The "Assess, Don't Prove" Invariant  *(the heart of this design)*

The judge must **never** emit any of these fields. They belong to separate, downstream layers (research-track) or to
the production pipeline — never to this layer:

```
┌──────────────────────── FORBIDDEN OUTPUT FIELDS ────────────────────────┐
│  is_bug · valid · severity · exploitability_score ·                      │
│  submission_recommendation · poc_required · recommended_next_step ·      │
│  verdict                                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

If any of those appear in the chain later, they must originate in a **separate** layer (a PoC-feasibility layer, a
submission-readiness layer) or in the production engines — never the judge. `plausibility_estimate` is an estimate
over *assembled evidence coherence only*; it is explicitly **not** a bug conclusion, **not** a severity, **not** an
exploitability score.

**Required safeguards a future prototype must implement and test:**
- Four research flags on every record (`is_gate:false`/`research_only:true`/`routes_in_production:false`/
  `routed_manifest_ids:[]`).
- `confidence` and `declared_severity_potential` carried **verbatim** (tested across all levels).
- **Refusal** of any input whose `routing_allowed` ≠ false (tested).
- A test asserting **every forbidden field above is absent** from the output (mirrors the evidence gate's
  `test_no_verdict_fields`).
- Grounding enforcement per §6 (an uncited signal is a malformed assessment).

---

## 6. Grounding Requirements  *(hard rules; prototype must enforce + test)*

These are what keep an LLM (or heuristic) judge from drifting into invention. All are testable.

- **No new evidence.** The judge may not introduce any fact not already present in the bundle. It cannot assert
  "the asset is X" unless X is in `evidence_signals`/`code_snippet`/`rationale`.
- **Evidence references required.** Every `supporting_signal` and every `counter_signal` MUST cite one or more
  evidence-bundle fields via an `evidence_refs[]` list. Shape:
  ```json
  {
    "supporting_signal": {
      "claim": "Expected asset identified",
      "evidence_refs": ["evidence_signals.expected_asset", "code_snippet"]
    }
  }
  ```
  An assessment containing a signal with an empty or absent `evidence_refs` is **malformed** — this makes
  hallucination testing tractable later (a uncited claim is mechanically detectable, independent of whether the
  claim is "true").
- **No source retrieval.** The judge does not read the filesystem or fetch additional source.
- **No repository traversal.** The judge does not walk the repo or open files beyond the bundle.
- **No code discovery.** The judge does not search for related functions/contracts. It reasons **only** over the
  `code_snippet` and evidence the Evidence Bundle Gate already assembled.

Net effect: the judge's whole world is one bundle. If the snippet is insufficient to assess, the correct output is
a `weak_signal` / explicit `information_needed[]` entry — **never** a fetched fact.

---

## 7. Reasoning-Engine Options (paper trade-offs)

- **(a) Deterministic heuristic** over evidence completeness + signal strength + suppression status. Fully
  reproducible, trivially testable, zero hallucination risk — but weak at the adversarial nuance that makes a judge
  worthwhile (it can't really articulate a novel `counter_signal`).
- **(b) Schema-constrained, grounded in-session LLM reasoning.** Richer supporting/counter signals and
  `information_needed`, consistent with the platform's API-free in-session posture — but carries hallucination
  risk, mitigated by: the forbidden-field schema (§5), the `evidence_refs` grounding rule (§6), and the
  no-new-evidence / no-retrieval constraints (§6).

**Recommendation:** structure the layer as **(b) gated by the discipline of (a)** — i.e. an in-session LLM judge
whose output is validated against a strict schema (forbidden fields absent, every signal carries `evidence_refs`,
flags present, confidence carried verbatim). The heuristic (a) survives as the fallback / cross-check and as the
deterministic test oracle. The LLM never gets to *widen* its inputs; it only gets to *reason over* the one bundle.

---

## 8. What It Feeds

A future research-track **PoC-feasibility layer** would consume `coherent_signal` assessments plus their
`information_needed[]` — the judge hands over an *assessment and a question list*, never a conclusion. The
`weak_signal` / `partial_signal` assessments are deprioritized (or returned for more evidence) before any expensive
PoC effort. As with every layer below it, the judge hands over **material and a question**, not a verdict.

---

## 9. Relationship to Production (restated)

Separate from the wired `judge_simulate.py`; un-wired; emits none of the production judge's verdict fields. The
research judge is an assistive, human-in-the-loop, research-only stage over evidence bundles. Connecting it to the
production pipeline is a future, explicit, human decision — this document neither does nor implies it. Nothing here
implies autonomous validity, severity, exploitability, or submission.

---

## 10. Open Questions (resolve before prototyping)

- **Ordinal wording.** Is `coherent_signal` / `partial_signal` / `weak_signal` sufficiently severity-neutral, or
  does even "coherent" leak a validity connotation? Consider alternatives that describe *evidence*, not *bug*.
- **Grounding for LLM counter-signals.** How strictly to bind a `counter_signal` to `evidence_refs` when the
  counter-argument is about an *absence* (e.g. "no authorization check is shown") — does "absence in `code_snippet`"
  count as a citation? Likely yes, but must be specified.
- **Evaluation method.** A judge that emits no ground-truth verdict can't be scored by answer-key recall. The
  natural evaluation is a **reviewer-agreement study** (does the judge's `plausibility_estimate` and its
  `counter_signals` agree with an expert's read of the same bundle?), not a HIT/MISS scorecard. This is itself a
  research design task.
- **Volume / cost.** Only `READY_FOR_REVIEW` bundles are judged, but at scale the LLM variant has a per-bundle
  cost; the deterministic pre-filter (a) may gate which bundles reach (b).

---

## Lifecycle & Next Steps

This is the **Research**-stage output for the future Judge Layer. Per `../architecture/research_methodology.md` the
remaining stages — Taxonomy (of judgeable evidence shapes), Ground-Truth (a reviewer-agreement corpus), Prototype,
Validation, Scope/Stability — are **deferred**. The next concrete step, if pursued, is resolving the §10 open
questions and drafting the output schema + a deterministic (a) prototype with the forbidden-field and grounding
tests, all research-only/un-wired.
