# P118 — Decision: SecondSwap_Marketplace.unlistVesting (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness refuted the suspected exploit with executed reverts — not source-only reasoning.

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| the suspected exploit cannot occur | Case A: an unauthorized caller (`attacker`, non-seller/non-admin) calling `unlistVesting` **reverts "Not the seller"** (PASS). |
| state stays bounded / no double effect | Case B: a second `unlistVesting` on the same listing **reverts "Listing not active"** — `status→DELIST` + `balance→0` after the first call prevent a double balance-return (PASS). |
| legitimate path remains intact | Case C: the seller unlists own active listing once → succeeds; Case D: `s2Admin` unlists → succeeds (PASS) — the access control admits exactly the seller/admin and no one else. |

**Verdict:** the high-ranked, "permissionless"-flagged `unlistVesting` is in fact **seller/admin-gated and
double-unlist-safe at runtime**. The suspected unauthorized-unlist / double-return exploit **cannot occur** →
KILLED_RUNTIME. This is a clean runtime REFUTATION of a NOVEL candidate (the methodology that CONFIRMED P117's true
positive also correctly KILLS a false lead).

## Why it ranked high (a second actor_clarity gap — recorded, not acted on here)
`unlistVesting` was flagged `actor_clarity = permissionless` only because the role-guard detector matches
`require(msg.sender==` / `only*` but **misses the `seller == msg.sender` (operand-reversed) and `msg.sender ==
s2Admin()` forms**. This is a distinct gap from P115's signature-modifier fix. A future ranking-precision phase
could extend the role-guard heuristic to these body-level forms (would correctly demote `unlistVesting` and similar
caller-equality-guarded functions). Out of scope for P118 (no machinery change this phase).

## Scope / honesty notes
- Hypothesis tested = unauthorized / double unlist (the access-integrity reading of a high-value "permissionless"
  function). The penalty branch and the VestingManager balance-return are intended behavior (the contract carries
  audit-fix annotations 3.3/3.4/3.6/3.7). Secondary accounting beyond double-return is not the framed question.
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).
- Novel candidate — but the verdict is KILLED, so there is nothing to submit regardless.

## Hard-stop self-check
- KILLED_RUNTIME claimed only with a passing runtime test (Cases A/B/C/D all PASS, executed). ✓
- No source-only reasoning as runtime proof — the reverts/successes are executed. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- secondswap `contracts/` (src) unmutated (`SecondSwap_Marketplace.sol` sha 80573b86); harness is test-only under
  `/tmp/p97-secondswap/test/audit/`. ✓
