# P190 — Upstream coverage & locus-routing failure analysis

**Question:** for every unresolved awarded finding, where does the correct locus disappear *before adjudication
ever begins*? **Read-only**, deterministic artifact join (manifest → queue → deep-trace → dispositions); D–F from
the 13 frozen P189 re-adjudications else `NEEDS_EVIDENCE`. No production/prompt/detector/answer-key/corpus edits.

## Funnel (114 unresolved awarded findings across 4 measured corpora; quantamm control = 0 unresolved rows here)
| loss label | count | % |
|---|---|---|
| DISCOVERY_GAP | 59 | **51.8** |
| LOCUS_ROUTING_GAP (sibling confusion) | 16 | 14.0 |
| PRIORITY_ROUTING_GAP (score starvation) | 9 | 7.9 |
| DEEP_PASS_GAP (queued, never analyzed) | 16 | 14.0 |
| ENUMERATION_GAP | 0 | 0.0 |
| ADJUDICATION_GAP | 3 | 2.6 |
| HARNESS_GAP | 1 | 0.9 |
| REPORT_FORMATION_GAP | 0 | 0.0 |
| NEEDS_EVIDENCE | 10 | 8.8 |

**Loss-phase split:** before deep-pass **87.7%** · during (enumeration) 0.0% · after deep-pass 3.5% ·
needs_evidence 8.8%. **Recall Loss Concentration: DISCOVERY/upstream.** **Decision: `ROUTING_IS_PRIMARY_BOTTLENECK`.**

### Critical caveat on the DISCOVERY number
DISCOVERY_GAP (59) splits into **genuine NOT_DISCOVERED = 8 (7.0%)** (contract absent from the manifest entirely)
and **DISCOVERED_CONTRACT_ONLY = 50 (43.9%)** (contract *was* enumerated, but the awarded function name was not
matched). The contract-only bucket — dominated by zaros (39) whose answer-key function fields are noisy (P189) —
is a **noise-prone upper bound**: it conflates true function-level coverage gaps with answer-key locus-string
mismatch. So "≈52% discovery" must NOT be read literally. The **robust, matching-independent** finding is the
phase split: **≥87.7% of recall loss occurs upstream of deep-pass**, and **0% is lost during enumeration** on
surfaces that were correctly deep-run.

## The seven required answers
1. **Where does recall die most often?** **Upstream of deep-pass (87.7%).** The single largest labeled bucket is
   surface discovery/coverage (51.8%, mostly contract-enumerated-but-function-unmatched), followed by routing
   (locus 14.0% + priority 7.9%) and deep-pass targeting (14.0%).
2. **% true discovery failures?** **7.0% genuine** (contract entirely absent); a further 43.9% are
   contract-only/function-unmatched (mixed coverage-gap + locus-noise — upper bound, not a clean discovery figure).
3. **% sibling-routing vs score-starvation?** **LOCUS_ROUTING_GAP 14.0%** (a same-contract sibling was queued
   instead of the awarded function) and **PRIORITY_ROUTING_GAP 7.9%** (awarded function was queued but
   out-competed for deep-pass by higher-scored surfaces) — reported separately as requested.
4. **% reaching deep-pass but missing the mechanism?** **~0% measurable** (`ENUMERATION_GAP` 0). Almost nothing
   reached a correct deep-run and then lost the mechanism at *enumeration* — because few awarded surfaces were
   deep-run at all in the original pipeline (zaros/ark ran no `deep` pass; revert-lend/panoptic deep-ran other
   surfaces). The original enumeration step is not in legacy artifacts → this slice is largely `NEEDS_EVIDENCE`.
5. **% surviving enumeration but failing adjudication?** **3.5%** (ADJUDICATION_GAP 2.6% + HARNESS_GAP 0.9%),
   attributed via P189 re-adjudication of the few findings whose correct function *was* originally deep-run.
6. **Single bottleneck with the largest recall gain if fixed?** **Get awarded surfaces discovered-at-function-
   level and routed/targeted into deep-pass.** Discovery+routing+deep-pass-targeting = 87.7% of loss. Adjudication
   (the P183–P188 investment) governs only ≤3.5%. The largest *clean, addressable* lever is **routing + deep-pass
   targeting** (locus 14% + priority 7.9% + deep-pass 14% = ~36% of all loss, all on already-discovered surfaces),
   plus function-level coverage to convert the contract-only bucket into queued surfaces.
7. **Is the next phase routing, enumeration, or adjudication?** **A routing/coverage problem — emphatically not
   enumeration or adjudication.** Within routing, both sub-modes are real: **sibling-confusion (LOCUS, 14%)** and
   **score-starvation (PRIORITY, 7.9%)** — P191 should target both (the candidate ranking starves the awarded
   locus, and the queue routes a neighbor).

## Sibling / starvation evidence (sibling_routing_table.json — 24 rows)
- **LOCUS** rows record the awarded function, the same-contract sibling(s) that were queued, and their queue
  `score`. Example (zaros M-31): awarded `_handleWethRewardDistribution` lost to siblings `initialize` (score 6),
  `updateConfig` (score 5) — the router preferred config/init surfaces over the reward-distribution logic.
- **PRIORITY** rows record the awarded function's queue score vs the higher-scored surfaces that *did* deep-run
  (the starvation margin).

## Decision: `ROUTING_IS_PRIMARY_BOTTLENECK`
DISCOVERY+LOCUS_ROUTING+PRIORITY_ROUTING+DEEP_PASS = 87.7% ≫ 50%. The frontier is upstream: **surface discovery
(function-level coverage) + candidate ranking + deep-pass targeting.** Audit-Watch's adjudication (P183–P188) is
no longer where recall dies; it now governs ≤3.5% of remaining loss.

## Honesty / limits
- **D–F partial by design:** original enumeration/selection are not in legacy artifacts; only the 13 P189
  re-adjudications inform stages D–F (rest `NEEDS_EVIDENCE`, 8.8%). So the enumeration-vs-adjudication split after
  deep-pass is intentionally under-resolved — but it is also a *small* slice (≤12%), so this does not threaten the
  headline.
- **Discovery bucket is noise-prone** (50/59 are contract-only/function-unmatched); treat 51.8% as an upper bound,
  7.0% as the genuine floor. The **phase split (87.7% upstream)** is the matching-robust headline.
- zaros/ark ran no `deep` assigned-pass; their losses concentrate at discovery/queue/deep-pass by construction.
  quantamm (control) had no candidate_queue and 0 unresolved rows under the strict match-matrix filter.
- Every per-finding label cites its artifact basis in `loss_funnel.json`. `fabrication_rate=0`.
