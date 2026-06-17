# P194 — Answer-key function-extraction repair + residual source audit

Implements the **safe** extraction repair as a shared tested eval-harness module and source-audits the residual.
**Eval-harness / measurement infrastructure only — no production routing/detector/prompt/answer-key/corpus
change.** A shrunk discovery bucket is a **measurement** improvement, **not recall** — recovered loci are **not**
newly discovered bugs.

## Decision: `EXTRACTION_FIX_SUFFICIENT` (with an explicit residual caveat)
The deterministic safe repair recovers 42.4% of the discovery bucket, and **0 of the 27 residual findings are
artifact-confirmable production coverage gaps** (every "candidate" was a contract name / event / state-variable,
verified against source). The discovery bottleneck is confirmed to be **measurement / answer-key-locus quality,
not production coverage.** Residual that is not auto-recoverable is answer-key-quality (22) + a small
human-mapping set (5) — not production work.

## What was built (Part A+B)
`scripts/eval_locus_resolver.py` — `resolve_locus(finding, manifest_index, match_terms=None)` →
`{status, function, manifest_id, tier, field_cited, evidence, candidates}`, `status ∈ {RESOLVED, AMBIGUOUS,
REVIEW_GATED, UNRESOLVED}`. **Auto-resolves SAFE tiers only** (DIRECT_NAME / ALT_TITLE / NORMALIZATION /
MATCH_TERM-verbatim). **Guardrails:** must exist in `coverage_manifest` (`kind=function`); contract-constrained
(never cross-contract auto); generic/Solidity/math-noise rejected; **cites the exact answer-key field**; multiple
in-contract matches → `AMBIGUOUS` (no auto-select); get/set/update drift + any broad fuzzy → `REVIEW_GATED` (never
auto). Tested by `tests/eval/test_eval_locus_resolver.py` (9 cases, all green): direct/alt_title/normalization
extraction, generic-token rejection, ambiguous multi-match rejection, contract-constrained, no-fuzzy-auto,
match-term-verbatim. **Un-wired from production** (imported by nothing in `run_pipeline.sh`/`agents/`/`prompts/`).

## Before/after (Part C — measurement-accounting, not recall)
| | count |
|---|---|
| discovery bucket BEFORE | 59 |
| **safely recovered (auto)** | **25 (42.4%)** |
| review-gated (get/set/fuzzy) | 4 |
| ambiguous (multi-match, not auto) | 1 |
| unresolved after safe repair | 29 |
| discovery bucket AFTER (safe) | 34 |

Redistribution of the 25 recovered into their true downstream stage (re-run P190 Stage B/C): REACHED_DEEP_PASS 3
· DEEP_PASS_GAP 12 · LOCUS_ROUTING_GAP 10 — they move into the real, smaller routing/deep-pass bottleneck. **No
claim those bugs would have been caught.** The safe module deliberately recovers **fewer** than P192's full ladder
(42.4% vs 54.2%) because it excludes auto-fuzzy. **Per-corpus: 23/25 recoveries are zaros** (revert-lend 1,
panoptic 1, ark 0) — the recoverable set is zaros-dominated (only corpus with `alt_titles`).

## Residual 27 source audit (Part D)
| classification | n |
|---|---|
| ANSWER_KEY_STILL_UNRESOLVED (no resolvable function — contract/event/var/prose only) | 22 |
| NEEDS_HUMAN_MAPPING (lowerCamel token absent from manifest; may be var/param — function status unconfirmable) | 5 |
| **TRUE_COVERAGE_GAP (artifact-confirmable)** | **0** |

The initial deterministic pass flagged 9 "TRUE_COVERAGE_GAP", but **source inspection refuted all of them** — the
"named functions" were contract names (`AutoCompound`, `CreditDelegationBranch`), events (`LogLiquidateAccount`),
or state vars (`referenceToken` = `address public immutable`, `amountOfOpenPositions` = event param,
`lastVaultDistributedWethRewardPerShareX18` = struct field). So **0 production coverage gaps are confirmable from
artifacts**; the 5 NEEDS_HUMAN_MAPPING are lowerCamel tokens absent from the manifest that cannot be confirmed as
functions without manual source review (kept `UNKNOWN`, never inferred).

## The six required answers
1. **Loci safely recovered:** **25** (DIRECT 7-ish / ALT_TITLE / NORMALIZATION / MATCH_TERM-verbatim).
2. **Discovery-bucket shrink after implementation:** **42.4%** (59 → 34) via the safe module (vs P192's 54.2%
   full ladder — the gap is the auto-fuzzy/get-set cases intentionally held back as REVIEW_GATED).
3. **Remain review-gated:** **4** (+ 1 ambiguous = 5 not auto-resolved).
4. **True production coverage gaps among the 27:** **0 artifact-confirmable** (source-verified; candidates were
   contracts/events/vars). 5 need human mapping to fully close; 22 are answer-key-locus-quality.
5. **Next step — measurement, source mapping, or production coverage?** **Not production coverage** (0 confirmed).
   The safe extraction fix is done; the remaining lever is **answer-key locus quality** (22 findings name no
   resolvable function) + **human mapping of the 5**. The one deferred *production* item remains deep-pass
   selection-by-score (P192 revert-lend inversions), independent of this.
6. **Did any production routing/conduct change?** **No** — the module is eval-harness-only and un-wired; frozen
   answer keys, manifests, dispositions, and all production hashes (deep_trace `ef93a6c2`, checker `5d2a97f9`,
   ledger `e23c5bc9`) are byte-identical.

## Honesty / limits
- **Measurement-accounting only.** Recovered loci are not newly found bugs; "resolved" = the awarded function is
  locatable in the manifest. The AFTER buckets are the real, smaller bottleneck; no catch is claimed.
- The safe module is intentionally conservative (recovers 42.4%, < P192's 54.2%) to keep precision high; the
  difference is REVIEW_GATED, not lost.
- Recoveries are **zaros-dominated (23/25)** — generalize cautiously.
- `TRUE_COVERAGE_GAP=0` is "not artifact-confirmable", not "proven none exist"; the 5 NEEDS_HUMAN_MAPPING require
  source review. `fabrication_rate=0`; every recovery cites its exact answer-key field.
