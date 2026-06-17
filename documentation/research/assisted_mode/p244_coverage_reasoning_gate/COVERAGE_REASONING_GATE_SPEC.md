# P244 — Coverage + Reasoning-Depth Gate (SPEC, design-only)

**Status:** research/process-spec. **This document does not change any code.** It specifies a pre-triage gate as a set
of *minimal deltas* over machinery that already exists. Nothing in `scripts/`, `config/`, `prompts/`, `schemas/`, or
`run_pipeline.sh` is edited by P244 — the deltas below are descriptions for a *future, separately-approved* build phase
(see `RECOMMENDATION.md`).

## 0. Premise
P243 (`../p243_miss_roi_audit/MISS_ROI_AUDIT.md`) measured that 61% of the frozen system's missed weighted recall is
**coverage-bound** (the relevant code was never read) and a further 13% is **reasoning-bound** (the right area was
read but the exploit chain was abandoned). Detector families are a distant third (26%, split, none dominant). The
lever is therefore **process, not knowledge**: force the system to (1) read the full in-scope surface before triage
and (2) complete the exploit/defense reasoning before rejecting a candidate in a sensitive area. This spec frames
both as gates layered on the existing coverage + triage stack.

The guiding constraint: *do not add a new system where an existing field/state/gate can carry the obligation.*

---

## Part A — Coverage Completion Gate

### A.1 What exists
- `scripts/build_coverage_manifest.py` enumerates manifest items of kind
  `{function, initializer, constructor, constant, immutable, address}`, each with `attack_surface_score` (0–8;
  deep-pass ≥3), `tags[]`, `in_scope`, `source_span`, `risk_score`. Architectural roles
  (facet/selector/module/guard/oracle/vault/router/external-integration) are captured **only as `tags[]`**, not as
  first-class kinds.
- `scripts/init_coverage_dispositions.py` seeds a per-item disposition; the **6-state machine** (enforced by
  `coverage_completeness_gate.py`) is:
  `{unassigned, assigned, examined, cleared, finding, deferred_out_of_scope}`.
  `cleared` requires `evidence` + `clear_reason`; a **high-surface** (`attack_surface_score ≥ 3`) `cleared` additionally
  requires the strong-clear triad `attacker_reachability / guard_or_invariant / no_impact_reason`.
- `scripts/coverage_completeness_gate.py` hard-blocks the review gate on 11 rules (unassigned, assigned-only,
  examined-without-disposition, unevidenced/unreasoned clears, high-surface clears missing the triad, findings without
  refs, deferrals without reason, …) with `AUDITWATCH_COVERAGE_OVERRIDE=1` as the documented escape hatch.
  Coverage% = `(cleared + finding) / in_scope_items`.

### A.2 The two real gaps
1. **Read-depth is not represented.** The state machine records *whether an item was dispositioned*, not *whether its
   body was actually read in full*. An item can be `cleared` with evidence yet the surrounding contract/facet never
   opened — exactly the P241 failure mode (large targets `cleared` at the contract level while trade/perp libs and
   diamond facets were never read).
2. **"Examined" hides honest blockers.** When source can't be fully read (too large, no build, missing source,
   generated interface, duplicate wrapper) there is no state that says *why*, so these collapse into `examined` /
   `deferred` and the gate can't distinguish "deliberately out of scope" from "we ran out of budget here."

### A.3 Delta Δ-A1 — read-state sub-field (NOT a new state machine)
Add an optional **`read_state`** annotation on each disposition record, orthogonal to the existing `status`:

| `read_state` | Meaning | Maps onto existing `status` |
|---|---|---|
| `READ_FULL` | entire item body (and its in-contract callees) read | `examined`/`cleared`/`finding` |
| `READ_PARTIAL` | item opened but not fully traced | `examined` (blocks unless justified) |
| `NOT_IN_SCOPE` | excluded by scope.txt/out_of_scope.txt | `deferred_out_of_scope` |
| `GENERATED_INTERFACE_ONLY` | interface/ABI stub, no logic to read | `deferred_out_of_scope` (justified) |
| `DUPLICATE_WRAPPER` | byte/semantic duplicate of an already-READ_FULL item | `deferred_out_of_scope` (ref the original) |
| `BLOCKED_BY_SIZE` | item/file exceeds read budget | `examined` + blocker reason |
| `BLOCKED_BY_BUILD` | needs deps that aren't vendored (the P228 gap) | `examined` + blocker reason |
| `BLOCKED_BY_MISSING_SOURCE` | referenced but source absent | `examined` + blocker reason |

This is a **field**, not a 7th–14th status — it reuses the 6-state machine and the existing evidence/reason plumbing.
The `BLOCKED_BY_*` and `*_ONLY`/`DUPLICATE_WRAPPER` values are the "honesty" states: they let an item be cleared from
the *coverage* obligation while remaining visibly *unread*, so the gate (and the human) can see the true denominator.

