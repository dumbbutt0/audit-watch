# P279 — CORPUS_DERIVATION_RESULTS

Corpus = 12 eval audits (P276/P278 set). Deriver joins each P278 validation-queue evidence package to its coverage-
manifest item, fills the evidence fields, then the (confidence-aware) readiness gate classifies.

## Before (P278) vs after (P279 deriver on)
| metric | before | after |
|---|---|---|
| READY_FOR_POC_INTENT (auto) | **0** | **3** |
| NEEDS_MORE_EVIDENCE | 84 | 81 |
| NEEDS_MORE_RUNTIME | 0 | 0 |
| REFUTED | 0 | 0 |
| **severe concluded/reportable FP** | 0 | **0** |

## READY breakdown (3, all manifest-true, unguarded, real anomaly)
- `IBeanstalk.cancelPodListing` (ORDER) — external, no modifier, order-cancel.
- `L2Governor.execute` (ACCESS) — public payable, no modifier, config/migration tags (ungated governance execute).
- `V3Vault.transform` (ACCESS) — external, no modifier, config tag, **external_calls** (arbitrary external call;
  the same locus hand-validated in P278).

## Reading
- The deriver moves auto READY from a hard **0 to 3**, concentrated in the classes whose anomaly is **manifest-visible**
  (ACCESS no-auth/config, ORDER, and external-call). severe FP stays **0**; advisory-only.
- The remaining 81 are NEEDS_MORE_EVIDENCE — correctly blocked: auth-guarded functions, internal helpers, and the
  ACCOUNTING/MATH/ORACLE/REWARDS/STATE classes whose anomaly is a value-flow/invariant fact the manifest cannot show
  (LOW attacker_path with a core-carrying unresolved assumption).
- Operator burden: ≤5 READY/contest (PoC budget); corpus-wide 3 total — a small, clean PoC-sweep queue.
