# Evidence Bundle Gate

**Type:** read-only, research-only stage on top of the normalization layer. It answers exactly one narrow
question per candidate — **"is this evidence-complete enough for a human/judge to investigate?"** — a
**completeness** check, **not** "is this a bug," not severity, not exploitability. Continuity invariant:
**assemble, don't adjudicate** (the sibling of the normalization layer's *rank, don't relabel*).

**Files:** `schemas/evidence_bundle.schema.json` (draft-07) · `config/evidence_bundle_gate.json` ·
`scripts/evidence_bundle_gate.py` · `tests/evidence_bundle_gate/test_evidence_bundle.py` (10 tests). Demo output:
`documentation/research/_evidence_demo/evidence_bundles.json`.

---

## 1. Purpose
The pipeline is now `detectors → normalized findings → evidence bundles → (future) judge / PoC / submission gates`.
This stage takes each normalized record and **assembles its concrete evidence** (code location + snippet + the
detector's evidence terms + rationale), then reports whether that bundle has enough material to hand to a reviewer.
It deliberately makes **no** judgment about whether the candidate is a real vulnerability — that is the job of the
later (not-yet-built) judge/exploitability stages. This keeps every layer single-purpose and auditable.

## 2. Input / Output
- **Input:** the normalization-layer file `research_findings_normalized.json` (the *only* input — composable).
- **Output:** `evidence_bundles.json`: top-level `routing_allowed:false` + `source_normalized` + `bundles[]` +
  `summary` (counts by status/detector).

## 3. Evidence Bundle (per record)
Carried **verbatim** from the normalized record: `candidate_id`, `detector`, `detector_version`, `signal_type`,
`candidate_surface`, `confidence`, `declared_severity_potential`, `source_audit_path`. Assembled here:
`location` `{file, start_line, resolvable}` · `code_snippet` (a bounded, brace-aware source extraction, read-only;
`null` if unresolvable) · `evidence_signals` (the detector's evidence object) · `rationale` (the detector's
explanation: `missing_binding_explanation` / `reason` / `missing_context`) · `evidence_completeness`
`{status, present[], missing[]}` · `bundle_status` (READY_FOR_REVIEW | INSUFFICIENT_EVIDENCE) ·
`investigate_recommendation` (ready_for_review | needs_more_evidence) · `routing_allowed:false` ·
`research_only:true`.

## 4. Completeness Criteria (presence-based, NOT adjudication)
A bundle is COMPLETE / READY_FOR_REVIEW iff all `required_elements` (config) are present:
`location_resolvable` · `code_snippet` · `candidate_surface` (`Contract.function`) · `signal_type` · `confidence` ·
`evidence_payload` (non-empty detector evidence) · `rationale` (a human-readable explanation) · `traceability`
(`candidate_id` + `source_audit_path`). Any missing element → INSUFFICIENT_EVIDENCE + a `missing[]` list. These are
pure *presence* checks — they never ask whether the code is actually vulnerable.

## 5. The "Assemble, Don't Adjudicate" Invariant (enforced + tested)
- **No verdict fields.** The bundle never contains `is_bug` / `severity` / `exploitability_score` /
  `recommended_next_step` / `verdict` — only a *completeness* recommendation (`ready_for_review` /
  `needs_more_evidence`). Asserted in `test_no_verdict_fields`.
- **Confidence & declared_severity_potential carried verbatim** — never recomputed or changed
  (`test_verbatim_carry`).
- **`routing_allowed:false` / `research_only:true`** on every bundle and top level.
- **Defensive guard:** if the input normalized file's `routing_allowed` is not `false`, the gate **refuses**
  (`test_refuse_non_research_input`). It never consumes a routed source.
- **Read-only:** reads the normalized file + source snippets; never writes to a workspace; never calls the
  production exploitability/submission/gate engine.

## 6. Demonstration (real pipeline output)
Run over the normalization demo (`detectors → normalized → evidence bundles`), 6 records → 6 bundles, all
`routing_allowed:false`:

| candidate_surface | bundle_status | snippet lines | confidence | declared_sev |
|---|---|--:|---|---|
| V3Vault.liquidate | READY_FOR_REVIEW | 40 | high | high |
| V3Vault._deposit | READY_FOR_REVIEW | 40 | high | high |
| V3Vault._repay | READY_FOR_REVIEW | 39 | high | high |
| PanopticPool.multicall | READY_FOR_REVIEW | 25 | high | medium |
| SemiFungiblePositionManager.multicall | READY_FOR_REVIEW | 25 | high | medium |
| PanopticFactory.multicall | READY_FOR_REVIEW | 25 | high | medium |

All six assembled a real code snippet, full evidence payload, and rationale → evidence-complete. (A record with an
unresolvable `file_line_refs`, or an empty evidence payload, would instead be INSUFFICIENT_EVIDENCE with the exact
missing elements listed — see the unit tests.)

## 7. How it feeds the next layers
A READY_FOR_REVIEW bundle is the unit a future **judge** or **PoC-feasibility** stage would consume: it already has
the code, the surface, the detector's claim, and traceability — everything needed to *investigate* without
re-deriving anything. INSUFFICIENT_EVIDENCE bundles are filtered out *before* expensive review, with a precise
reason (e.g. "needs a resolvable snippet"). Crucially, the gate hands over *material*, never a conclusion.

## 8. Known Limitations
- Completeness ≠ correctness: a READY bundle only means "enough to look at," not "likely a bug."
- The snippet is a bounded brace-aware window from the candidate's start line; multi-file or deep cross-function
  evidence is not stitched (a later evidence-expansion stage could deepen this).
- It reflects the normalized record faithfully; it cannot add evidence the detector did not surface.
- Read-only and un-wired by design; feeding it into the live judge/PoC pipeline is a separate future decision.

## 9. Recommendation
**Adopt as the standard pre-review completeness gate; keep read-only / un-wired.** It cleanly extends the platform
(`detectors → normalized → evidence bundles`), preserves the discipline (no verdict, no relabeling, refuses routed
input), and gives the future judge/PoC stages a clean, evidence-complete unit to consume. This is the right next
layer — material assembly and completeness triage, not adjudication.

### Integrity
Frozen platform (both detectors + normalization layer: 9 files) **0 drift** (sha256); gate **un-wired** (no
references in routing/gate/run_pipeline/agent_policy/submission); **56 tests pass** (10 evidence + 10 normalization
+ 11 permit + 25 multicall). New files only; no detector, manifest, routing, gate, or answer-key change.
