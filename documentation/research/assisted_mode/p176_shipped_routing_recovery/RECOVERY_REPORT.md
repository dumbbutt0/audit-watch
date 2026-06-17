# P176 — Shipped-routing recovery on Zaros + Revert-Lend

**Question:** does the already-shipped clear-routing (guarded-downstream + math-estimator + F1) recover the
remaining accounting/liquidation misses on zaros + revert-lend — i.e. were those misses over-*cleared* (a
routing/instrumentation problem) rather than un-*seen* (a discovery problem)?

**Method:** a read-only harness (`routing_recovery.py`) replays the **exact production predicates** (imported
from `scripts/`) over the **existing** cleared dispositions — no sweep run, no disposition mutation. Full-audit
strict assumed. Mechanisms simulated in the sweep's first-match order: `strong_clear_gate` → `guarded_downstream`
→ `math_estimator` → `f1_lifecycle` (special-focus/gate-DoS/spec-checklist NOT simulated → deep-pass load is a
lower bound). Reproduce: `python …/p176_shipped_routing_recovery/routing_recovery.py`.

## The key distinction: precise recovery vs blunt re-surface
`dcu.is_dependency_based_clear` fires on clear **prose** tokens ("invariant"/"guard"/"oracle"/"downstream"/…),
and because these older clears lack the structured dependency fields, `classify_clear` returns
`missing_dependency_metadata`, which is **blocking** under `require_dependency_clear_metadata=true`. So
guarded-downstream here degenerates into "re-surface any clear that *mentions* a guard-ish word" — high recall,
near-zero precision. The harness separates:
- **precise recovery** — `math_estimator` / `f1_lifecycle` (function-classification based) or guarded-downstream
  with *structured* metadata adjudicated blocking.
- **blunt re-surface** — guarded-downstream `missing_dependency_metadata` on prose only (mined dependency names
  are junk, e.g. `['scope']`, `['traced','pass','level']`).

## Population-level routing (all cleared items)
| corpus | cleared | routed→deep-pass | deep-pass load | mechanism counts | off-target (FP) surface |
|---|--:|--:|--:|---|--:|
| zaros | 471 | 266 | **56.5%** | guarded_blunt 237 · math_estimator 28 · f1 1 | 255/266 = **95.9%** |
| revert-lend | 102 | 30 | **29.4%** | guarded_blunt 30 | 26/30 = **86.7%** |

`strong_clear_gate` fired **0×** (existing high-surface clears already carry the strong-clear triplet — they'd
have been rejected at write-time otherwise). The deep-pass load is overwhelmingly the **blunt** fallback.

## Per-finding recovery — accounting_drift + liquidation_accounting misses
| corpus | target misses | precise recovered | blunt re-surface | discovery_gap | unrecoverable (no evidence) | unmappable |
|---|--:|--:|--:|--:|--:|--:|
| zaros | 27 | **5** (H-04,H-06,M-10,M-32 math · M-03 f1) | 4 (H-11,L-05,L-07,M-18) | 2 (M-11,M-28) | 2 (H-07,M-02) | 14 |
| revert-lend | 12 | **0** | 4 (H-06,M-05,M-06,M-11) | 0 | 0 | 8 |

Mappable subset (excludes unmappable): zaros 13 → 5 precise / 4 blunt / 2 discovery / 2 unrecoverable;
revert-lend 4 → 0 precise / 4 blunt.

**Unmappable is high and largely genuine** (zaros 14/27, revert-lend 8/12): the answer-key titles often name a
struct/field (`AutoDeleverageFactor`, `usdcAvailableForEngine`, `PremiumDiscountFactor`) or a spelling variant
(`settleVaultDebts`) that does not resolve to a manifest function. Fuzzy-matching was deliberately *not* used
(would manufacture false recoveries). Per-finding results therefore describe the mappable subset; the
population table carries the precision signal.

## Which outcome is this?
Mapping to the reviewer's framework:
- **Outcome A (routing recovers a large fraction, precisely)** — only *partially*, and only on zaros's
  **estimator-shaped** accounting misses (math-estimator caught H-04/H-06/M-10/M-32; F1 caught M-03). Lending
  accounting on revert-lend is **not** estimator/lifecycle-shaped → 0 precise recovery.
- **Outcome C (recovery blocked/blunted by missing metadata)** — **dominant.** The routing *can* re-surface
  most of these, but only via the blunt `missing_dependency_metadata` fallback that floods deep-pass at
  ~96% off-target. The precise lenses cover only the estimator-shaped subset.
- **Outcome B (recovers nothing)** — false; precise lenses do recover the estimator-shaped subset.
- **Genuine discovery gaps are tiny** (zaros 2 mappable, revert-lend 0) → a dedicated accounting/liquidation
  *discovery* selector is **not** justified by this evidence.

## Go / no-go (decision rule)
**NO new accounting/liquidation selector.** The evidence does not show a discovery problem: genuine
discovery_gap is 2 (zaros) / 0 (revert-lend) on the mappable subset, and the estimator-shaped accounting misses
are already covered by the shipped math-estimator/F1 lenses. The real bottleneck is **routing precision +
evidence capture**, not recall.

**Highest-ROI next investment — improve the shipped routing/instrumentation (no new family):**
1. **Tighten guarded-downstream precision.** The prose token-match + "missing_dependency_metadata ⇒ blocking"
   default re-surfaces ~half of all clears at ~96% off-target on metadata-poor corpora. Options: require a
   *structured* dependency signal (not incidental prose) before routing, or down-weight `missing_dependency_metadata`
   to advisory when the dependency was detected by prose only. This is the single biggest deep-pass-load driver.
2. **Improve evidence capture at clear-time.** zaros has 294/471 clears with only `clear_reason`+`evidence`
   (no strong-clear triplet, no structured dependency metadata, no proof). Capturing the triplet + structured
   dependency fields would let `classify_clear` adjudicate (`all_cleared` vs `unreviewed`) *precisely* instead
   of blunt-sweeping — converting the bucket-3 instrumentation gap into precise routing.
3. **Then re-measure.** Reducing the unmappable rate (better answer-key→function mapping) + the two fixes above
   would give a clean precise-recovery number; only if that still shows a real lending-accounting discovery gap
   on revert-lend would a targeted accounting selector be justified.

## Limitations (honest)
- Per-finding recovery is measured only on the mappable subset; unmappable findings are reported, never counted
  as recovered or failed.
- special-focus / gate-DoS / spec-checklist routers are not simulated → deep-pass load is a lower bound.
- "recovery" = the cleared item would be re-surfaced to deep-pass; it does NOT assert the deep-pass would then
  confirm the bug (that's a separate, unmeasured step). Re-surfacing is necessary, not sufficient.
- Recovery is computed against TODAY's shipped predicates applied to OLD clears; it is a "what-if-re-swept"
  measure, not a record of the original run.
