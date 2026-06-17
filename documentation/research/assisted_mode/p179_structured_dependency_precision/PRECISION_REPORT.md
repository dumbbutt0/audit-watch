# P179 — Precision of the P178 structured guarded-downstream blocks (zaros)

**Question:** do the 83 zaros clears that P178 resolved into structured dependency metadata (and that route to
block under P177) correspond to awarded findings, or are they clean-but-low-value re-surfaces?

**Method (read-only):** re-derive the 83 structured blocks; classify each by the cleared ITEM it re-surfaces
against the zaros answer key (awarded_exact / awarded_adjacent / awarded_subsystem / non_awarded_resurface /
unmappable); classify the P176 legacy 237 blunt guarded routes the same way for a before/after comparison.
`precision_harness.py` → `precision_by_block.json` + `metrics.json`.

## Headline: the 83 blocks are a boilerplate ARTIFACT
- **`dependency_name` concentration = 100% `loadLive`** (all 83 blocks). Every one comes from the SAME
  boilerplate out-of-scope disposition whose `guard_or_invariant` generically enumerates
  *"…guards/invariants identified (loadLive/loadExisting existence checks, access modifiers, slippage/deadline…)"*
  and whose `clear_reason` is *"Out of contest README scope … light pass … not answer-key eligible."*
- All 83 route via **locality (`guard_not_path_dominant`)**, not via a genuine unreviewed dependency: the
  extractor mines `loadLive` (a real but near-generic storage-load helper) from that enumeration, resolves it
  cross-contract, and locality trips the block.
- The block items are interfaces (`IAutomationCompatible`), constants (`BASE_KEEPER_LOCATION`,
  `SYSTEM_DECIMALS`), constructors, `_authorizeUpgrade`, etc. — not awarded-bug sites.

## Precision numbers
| metric | P178 structured (83) | P176 blunt (237) | Δ |
|---|--:|--:|--:|
| awarded_exact | 9.6% (8) | 7.2% (17) | +2.4 pts |
| awarded_adjacent (cum) | 41.0% | 40.1% | +0.9 pts |
| awarded_subsystem (cum) | 74.7% | 84.0% | **−9.3 pts** |
| non_awarded_resurface | 21 | 38 | — |

Two caveats make even these numbers optimistic:
- The 8 "awarded_exact" are **common-function-name coincidences** (`performUpkeep`/`mint`/`create`/`checkUpkeep`
  on Keepers, NFT, UsdToken, interfaces) — matched because an awarded finding mentions those generic names
  (e.g. M-07 `FeeConversionKeeper.performUpkeep`); the matcher credits any same-named function. The genuine
  "this block re-surfaces the awarded bug's actual site" rate is ≈ **0**.
- **awarded_subsystem precision (~75–84%) is near the base rate** — zaros findings span 12 subsystems / 29
  contracts, so almost any re-surface lands in an "awarded subsystem" by chance. Only the exact metric is
  meaningful, and it is low.

## Did structured metadata improve precision vs P176 blunt prose?
**No, not meaningfully.** Exact precision rose only +2.4 pts (9.6% vs 7.2%), adjacent was flat, and subsystem
fell 9.3 pts. Structured capture mainly **reduced volume** (237 → 83) by keeping the `loadLive`-mentioning
subset — it did not concentrate on awarded sites. The apparent P178 "revival of guarded-downstream to 83 precise
blocks" is **refuted**: those 83 are low-value, driven by one boilerplate token.

## What P178 still got right
The resolve-or-nothing guardrail itself is sound: it correctly kept the **154** generic-prose zaros clears
advisory (no flood), and the extractor mechanism works. The failure is narrower — the extractor treats a
near-generic plumbing helper (`loadLive`) enumerated in boilerplate as a real dependency.

## Decision (precision is poor → recommend, do NOT implement)
1. **Stoplist near-generic storage-load / plumbing helpers** (`loadLive`, `loadExisting`, and similar
   getter/load accessors) in `dependency_metadata.NAME_STOPLIST` — they are plumbing, not guards.
2. **Skip extraction on boilerplate / out-of-scope dispositions** — when `clear_reason` signals
   "out of scope / light pass / not answer-key eligible", do not synthesize a dependency claim.
3. **Do not mine dependency names from enumerated guard surveys** ("guards identified: A/B/C/…") — a slash/comma
   list is a survey, not a specific protective-dependency claim.
4. **Answer-key/function-mapping is weak** (only 27 of 70 zaros findings resolve to a manifest function), which
   both undercounts exact precision and lets common names over-credit it → improve answer-key→function mapping
   before trusting any precision number on this corpus.

## Final answer
- **83-block precision:** exact ≈ 9.6% (and ≈0 after removing common-name coincidences); adjacent 41%,
  subsystem 75% (≈ base rate, not informative).
- **Awarded overlap count:** 8 exact (coincidental) / 26 adjacent / 28 subsystem / 21 non-awarded.
- **Non-awarded deep-pass load:** ≥21 outright + the bulk of the rest are boilerplate out-of-scope items →
  the 83 blocks are largely wasted deep-pass cost.
- **Is P178 justified?** The resolve-or-nothing *mechanism* is justified and retained; the *specific zaros block
  revival is not precise* — it is a `loadLive`/boilerplate artifact. P178 needs refinements (1)–(3) before its
  structured blocks are trustworthy.
- **Next recommendation:** implement refinements (1)–(3) as a small precision patch (a future approved change),
  and improve answer-key function mapping (4); then re-run P179. Do not expand guarded-downstream further until
  then.
- **Integrity:** read-only; no routing/selector/prompt/corpus/disposition/answer-key change.
