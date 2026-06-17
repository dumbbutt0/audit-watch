# Design — `sibling_function_parity` detector

Research-only, deterministic, un-wired. Built from the Phase-2 corpus
(`documentation/research/sibling_function_candidates.md`, 1489 candidate pairs / 984 asymmetric / 248
name-stem). Architecture mirrors `permit_asset_binding` (config + pure taxonomy + audit + tests).

## Threat Model

Two or more functions in a contract reach the **same state transition** (token transfer, mint/burn,
debt/share update, registry change) but one omits a guard, validation, recipient resolution, cap check,
state update, or pause gate that its sibling enforces. An attacker drives the **weaker** sibling to
reach the transition while bypassing the control — sending rewards to the wrong recipient (blackhole
M-04), executing without the validated threshold (Size M-02), skipping a cap, or leaving accounting
inconsistent (Size M-12). The detector surfaces the asymmetric sibling pair for review; it does **not**
assert exploitability or severity (research-only).

## Signal Sources

Per function (extracted from the brace-matched body via regex, manifest for modifiers):
- **call-set** — internal/external call identifiers (`_CALL` / `.method` regex), minus language
  keywords. Used for sibling kinship *and* asymmetry.
- **state-write targets** — LHS of `=`/`+=`/`-=` (incl. `x[..]`, `x.y`).
- **guard signals** — `require(` / `revert` / `if(...)return|break` count; `msg.sender` gates.
- **modifiers** — from manifest `modifiers`.
- **emits** — `emit X` (recorded but **never** the sole basis for a finding).

**Sibling kinship (precondition):** name-stem match after stripping variant affixes
(`_many`/`batch`/`For`/`To`/`All`/`s`/`internal`) **OR** ≥2 shared calls with Jaccard ≥ 0.3.

**Asymmetry → finding (the FP-critical part):** the component present in one sibling and absent in the
other must be **security-relevant controlled vocabulary**, classified into a `parity_type`:
| parity_type | controlled tokens (config) |
|---|---|
| validation_parity | `require`-count delta; calls matching `validate|check|verify|ensure|assert|_require` |
| recipient_parity | `getOriginalOwner|resolve|recipientOf|beneficiary|ownerOf`-resolution branch |
| cap_enforcement_parity | tokens matching `cap|limit|ceiling|maxSupply|borrowCap|maxMint` |
| access_control_parity | modifier delta; `require(msg.sender` / `onlyX` delta |
| registry_parity | `add|remove|register|deregister|delete|push|pop|updateHolding|updatePosition` |
| state_transition_parity | a state-write target in one, absent in the sibling, on a shared value-move |
| pause_emergency_parity | `whenNotPaused|paused|emergency` delta |

The missing token must NOT be: an event name, an interface/type cast (`I[A-Z]\w+`, `address`, `uint*`),
or a pure-getter (`balanceOf|totalSupply|length|decimals`) — these dominate the corpus noise and are
excluded by `exclude_components`.

## Reachability Rules (when a parity gap is flagged, not "exploitable")

Flag only when the **weaker** sibling is reachable and mutating:
1. weaker sibling is `external`/`public` (or `internal` reached by an external sibling), **and**
2. both siblings share the downstream mutating call/state-write (the same transition), **and**
3. the missing component sits on that shared mutating path (not in dead/branch-only code).
No privileged-setup assumption is asserted; we report the asymmetry + the shared path as *evidence*,
leaving exploitability to human/deep-pass review (consistent with research-only "signal, don't submit").

## False-Positive Controls (Phase-7, validated against the corpus noise)

1. **Two-signal gate** — sibling kinship AND a controlled-vocabulary asymmetry. (Kills the 736
   asymmetric-but-non-kin / non-security pairs.)
2. **Controlled-component filter** — missing token must be security-relevant; exclude
   events/type-casts/getters. (Kills `_mint`/`mint` `Transfer`-event diffs, `IERC20`/`IBribe` casts.)
3. **Wrapper suppression** — if one sibling's body is essentially a single call to the other
   (`return f(...)` / one statement), suppress (overload/forwarder).
4. **Both-admin suppression** — if both siblings carry an admin modifier (`onlyOwner|onlyRole|
   onlyGovernance|onlyMaintainer`), the asymmetry is intended maintenance; suppress unless the weaker
   sibling is externally reachable by non-admins.
5. **View/pure & interface/abstract suppression** — non-mutating or body-less siblings dropped at
   manifest read.
6. **No observability-only findings** — a missing `emit` with no correlated state/guard asymmetry is
   never emitted.
7. **One-level helper resolution** — before declaring a component "missing", append same-contract
   helper bodies the sibling calls; if the component appears there, downgrade/suppress (avoids the
   "validation moved into a shared `_validate()`" FP).

## Confidence

- **high** — name-stem sibling + ≥2 shared calls + exactly the missing controlled component on the
  shared path, weaker sibling external (the blackhole-M-04 shape).
- **medium** — behavioral-kinship sibling (no name stem) + one missing controlled component.
- **low / needs_context** — weak kinship, or component possibly relocated to an unresolved helper.

## Output contract (research-only)

`output/sibling_function_parity_audit.json`: `lens`, `is_gate:false`, `research_only:true`,
`routes_in_production:false`, `routed_manifest_ids:[]`, `by_confidence`, `candidates[]` each with
`contract, sibling_pair:[A,B], parity_type, missing_component, confidence, evidence, signals,
file_line_refs, in_scope, manifest_id, false_positive_controls`. Never mints findings, never routes.
