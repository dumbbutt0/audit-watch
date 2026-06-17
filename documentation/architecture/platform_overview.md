# Audit-Watch — Research Detector Platform Overview

> **Scope of this document:** the **research-only detector platform** that emerged from the detector experiments —
> a chain of small, single-purpose, **un-wired** stages. This is a *separate track* from the production audit
> pipeline (ICE, coverage gate, triage, exploitability/judge/PoC/submission engines), which is documented in
> `documentation/pipeline.md` and `documentation/architecture.md`. Nothing described here routes, submits, or
> influences production gating. See `current_platform_state.md` for the research-vs-production split.

## What Audit-Watch is (today)
Two things, kept deliberately separate:
1. **A production audit pipeline** (pre-existing, wired): `analyze → deep-analysis → Step-2 specialists →
   synthesis → ICE → gates → triage → exploitability/judge → PoC → submission`. Real, gated, human-in-the-loop.
2. **A research detector platform** (built incrementally, **research-only / un-wired**): a repeatable way to
   create high-precision detector families and compose their output, *without* touching production routing. This
   document covers (2).

## The research-track flow

```
Research Detectors            (built: multicall_invariant, permit_asset_binding)
        │   emit *_audit.json candidates (research_only, routes_in_production:false, routed_manifest_ids:[])
        ▼
Normalization Layer           (built: normalize_research_findings.py)
        │   one comparable record per candidate + transparent review_priority ("rank, don't relabel")
        ▼
Evidence Bundle Gate          (built: evidence_bundle_gate.py)
        │   assembles code+evidence; "evidence-complete enough to investigate?" ("assemble, don't adjudicate")
        ▼
Judge Layer                   (FUTURE — research-track; production already has judge_simulate.py separately)
        ▼
PoC Feasibility Layer         (FUTURE — research-track; production already has a PoC engine separately)
        ▼
Submission Readiness Layer    (FUTURE — research-track; production already has the submission/ engine separately)
```

The first three stages are **built and demonstrated end-to-end**; the last three are **not built** — they are
research-track continuations (see `roadmap.md`). The production pipeline already has analogous *wired* systems
(`model_exploitability.py`, `judge_simulate.py`, the PoC scripts, the `submission/` engine); the future
research-track layers are a separate, not-yet-existing path that would consume evidence bundles. Bridging the two
tracks is an explicit future decision, not a built capability.

---

## Layer 1 — Research Detectors  *(built)*
- **Purpose:** surface a *candidate surface* for one narrow vulnerability shape, optimizing precision over recall.
- **Inputs:** a workspace `coverage_manifest.json` (function inventory) + source (read-only).
- **Outputs:** `<lens>_audit.json` — candidates with `confidence`, `finding_shape`, evidence terms, `file_line_refs`,
  and the four research flags.
- **Guarantees:** deterministic; high-precision within a declared scope; emits `is_gate:false`,
  `research_only:true`, `routes_in_production:false`, `routed_manifest_ids:[]`.
- **Does NOT:** decide a bug exists · assign severity · prove exploitability · route · submit. (Invariant:
  *"signal, don't submit."*)

## Layer 2 — Normalization Layer  *(built)*
- **Purpose:** map every detector's candidates into ONE comparable record so families can be compared/ranked, and
  make new detectors plug-in via a registry.
- **Inputs:** one or more `<lens>_audit.json`.
- **Outputs:** `research_findings_normalized.json` — records with `detector`, `signal_type`, `confidence`
  (verbatim), `candidate_surface`, `declared_severity_potential` (a family hint), `review_priority` + `why_priority`,
  `candidate_id`/`source_audit_path` (traceability), `routing_allowed:false`.
- **Guarantees:** confidence copied verbatim; transparent deterministic ranking; refuses any source claiming to be
  production-routed.
- **Does NOT:** change a detector's confidence · compute a per-finding severity · decide bug/validity · route.
  (Invariant: *"rank, don't relabel."*)

## Layer 3 — Evidence Bundle Gate  *(built)*
- **Purpose:** for each normalized record, assemble its concrete evidence (code location + snippet + detector
  evidence + rationale) and answer ONLY *"is this evidence-complete enough for a human/judge to investigate?"*
- **Inputs:** `research_findings_normalized.json`.
- **Outputs:** `evidence_bundles.json` — bundles with `location`, `code_snippet`, `evidence_signals`, `rationale`,
  `evidence_completeness {status, present[], missing[]}`, `bundle_status` (READY_FOR_REVIEW / INSUFFICIENT_EVIDENCE),
  `investigate_recommendation` (a completeness recommendation), `routing_allowed:false`.
- **Guarantees:** presence-based completeness only; confidence & declared_severity_potential carried verbatim;
  refuses input whose `routing_allowed` ≠ false; emits no verdict fields.
- **Does NOT:** determine exploitability · determine severity · determine validity · determine bug status · route.
  (Invariant: *"assemble, don't adjudicate."*)

## Layer 4 — Judge Layer  *(FUTURE — research-track, not built)*
- **Intended purpose:** given a READY_FOR_REVIEW bundle, simulate adversarial review to estimate whether the
  evidence supports a plausible issue. **Not built.** Production has a separate wired `judge_simulate.py` operating
  on the production triage flow; the research-track judge would instead consume evidence bundles.
- **Would NOT:** auto-submit · assign final severity autonomously · bypass human review.

## Layer 5 — PoC Feasibility Layer  *(FUTURE — research-track, not built)*
- **Intended purpose:** estimate whether a bundle is PoC-able and what proof is missing. **Not built.** Production
  has a separate wired PoC engine (build_poc_queue / generate_poc_* / run_poc_tests / poc_validation_gate).
- **Would NOT:** run untrusted code without sandboxing · claim a proven exploit it did not run.

## Layer 6 — Submission Readiness Layer  *(FUTURE — research-track, not built)*
- **Intended purpose:** decide whether a research finding has cleared enough gates to warrant human submission
  review. **Not built.** Production already has the `submission/` engine (8 gates + renderers) which is the real
  submission-readiness system; it never auto-submits.
- **Would NOT:** submit autonomously · set severity autonomously.

---

## Cross-references
- Production pipeline: `documentation/pipeline.md`, `documentation/architecture.md`, `documentation/finding-lifecycle.md`.
- Invariants: `platform_invariants.md`. Detector inventory: `detector_registry.md`. Lifecycle:
  `research_methodology.md`. State split: `current_platform_state.md`. Roadmap: `roadmap.md`.
