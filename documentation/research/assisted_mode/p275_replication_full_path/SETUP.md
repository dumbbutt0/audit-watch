# P275 — SETUP

## Isolation
- Source: `code-423n4/2024-10-ronin` cloned **source-only** to `/tmp/p275_fresh/ronin` (NEVER under `audits/`).
  Submodules fetched (`git submodule update --init --recursive --depth 1`): `katana-v3-contracts` @ `03c8017`,
  `katana-operation-contracts` @ `27f9d28`.
- Findings repo (`2024-10-ronin-findings`) **NOT cloned until Phase 10**.
- Active audit `size-credit-2024-06-blind` untouched; `output` symlink → `audits/size-credit-2024-06-blind/output`.

## Frozen-module baselines (must hold byte-identical pre/post)
| module / config | sha256[:16] |
|---|---|
| scripts/research/locus_shape_prioritizer.py (P260) | `d6b494bc3c0cc746` |
| scripts/research/recall_first_shape_sweep.py (P262) | `a48336275cb65a4f` |
| scripts/research/recall_first_harness.py (P264) | `85f9cbe662d2d991` |
| scripts/research/mechanism_pairwise_selector.py (P267) | `b0623b8c88752059` |
| scripts/research/impact_first_poc_triage.py (P269) | `63c88d02d2c7eefa` |
| scripts/research/award_class_coverage_router.py (P273) | `b87e3d22d1fb915b` |
| config/research_award_class_coverage_router.json | `3fbc476e3d8945b6` |
| config/research_impact_first_poc_triage.json | `7c174b5d1ae6b52f` |
| config/research_mechanism_pairwise_selector.json | `9dab060dca027c24` |
| P271 LENDING_COMPLETION_CHECKLIST.md | `2929a2154a88104e` |

## Forbidden-5 baselines (must hold)
dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9` ·
validate_p208 `ae55eb80`.

## Commands (Phase 1)
```
OUT=documentation/research/assisted_mode/p275_replication_full_path/outputs
python scripts/build_coverage_manifest.py --contract /tmp/p275_fresh/ronin --out $OUT/ronin_coverage_manifest.json
python scripts/accounting_checkpoint_audit.py       --manifest $OUT/ronin_coverage_manifest.json --out $OUT/ronin_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py --manifest $OUT/ronin_coverage_manifest.json --out $OUT/ronin_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $OUT/ronin_coverage_manifest.json \
   --accounting $OUT/ronin_accounting_checkpoint.json --state-transition $OUT/ronin_state_transition_checkpoint.json \
   --out-dir $OUT/ronin_shadow --mode shadow --quiet
```
No answer key, no API. Deterministic.
