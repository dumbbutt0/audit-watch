# Dependency-Aware Clear Policy

**A dependency is not a proof unless the dependency has itself been reviewed.** A coverage clear (cheap
sweep `cleared` or deep-pass `strong_clear`) may not rely on a downstream guard / estimator / oracle /
math-rule / invariant / lifecycle-check to absorb the threat **unless that dependency is itself**:
finding-linked · deeply reviewed with evidence · strongly cleared with its own evidence · or explicitly
out of scope.

## Why downstream-dependency clears are risky

A clear that says *"this is safe because X validates it downstream"* is only as strong as X. If X is
itself in-scope and **unreviewed**, the clear is circular: it asserts safety by appealing to code nobody
has checked. The coverage gate then reports 100% coverage **by process** while real bugs sit inside the
very guards the clears leaned on — coverage completeness ≠ depth.

### QuantAMM 2024-12 failure example (what this policy prevents)

In the QuantAMM fresh blind eval the coverage sweep strong-cleared the rule-math / packing / pool-math
functions with reasoning like:

> *"QuantAMMStorage._quantAMMPackTwo128: bounded math. Inputs validated at registration
> (validParameters/lambda/epsilon/guardRail) and outputs pass through `_guardQuantAMMWeights` (clamp to
> guard rails + epsilon-normalize) before setWeights."*

But `_guardQuantAMMWeights` (and the estimators/validators it named) were **themselves in-scope and
unproven** — and they contained multiple missed High/Medium bugs (integer overflow in the MathGuard,
weight-normalization violating the epsilon guard rail, incorrect covariance estimation). 58 of 197 clears
were dependency-based; 52 of those leaned on rule-math/guard code. Pointing at the guard *was* the bug.

## Required metadata for a dependency-based clear

When a clear leans on another component, the decision MUST carry:

| field | meaning |
|---|---|
| `clear_depends_on` | list of dependency `manifest_id`s (or function names) the clear relies on |
| `dependency_clearance_status` | `all_cleared` \| `finding_linked` \| `partially_cleared` \| `unreviewed_dependency` \| `unknown_dependency` \| `out_of_scope_dependency` |
| `dependency_reason` | how the dependency actually blocks the bug |
| `dependency_evidence` | source span(s) for the dependency itself |
| `downstream_guard_claim` | `true` if this clear leans on a downstream component |
| `downstream_guard_type` | `guard` \| `estimator` \| `oracle` \| `math_rule` \| `invariant` \| `lifecycle_check` \| `bounds_check` \| `access_control` \| `other` |

A dependency counts as "reviewed" only if its own disposition is `finding`, `deferred_out_of_scope`, or
`cleared` **with evidence** (and, if that clear itself explicitly declares a further dependency, that
further dependency must also resolve OK — one level of transitive-laundering protection).

## Invalid clears (rejected / routed to needs_deep_pass)

- *"safe because guarded downstream"* — no dependency named, no metadata.
- *"bounded by MathGuard"* / *"handled by the estimator"* / *"the oracle prevents this"* /
  *"validated later"* / *"the lifecycle check prevents this"* — when the named component is in-scope and
  not yet reviewed.
- *"outputs pass through `_guardQuantAMMWeights` before setWeights"* while `_guardQuantAMMWeights` is
  `unassigned`/`assigned`/`examined` (not reviewed).

## Valid clears

- *"Cleared. clear_depends_on=[function:Guard:_guardQuantAMMWeights#…]; dependency_clearance_status=
  finding_linked (the guard is filed as DT-009); dependency_reason=the overflow is captured there;
  dependency_evidence=[Guard.sol:19-30]."*
- *"Cleared. The clamp dependency `_guardQuantAMMWeights` is itself strong-cleared with evidence
  (Guard.sol:19-30, attacker_reachability/guard_or_invariant/no_impact_reason all present);
  dependency_clearance_status=all_cleared."*
- A clear that names a concrete LOCAL guard (`require(msg.sender==owner)` at L42) with its own evidence —
  not a *downstream* dependency at all → `not_dependency_based`, passes normally.

### Finding-linked dependency clears (valid, non-blocking)

A dependency-based clear is **non-blocking** when it is explicitly anchored to an **existing finding** —
the dependency (the bug) has already been reviewed and filed, so leaning on it is not circular. Such a
clear is classified `finding_linked_dependency` and is **not** downgraded, even if the structured
`clear_depends_on` metadata is absent. A clear is finding-linked when either:

- a structured field is set — `finding_refs`, `finding_ref`, `duplicate_of`, or `related_finding`; or
- the `clear_reason` / `dependency_reason` / `evidence` cites a concrete finding id matching
  `\b[A-Z]{1,5}-\d{2,4}\b` (e.g. `DT-003`, `DPF-036`, `EVAL-001`, `GOR-001`, `CHAIN-001`, `H-01`).

To avoid false matches, standard/token ids are **excluded** and never count as a finding link:
`ERC`, `EIP`, `BIP`, `SIP`, `CWE`, `CVE`, `RFC`, `ISO`, `SHA`, `UTF`, `AES`, `RSA` (so `ERC-20`,
`EIP-1153`, `CWE-841` do not trigger the escape).

| | example |
|---|---|
| **Invalid** (still blocks) | *"safe because guarded downstream"* — no finding link, no reviewed dependency |
| **Valid** (non-blocking) | *"dependency is the same root cause as DT-003"* or `finding_refs=[DT-003]` |

This refinement (from the QuantAMM strict dry run) removes false downgrades of clears already covered by a
filed finding **without weakening the core policy** — an unreviewed downstream dependency with no finding
link still does not justify a clear.

### Generic dependency-token stop-list

