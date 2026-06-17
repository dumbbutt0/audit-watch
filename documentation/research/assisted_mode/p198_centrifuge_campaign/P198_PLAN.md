# P198 — plan (frozen)

First post-measurement, non-tooling generalization campaign: test the validated P183–P188 adjudication stack on
`centrifuge-2023-09-holdout` (RWA tranches/epochs/escrow), blind, then score after freeze.

Sequence (executed): 1 integrity precheck → 2 controlled MINIMAL unseal (count-only) → 3 viability decision →
4 read-only source-grounded coverage manifest (blind) → 5 bounded 12-surface blind Sonnet run on `deep_trace.md` +
verbatim source (firewall-sealed, token-scanned) → 6 score vs awarded key (full `report.md`, post-freeze) →
7 failure modes → 8 decision.

Guardrails: campaign/evaluation only; no routing/ranking/selection/execution/detector/prompt/script optimization;
`deep_trace.md` + checker used read-only; no mid-run patching; answer-key access controlled & documented; blind
firewall (frozen prompts, verbatim outputs, scorer answer-aware only post-freeze, no backfill); integrity recorded
start & end; `fabrication_rate=0`. Blind model = Sonnet.

Decision space: GENERALIZES · PARTIAL_GENERALIZATION · ARCHITECTURE_SPECIFIC_FAILURE ·
CORPUS_TOO_THIN_FALLBACK_REQUIRED · INVALID_RUN. **Outcome: `PARTIAL_GENERALIZATION`** (see P198_RECOMMENDATION.md).