### A.4 Delta Δ-A2 — critical-item list + READ_FULL requirement
Define **critical items** (a derived predicate over existing manifest fields, no manifest schema change):
- public/external entrypoints (`visibility ∈ {public, external}` ∧ state-mutating);
- privileged/admin functions (permission modifier present);
- hooks/callbacks (`on*Received`, `*Hook`, `beforeX/afterX`), fallback/receive;
- token-transfer / settlement / oracle / reward / liquidation / upgrade paths (by existing `tags[]`);
- facets/selectors, module/guard paths (by `tags[]` / contract_type).

**Rule Δ-A2:** *candidate triage cannot begin* (i.e. the review gate stays blocked) while any **critical** in-scope
item is not `read_state = READ_FULL` **or** carries an explicit justification (`NOT_IN_SCOPE` /
`GENERATED_INTERFACE_ONLY` / `DUPLICATE_WRAPPER` / a `BLOCKED_BY_*` with a recorded reason). Non-critical items keep
the *current* (looser) coverage rules. This is a new blocking rule appended to
`coverage_completeness_gate.py`'s set — gated behind a policy flag (default off until validated) and respecting the
existing `AUDITWATCH_COVERAGE_OVERRIDE`.

### A.5 Delta Δ-A3 — first-class architectural kinds (optional, low priority)
Promote `facet/selector/module/guard/oracle/vault/router/external-integration` from `tags[]` to a `role` enum on the
manifest item so the critical-item predicate and per-role coverage% are exact rather than tag-inferred. **Optional** —
the tag-based predicate in Δ-A2 already works; this only sharpens reporting. Listed for completeness, not recommended
for the first build.

---

## Part B — Lifecycle Flow Matrix

### B.1 What exists
Step-0 deep analysis already builds interaction/thread artifacts: `schemas/call_graph.schema.json`
(`interaction_chains` with `path`, `depth`, `danger_score`, `shared_state_vars`, `touched_invariants`),
`schemas/thread.schema.json` (`violation_path`, `hop_traces` with per-hop state reads/writes, `entry_conditions`,
`invariants_false_here`), and `output/context_pack.md`. `scripts/deep_analysis_prepare.py` sequences
`0a-extract_invariants → 0b-map_interactions → 0c-deep_trace → 0d-escalate_threads`.

### B.2 Gap
These artifacts are **finding-driven** (built around suspected violation paths), not **flow-complete** (one row per
protocol lifecycle flow whether or not a bug is suspected). A flow the system never suspected (e.g. fenix
`killGauge` emission accounting, predy reallocation) gets no matrix row → no structured prompt to reason about it.

### B.3 Delta Δ-B — lifecycle matrix as a deep-analysis output
Specify a **Lifecycle Flow Matrix** produced at Step-0 (reusing the deep-analysis substage machinery, not a new
pipeline stage). For each lifecycle flow **present** in the target —
`deposit, withdraw, mint, burn, borrow, repay, liquidate, claim, stake, unstake, bridge, settle, stop/reclaim,
create/list/register, upgrade/admin, oracle-update, reward-notify/checkpoint/claim` — record:

| Field | Source it reuses |
|---|---|
| entry function | manifest item id |
| internal calls | call_graph `path` |
| external calls | manifest `external_calls` |
| state writes | thread `hop_traces` (writes) |
| asset movements | thread `hop_traces` (transfers) |
| callbacks/hooks | manifest hook tags |
| guards/defenses | `defense_mapper.py` output |
| failure modes | thread `invariants_false_here` |
| who can trigger | manifest `visibility` + permission modifier |