`extract_dependency_names` filters out generic words so they are never reported as a dependency *name*:
`require`, `assert`, `revert`, `zero`, `path`, `check`, `validate`, `validation`, `guard`, `math`,
`condition`, `bounds`, `later`, `downstream`. This is **report hygiene only** — phrase/token detection in
`is_dependency_based_clear` is unchanged, so *"guarded downstream"* still classifies the clear as
dependency-based (it just yields no bare `guard`/`downstream` "dependency"). Real named dependencies
(`_guardQuantAMMWeights`, `MathGuard`, `validParameters`, `setWeights`) are unaffected.

## Locality / path-dominance (the Swan/Dria H-02 miss)

**A guard "somewhere" is not a guard "on every path."** A reviewed dependency is necessary but not
sufficient: when the guard lives in a *different function or contract* than the cleared item, the clear
is only valid if that guard **dominates every attacker-reachable path** to the item.

In the Swan/Dria 2024-10 eval, `Swan.purchase` had **no local round check**; a clear leaned on
`BuyerAgent.getRoundPhase` (the phase guard, in another contract) to absorb the missing validation. But
`purchase` is `external` and directly callable by the listing buyer — it never routes through the
BuyerAgent guard. The guard was reviewed; it simply did not dominate the purchase path. The High was
under-called.

A dependency clear on a **non-local** guard (the guard resolves to a different function/contract than the
item) must therefore carry:

| field | meaning |
|---|---|
| `guard_locality` | `same_function` \| `same_contract_dominates` \| `cross_contract_dominates` \| `non_local` |
| `path_dominance_evidence` | proof (citing the call graph) that EVERY attacker-reachable path to the item passes through the guard |
| `alternative_paths_considered` | the other ways the item is reachable and why each is also guarded or impossible |

`alternative_paths_considered` must address: a direct public/external call to the item; proxy / facet /
router / library routing; callbacks, hooks, relays, bridges; governance / batch / delegatecall execution;
and whether the validated parameter can change between the guard and the item.

`dependency_clear_utils.classify_clear` (given the manifest + `data/interactions/call_graph.json`) raises
**`guard_not_path_dominant`** (blocking) when a non-local guard lacks `guard_locality ∈
{same_contract_dominates, cross_contract_dominates}` + `path_dominance_evidence` +
`alternative_paths_considered`, when `guard_locality == non_local`, or when the **call graph disproves
dominance** — i.e. there is an attacker entry (including the item itself if it is public/external and does
not call the guard) that reaches the item on a guard-free path. The call-graph check is a *disproof*
(sound for blocking, not a complete dominator analysis): an entry that itself calls a guard is given the
benefit of the doubt (intra-function ordering is not encoded in the graph), so legitimate
“guard-then-sink” callers are not false-flagged. When the call graph is absent or the guard is unresolved,
only the field-presence gate applies. Locality is evaluated **only** when the guard resolves to a
different function/contract; a same-function/local guard is never over-blocked.

### Invalid vs valid locality clears

| | example |
|---|---|
| **Invalid** (`guard_not_path_dominant`) | `Swan.purchase` cleared via `BuyerAgent.getRoundPhase` while `purchase` is externally callable and never calls the guard |
| **Invalid** | a sink reachable from a `Router`/proxy on a guard-free path, even if one path is guarded |
| **Valid** (`dependency_valid`) | an `internal` sink whose only caller is the guarding function (call graph shows no guard-free entry), with `cross_contract_dominates` + evidence |
| **Valid** | a public sink that calls the guard in its own body (`same_contract_dominates`, edge sink→guard present) |

Config flags (mirroring the dependency-clear pattern): `dependency_locality_strict` (default `false`) and
`dependency_locality_strict_full_audit` (default `true`) — locality blocks on a full audit
(`AUDITWATCH_FULL_AUDIT=1`); advisory otherwise.

## Advisory vs strict

- **Validator** `scripts/validate_dependency_clears.py`:
  - `--mode advisory` (default): exit 0; reports every dependency-based clear and its classification
    (`output/dependency_clear_validation.{json,md}`). Use on current/in-flight audits.
  - `--mode strict`: exit nonzero if any dependency-based clear is missing metadata / relies on an
    unreviewed or unknown dependency / lacks dependency evidence.
- **Writer enforcement** (`coverage_sweep_write.py`, `deep_pass_write.py`), config-gated in
  `config/agent_policy.json → coverage_policy`:
  - `require_dependency_clear_metadata` (default `true`) — metadata is expected on dependency clears.
  - `dependency_clear_strict` (default `false`) — when true, a metadata-less / unreviewed-dependency
    clear is **routed to `needs_deep_pass`** (status `assigned`/`deep`, tagged
    `dependency_review_required:true` + `routed_reason`) instead of being applied. This reuses the
    existing blocking disposition — **no new status, the coverage gate is untouched, no gate is weakened.**
  - `dependency_clear_strict_full_audit` (default `true`) — strict applies on a **full audit**, signalled
    by the env var `AUDITWATCH_FULL_AUDIT=1`. Current/incremental audits stay lenient (advisory) by
    default; a final full audit opts into strict downgrades.

### How full-audit mode should use strict

For a final, submission-grade full audit, run with `AUDITWATCH_FULL_AUDIT=1` so the sweep/deep-pass
writers downgrade any clear that leans on an unreviewed dependency to `needs_deep_pass` — forcing the
guard/estimator/oracle itself onto a deep specialist before the review gate can pass. In advisory
(default) runs, use `validate_dependency_clears.py --mode advisory` to see the same items as a report
without changing dispositions.

## Backward compatibility

All fields are optional and read with `.get`; old dispositions without them never crash. When no
dependency language is present and strict is off, writer behavior is byte-identical to before. No
disposition status enum value was added; the coverage completeness gate is unchanged.
