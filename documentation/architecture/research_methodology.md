# Audit-Watch — Research Detector Development Methodology

The official, repeatable lifecycle for creating a high-precision detector family **without blowing up noise**. Both
`multicall_invariant` and `permit_asset_binding` went through every stage; this codifies it. Every stage is
research-only and produces a written artifact under `documentation/research/` or `documentation/evals/`.

```
Research → Taxonomy → Ground-Truth Corpus → Prototype → Validation → Scope Classification → Stability Classification
```

Guiding principle (whole lifecycle): **high precision over recall** — false negatives are acceptable; high-confidence
false positives are not. Never optimize for historical HITs or answer-key matching.

---

## 1. Research
- **Inputs:** an observed gap/blind spot (often from a prior eval), public vulnerability corpus (KB / Solodit /
  Code4rena / Sherlock / Immunefi), the existing lenses.
- **Outputs:** a research doc stating the candidate family, the core question, and the precision tension.
- **Exit criteria:** the family is articulated as a *narrow shape* with a plausible two/three-signal definition.
- **Required validation:** none yet (analysis).
- **Failure modes:** scope too broad (a "permit detector"); the bug is an *absence* check with no anchor (precision
  trap) → either narrow further or stop.

## 2. Taxonomy
- **Inputs:** the research doc + corpus.
- **Outputs:** a root-cause taxonomy (categories, frequency, severity, common code patterns), explicit IN/OUT scope,
  and candidate detection signals each with expected coverage / precision / FP-risk.
- **Exit criteria:** a single highest-precision sub-shape is identified; out-of-scope classes named.
- **Required validation:** category frequencies grounded in real findings (no fabrication; verification-tagged).
- **Failure modes:** the high-value sub-shape is rare/contextual (document as accepted FN); overlap with an existing
  lens (defer to it, don't duplicate).

## 3. Ground-Truth Corpus
- **Inputs:** the taxonomy.
- **Outputs:** a frozen dataset of verified findings (protocol · source URL · finding ID · severity · permit/shape
  type · root cause), with at least one **runnable in-repo anchor**.
- **Exit criteria:** ≥1 verified anchor the detector must recover + a set of negatives/controls.
- **Required validation:** every row tagged `in-repo` / `web-confirmed` / `kb`; unverifiable rows excluded or marked.
- **Failure modes:** no runnable anchor (recall unmeasurable) → acquire/stage one or downgrade ambitions.

## 4. Prototype
- **Inputs:** corpus + taxonomy.
- **Outputs:** `<lens>_taxonomy.py` (pure classifier) + `<lens>_audit.py` (manifest-driven runner) +
  `config/<lens>_patterns.json` + `tests/<lens>/`. Research-only flags; un-wired.
- **Exit criteria:** the anchor fires at high confidence; a focused negative set stays quiet; 0 high-confidence FP;
  reviewable volume.
- **Required validation:** unit tests for every signal + suppression; a read-only anchor-recovery test.
- **Failure modes:** anchor missed (capability gap → redesign); volume explosion / router domination (tighten the
  two/three-signal gate + suppressions — *not* the threshold to chase recall).

## 5. Validation (campaign)
- **Inputs:** the unchanged prototype.
- **Outputs:** a 15–20 target validation run (positive anchors + permit/router/vault stressors + controls), a
  scorecard.jsonl, per-target notes, and a validation report.
- **Exit criteria:** anchor still detected; **0 high-confidence false positives**; candidate volume reviewable;
  scope explainable; every quiet result a *correct* TN (no hidden miss).
- **Required validation:** detector run **unchanged** (sha256 0-drift); integrity verified; FP review + miss review
  documented; no auto-suppression mid-campaign.
- **Failure modes:** routers dominate / noise / precision deterioration → PROMISING-BUT-NEEDS-REFINEMENT (name where
  precision breaks); do not patch to force a pass.

## 6. Scope Classification
- **Outputs:** a one-line scope statement (what it detects, what it does not) + one of: NARROW SCOPE CONFIRMED /
  HIGH PRECISION VALIDATED / PARTIALLY-{visibility|taxonomy|implementation} / PRECISION TOO LOW.
- **Exit criteria:** the scope statement is evidence-only (no aspiration) and matches observed behavior.

## 7. Stability Classification
- **Outputs:** one of: **RESEARCH-STABLE** (precision validated across a diverse corpus, un-wired) ·
  PROMISING-BUT-NEEDS-REFINEMENT · PRECISION TOO LOW · NOT A DETECTOR FAMILY. Plus a registry entry
  (`detector_registry.md`) and a normalization-registry entry so it composes.
- **Exit criteria:** RESEARCH-STABLE requires: anchor recovered + 0 high-confidence FP on the validation corpus +
  reviewable volume + 0-drift integrity + research-only/un-wired.
- **Promotion note:** RESEARCH-STABLE ≠ production. Routing/promotion is a **separate, later, human decision** and
  out of scope of this lifecycle; nothing here authorizes wiring a detector into production.

---

## Artifacts every detector leaves behind
research doc · taxonomy + config · ground-truth corpus (frozen) · prototype (`taxonomy`/`audit`/`patterns`/tests) ·
validation report + scorecard + per-target notes · integrity review · registry entries. This trail is what lets a
new contributor trust the precision claim and reproduce it.
