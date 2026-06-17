# P288 — BASELINE_FREEZE

Full hashes in `outputs/hash_manifest.json`. Recorded BEFORE running discovery on ECG.

## Target
`ecg-2023-12-holdout` (Ethereum Credit Guild) · source hash `4473c29618dc18a6…` · H/M count 29 (4H/25M, content-light) ·
answer key SEALED (no local findings; external report NOT opened pre-reveal).

## Frozen stack — IDENTICAL to the P287 baseline (0 mismatches; re-verified file-by-file)
P260 · P262 · P264 · P267 · P273 (`6debb753`/`91f9deac`) · P269 · P278 queue+config · P279/P282/P283/P284
completion_evidence_deriver (`c41eaf9d…`) · P281/P285 source_span_guard_extractor (`cd472bd8…`) +
research_poc_readiness_gate.json · gate (`9a4e3834…`) · P283 tracer (`f28f0620…`)+config · P284 invariant_delta_deriver
(`dd549b9f…`)+config (`3eb86fcc…`) · p276_corpus_replay · reused detector platform · P271 checklist. **No module edited
during the run** (re-verified at the end).

## Forbidden 5 (sha256-8): c1af70e1 · c095c426 · 2a15169a · afc481c9 · ae55eb80.
## Active audit: `output` → `audits/size-credit-2024-06-blind/output` (unchanged).

## Command plan (blind, award-free) — identical to P287
1. `p276_corpus_replay.py --audit-id ecg-2023-12-holdout --out-dir <run>`.
2. `expanded_validation_queue.py --replay-dir <run> --out-dir <run>`.
3. `completion_evidence_deriver.py --manifest audits/ecg-2023-12-holdout/output/coverage_manifest.json --packages
   <run>/evidence_packages.json --out <run>/derived.json`.
4. `poc_readiness_evidence_gate.py --packages <run>/derived.json --out <run>/readiness.json`.
5. Freeze pre-reveal artifacts + hashes → PoC-intent → ≤3 PoCs → PRE_REVEAL_GATE → reveal.
