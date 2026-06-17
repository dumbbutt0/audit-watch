# P182 — Top downstream failure modes (ranked)

Ranked by: misses affected · severity of misses · fixability · false-positive risk · implementation cost.
Read-only analysis; recommendations are not implemented in P182.

## 1. DEEP_RUN_BUT_WRONG_MECHANISM — mechanism selection within a deep-read surface  ← TOP STILL-OPEN
- **Misses affected:** 17 (9 function-level high-confidence + 8 contract-level coarse), incl. **High** H-03, H-07
  (+ contract-level H-04, H-05). The exact function was deep-read and a finding produced there, but the awarded
  mechanism was not the one reported (match note: *"no blind finding addressed this root cause"*).
- **Severity:** high — 2–4 Highs.
- **Fixability:** medium — a prompt/process change, no new detector.
- **FP risk:** low–medium (enumerating more mechanisms per surface can add candidates → triage cost, not false
  reportables).
- **Cost:** medium (deep-pass/specialist prompt + a mechanism-enumeration requirement).
- **Already covered by shipped gates?** No — this is downstream of routing; F1/math_estimator re-surface the
  surface but the deep-pass then reports a different bug.
- **Fix:** deep-pass / specialist **mechanism-enumeration + exploit-framing** (who-gains / who-loses /
  impact-direction; don't stop at the first bug on a hot function).

## 2. SURFACED_BUT_CLEARED — rule-math over-clearance  ← LARGELY ALREADY FIXED
- **Misses affected:** 13 (12 already-fixed by shipped gates incl. **High** H-08, H-09, H-10, H-11; 1 residual
  M-07).
- **Severity:** high (4 Highs) — but historical.
- **Fixability:** already shipped — P174 F1 re-surface + math_estimator proof-gate would now re-route these
  cleared sites to deep-pass; P177 made prose-only guarded-downstream advisory.
- **FP risk:** n/a (shipped, validated P174/P177/P180).
- **Cost:** ~0 (done). Residual M-07 (`quantAMMPack32Array`) = extend math_estimator to the pack helper (tiny).
- **Fix:** none for the class (verify the shipped gates on a fresh run); optionally extend math_estimator to
  `quantAMMPack32*` for M-07.

## 3. TRUE_DISCOVERY_GAP / NOT_SURFACED + UNMAPPABLE — minor, low-severity
- **Misses affected:** 6, **all Low** (L-07 oracle NOT_SURFACED; L-10/L-11/L-13/L-14 out-of-scope/hygiene;
  L-09 unmappable `rules/*`).
- **Severity:** low.
- **Fixability:** low value (oracle-robustness checklist = P175 F4, low yield) / answer-key mapping for L-09.
- **FP risk:** n/a. **Cost:** low.
- **Fix:** no new family warranted; improve answer-key `affected` mapping for the wildcard case.

## Bottom line
The recall loss is **downstream**, and it has two distinct parts: (a) the historical clear-policy class is
**already solved** by the shipped P174–P178 arc (12 findings), and (b) the genuine remaining lever is
**deep-pass mechanism selection / exploit framing** (17 findings, incl. Highs) — not a new selector, not more
clear-policy. Per the decision rule: *the top remaining loss is downstream triage → improve deep-pass /
specialist routing next.*
