# P193 — Answer-key function-resolution repair: extraction-failure analysis

**Read-only**, deterministic, no model runs. Diagnoses *why* function extraction missed names already present in
answer-key artifacts, and quantifies the **measurement-accounting** change when extraction is repaired.
**A shrunk discovery bucket is a measurement improvement, NOT recall — recovered loci are not newly discovered bugs.**

## Decision: `EXTRACTION_PIPELINE_PRIMARY`
**75% of recovered loci were sitting verbatim in answer-key fields** (title/alt_titles/match_terms); the extraction
pipeline simply didn't pull them into the locus field. Most repairs are safely automatable. The remaining loss is
genuinely unresolvable, not an alias-map problem.

## Question A — why extraction failed (32 recovered discovery findings)
| failure bucket | n | present verbatim? |
|---|---|---|
| ALT_TITLE_MISSED | 10 | yes (`alt_titles`) |
| DIRECT_NAME_MISSED | 7 | yes (`title`) |
| MATCH_TERM_MISSED | 7 | yes (`match_terms`) |
| GET_SET_DRIFT | 5 | no (get/set/`_` prefix) |
| OTHER (non-prefix fuzzy) | 2 | no |
| NORMALIZATION_FAILURE | 1 | no (underscore/case) |

**24/32 = 75%** of the recovered function names were present **verbatim** in an answer-key field but were dropped;
the structured `affected_functions`/`functions` field instead captured noise. Concrete:
- zaros H-06 — extracted `['amount','marketId','solidity']`; the **title named `withdrawUsdTokenFromMarket`**.
- zaros M-01 — extracted only `['solidity']` (code-fence noise); title named `configureFeeRecipient`.
- panoptic M-16 — extracted `forceExercise`; manifest fn is `_forceExercise` (underscore drift = NORMALIZATION).

**Per-corpus concentration (critical caveat): 30 of 32 recoveries are zaros** (1 revert-lend, 1 panoptic) — zaros
is the only corpus with `alt_titles`/`match_terms` **and** had the largest discovery bucket (40 vs 8/5/5). So the
`ALT_TITLE_MISSED`/`MATCH_TERM_MISSED` modes are **zaros-specific**; for the other corpora the discovery bucket
was small and recovered via title (DIRECT) or normalization. Do not generalize the alias modes cross-corpus.

## Question B — measurement-accounting change (BEFORE vs AFTER; not recall)
- Discovery bucket **before = 59**; recovered to a real manifest function = **32 (54.2%)**; after = **27 (45.8%)**.
- The 32 redistribute into their true downstream stage (re-running P190 Stage B/C on the recovered locus):
  `REACHED_DEEP_PASS` 6 · `DEEP_PASS_GAP` 15 · `LOCUS_ROUTING_GAP` 5 · `LOCUS_ROUTING(none_routed)` 6. The 27
  unresolvable stay `DISCOVERY_GAP`.
- **This is accounting only:** the recovered findings move from "discovery loss" into the *routing/deep-pass*
  buckets that are the real (smaller) bottleneck — it does **not** claim those bugs would have been caught. Note
  15/32 land in `DEEP_PASS_GAP` largely because zaros ran no `deep` pass at all.

## Question C — automation safety
| safety | buckets | n |
|---|---|---|
| SAFE_AUTOMATION | DIRECT_NAME_MISSED, ALT_TITLE_MISSED, NORMALIZATION_FAILURE | **18 (56%)** |
| REVIEW_REQUIRED | MATCH_TERM_MISSED, GET_SET_DRIFT, OTHER | **14 (44%)** |
| UNSAFE | — | 0 |

SAFE = the function name is present verbatim AND matches an in-contract manifest function, or is a pure
deterministic normalization. REVIEW = `match_terms` can carry non-function tokens; get/set prefix mapping and
non-prefix fuzzy are ambiguous. No `MULTI_FUNCTION_AMBIGUITY` collisions were observed in this sample.

## The seven required answers
1. **Largest extraction-failure mode:** `ALT_TITLE_MISSED` (10) — but "name present verbatim in *some* answer-key
   field" (DIRECT+ALT+MATCH) dominates at **24/32**.
2. **% of recovered loci explicitly present verbatim:** **75%** (24/32).
3. **Discovery bucket shrink after deterministic repair:** **54.2%** (59 → 27).
4. **Safe to automate:** DIRECT_NAME_MISSED, ALT_TITLE_MISSED, NORMALIZATION_FAILURE = **18 (56%)**.
5. **Require human review:** MATCH_TERM_MISSED, GET_SET_DRIFT, OTHER = **14 (44%)**.
6. **% of discovery loss genuinely unresolved:** **45.8%** (27/59).
7. **Is P194 an extraction fix, an alias system, or source-inspection?** **An extraction fix, then source-
   inspection** — NOT an alias system (the names are already in fields; they just need to be extracted). P194 (a)
   repairs the locus extractor for the SAFE buckets (pull function-like tokens from title/alt_titles/match_terms
   that match an in-contract manifest function; normalize underscore/case), and (b) opens a **source-inspection
   sub-phase for the 27 unresolvable** to determine whether they are real coverage gaps. This is **eval-harness /
   measurement** work, not production routing.

## Honesty / limits
- **Measurement, not recall.** Recovered loci are not newly found bugs; "resolved" = the awarded function is
  *locatable* in artifacts. The AFTER buckets are the real, smaller bottleneck — no catch is claimed.
- **Heavily zaros (30/32).** The taxonomy's alias modes are a zaros artifact; the cross-corpus generality is
  limited. revert-lend/panoptic discovery buckets were small.
- Only ~few recoveries are high-confidence exact/normalization; the rest rely on verbatim-presence (strong) or
  fuzzy (candidate). Every recovery cites its exact artifact field. `fabrication_rate=0`.
