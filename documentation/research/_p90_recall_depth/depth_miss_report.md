# P90-B — Depth miss taxonomy (P85 / P87 / P89, + P81e)

Data: `depth_miss_taxonomy.json`. Each miss is tagged with a class and a **fix owner** (which layer should
change). Historical scores unchanged.

## Fix-owner distribution (where the recall is actually lost)
| Fix owner | # misses | Reading |
|---|---|---|
| **deep_pass (conversion depth)** | **8** | the dominant bucket — wrong harmlessness calls, un-enumerated mechanisms, abstains |
| **lead_selection** | 5 | below-cutoff low-scoring contracts + selected-but-NOT_RUN + unsurfaced |
| **taxonomy (P84 types)** | 4 | index-integrity, signature-replay, enumerable-growth, missing-function |
| **maximal_consequence_check (P90-C)** | 3 | High under-labelled Medium + admin-footgun misread |
| **severity_gate_input** | 2 | self-inflicted-vs-involuntary impact-assessment input (gate LOGIC is fine — P88) |
| **adversarial_review** | 1 | should have caught the P85 H-01 harmlessness misjudgment |
| **severity_gate_logic** | 0 | the gate itself is validated in both directions (P87/P89) — do NOT touch |

## The recurring miss patterns
1. **Conversion depth (deep_pass) is the #1 loss.** Eight awarded findings were *surfaced and selected* but the
   deep pass rejected them on a wrong harmlessness call (P85 H-01 "harmless plot move"), failed to enumerate
   the awarded mechanism (P85 H-02/H-04, P89 H-03), or abstained. No cap or gate change recovers these — only
   a more aggressive, source-traced deep pass.
2. **High under-labelled Medium (×2 confirmed, both kept).** P87 H-01 `mintWithBudget` and P89 H-05 public
   helpers were *correctly converted* but assigned Medium when judged High. The gate kept them (good); the
   under-label is in the **impact assessment** → P90-C maximal-consequence check targets exactly this.
3. **Admin-footgun misclassification.** P87 H-03 (`taxCut` wrong-%) was rejected as "admin footgun" when it is
   externally-consequential (every fee flow mis-distributes once `taxCut` is changed). → P90-C adds the
   admin-footgun-vs-user-harm distinction.
4. **Self-inflicted vs involuntary misread.** P87 M-18 (involuntary fee-reduction race) demoted as
   "self-inflicted"; P85 M-01 (zero-tax config gap) rejected as "landlord misconfig". The gate now keeps these
   *if tagged involuntary/concrete* (P88) — the residual is the **impact-assessment input** (the investigator
   must recognize involuntariness) → P90-C.
5. **Lead selection: per-contract floor + NOT_RUN.** P87 H-06 (`EntropyGenerator` scored 1, below cutoff) and
   P89 H-01 (`signatureClaim` selected but NOT_RUN) are the only clearly selection/throughput-addressable
   Highs → P90-A's `top-2-per-contract floor` + `NOT_RUN→0` policy.
6. **Negative space / new shapes → taxonomy.** P89 H-05 (public internal-index mutation), P89 H-01/H-02
   (signature replay), P81e M-01 (missing function), P89 H-03 (enumerable-map growth) → P90-D adds
   index-integrity + signature-replay handoff types (negative-space/missing-function deferred: single
   confirmed instance).

## Conclusion
The recall bottleneck is **conversion depth first, lead selection/throughput second, and impact under-labelling
third** — not the severity gate (validated) and not a bigger global cap (P90-A). P90 therefore ships:
(C) a maximal-consequence impact check (under-labelling + footgun + involuntary), (D) two taxonomy types, and
(A) the per-contract-floor + NOT_RUN→0 selection policy. The deep-pass depth gap is the largest and is the
recommended focus of P91's prompt + measurement (not a machinery rewrite).
