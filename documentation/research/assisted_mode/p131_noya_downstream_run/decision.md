# P131 — Decision

## Decision: **ACCEPT_WITH_LIMITS confirmed (downstream-supported); keep boost default-ON, add two noise trims**

The focused noya A/B shows the P130 boost's downstream behavior is **net-positive**: it converts the candidate-
coverage gain into **genuinely reviewable bug surface** without inflating the speculative FPs P129 worried
about. It does **not** warrant default-OFF, and the +44% volume is mostly productive. The original
ACCEPT_WITH_LIMITS stands, now **evidence-backed**, with two concrete, general noise trims identified.

### Evidence
- **Recall is real:** awarded-FUNCTION deep-pass coverage 6/19 (32%) → **14/19 (74%)**; the +8 newly-surfaced
  functions are all `value_exit`/oracle logic (spot-LP TVL, chainlink staleness, oracle-source chaining) that
  is substantively reviewable. OFF they sit at score 2 in clear-biased cheap-sweep — the P129 miss pattern.
- **FP-tendency is low/benign:** of +70 boosted, ~62% are on-class value/TVL logic (intended widening; valid-
  unawarded → human review), ~21% trimmable noise (trivial getters + a mock), and the set is **view value-
  getters** — the boost adds **no new state-mutating paths**, so there is **no mechanism for speculative
  `arithmetic`/`economic_attack` FP inflation** (P129's specific fear is not realized).
- **No regression:** precision loop invariant (FP 0.143, over-severity 0.267); pytest 1572/2/4 unchanged;
  no new production code; config + active audit restored.

### Limits on the conclusion (honest)
Recall = deep-pass visibility + source-grounded discoverability (not confirmed automated findings); FP = a
mechanism-based + sample-grounded estimate (non-awarded leads → needs_human_review). A human-graded specialist
run would convert these into hard rates. slither/static was degraded (no build env).

## Final answer
- **Recall delta:** awarded-function deep-pass coverage **32% → 74% (+8 functions)** under noya's real scope;
  the recovered functions are genuinely reviewable `value_exit`/oracle surface.
- **FP / speculative-FP impact:** deep-pass volume +44%; ~79% productive, ~21% trimmable noise; **no evidence
  of speculative `arithmetic`/`economic_attack` FP inflation** (boost re-ranks read logic, adds no new
  state-mutating paths). Precision metrics invariant.
- **Decision:** ACCEPT_WITH_LIMITS confirmed — keep `library_internal_surface_boost` default-ON with the cap;
  add the two noise trims below.
- **Two general trims (for P132, not implemented here):** (1) exclude mock contracts from scope/boost (broaden
  `Mock*.sol` → `*Mock*.sol`, catches `ConnectorMock2.sol`); (2) don't boost trivial-bodied helpers (require an
  external call or non-trivial body), removing ~12 noise boosts while keeping all 8 awarded.
- **Next recommended phase (P132):** implement the two trims + a human-graded specialist run on the noya
  boost-delta to convert the recall ceiling (74%) and FP estimate into measured rates; then address the residual
  non-ranking misses — `(absent)` functions (enumeration/scope) and untagged awarded entrypoints (e.g.
  `updateTVL`), possibly via callgraph-reachability boosting.
