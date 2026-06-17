# P284 — VERDICT

## Verdict: **B — INVARIANT_DELTA_PROMISING_NEEDS_REFINEMENT**

## Core question
Can the pipeline derive source-backed invariant-delta evidence (sibling / registry / conservation / before-after /
oracle / state-machine) and lift some value/state candidates to READY without inventing references or reintroducing
false READYs? **Answer:** it derives a real, correct deviation (Blackhole M-04, sibling-recipient, HIGH) end-to-end with
0 FP, but lifts 0 — one because of an upstream D1 over-match, the rest because the corpus supplies no source-local
deviation reference. The approach is validated; the next blocker is localized.

## Why B (not A)
- **Newly lifted: 0.** A requires ≥2 newly lifted (or a clear source-backed supply reason). The supply reason is clear
  and source-backed (only 1 in-source deviation exists corpus-wide, and it is D1-blocked), but lift is 0 → B.
- The lift MECHANISM is proven correct (claim_many reached SIBLING_REFERENCE_FOUND/HIGH with core dims upgraded and a
  specific assertion; only D1 precedence — out of P284 scope — prevented READY).

## Why not C
- No unsupported/noisy READYs. 81/82 candidates fail-closed to NO_REFERENCE; the one FOUND is a real awarded shape. No
  invented corrected expressions; naming-only similarity never produced a FOUND. Severe concluded/reportable FP = 0.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| ≥2 newly lifted OR clear source-backed supply reason | supply reason ✔ (1 in-source deviation, D1-blocked); lifts 0 |
| no P281/P282/P283 false-READY regressions | ✔ (distribution identical) |
| L2Governor.execute stays READY / PASS_SUPPORTED | ✔ (PoC 2/2) |
| audit finds no invented core | ✔ |
| generic transfer/write doesn't create READY | ✔ (test + audit) |
| severe FP = 0 | ✔ |
| no production-authority leakage | ✔ (advisory stamps, reused detectors read-only) |
| tests green | ✔ |

## Net effect of P284
- **The corrected-reference / invariant-delta layer is built and validated:** it recovered a real awarded bug shape
  (M-04) from source alone via the reused 0-FP sibling classifier — the first time the assisted-mode chain has surfaced
  a *relationship-error* deviation rather than a lexical anomaly.
- **Precision preserved:** 81/82 fail-closed; 0 FP; reused detectors byte-identical.
- **Backlog sharpened + localized:** the headline next repair is D1 read-vs-guard granularity (unblocks the one HIGH
  deviation); then a share-math corrected-reference helper + cross-contract sibling pairing for breadth.

## Production authority
**WITHHELD.** Research-only, advisory, un-wired, default-off, fail-closed throughout; reused detectors imported read-only.

## Next (per plan)
P285: refine D1 inline-guard to distinguish ownership READ from access GUARD (unblocks claim_many; separate approval —
it changes P281–P283 outputs) → re-map → if a trustworthy READY set materializes, a small PoC sweep → fresh blind target.