A flow present in the manifest (by entrypoint name/tag) but **absent from the matrix** is a coverage hole surfaced to
the Part-A gate (it ties back to Δ-A2: the flow's entry function is a critical item that must be READ_FULL). The
matrix is the *evidence* that the lifecycle was reasoned about, not just the entry function read.

---

## Part C — Reasoning-Depth Checklist

### C.1 What exists
`schemas/triage.schema.json` already carries `decision_reason` (free-text), `defense_analysis`
(`coverage ∈ {full,partial,none,unknown}`, `evasion_confirmed`, `inherited_guard_found`, `hard_rejected_by_defense`),
`attacker_model`, and an `exploitability` block. `schemas/exploitability.schema.json` carries `execution_sequence`,
`blockers`, `profit_or_damage`. `prompts/deep_trace.md` (FORBIDDEN — read-only) already mandates a ≥3-mechanism
inventory, a carry-forward rule, a claimed-locus rejection table, and a severity floor.

### C.2 Gap
The fields exist but are **not required to be populated** for a *rejection*. A candidate can be rejected with a
one-line `decision_reason` and empty `execution_sequence`/`defense_analysis`. The depth machinery is available for
*confirmations* (deep_trace) but not *enforced* on *dismissals* — which is exactly where the P241 reasoning-bound
misses occurred (nextgen H-02 `==endTime`, kelp H-02 transfers-before-mint: read, then dismissed without a completed
chain).

### C.3 Delta Δ-C — checklist = required-population of existing fields
The Reasoning-Depth Checklist is **not new schema**; it is a *completeness predicate* over the fields above, required
before a candidate in a sensitive area (Part D) may be rejected:

1. **Exploitability chain** (populate `attacker_model` + `exploitability.execution_sequence`):
   attacker starting capability → first function called → required pre-state → state change before impact → intended
   defense → why defense fails → who loses → who gains → measurable delta.
2. **Defense dismissal** (populate `defense_analysis` with anchors): a candidate may NOT be rejected as "mitigated"
   unless it cites *exact defense* + *exact source location (file:line)* + *exact condition checked* + *exact reason
   it fully covers the path*. (This is the structured version of the existing `hard_rejected_by_defense`.)
3. **Integration completion** (populate `exploitability.blockers` + cross-component refs): if the bug depends on
   another contract/module/facet, the call chain into the callee, its return values, callbacks, revert behavior, and
   shared state must be inspected and recorded — not assumed.
4. **State timeline** (populate from `thread.hop_traces`): for stateful bugs, pre-state → step1 → step2 → step3 →
   post-state → invariant violated.

The checklist passes when the relevant fields are non-empty and source-anchored; it fails to *free-text-only*. On
failure for a sensitive-area candidate, see Part D.

---

## Part D — Anti-Shallow-Rejection Rule

### D.1 What exists
`scripts/triage_write.py` already implements a *no-silent-clear* pattern: a rejection of **safety-net code** without a
`disproof` field is rerouted to `human_review_queue.jsonl` rather than silently dropped. This is the exact mechanism
P244 generalizes.

### D.2 Delta Δ-D — extend no-silent-clear to the sensitive-area list
A candidate that **touches any sensitive area** —
`callbacks · hooks · permits/signatures · Safe/module/guard logic · oracle freshness · reward/emission accounting ·
vault share-conversion · liquidation · cross-chain settlement · token-transfer settlement · diamond facets ·
lifecycle registration` — may **not be rejected** unless it carries a **depth record**:

| Depth-record field | Backed by |
|---|---|
| source anchors | manifest `source_span` / file:line |
| defense anchors | Part C.2 defense dismissal |
| attacker path | Part C.1 `execution_sequence` |
| impact path | `exploitability.profit_or_damage` |
| rejection reason | `decision_reason` + the Part-C checklist pass |

**Rule Δ-D:** if a sensitive-area candidate is marked `rejected` and the depth record is incomplete, `triage_write.py`
reroutes it to `human_review_queue.jsonl` (identical to the existing safety-net behavior) instead of accepting the
rejection. Non-sensitive candidates are unaffected. Sensitive-area membership is derived from the same `tags[]` /
hook predicates as Part A's critical-item list, so the two gates share one classifier.

### D.3 Why this is FP-safe / burden-bounded
- It **never invents findings** — it only refuses to *silently drop* a sensitive-area candidate, routing weak
  rejections to a human queue that already exists. Recall-protective, not precision-degrading.
- Burden is bounded to sensitive-area rejections, not all rejections; and the required fields are ones a real
  dismissal should already have. A genuine "guarded by `onlyOwner` at X.sol:42" rejection passes trivially.

---

## Summary of deltas (all behind a default-off policy flag until validated)

| Δ | Where | Type | Priority |
|---|---|---|---|
| Δ-A1 read_state sub-field (incl. READ_FULL/READ_PARTIAL/BLOCKED_BY_*/GENERATED_INTERFACE_ONLY/DUPLICATE_WRAPPER) | `init_coverage_dispositions.py` + `coverage_completeness_gate.py` | field + reporting | HIGH |
| Δ-A2 critical-item list + READ_FULL-before-triage block | `coverage_completeness_gate.py` (new rule) | gate rule | HIGH |
| Δ-A3 first-class architectural `role` enum | `build_coverage_manifest.py` | manifest field | LOW (optional) |
| Δ-B lifecycle flow matrix | Step-0 deep-analysis output | new artifact (reuses schemas) | MED |
| Δ-C reasoning-depth completeness predicate | `triage_findings.py` (validation over existing schema fields) | validation | MED |
| Δ-D anti-shallow-rejection reroute for sensitive areas | `triage_write.py` (extend no-silent-clear) | reroute rule | HIGH |

Every delta reuses an existing field, state, gate, or schema. No new detector, no taxonomy expansion, no severity
policy change. The forbidden `deep_trace.md` is *read* by Δ-C (its mechanism-inventory discipline is the model) but
**not modified**. See `IMPLEMENTATION_OPTIONS.md` for how these map to the 5 packaging options and `P241_MISS_REPLAY.md`
for the measured recovery each delta would have produced.
