# P290 — BASELINE_FREEZE

Full hashes in `outputs/hash_manifest.json`. Recorded BEFORE running discovery on salty.

## Target
`salty-2024-01-holdout` (Salty.IO) · source hash `e045163fa6cc1b93…` · H/M = 37 (6H/31M, content-light) · answer key
SEALED (no local findings; external report NOT opened pre-reveal).

## Frozen stack (post-P289; sha256-16, all present)
P260 · P262 · P264 · P267 · P273 router(`6debb753`)+config(`91f9deac`) · P269 · P278 queue+config · P279/P282/P283/P284
+ **P289** `completion_evidence_deriver`(`c41eaf9d`) + `invariant_delta_deriver`(`cf7de22e`) + config(`39d3cf44`) ·
P281/P285 `source_span_guard_extractor`(`cd472bd8`) + gate(`9a4e3834`) · P283 tracer(`f28f0620`) · p276_corpus_replay ·
reused detector platform · P271 checklist. **No module edited during the run** (re-verified at the end).

## Forbidden 5 (sha256-8): c1af70e1 · c095c426 · 2a15169a · afc481c9 · ae55eb80.
## Active audit: `output` → `audits/size-credit-2024-06-blind/output` (unchanged).

## Command plan (blind, award-free) — identical to P287/P288
1. `p276_corpus_replay.py --audit-id salty-2024-01-holdout --out-dir <run>`.
2. `expanded_validation_queue.py --replay-dir <run> --out-dir <run>`.
3. `completion_evidence_deriver.py --manifest audits/salty-2024-01-holdout/output/coverage_manifest.json --packages
   <run>/evidence_packages.json --out <run>/derived.json` (incl. P289 lenses).
4. `poc_readiness_evidence_gate.py --packages <run>/derived.json --out <run>/readiness.json`.
5. Freeze pre-reveal artifacts + hashes → PoC-intent/NO_READY → ≤3 PoCs → PRE_REVEAL_GATE → reveal.
