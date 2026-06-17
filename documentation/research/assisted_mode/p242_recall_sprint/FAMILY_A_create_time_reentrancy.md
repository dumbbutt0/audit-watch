# P242 Family A — `create_time_reentrancy` (RESEARCH-ONLY, un-wired)

is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[].

## Research / motivation
P236/P241 recurring miss: a create/mint/register/list/deposit/stake flow performs a callback-yielding external
interaction BEFORE committing the registration/limit/accounting state, with no reentrancy guard → a reentrant call
observes partially-initialized state (e.g. a stale per-address mint counter) and bypasses the invariant.

## Taxonomy / 4-signal gate (per-function classifier, +1 helper resolution)
S1 create-verb fn (mint/create/register/list/deposit/stake/open/start/add/airdrop/burnToMint/initialize) · S2 a
RECEIVER/arbitrary callback in the resolved body (`_safeMint`/`safeBatchTransferFrom`/`onERC721Received`/
`onERC1155Received`/`_mintProcessing`/`.call{`) · S3 a state-commit textually AFTER the callback (CEI violation) ·
S4 no nonReentrant. ADVANCE high = S1+S2+S3+S4.

## Anchor + scope
**In-repo anchor (recovered):** nextgen `NextGenCore.mint` → `_mintProcessing` → `_safeMint` before
`tokensMintedPerAddress += 1`, no guard (= nextgen H-01 mint-reentrancy). Replay also surfaces airDropTokens/
burnToMint (same pattern).
**Precision fix (P242):** dropped ambiguous ERC20 `safeTransferFrom`/`safeTransfer(`/`.call(` from S2 (ERC20
transferFrom triggers no recipient callback → the safeTransferFrom-before-_mint deposit pattern is the intentional,
CEI-safe shape; was 4 FPs on pooltogether + sentiment/concrete/reserve). Now 0 FP / 0 noise across 16 targets.
**Known blind spot:** cross-CONTRACT stale-check reentrancy + Seaport/conduit-mediated transfers (reNFT H-03) — not
detectable by a per-function source classifier.

## Files
scripts/create_time_reentrancy_{taxonomy,audit}.py · config/create_time_reentrancy_patterns.json ·
tests/create_time_reentrancy/ (7 tests, incl. NextGenCore.mint replay + ERC20-deposit regression) ·
research_finding_normalization.json entry.

## Stability classification
**PROMISING / READY-FOR-ADVISORY** — recovers the anchor family, 0 high-confidence FP, 0 noise across 16 diverse
targets; single in-repo anchor (no independent non-anchor TP in this corpus). Un-wired; promotion = human decision.
