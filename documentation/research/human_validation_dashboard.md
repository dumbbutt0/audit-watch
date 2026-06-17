# Human Validation Console

A research-only surface in the dashboard for **human labeling of frozen evidence-bundle corpora**. It is the
operational tool for Week-2 of `../architecture/strategic_review_2026-06.md` (blind, human-authored coherence /
effort labels over the judge corpus).

> **Core invariant: human validation, not routing.** Nothing here decides a bug, severity, exploitability,
> submission, or routing action. It records a human's read of whether assembled evidence is *coherent and worth
> investigating* — the answer-key-free signal the future judge will be evaluated against
> (`research_judge_evaluation_methodology.md`). It is **not** a bug-submission tool.

## Purpose
Sits at the human-validation step of the research track:
```
detectors → normalized findings → evidence bundles → frozen judge corpus → [HUMAN VALIDATION] → future judge eval
```
It lets a reviewer browse frozen READY_FOR_REVIEW bundles, inspect detector metadata / code / carried confidence,
and attach labels — saved to a **separate** append-only file without ever modifying the corpus.

## How to run
```bash
python scripts/dashboard.py        # FastAPI on http://localhost:8765
# open http://localhost:8765/validation
```
It is a standalone page, fully isolated from the production pipeline dashboard at `/` (which renders
severity/exploitability/judge/submit — none of that is reused here).

## Input corpus
- Default: `documentation/evals/judge_corpus/frozen_corpus.json` (the Week-1 frozen corpus, 13 READY bundles).
- Also loads any `evidence_bundles.json` (same bundle schema) or future frozen corpus files via
  `?path=<repo-relative>`. Paths are confined to the repo.

## Output (labels)
- Real labels → `documentation/evals/judge_corpus/human_labels.jsonl`
- Demo labels → `documentation/evals/judge_corpus/human_labels.demo.jsonl` (toggle "demo labels file" in the header)
- **Append-only.** Saving never rewrites or deletes prior rows; the "current" label for a candidate is the newest
  row by timestamp (an explicit re-save appends a superseding row, so history is preserved).

## Label schema (`label_schema_version: hv-1`)
Each JSONL row contains **exactly** these keys (enforced by an allowlist in `scripts/human_validation.py`):

`label_schema_version, timestamp, reviewer_alias, candidate_id, source_corpus_hash, detector, candidate_surface,
coherence, investigation_worthiness, poc_followup_worthiness, expected_review_effort, missing_information,
counter_signals, reviewer_notes, reviewer_confidence, routing_allowed:false, research_only:true`

## Allowed labels
| Field | Values |
|---|---|
| coherence | `coherent` / `partially_coherent` / `weak` / `incoherent` |
| investigation_worthiness | `investigate` / `maybe` / `skip` |
| poc_followup_worthiness | `yes` / `maybe` / `no` (worth *considering* a PoC later — **not** a verdict) |
| expected_review_effort | `low` / `medium` / `high` |
| reviewer_confidence | `high` / `medium` / `low` |
| missing_information | free text or list |
| counter_signals | free text or list (reasons it may be benign / weak / FP) |
| reviewer_notes | free text |

## Forbidden labels (never requested, never emitted)
`is_bug`, `valid`/`validity`, `severity`, `exploitability_score`, `submit`, `reject`, `bounty`/`bounty_worthy`,
`verdict`/`final_verdict`, `predicted_outcome`, and any routing field. The row builder copies only allowlisted
keys, and `assert_no_forbidden_fields()` rejects any row carrying them (tested).

## Workflow
1. Open `/validation`; the corpus loads and its hash is shown.
2. Pick an unlabeled bundle (queue is filterable by detector / confidence / declared_severity_potential /
   bundle_status / candidate_surface / workspace / label status; "Next unlabeled →" jumps).
3. Review the detail view (code snippet, evidence_signals, rationale, present/missing evidence, carried confidence).
4. Fill the label form (allowed fields only).
5. Save — appends one row; "Save → next" advances to the next unlabeled bundle.
6. Progress panel shows labeled/unlabeled/percent + distributions by coherence / investigation_worthiness /
   poc_followup_worthiness. Export downloads the JSONL.

## Safety constraints
- **Corpus is read-only.** The frozen corpus is never modified; only the labels JSONL is written.
- Every label is `routing_allowed:false` / `research_only:true`.
- **Corpus-hash binding:** each label records `source_corpus_hash`; the UI shows the live hash and a drift banner,
  and the API refuses (HTTP 409) a label stamped against a different corpus unless drift is explicitly allowed.
- No production engine is touched (no detector / normalization / evidence gate / gate / manifest / answer key /
  submission / exploitability change). The dashboard change is additive routes + a standalone page only.

## Known limitations
- Small corpus (13 bundles) — reflects the two narrow RESEARCH-STABLE detectors; enough for a Week-2 pilot, not a
  high-powered agreement statistic.
- Append-only history is by timestamp; there is no row-deletion UI (by design — never silently overwrite).
- Single local reviewer at a time; multi-reviewer agreement is computed offline from the JSONL.
- Un-wired: labels feed the (not-yet-built) judge evaluation only; nothing here routes to production.

## Tests
`tests/human_validation/test_human_validation.py` (pure functions): corpus loading (frozen + evidence shapes; 13
bundles), corpus-hash stability/sensitivity, label-row construction + enum validation, forbidden-field rejection,
flag preservation, append-only history + progress + drift.

## Related read-only surfaces
- `/candidates` — candidate-validation detail view (`../architecture/dashboard_candidate_detail_implementation_notes.md`).
- `/funnel` — **Blind-to-Reproducible Funnel** (`../architecture/blind_to_reproducible_funnel.md`): tracks a finding
  from surfaced lead → blind conversion → severity gate → PoC handoff → reproduced → submission readiness, reject-first
  (REPRODUCED ≠ submitted). Seeded with the Vultisig 2024-06 / H-01 P82 milestone.
