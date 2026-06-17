# Synthetic fixtures — bridge cross-artifact lifecycle + recipient/custody + thread escalation

Minimal reference examples for the bridge-escalation features (ArkProject AK-H4 / AK-M2 / AK-M3
miss-classes). The deterministic tests in `tests/bridge_escalation/` drive the classifiers/gate with
inline snippets mirroring these files; the `.sol` files are the human-readable reference.

| Fixture | Feature | Expected outcome |
|---|---|---|
| `deployer_no_ownership_transfer.sol` | cross-artifact lifecycle | in-scope deployer deploys upgradeable ERC721, no ownership handover → `cross_artifact_lifecycle_risk` / `lifecycle_under_escalated` |
| `factory_no_disable_initializer.sol` | cross-artifact lifecycle | factory deploys proxy, never `_disableInitializers` → risk (missing `disable_initializers`) |
| `withdraw_to_non_receiver.sol` | recipient/custody | bridge withdraw `safeTransferFrom`s to a recipient with no receiver check → `non_receiver_lock` (high-risk) |
| `dropped_reentrancy_thread.json` | thread escalation guard | a promising bridge reentrancy thread + a vague drop → gate **BLOCKS** (no escalation, no concrete invalidation) |
| `out_of_scope_artifact_uncontrolled.sol` | scope rule | out-of-scope artifact with NO in-scope controller → NOT flagged (cross-artifact requires an in-scope controller) |
| `safe_lifecycle.sol` | safe (no FP) | deployer `_disableInitializers` + transfers ownership + retains upgrade authority → `lifecycle_cleared_with_local_proof`, no escalation |

Rule: an out-of-scope artifact's lifecycle is audit-relevant **only through an in-scope controller** that
deploys/initializes/owns/upgrades/configures/holds-custody-over it. A bridge-relevant deep-analysis thread
must be escalated or concretely invalidated (exact sink + attacker entrypoint + unreachable/bounded/subsumed
reason). Cairo support is future work — not covered here.
