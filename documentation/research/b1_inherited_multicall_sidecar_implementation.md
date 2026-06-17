# B1 Inherited-Multicall Sidecar — Implementation Report

**Type:** implementation of the approved B1 design (multicall-only inherited-executor attribution via an isolated,
research-only sidecar). The detector **taxonomy** is unchanged; the only detector-side change is an optional,
flag-gated merge path in the runner. The canonical `coverage_manifest.json`, the Step 3.9 coverage gate, routing,
answer keys, and frozen snapshots are untouched. The detector stays `is_gate:false` / `research_only:true` /
`routes_in_production:false` / `routed_manifest_ids:[]` and is **not promoted**.

## Purpose
Close the B1 *visibility* gap (the per-file manifest builder never attributes an inherited `multicall` to the
deriving in-scope contract) **without** changing the detector and **without** polluting the canonical manifest.
A separate sidecar attributes known inherited Solidity-level multicall executors to their derivers; the research
runner can optionally merge it for a visibility run only.

## Design
- **`scripts/build_inherited_multicall_sidecar.py`** (new) — reads a canonical manifest **read-only** to learn the
  in-scope files, parses each deriver's `contract X is …` clause, and for bases on the allowlist resolves the base
  source, confirms a Solidity-level multicall structurally, and emits one entry per (deriver, executor) into
  `inherited_executors.json`.
- **`scripts/multicall_invariant_audit.py`** (edited) — new optional `--inherited-sidecar <path>`. When provided,
  sidecar items are merged into the **in-memory** item list for that run only; sidecar-derived candidates are
  stamped with their provenance + un-routed flags. When absent, behavior is byte-for-byte identical (verified by
  test).

### Structural confidence gate (`is_solidity_multicall`)
A base is attributed only if its `multicall` body has: `bytes[]` in the signature **AND** literal `address(this)`
**AND** `delegatecall`/`functionDelegateCall` **AND** a parenthesised `for(`/`while(` loop. This is precisely what
**excludes solady `Multicallable`** (assembly `delegatecall(gas(), address(), …)` inside `for {} 1 {}` — no literal
`address(this)`, no parenthesised loop) and any low-confidence base.

### Fail-safe resolution
Base name must be on the allowlist (`{"Multicall"}`; `Multicallable` excluded). The base file is chosen by
token-overlap against the deriver's `Multicall.sol` import path (handles remap aliases like `@base/`); on a tie of
**identical-bodied** bases the lexicographically-first is chosen deterministically; a genuinely ambiguous or
unreadable base is **skipped, never guessed**.

## CLI usage
```bash
# build the sidecar (read-only; writes only the sidecar file)
python scripts/build_inherited_multicall_sidecar.py \
    --manifest audits/<id>/output/coverage_manifest.json \
    --workspace-root audits/<id>/contracts/<contest-root> \
    --out <sidecar>/inherited_executors.json

# research run: merge the sidecar for visibility (canonical manifest untouched)
python scripts/multicall_invariant_audit.py \
    --manifest audits/<id>/output/coverage_manifest.json \
    --inherited-sidecar <sidecar>/inherited_executors.json
```
`--workspace-root` should point at a root that contains **both** the in-scope sources and the base sources (incl.
`lib/`); the recorded `contracts_root` is often just the in-scope `src/`, which excludes `lib/`.

## Safety constraints (enforced / verified)
- Canonical `coverage_manifest.json` is **read-only** and never rewritten (test `test_merge_does_not_mutate_manifest`,
  `test_gate_input_unaffected`; integrity sha256 OK).
- The sidecar is a **separate file** never read by the Step 3.9 gate or routing.
- Default (no `--inherited-sidecar`) run is **byte-for-byte unchanged** (test `test_default_runner_unchanged`).
- Every sidecar entry and every sidecar-derived candidate carries `synthetic_attribution:true`,
  `source_kind:"inherited_multicall_sidecar"`, `research_only:true`, `routes_in_production:false`,
  `routed_manifest_ids:[]`.

## Sidecar schema (`inherited_executors.json`)
Top-level: `schema_version`, `source_kind:"inherited_multicall_sidecar"`, `research_only:true`,
`routes_in_production:false`, `is_gate:false`, `manifest`, `workspace_root`, `base_multicalls_found[]`, `items[]`,
`skipped[]`. Each `items[]` entry: `id` (`sidecar:<target_file>:<target_contract>:<base_contract>:<signature>`,
deterministic), `kind:"function"`, `contract` (=deriver), `name:"multicall"`, `file` (=base source, where the body
is read), `signature`, `source_span`, `in_scope:true`, `target_contract`, `target_file`, `base_contract`,
`base_source_file`, `attribution_reason`, plus the four safety flags.

## Supported bases
OpenZeppelin `utils/Multicall`, Uniswap-v3-periphery `base/Multicall`, and in-repo Solidity-level `Multicall`
bases using `bytes[]` + `address(this).delegatecall` (or OZ `Address.functionDelegateCall(address(this), …)`) in a
parenthesised loop.

