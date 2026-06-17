# P139 — Tests & Commands

## Tests (`tests/mechanism_advisory/test_value_provenance_auto_advisory.py`) — 14 pass
config off / mode off / eval_only-needs-flag; H-03-class rec triggers pending job; no recommended_prompt no
trigger; mock excluded; trivial excluded; research-only excluded unless enabled; max_total cap; malformed/None
context no block; main() fail-open (build raises → no crash, error recorded); review_gate renders the VP
subsection; VP job NOT in Validated Findings; review_gate absent when no results; confirmed count unchanged
(capsys "Confirmed findings: 2"); pending_manual_execution + prompt_decision=pending (no faked decision).

## Commands
```
python -m pytest tests/mechanism_advisory/test_value_provenance_auto_advisory.py -q   # 14 passed
bash -n run_pipeline.sh                                                               # OK
python scripts/audit_manager.py switch noya-2024-04-eval
python scripts/surface_mechanism_advisories.py --quiet
python scripts/run_value_provenance_advisories.py        # 2 pending jobs (incl NoyaValueOracle._getValue)
python scripts/generate_review_gate.py                   # Confirmed findings: 0
python scripts/audit_manager.py switch quantamm-2024-12-eval   # restore
python scripts/assisted/rank_signal_probe.py --self-test       # OK
python -m pytest -q                                            # 1621 passed, 2 failed, 4 skipped
```
Full suite: 1621 passed / 2 pre-existing deep_solidity snapshot fails / 4 skipped (+14 vs P138's 1607).
