# P214 — recommendation

## Decision: `DOS_CARVEOUT_DARK_WIRING_READY`

The P213 deterministic core-path DoS carve-out is implemented in the real L3 path behind the default-off
`AUDITWATCH_L3_READINESS` flag, fixing the P212 SOPH-03 under-rating with **0 new false-Highs** and full flag-off
equivalence.

## Evidence
- **Flag-off output-equivalent:** P208 backtest 10/10 unchanged; SOPH-03 `decide()` → medium with no carve-out keys;
  existing P210 tests 20+14 green.
- **Flag-on fix:** SOPH-03 → High (`dos_carveout_applied=true`) only with all 10 criteria; every criterion-missing
  variant blocked (×10); not-candidate / NEEDS_HARNESS / source-refuted / production-modified / human-judgment-without-
  notes / malformed all blocked; non-DoS theft High untouched.
- **Negative controls hold:** decent M-03 / vultisig M-03 / decent-06 stay < High; munchables DoS not auto-High;
  static-High-no-PoC blocked (P213 set still 10/10).
- **Integrity:** `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py`/ledger byte-identical START==END; only the 4
  intended files + SOPH-03 record + new test/p212 badge changed; no submit/route/promote; active audit unchanged.

## Why it's safe to keep (still default-off)
The carve-out cannot fire flag-off, cannot fire without an explicit candidate record carrying all 10 criteria + a
control case + executed harness, and never upgrades invalid/refuted/unexecuted. It is narrow by construction.

## Next (NOT this phase; human decision)
1. **Enable the flag on a real hunt** (operator sets `AUDITWATCH_L3_READINESS=1`; authors L3 records with the carve-out
   evidence + human sign-off on the 4 judgment criteria).
2. P212 **conversion-family sibling-parity lens** (the 002-M eETH near-miss) + a **recall sweep** — separate tracks.
The L3 standard now calibrates both over-rating (P199 origin) and the under-rating found live (P212), wired and tested.
