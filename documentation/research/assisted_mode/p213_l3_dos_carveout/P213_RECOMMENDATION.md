# P213 — recommendation

## Decision: `DOS_CARVEOUT_VALIDATED_RESEARCH_ONLY`

The deterministic core-path DoS carve-out fixes the P212 under-rating with **zero new false-Highs**, validated against
10 regression cases (rule written before testing; research-only; un-wired).

## Results (`validate_p213.py`, 10/10 pass)
- **SOPH-03: medium → High** (all 10 criteria; matches official 003-H). The under-rating is repaired.
- **0 new false-Highs.** Every validated negative control stays below High: decent M-03 / vultisig M-03 / decent-06
  (medium), decent-12 / generic-static / precision / **munchables-DoS** (needs_harness), source-refuted (invalid).
- **Over-HIGH guards proven:** munchables DoS does NOT auto-upgrade (no executed deterministic proof + no control);
  generic-dos-no-core-path stays Medium (criterion 2 fails); a source-refuted case is never upgraded even with all 10
  nominally true.

## Why it's narrow (won't reintroduce P199 over-HIGH)
Criterion 1 requires an EXECUTED deterministic harness; 2 requires a core entry/exit/conversion path; 4/8 exclude
optional/self-inflicted griefing; 6/10 exclude admin/privileged; 7 requires no workaround; 9 requires a control. A DoS
must clear all ten to reach High — "it reverts" alone is still Medium.

## Recommended next: **P214 — implement behind the existing `AUDITWATCH_L3_READINESS` flag** (after one consolidation)
1. Add the 10 carve-out fields to `L3_READINESS_SCHEMA.json` (additive).
2. Fold the carve-out into `decide()`'s severity branch (or a thin post-step), gated by the existing flag; re-run the
   P208 backtest + P210 tests + this P213 set to confirm no regression; keep default-off.
3. Pull carve-out fields from real L3 records (not fixtures); require human sign-off on the judgment criteria (4/7/8).
Also queue the P212 conversion-family sibling-parity lens (002-M near-miss) + a recall sweep — separate tracks.
**Do not wire in P213.**

## Guardrails honored
Research-only; `validate_p213.py` un-wired (grep-confirmed: no production reference); reads fixtures only; mutates no
artifacts; production prompt/gate/ledger + `validate_p208`/`dashboard` byte-identical START==END; api_free=true; JSON
valid; fabrication 0.