## Unsupported (deliberately skipped)
solady/solmate `Multicallable` assembly delegatecall; arbitrary inheritance; diamond/facet inheritance;
typed-struct dispatch; internal-call batch systems. (assembly recognition is a separate detector item, out of
scope.)

## Validation results (approved B1 targets)

Builder output: Revert → 2 attributed (V3Vault, AutoCompound ← OZ `utils/Multicall`); Panoptic → in-scope derivers
CollateralTracker, PanopticPool, SemiFungiblePositionManager ← in-repo `base/Multicall` (PanopticFactory is
out-of-scope, correctly not attributed); Maia → 0 (solady `Multicallable` not vendored **and** would fail the
assembly gate).

Detector (unchanged) run, baseline vs canonical ∪ sidecar:

| Target | Before (baseline) | After (with sidecar) | Δ | Shape/confidence | Result |
|---|---:|---:|---:|---|---|
| Revert Lend | 0 (MISS) | **2** | +2 | `delegatecall_self_context/medium` (V3Vault, AutoCompound) | **MISS → executor candidate** |
| Panoptic | 0 (TN) | **3** | +3 | `delegatecall_self_context/high` (CollateralTracker, PanopticPool, SFPM) | **MISS/TN → executor candidate** |
| Maia | 0 (MISS) | **0** | 0 | — | **remains MISS** (solady assembly unsupported) |
| OZ control | medium | medium | 0 | base manifested directly; sidecar N/A (it's the base, not a deriver) | unchanged |
| UniV3 control | high | high | 0 | base manifested directly; sidecar N/A | unchanged |

- **Coverage delta:** +5 inherited executor candidates across 2 of 3 targets; category *inherited-library multicall
  (Solidity-level)* Unsupported → Supported. (Panoptic yielded 3, not the 2 initially scoped, because
  CollateralTracker is also an in-scope Multicall inheritor — a more complete, correct result.)
- **Precision delta:** **0 new wrong-domain / noise false positives.** Every new candidate is a *correct* executor
  identification (a real `bytes[]` self-delegatecall multicall). The new flags are benign-but-real multicalls (the
  detector flags opportunity, not a bug) — i.e. the expected, documented **volume** cost, not noise. This is why
  the executor flag must stay non-routing.
- **Flags:** all runs `is_gate:false`/`research_only:true`/`routes_in_production:false`/`routed_manifest_ids:[]`;
  all sidecar-derived candidates carry full synthetic/inherited metadata.

Validation artifacts: `documentation/research/_b1_experiment/_sidecar/{revert,panoptic,maia}_inherited_executors.json`
and `…/_sidecar/_runs/<slug>/{baseline,with_sidecar}/output/multicall_invariant_audit.json`.

## Known limitations
- **Assembly multicalls (solady/solmate) are not surfaced** — by design; needs a separate detector-implementation
  effort, not a manifest fix.
- **`--workspace-root` may need to be supplied** when the manifest's `contracts_root` is the in-scope `src/` only
  (excludes `lib/`); otherwise base resolution finds nothing and the builder fails safe (0 attributions).
- The sidecar surfaces benign multicalls broadly (volume) — acceptable for research, **not** for routing.
- Builder is regex-based (consistent with `build_coverage_manifest.py`); it relies on the base being physically
  present in the workspace.

## Rollback notes
Fully reversible with no residue: delete `scripts/build_inherited_multicall_sidecar.py`,
`tests/multicall_invariant/test_b1_sidecar.py`, this doc, and `documentation/research/_b1_experiment/_sidecar/`;
and remove the `--inherited-sidecar` block (arg + merge + candidate stamp + the two conditional report keys) from
`scripts/multicall_invariant_audit.py`. No canonical manifest, gate, routing, or detector-taxonomy change to undo.

## Integrity verification
| Check | Result |
|---|---|
| `multicall_invariant_taxonomy.py` / `multicall_invariant_patterns.json` / `advisory_escalation_gate.py` / `build_coverage_manifest.py` sha256 | **OK — 0 drift** |
| `multicall_invariant_audit.py` | **Intentionally changed** (optional sidecar merge; taxonomy logic untouched) |
| Canonical `coverage_manifest.json` (Revert/Panoptic/Maia) sha256 | **OK — 0 drift** |
| Frozen `pre_answer_key_snapshot` baselines / `ground_truth*` | **untouched** (none modified) |
| Routing / Step 3.9 gate | **untouched**; `routed_manifest_ids:[]` on all runs |
| `tests/multicall_invariant/` | **25 passed** (14 prior + 11 new) |

**Integrity verdict: VERIFIED CLEAN** (the single intended exception is the runner's optional merge path).

## Final recommendation
**Keep research-only. Do not route. Do not promote.** The sidecar may be used only for research multicall-
visibility runs until separately approved. It is opt-in (`--inherited-sidecar`), isolated from the canonical
manifest and the production gate, and surfaces benign executors broadly (volume) — so it is a *visibility* aid for
the research lens, not a finding source.
