# P138 — Grading (blind decisions vs labels)

Grades assigned by me (informed) on the genuinely-blind subagent outputs.

## Per-item
| id | arch | label | blind decision | grade | aided? |
|---|---|---|---|---|---|
| B1 | noya | buggy (H-03 loop var) | finding | **PROMPT_HIT** | no (self-contained) |
| B2 | noya | buggy (H-19 debt sign) | finding | **PROMPT_HIT** | mild (factual primitive note) |
| B3 | noya | buggy (H-13 ÷weight) | strong_clear | **PROMPT_MISS** | n/a (subtle; answer key itself predicts MISS) |
| B4 | size | buggy (M-02 wrong-basis) | needs_human | **PROMPT_PARTIAL** | no (found exact divergence; didn't confirm impact) |
| B5 | blackhole | buggy (M-04 wrong recipient) | finding | **PROMPT_HIT** | yes (AVM ownerOf-vs-getOriginalOwner context supplied) |
| C1 | blackhole | clean (HIGH) | strong_clear | correct clear | — |
| C2 | noya | clean (MEDIUM) | strong_clear | correct clear | — |
| C3 | blackhole | clean (MEDIUM) | strong_clear | correct clear | — |
| C4 | noya | clean (MEDIUM) | strong_clear | correct clear | — |
| C5 | size | clean (MEDIUM) | strong_clear | correct clear | — |

## Rates
- **Useful recall** (HIT+PARTIAL / buggy) = **4/5 = 80%** (B1,B2,B4,B5); MISS = B3.
- **Strict recall** (HIT / buggy) = **3/5 = 60%** (B1,B2,B5).
- **Unaided strict recall** (excluding the AVM-aided B5; B2 only mildly aided) = 2–3/5.
- **Finding precision** (real-buggy findings / all findings) = **3/3 = 100%** (B1,B2,B5; zero false findings).
- **strict_clean_fp_rate** = flagged cleans / all cleans = **0/5 = 0%**.
- **high_confidence_clean_fp_rate** = **0/1 = 0%** (C1).
- **needs_human on cleans** = 0 (no clean needed the softening rule).
- **needs_human overall** = 1 (B4, a real bug → correct uncertainty).

## Notes (honesty)
- B3 is an honest recall MISS: the blind agent produced mathematically sound weighted-pool reasoning and cleared;
  H-13 is the subtle "÷weight twice" case the noya answer key itself flagged as MISS-expected.
- B5 (and to a lesser extent B2) required factual domain CONTEXT in the bundle (AVM ownerOf semantics; Morpho
  share→asset primitives). This is legitimate bundle context (deep_pass_prepare supplies callees/interfaces), not
  an answer-key hint — but the recall on B5 should be read as "with adequate context," not pure-source.
- The headline safety signal for advisory routing is **0 false positives across all 5 cleans (incl. the HIGH-
  confidence clean)** — the prompt is specific, not noisy.
