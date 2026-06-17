# P251 — Part B: Implementation

All additive, research-only, **default-off**, un-wired. Mirrors the P249 accounting checkpoint file-for-file.
No severity/routing/dashboard/prompt edits; forbidden files byte-identical.

## Files
- `scripts/state_transition_checkpoint_taxonomy.py` — pure classifier (no I/O). `classify(...)` returns
  interrogative `STATE_TRANSITION_CHECKPOINT` records (one per matched family). Two-signal shape detection;
  never returns severity/confidence/verdict. Consts `QUESTIONS` (8) + `FAMILIES` (exactly 5).
- `scripts/state_transition_checkpoint_audit.py` — manifest-driven runner (`--manifest`/`--out`/`--no-source`/
  `--quiet`); brace-matched bodies + +1-level helper resolution; dedup per (contract,function,family); report
  flags `is_gate:false research_only:true routes_in_production:false emits_findings:false
  concludes_vulnerability:false output_type:"reasoning_records"` + a runtime **assert** that no record carries
  a conclusion (tripwire vs detector drift).
- `config/state_transition_checkpoint_patterns.json` — S1–S5 markers + the 8 questions. `checkpoint_only:true`.
- `config/agent_policy.json` — `"state_transition_checkpoint_enabled": false` (default-off; module un-wired).
- `tests/state_transition_checkpoint/test_state_transition_checkpoint.py` — 8 unit tests.

## Families (S1–S5) and two-signal shapes
| Family | Two-signal shape | Anchor |
|---|---|---|
| S1 reset/overwrite user-critical state | critical var (unlockTime/expir/status/balance/owner) + overwrite (`=`, on-behalf/recipient) | munchables H-01 (`lockOnBehalf`/`_lock`) |
| S2 growable set / unbounded loop | a loop (`for`/`while`) + a STORAGE-set op (`.values()`/`.add`/`.remove`/EnumerableSet/`_liveProposals`) | kleidi M-01 (`pause`) |
| S3 dual-state inconsistency | paired status/vote vocab (approv/disapprov/valid/invalid/frozen/paused) + a state write | munchables M-01 (`approveUSDPrice`) |
| S4 branch consequence not traced | a failure/shortfall branch (`balanceOf < amount`/`!success`/reserve/insufficient/catch) + a value-mutation | decent H-04 (`onOFTReceived`) |
| S5 time-window/expiry interaction | time var (expir/duration/window/timestamp) + an update/comparison (`newPeriod`/`+ duration`/`< expiry`) | kleidi M-03 (`updateExpirationPeriod`) |

## Tuning applied during build (bounded, regression-tested)
First-pass over-fired (munchables 91, kleidi 39 records) and **missed the kleidi M-01 S2 anchor** (growth is
in `schedule`, the loop in `pause` — within-function two-signal couldn't span them). Three narrow fixes:
- **S2:** require *loop + storage-set operation* (not grow+loop in one fn) → catches the consume-side loop
  (`pause` iterating `_liveProposals`) while a generic memory-array loop (no set-op) stays silent.
- **S3:** dropped over-common vocab (lock/unlock/enable/disable/active) → keep approve/disapprove/valid/
  invalid/frozen/paused.
- **S4:** dropped generic `} else` / `return;` / bare `=` → require a genuine failure/shortfall branch + a
  value-mutation.
Result: volumes dropped (munchables 91→46, kleidi 39→25, spectra 36→12) and all 5 anchors observed.

## Record fields
`state_family · state_variable · pre_state · triggering_action · post_state · repeated_action_effect ·
affected_actor · invariant_expected · invariant_after_transition · exploit_hypothesis` (empty until answered)
+ the 8 questions + `concluded:false`/`severity:null`. Shape-derived fields (state_variable, triggering_action,
invariant_expected) seed reasoning; the empty fields are filled only by answering the questions.
