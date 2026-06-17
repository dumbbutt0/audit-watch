# Coverage System

Deterministic coverage enforcement so point-and-shoot audit accuracy is bounded by **reasoning
quality**, not by invisible unexamined code.

## Why it exists

The API-free Beanstalk eval scored 42% useful detection — but the loss was **breadth, not reasoning**.
Where the pipeline looked, it landed (migration cluster HIT, oracle inverted-ternary HIT, flood 6/6);
the misses were *unexamined surfaces*: hardcoded L1 constants used on L2 (#133/#135/#419/#469), the
bridge address pairing (#142), the Uniswap oracle branch (#350), quickSort in flood (#461), plot-spam
DoS (#379). Nothing reviewed them, so they could never be found. The fix is structural:

> No depth without coverage. No finding without reachability. No clear without evidence.
> No review pass with invisible unexamined code. No submission without confirmation.

Everything here is **deterministic and API-free**: the gate/manifest/metrics scripts call no LLM; the
only reasoning step (the cheap sweep) is an in-session Claude Code skill.

## The four artifacts

| File | Produced by | What it is |
|---|---|---|
| `output/coverage_manifest.json` | `build_coverage_manifest.py` | the complete review **denominator** — every function, constructor/initializer, constant, immutable, hardcoded address, with a stable id, tags, a deterministic attack-surface score, and an `in_scope` flag |
| `output/coverage_dispositions.json` | `init_coverage_dispositions.py` (+ updaters) | one disposition per manifest id: `unassigned / assigned / examined / cleared / finding / deferred_out_of_scope` |
| `output/coverage_gate.json` | `coverage_completeness_gate.py` | gate verdict + blocking items |
| `output/coverage_metrics.json` | `coverage_metrics.py` | coverage% decomposed from detection |

## Generate the manifest

```
./run_pipeline.sh coverage-manifest [contract_path]      # build + init dispositions
# or directly:
python scripts/build_coverage_manifest.py --contract <path>
python scripts/init_coverage_dispositions.py
```
The manifest reuses `output/static.json` for signals (tainted sinks, external-call sites, slither
hits, proxy/erc4626 flags) and a source regex pass for what static.json lacks (line spans,
mutability, constants/immutables/addresses). It does **not** depend on an answer key.

**Attack-surface score** (deterministic, explainable): +2 external/public state-changing · +2
accounting/token/oracle/migration/config/**amm_pol** tag · **+1 value-at-risk boost for oracle/amm_pol**
(price/AMM/POL machinery) · +1 external call · +1 loop · +1 permission modifier ·
+1 constant/immutable/address in accounting/oracle/config/amm_pol context · +1 initializer/constructor/
migration · +2 in a tainted sink. Items with score ≥ `coverage_policy.deep_pass_attack_surface_score_min`
(default 3) deserve a deep specialist; the rest are the cheap-sweep long tail.

**Value-at-risk (price/oracle/AMM/POL) priority.** The `amm_pol` tag (swap/liquidity/pool/tick/slippage/
buyback/POL/rebalance/slipstream/balancer/uniswap…) plus the expanded `oracle` tag (cumulative-price/spot/
getReserves/slot0/validatePrice…) flag the **price machinery where loss-of-funds concentrates**. A VaR boost
ranks these above generic state-changing functions, and `generate_context_pack.py` lists VaR★ clusters
**first** — investigated before sink-driven clusters, since oracle manipulation / missing slippage / POL
accounting are recurring Critical/High classes that static analysis routinely misses. (Recall-lab fix,
generalized from the Olas miss where ~15/23 awarded findings lived in a deprioritized oracle/POL cluster.)

## Dispositions

Every in-scope item must reach a terminal disposition:
- **cleared** — examined, no attacker path. REQUIRES `evidence` (file:line you read) **and** a
  `clear_reason`. A clear without both is rejected (the item stays pending).
- **finding** — attached to ≥1 finding (`finding_refs`). Set automatically by
  `link_findings_to_manifest.py` and by sweep `finding` decisions.
- **deferred_out_of_scope** — REQUIRES a reason. Auto-applied to `exclude_globs` paths
  (mocks/tests/pure-interfaces) at init.
- **assigned** — claimed for a deep pass but not yet resolved (e.g. sweep `needs_deep_pass`). Still
  blocks the gate (work remains).
- **unassigned** — initial state; blocks the gate.

Update a disposition: `python scripts/update_coverage_disposition.py --id <mid> --status cleared
--evidence "Foo.sol:42 onlyOwner" --clear-reason "owner-gated"`.

## How the coverage gate blocks the review gate

`run_pipeline.sh full` and `review-gate` run **Step 3.9** (`coverage_review_gate`) before writing
`review_gate.md`. It links findings → manifest, recomputes metrics, then **hard-fails** (`die`) if:
missing manifest/dispositions; any in-scope item `unassigned`; in-scope `assigned`-only;
`examined` without clear/finding; `cleared` without evidence/reason; `finding` without a ref;
`deferred` without a reason; duplicate/unknown ids. Then `min_confirm_gate.py` blocks if any
submission candidate lacks its confirmation skeleton.

Escape hatches (not recommended): `AUDITWATCH_COVERAGE_OVERRIDE=1`, `AUDITWATCH_MINCONFIRM_OVERRIDE=1`.

## Cheap sweep vs deep specialist review

- **Deep specialists** (`/ite-audit`) own high-attack-surface items — full ITE exploit reasoning.
- **Cheap sweep** (`/coverage-sweep`, an in-session skill) closes the long tail the specialists
  skipped: a *minimal, evidence-anchored* review of each remaining item — `cleared` (with span +
  reason), `finding`, `needs_deep_pass` (escalate), or `deferred_out_of_scope`. It is not allowed to
  clear without evidence, and must escalate (not clear) risky constants/addresses.

```
./run_pipeline.sh coverage-sweep        # prepare bundles → run /coverage-sweep skill → coverage_sweep_write.py
```

## Interpreting metrics (coverage ≠ detection)

`coverage_metrics.py` separates what the 42% conflated:
- **coverage_percent** = (cleared + finding) / in-scope — how much of the denominator was resolved.
- **finding_density_by_tag** — where findings concentrate.
- **unexamined_by_tag / unexamined_high_score_items / top_coverage_gaps** — the blind spots still open.

A future eval should report coverage%, detection-rate-on-covered, FP-rate, and missed-surface-rate
separately, so a low score attributable to coverage (fixable by the sweep) is not confused with a
reasoning failure.

## Rerun Beanstalk deterministically

```
# active audit = beanstalk-2024-05-eval2 (contracts shared, read-only)
./run_pipeline.sh coverage-manifest
python scripts/link_findings_to_manifest.py      # link the existing 48 findings
./run_pipeline.sh coverage-status                # see coverage% + top gaps
./run_pipeline.sh coverage-sweep                 # then /coverage-sweep skill + write
./run_pipeline.sh coverage-gate                  # confirm pass
```
The manifest is built from source + static.json only — no answer key — so the denominator is
reproducible across API-free and API runs (enables a fair parity test).

## How this protects API-free eval fairness

API-free and API modes now share the **same deterministic manifest** as the denominator. Coverage is
measured identically regardless of how reasoning was produced, so an API-free eval can be compared to
an API-mode eval on equal footing (coverage% is mode-independent; only detection-on-covered reflects
reasoning).

## Limitations

- **Source spans are regex/brace-match approximations.** `static.json` has no function line numbers,
  so spans are derived from source; each carries `source_span.method` (`regex_brace_match`,
  `regex_start_only`). Treat end-lines as approximate.
- **Magic numbers are not exhaustively enumerated** — constants/immutables/addresses are captured
  reliably; bare numeric literals are out of the manifest by default (high false-positive rate). Tag
  `decimals` flags the accounting/oracle precision constants that matter.
- **Contract attribution** for an item is best-effort (regex contract tracking); the id + file are
  authoritative.
- **`min_confirm_gate` checks presence, not truth.** It blocks vague/under-anchored candidates (missing
  skeleton) but cannot prove a precondition is reachable — deeper FP suppression is the deferred full
  `/confirm` system (see the eval backlog).
- The gate **will block** an audit until the sweep/specialists populate dispositions — that is the
  intended behavior, not a regression.

## Bridge escalation (cross-artifact lifecycle, thread guard, recipient/custody)

For bridge-shaped protocols, three additive components close under-escalation gaps (ArkProject AK-H4/M2/M3):
the **cross-artifact lifecycle** lens (`cross_artifact_lifecycle_audit.py`) keeps an out-of-scope artifact's
lifecycle audit-relevant through any in-scope controller; the **bridge thread escalation gate**
(`bridge_thread_escalation_gate.py`) blocks silent drops of bridge-relevant deep-analysis threads (escalate
or concretely invalidate); the **recipient/custody** lens (`recipient_custody_audit.py`) flags
non-receiver / no-retry asset locks. Full policy: `documentation/bridge_lifecycle_escalation_policy.md`.
Cairo support is future work.

## Deep-Solidity reasoning (cross-function invariants, special-focus clears, advisory escalation)

After the Recall eval (depth, not language, was the bottleneck), three advisory lenses + two routing rules
harden deep Solidity reasoning, always preferring `needs_deep_pass` over a thin clear: the **cross-function
invariant** lens (`cross_function_invariant_audit.py`, store-key/read-key, counter/limit, cross-function
reentrancy, queue compaction), the **asset-source consistency** lens (`asset_source_consistency_audit.py`,
amount-origin ≠ transfer-source), the **checkpoint/queue/returndata liveness** lens
(`checkpoint_liveness_audit.py`); the **special-focus strong-clear** rule in `coverage_sweep_write.py`
(a clear on a state-mutating gateway/checkpoint/collateral/queue surface needs the deep fields, not a thin
local note); and the **advisory escalation gate** (`advisory_escalation_gate.py`, high-risk advisory hit on
a cleared high-risk surface → `needs_deep_pass`). Full policy:
`documentation/deep_solidity_reasoning_policy.md`. Rust support remains future work.

## P315 — Mandatory full-coverage drive in the full workflow

The full workflow reaches **every necessary (in-scope) file** before producing a clean review gate.
"Necessary files" = the in-scope manifest items from `build_coverage_manifest.py` (production contracts;
mocks/tests/pure-interfaces are `deferred_out_of_scope`).

- **Depth model (prioritized-deep + mandatory full sweep):** specialists (`/ite-audit`) deep-dive the hot
  Priority Investigation Clusters first for DEPTH; this is ordering, not exclusion. Every remaining in-scope
  item is then examined by the **mandatory coverage sweep** (`/coverage-sweep`) with evidence-anchored
  dispositions. The `ite-audit` skill, the per-agent prompts, and `generate_context_pack.py` (which now lists
  ALL in-scope clusters, including a **"Remaining in-scope — mandatory sweep"** section) no longer drop
  low-signal files.
- **Enforcement (hard fail-closed + resumable drive):** `run_pipeline.sh` **Step 3.85** always (re)stages the
  full sweep over all in-scope items; the unchanged `coverage_completeness_gate.py` fail-closes the review gate
  until coverage is 100% (`review_gate_blocks_unassigned`/`review_gate_blocks_unexamined`). On a gap the gate
  stages the sweep and dies with the resumable loop (`/coverage-sweep` → `coverage_sweep_write.py` →
  `./run_pipeline.sh review-gate`), so completion can span sessions. `review_gate.md` carries a
  **Necessary-file coverage** summary (coverage % + any unexamined in-scope files) so under-coverage is never
  silent. Override: `AUDITWATCH_COVERAGE_OVERRIDE=1` (loudly logged; review gate marks coverage<100%).
- **No weakened evidence:** clears still require an evidence span + reason; high-surface items still cannot be
  cheap-cleared. "Reach all files" = examine with evidence, never rubber-stamp. Config flag:
  `coverage_policy.mandatory_full_sweep`.
