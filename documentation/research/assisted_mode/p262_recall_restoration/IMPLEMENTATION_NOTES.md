# P262 — IMPLEMENTATION_NOTES
- Imports P260 helpers (prioritize/_route_templates/_mk_mechanism/_checkpoint_hits/CONFIG_PATH) from
  scripts/research/locus_shape_prioritizer.py — REUSE, not modify (hashes verified unchanged).
- Deterministic; no LLM; no answer key. Ranks swept loci by P260 score; clause-4/5 iterate ALL manifest fn items so
  pruned loci are rescued (the leak fix). T9 appended as trailing template, sorted last per-locus so subtle-
  accounting mechs are never displaced.
- Build iteration: initial backtest showed basin math loci still missed (clauses 1–4 don't match math names / they
  were pre-pruned) → added clause-5 (T9 math-name inclusion, bounded ≤8). No answer keys were used; this is module
  iteration against the frozen backtest, not tuning to a key.
- FP-guard is a hard runtime assert (_assert_no_conclusions) — the module raises rather than emit any conclusion.
