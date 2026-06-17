# ArkProject NFT Bridge — Scope Reconstruction (public sources only)

Reconstructed from the repo README scope table + foundry.toml + source pragmas. **No answer-key /
submissions consulted** (`answer_key_used: false`).

- **Repo:** github.com/Cyfrin/2024-07-ark-project @ `273b7b94986d3914d5ee737c99a59ec8728b1517`
- **Full contest:** 2,301 nSLOC, bilingual — Ethereum (Solidity L1) + Starknet (Cairo L2), bridging ERC-721
  via the Starknet L1↔L2 messaging protocol (Everai collection).

## Tool-scope decision (language limitation, not a scope judgment)

The Audit-Watch coverage/manifest/gate/lens machinery is **Solidity-only**. The Cairo L2 side
(`starknet/src/**`) is **in the contest** but **out of current pipeline capability** and is **excluded**
from the pipeline run (no hand-analysis — that would violate the no-mid-run-tuning rule). It is recorded
explicitly in `program_scope.json → excluded_cairo_out_of_tool_scope` and scored in a separate bucket.

## In-scope (Solidity L1) — the eval surface (12 files)

Bridge.sol · Escrow.sol · Messaging.sol · Protocol.sol · State.sol · UUPSProxied.sol · sn/Cairo.sol ·
token/CollectionManager.sol · token/Deployer.sol · token/TokenUtil.sol · IStarklane.sol · IStarklaneEvent.sol

Surface map to the special-focus areas:
- **Message validation** → Messaging.sol, Protocol.sol (request hash/header, message consume).
- **Bridge custody** → Escrow.sol (lock/release accounting).
- **NFT lock/release/burn/mint** → Bridge.sol (deposit/withdraw), token/CollectionManager.sol, Deployer.sol.
- **Replay / domain separation** → Protocol.requestHash, Bridge replay TODO (Bridge.sol:111), Messaging.
- **Alternative entrypoints / proxy** → UUPSProxied.sol (UUPS upgrade), Bridge external entrypoints, State.
- **Economic shift/math** → minimal (bridge has little estimator math) — recorded if the lens fires.

## Out-of-scope Solidity (excluded from the manifest)
sn/IStarknetMessagingLocal.sol · sn/StarknetMessagingLocal.sol · TestMessaging.sol ·
token/{ERC1155Bridgeable, ERC721Bridgeable, IERC1155Bridgeable, IERC721Bridgeable}.sol

## Build/test
Foundry; `forge build` SUCCESS (82 files, solc 0.8.30). `forge test` 21/27 pass — the 6 failures are
Foundry-1.5.1 harness incompatibilities (`testFail*` removal + cheatcode depth), not contract defects.
See `output/pre_audit_snapshot/build_status.json`.
