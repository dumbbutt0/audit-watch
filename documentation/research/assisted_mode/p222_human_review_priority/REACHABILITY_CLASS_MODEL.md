# Reachability class model (P222, extends P221)

`reachability_class` explains **why a candidate is or is not auto-reportable** — who has to act for the bug
to fire. It is **not** a severity label and **not** a submission label. It lives in a namespace entirely
separate from the `attacker_model` severity enum that `decide()` reads, so adding/changing a class never
moves severity (proven byte-identical in `SEVERITY_INVARIANCE` / `metrics.json`).

P221 introduced six classes; P222 adds four more so the full reachability spectrum can be expressed.

| class | meaning | auto-reportable? |
|-------|---------|------------------|
| `UNPRIVILEGED_REACHABLE` | any EOA can trigger it with no privileged setup | yes (normal path) |
| `PROGRAM_ACCEPTED_ACTOR_REACHABLE` | a program-accepted actor (per the program's own rules) | usually yes — program-dependent |
| `TRUSTED_SYSTEM_ACTOR_REACHABLE` | an authorized trusted-system actor: TSS, bridge/cross-chain executor, gateway, protocol module | **no** — program threat-model decision required |
| `KEEPER_OR_RELAYER_REACHABLE` | a keeper / relayer / off-chain automation actor | **no** — threat-model decision required |
| `ADMIN_OR_OWNER_REACHABLE` | an admin / owner / privileged role | **no** — usually accepted trust, but core-invariant cases need a human |
| `PRIVILEGED_ONLY_REACHABLE` | requires *some* privileged caller (unspecified which) | **no** — privileged trigger |
| `COMPROMISE_REQUIRED` | requires key/role compromise | **no** — out of normal threat model |
| `SELF_INFLICTED_ONLY` | only the victim acting against themselves | **no** — not a finding |
| `REACHABILITY_UNKNOWN` | reachability not determinable from in-scope source | unknown — needs interpretation |
| `SOURCE_REFUTED` | the path was disproven against real source | no — refuted |

## Derivation (deterministic, artifact-backed)
Computed in `sync_hunt_findings.build_bundle` (P221 `_REACH_CLASS` map) from the L3 record's
`attacker_model`, **overridable** by an explicit `reachability_class` in the L3 record (set when the gate is
a specific trusted-system actor — e.g. ZETA-04's `onlyTssAddress` → `TRUSTED_SYSTEM_ACTOR_REACHABLE`).
`permissionless→UNPRIVILEGED_REACHABLE`, `program_accepted→PROGRAM_ACCEPTED_ACTOR_REACHABLE`,
`privileged_only/privileged/trusted_admin→PRIVILEGED_ONLY_REACHABLE`, `compromise_required→COMPROMISE_REQUIRED`,
`unknown/none/conditional→REACHABILITY_UNKNOWN`. The four P222-added classes are applied **only** when an L3
record records them explicitly (HARD RULE — no invention).

## Which classes gate the HIGH human-review lane
The HIGH rule (`PRIORITY_RULES.md`) fires only for the **privileged-but-trusted-actor** band:
`{TRUSTED_SYSTEM_ACTOR_REACHABLE, PROGRAM_ACCEPTED_ACTOR_REACHABLE, KEEPER_OR_RELAYER_REACHABLE,
ADMIN_OR_OWNER_REACHABLE, PRIVILEGED_ONLY_REACHABLE}`.

`UNPRIVILEGED_REACHABLE` is **deliberately excluded** — those findings are reportable through the normal
path and don't need the human-review lane (this is why an H5-style unprivileged finding is never pulled into
the lane). `REACHABILITY_UNKNOWN`, `SELF_INFLICTED_ONLY`, `COMPROMISE_REQUIRED`, and `SOURCE_REFUTED` are
also excluded from HIGH.
