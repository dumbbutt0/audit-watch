# P276 — ROLLBACK_PLAN

Research-only / advisory / un-wired — nothing to roll back in production. To remove:
1. Delete `documentation/research/assisted_mode/p276_supervised_award_corpus_hardening/`,
   `scripts/research/p276_corpus_replay.py`, `scripts/research/p276_award_funnel_map.py`,
   `scripts/research/p276_metrics.py`, and `tests/research/test_p276_supervised_award_corpus_hardening.py`.
2. Verify frozen modules/configs + P271 checklist + 5 forbidden files byte-identical to the SETUP.md baselines (P276
   never edited them).
3. Verify `output` symlink → `audits/size-credit-2024-06-blind/output`.
4. No eval-audit source/award keys were mutated (read-only); the per-contest checkpoint files written are only under
   the P276 `outputs/` dir.

No config flags / routing / gate wiring added. No production authority granted. No award-key content was used to set
severity/reportability or to fabricate blind claims.
