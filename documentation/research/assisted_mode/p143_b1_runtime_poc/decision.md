# P143 — Decision

## Decision: **RUNTIME_CONFIRMED**

A Foundry test deploys the **real `NoyaValueOracle`** and calls its real public `getValue` on a controlled 2-hop
route. The real contract returns **20e18** where the corrected (loop-carried `quotingToken`) reference returns
**6e18** — a clear 3.33× discrepancy — while a single-hop control and an equal-per-hop-price control show **no**
divergence. This executes the vulnerable behavior and shows a clear discrepancy versus corrected/control behavior.

### Rubric
- **RUNTIME_CONFIRMED** ✅: real vulnerable behavior executed; clear discrepancy vs corrected + controls.
- Not RUNTIME_PARTIAL: a full real-contract deployment was achieved (not just a wrapper); the corrected oracle is
  only the comparison control.
- Not RUNTIME_KILLED: runtime matches the prompt-derived mechanism exactly.
- Not RUNTIME_BLOCKED: deps resolved; the test compiles and runs.

## Final response

**What this phase tested** — the H-03-class B1 mechanism (`NoyaValueOracle._getValue` multi-hop loop uses the
static `asset` instead of the loop-carried `quotingToken`) at runtime.

**Harness** — real-contract Foundry PoC (`audits/noya-2024-04-eval/pocs/p143/`): real `NoyaValueOracle` + stub
registry (real setters) + mock `INoyaValueOracle` price oracle + a one-line-fixed corrected reference control.

**Runtime result** — 4/4 pass; vulnerable 20e18 vs corrected 6e18, delta 14e18 (3.33×); controls show no
divergence.

**Prompt vs runtime status** — prompt_decision=finding / prompt_status=completed (unchanged) recorded **separately**
from runtime_status=runtime_confirmed (research-only sidecar); prompt metrics untouched.

**Limitations** — mechanism proven, not severity/economic impact or production route reachability; mock oracles;
corrected output is a control.

**Safety** — no submission; no production contract/detector/severity/gate change; not submission-ready; human +
PoC review still mandatory; active audit unchanged.

**Tests / integrity** — `forge test` 4 passed; no Python production code touched (full pytest unaffected);
`output/` symlink still quantamm-2024-12-eval.

**Decision** — RUNTIME_CONFIRMED.

**Next recommended phase (P144)** — human-review the *reachability/severity* question (do production noya
deployments register ≥2-source routes with materially different per-hop oracles, and what consumes the
mis-value?), and/or add an optional `runtime_status` column to the P142 scorecard **as a separate research-only
panel** (default `not_run`) so prompt-derived and runtime-confirmed counts are reported side-by-side without
blurring. Submission remains gated on human scope/duplicate/severity sign-off.
