# P262 — One-Shot Recall Restoration — SETUP
Research-only, default-off, un-wired recall-expansion wrapper (scripts/research/recall_first_shape_sweep.py) that
moves SHAPE DISCOVERY BEFORE narrow manual selection — the one-shot fix for the P259 early-locus-pruning leak.
Reuses (does not modify) the P260 prioritizer. Backtest on FROZEN P254–P261 artifacts only (no new keys). NOT a
scaffold; no severity/routing/dashboard/schema/submission changes.

## Files
- scripts/research/recall_first_shape_sweep.py · config/research_recall_first_shape_sweep.json
- prompts/research/recall_first_shape_sweep.md · tests/research/test_p262_recall_restoration.py
- documentation/research/assisted_mode/p262_recall_restoration/{this dir} + outputs/*.json + sample .md

## Invariants
Advisory-only: every candidate RECALL_CANDIDATE_ONLY + needs[NEEDS_RANKING/COMPLETION/REFUTATION]; output flags
is_gate:false/research_only:true/routes_in_production:false/emits_findings:false/concludes_vulnerability:false;
runtime-assert no severity/concluded/vulnerability/reportable/submission_ready. Bounded (≤25 loci, ≤5 mech/locus,
≤30 mech total). Active audit unchanged; P260 module + forbidden files byte-identical.
