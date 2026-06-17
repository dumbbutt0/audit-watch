# P264 — LIMITATIONS
1. SHADOW authority only: the harness does NOT detect/confirm/submit findings. It prepares bounded ADVISORY recall
   candidates; all detection authority remains with the downstream manual B/C+5ops+refutation + human review.
2. No B/C/completion executed in-harness: completion_status/refutation_status are null in shadow output (those are
   LLM/operator stages). So advisory candidates are pre-ranking, pre-completion.
3. Recall vs precision: by design the sweep widens recall (incl T9 math); many advisory candidates will be benign —
   acceptable ONLY because they cannot promote themselves.
4. Caps can truncate: bounded output may drop a real locus; truncation is recorded but not recovered here.
5. Not wired into run_pipeline/dashboard (intentional). Operator must invoke manually.
6. "Production-grade" = engineering quality (modes/guards/metrics/repro/rollback/tests) — NOT validated production
   vulnerability detection. That requires P265 shadow operational trial across real audits.
7. Inherits P260/P262 limits (template precision, sibling-locus misses, training-confound on scored claims).
