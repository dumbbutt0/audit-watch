# P276 — LIMITATIONS

- **Upstream-only, corpus-wide; completion/PoC sampled, not run per-award.** chain_completed/poc_supported/exact are
  `NOT_SAMPLED` corpus-wide (the expensive tail). The exact-recovery existence proof is the blind P274 run (2 EXACT);
  P276 maps where awards fall out *before* that tail.
- **Auto-built coverage/triage inputs are heuristic.** Pass A derives P273 class signals from locus name tokens (+
  mechanism-summary tokens) and P269 impact dims from a fixed class→impact map. The frozen modules are byte-identical,
  but their *inputs* are coarser than the hand-authored inputs in P274/P275. This can under-route (a contributing cause
  of the COVERAGE_CLASS_GAP count) — R1 proposes the body-signal fix.
- **Class inference for the breakdown is keyword-based** (P273 taxonomy on title+root_cause); `UNKNOWN_OTHER` (36) is
  the residue where the taxonomy can't infer a class from the title — an undercount of true class coverage, not
  necessarily a pipeline miss.
- **Award-key heterogeneity.** 7 corpora have locus-level keys; 2 are title-only (no affected contract/function → not
  funnel-mappable, recorded as ambiguity); 3 have md/none keys (excluded). The mapped denominator is 144 of 249
  machine-readable awarded H/M.
- **Locus matching is name-based** (contract/function string match with a contract-only fallback) — can both miss
  (renamed/inherited loci → some MANIFEST_GAP/RECALL_GAP) and over-credit (contract-only fallback). Conservative where
  ambiguous.
- **Supervised, not blind.** All numbers are calibration/eval; they measure *where the funnel leaks*, not
  generalization. Generalization is measured only by blind runs (P274/P275/next).
