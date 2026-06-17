# Bridge Lifecycle & Escalation Policy

**An out-of-scope artifact's lifecycle is audit-relevant through any in-scope contract that controls it,
and a bridge-relevant deep-analysis thread may never be silently dropped.** Three additive components
(two advisory recall lenses + one no-silent-drop gate) close the ArkProject bridge under-escalation
miss-classes (AK-H4 cross-artifact lifecycle, AK-M2 recipient lock, AK-M3 dropped reentrancy thread)
without weakening any strict gate or adding gate false positives.

## 1. Cross-artifact lifecycle rule (advisory lens)

If an in-scope contract **deploys / initializes / owns / upgrades / configures / transfers ownership of /
routes to / holds privileged control or custody over** an artifact, that artifact's lifecycle invariants
stay in scope **through the in-scope controller** — even when the artifact's own file is out of strict
scope (or absent from the manifest entirely).

`scripts/cross_artifact_lifecycle_audit.py` (config `config/cross_artifact_lifecycle_patterns.json`,
taxonomy `cross_artifact_lifecycle_taxonomy.py`) classifies in-scope deployer/factory/custodian/upgrader
items and tracks: deployer/factory creates a token/collection/escrow/vault/bridge-asset/proxy; initializer
called or not; `_disableInitializers` called or not; owner/admin/upgrader assigned; ownership transfer
present or missing; proxy-admin/implementation/beacon relationship; bridge custody authority over the
deployed asset; upgradeability of the deployed artifact; whether the artifact is controllable after
deployment. **Statuses:**

| status | meaning |
|---|---|
| `cross_artifact_lifecycle_risk` | in-scope controller deploys/controls an artifact AND a lifecycle step is missing (filed or risk-acknowledged) |
| `cross_artifact_scope_linked` | the controlled artifact resolves to a `deferred_out_of_scope` manifest item — link recorded so it stays audit-relevant |
| `lifecycle_under_escalated` | a lifecycle risk with **no finding referencing it** (the AK-H4 case: discovered, never filed) |
| `lifecycle_cleared_with_local_proof` | controller demonstrably handles the full lifecycle (deploy → `_disableInitializers` → ownership transfer → upgrade authority); safe, no escalation |

Detection of `new X(` is **case-sensitive** so Solidity memory allocations (`new string(`, `new bytes(`,
`new uint256[](`) are not mistaken for contract deploys.

### Cross-artifact scope-linking rule

A finding/clear may not be skipped *merely because the vulnerable artifact is outside the strict file
list* when its lifecycle is controlled by an in-scope contract. The lens flags such relationships even
when the artifact is not in the manifest at all (the ArkProject reality: `ERC721Bridgeable` was a
separate excluded file). When the artifact *is* a `deferred_out_of_scope` manifest item, the link is
recorded explicitly (`cross_artifact_scope_linked`).

**Invalid clear:** "the deployed token is out of scope, so its ownership/upgrade is not our concern."
**Valid clear (`lifecycle_cleared_with_local_proof`):** "the in-scope deployer calls `_disableInitializers`,
`transferOwnership(bridge)`, and the bridge retains `_authorizeUpgrade` — full lifecycle handled locally."

## 2. Bridge thread escalation rule (no-silent-drop gate)

`scripts/bridge_thread_escalation_gate.py` (terms in `scripts/bridge_terms.py`) blocks the review gate when
a **promising** deep-analysis thread whose text mentions any bridge term — `bridge, deposit, withdraw,
mint, burn, lock, release, escrow, collection, message, L1, L2, handler, retry, replay, recipient,
onERC721Received, ownership, initializer, proxy, upgrade, whitelist, mapping, custody` — is dropped without
either:

- **escalation** — a finding references its `thread_id` (in `thread_refs`); or
- **concrete invalidation** in `data/threads/_bridge_thread_dispositions.json`:
  `{thread_id, exact_sink, attacker_entrypoint, resolution{type ∈ unreachable|bounded|subsumed, reason}}`,
  with a **non-vague** reason.

Vague labels (`low confidence`, `already covered`, `needs more evidence`, `minor`, `n/a`, `unclear`,
`maybe`) are rejected. Blocked threads route to `human_review_queue.jsonl` (no silent drop). Gated by
`coverage_policy.bridge_thread_escalation_strict[_full_audit]` (blocks under `AUDITWATCH_FULL_AUDIT=1`);
override `AUDITWATCH_BRIDGE_THREAD_OVERRIDE=1`. Mirrors the triage no-silent-clear / coverage-gate
precedents. **Non-bridge threads are unaffected** — normal drop rules still apply.

**Invalid drop (blocks):** thread "withdraw reentrancy releases escrow to recipient" dropped with
"low confidence, already covered."
**Valid invalidation (passes):** `exact_sink=Escrow._withdrawFromEscrow safeTransferFrom (Escrow.sol:79)`,
`attacker_entrypoint=Bridge.withdraw(request) by the listing recipient`, `resolution=bounded: escrow slot
zeroed before the external call (CEI); a reentrant withdraw finds _escrow==0 and returns false.`

## 3. Recipient / custody compatibility rule (advisory lens)

`scripts/recipient_custody_audit.py` (config `config/recipient_custody_patterns.json`) flags asset-delivery
incompatibility: `safe_vs_raw_transfer`; `non_receiver_lock` (a `safeTransferFrom`/`safeMint` to a recipient
with no `onERC721Received`/`onERC1155Received` capability check → permanent revert-lock); `no_retry_recovery`
(failed delivery with no retry/recover path); `custody_released_but_trapped` (custody accounting says
released while the asset stays trapped). High-risk items route to `bridge_custody_review`. Recovers AK-M2.

## Configuration

`config/agent_policy.json → coverage_policy`: `cross_artifact_lifecycle_advisory: true`,
`recipient_custody_advisory: true`, `bridge_thread_escalation_strict: false`,
`bridge_thread_escalation_strict_full_audit: true`. The two lenses are **advisory** (never block → no gate
FP); only the thread guard blocks, and only on a full audit, with an override + human-queue routing.

## Cairo support is future work — NOT part of this patch

The ArkProject Cairo L2 side remains out of pipeline capability. These features operate purely on the
Solidity side. Cross-chain L1↔L2 custody correlation and Cairo `.cairo` ingestion are tracked as future
work (see `documentation/evals/ark-project-2024-07/strict_eval_report.md`), not addressed here.
