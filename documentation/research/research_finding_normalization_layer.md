# Research Finding Normalization Layer

**Type:** read-only, research-only infrastructure (the "missing middle layer" between detectors and any future
evidence/judge/PoC/submission gates). It does **not** route, does **not** auto-assign per-finding severity, and is
**not** wired into the production exploitability / submission / gate engine. Every normalized record carries
`routing_allowed:false` + `research_only:true`, and the layer **refuses** any source that claims to be
production-routed.

**Files:** `schemas/research_finding_normalized.schema.json` (draft-07) · `config/research_finding_normalization.json`
(per-detector registry) · `scripts/normalize_research_findings.py` (read-only aggregator) ·
`tests/research_normalization/test_normalize.py` (10 tests). Demo output:
`documentation/research/_normalization_demo/research_findings_normalized.json`.

---

## 1. Purpose
Two detectors are RESEARCH-STABLE (`multicall_invariant`, `permit_asset_binding`) but emit similar-yet-different
JSON, so there was no standard way to *compare* confidence / declared severity-potential / signal-quality /
review-priority across families, nor a clean way to add a third detector. This layer maps every detector's
`*_audit.json` candidates into **one comparable record** with a transparent ranking, so detectors compose and
future detectors plug in with a single registry entry. It is the layer the architecture needs *before* a router or
judge:

```
detectors → normalized research findings → (later) evidence / judge / PoC / submission gates
```

## 2. Normalized Schema (per record)
`detector` · `detector_version` · `schema_version` (per record, for painless migrations) · `candidate_id` +
`source_audit_path` (stable traceability back to the origin candidate/file) · `signal_type` · `finding_shape` ·
`confidence` (copied **verbatim**) · `candidate_surface` (`Contract.function`) · `file_line_refs` · `evidence`
(detector-specific terms lifted via the registry) · `declared_severity_potential` (a **family-level capability
hint**, explicitly named so it can never be mistaken for a computed per-finding severity) · `review_priority`
(0–1) · `why_priority` `{confidence_weight, severity_weight, suppression_penalty}` · `suppression_status` ·
`routing_allowed` (**const false**) · `research_only` (**const true**). Top level: `schema_version`,
`generated_at`, `routing_allowed:false`, `sources[]` (accepted/refused + reason), `records[]`, `summary`.

## 3. Registry & Extensibility (how detector #3 plugs in)
`config/research_finding_normalization.json` holds one entry per detector:
```json
"permit_asset_binding": {
  "detector_version": "v1",
  "signal_type": "asset_binding_missing",
  "declared_severity_potential": "high",
  "surface_fields": ["contract", "function"],
  "evidence_fields": ["permit_source", "expected_asset_source", "missing_binding_explanation"]
}
```
**Adding a future detector = add one entry here** (signal_type + declared_severity_potential hint + which candidate
keys to lift into `evidence`). No code change to the normalizer. An unregistered lens still normalizes via
`unknown_detector_fallback` (signal_type `unclassified_research_signal`, `declared_severity_potential: info`) — no
crash, low priority.

## 4. Review-Priority Formula (explainable, deterministic)
`review_priority = clamp01( confidence_weight × severity_weight − suppression_penalty )`, with the weights from the
registry (`confidence_weights`: high 1.0 / medium 0.6 / low 0.3 / needs_context 0.2; `severity_weights`: high 1.0 /
medium 0.7 / low 0.4 / info 0.2; `suppression_penalty` 0.5 when suppressed). The exact factors used are echoed into
each record's `why_priority`. No ML, no black box — fully reproducible. **It ranks; it never relabels.**

## 5. Safety Constraints (enforced + tested)
- **Confidence is never changed.** The normalizer copies the detector's `confidence` verbatim and may only *rank*
  (review_priority). Asserted across all confidence levels (`test_confidence_never_changed`).
- **`routing_allowed:false` / `research_only:true`** on every record and at top level (forced in code).
- **Routed sources refused.** A source with `routes_in_production:true` or non-empty `routed_manifest_ids` is
  rejected with a logged reason and contributes 0 records (`test_routed_source_refused`) — the layer never launders
  a routed source.
- **No per-finding severity automation** — only the family-level `declared_severity_potential` hint.
- **No production wiring** — reads detector outputs and writes one file; never calls
  `model_exploitability` / `submission/` / gates / routing (verified: no references in those modules).

## 6. Demonstration (both detectors, real outputs)
Normalizing the permit run (Revert Lend validation) + the multicall run (Panoptic B1): **2/2 sources accepted, 6
records, both families comparable**, all `routing_allowed:false`:

| detector | candidate_surface | confidence | declared_sev | review_priority |
|---|---|---|---|---|
| permit_asset_binding | V3Vault.liquidate | high | high | **1.000** |
| permit_asset_binding | V3Vault._deposit | high | high | **1.000** |
| permit_asset_binding | V3Vault._repay | high | high | **1.000** |
| multicall_invariant | PanopticPool.multicall | high | medium | 0.700 |
| multicall_invariant | SemiFungiblePositionManager.multicall | high | medium | 0.700 |
| multicall_invariant | PanopticFactory.multicall | high | medium | 0.700 |

The two equally-confident families are now *comparable*: the permit asset-mismatch family (declared High potential =
fund loss) ranks above the multicall executor family (declared Medium = opportunity) — without altering either
detector's own confidence.

## 7. Known Limitations
- `declared_severity_potential` is a coarse, family-level constant — intentionally not a per-finding severity (that
  is a downstream, context-dependent judgment for the exploitability/severity stages, out of scope here).
- `review_priority` is a deliberately simple linear function; it orders for human review, it is not an
  exploitability or severity verdict.
- The layer reflects detector output faithfully — it cannot improve a detector's recall or precision, only present
  it comparably.
- It is read-only and un-wired by design; promoting it into the live pipeline (feeding the evidence/judge/PoC
  gates) is a separate, future decision.

## 8. Recommendation
**Adopt as the standard research-finding interface; keep read-only / un-wired.** It cleanly composes the two
RESEARCH-STABLE detectors, preserves the precision discipline (never relabels confidence, refuses routed sources,
no auto-severity), and makes detector #3 a one-entry registry change. This is the right next layer — not a router
or judge yet, but the normalized substrate they will eventually consume.

### Integrity
Frozen `multicall_invariant` + `permit_asset_binding` detectors/patterns **0 drift** (sha256); layer **un-wired**
(no references in routing/gate/run_pipeline/agent_policy/submission); **46 tests pass** (10 normalization + 11
permit + 25 multicall). New files only; no detector, manifest, routing, gate, or answer-key change.
