# P135 — Tests & Commands

## Tests (`tests/mechanism_advisory/test_surface_mechanism_advisories.py`) — 13 pass
Covers the 12 required behaviors: (1) CPA entry, (2) AC entry, (3) units report-only → submission_ready:false,
(4) STC research_only preserved, (5) master gate disables all, (6) research-only excluded unless gate on,
(7) dedup, (8) attach-to-candidate, (9) standalone entry advisory_only + requires_human_review, (10) no entry
confirmed/submission_ready/severity, (11) per-detector + total caps, (12) H-03 oracle/value loop →
deep_pass_value_provenance recommendation (no finding) + a negative (no loop → no rec).

## Commands
```
python -m pytest tests/mechanism_advisory/ -q                       # 13 passed
python scripts/audit_manager.py switch noya-2024-04-eval
python scripts/surface_mechanism_advisories.py                      # production default
python scripts/surface_mechanism_advisories.py --eval               # research-only + standalone queue
python scripts/audit_manager.py switch quantamm-2024-12-eval        # restore
python scripts/assisted/rank_signal_probe.py --self-test            # OK
python -m pytest -q                                                 # 1599 passed, 2 failed, 4 skipped
```

## Results
- Focused: **13 passed**.
- Full suite: **1599 passed, 2 failed, 4 skipped** — the 2 failures are the pre-existing `deep_solidity`
  frozen-snapshot tests (unchanged); +13 vs P134's 1586 are the new P135 tests. No new regressions.
- `rank_signal_probe --self-test`: OK.
- noya `human_review_queue.jsonl` restored to its P133 baseline (39) after the eval-mode append measurement.
- Active audit restored to `quantamm-2024-12-eval`.
