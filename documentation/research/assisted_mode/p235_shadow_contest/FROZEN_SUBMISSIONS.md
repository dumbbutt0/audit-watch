# P235 — Frozen submission drafts (predictions, pre-reveal)

> Frozen BEFORE the answer key was fetched. Predicted severity/impact/confidence/evidence-depth are the system's
> own pre-reveal judgments. No edits after reveal.

| ID | Predicted severity | Predicted impact | Confidence | Evidence depth | Submission-ready w/o rewrite? |
|---|---|---|---|---|---|
| RENFT-01 | **High** | Permanent loss of lent NFT + escrowed payment; renter bricks reclaim by removing Stop module | Confirmed (runtime L3, 2/2) | L3 (real-contract PoC + control) | YES |
| RENFT-04 | Medium | Renter destroys/degrades or siphons value from rented NFT (burn/claim/consume) | High (reasoned; token-dependent) | L2 (path + selector analysis) | Mostly (needs token-specific PoC) |
| RENFT-05 | Medium | Protocol-signer authorization reuse across orders within expiry | Medium | L2 (signature-scheme analysis) | Mostly |
| RENFT-02 | Medium | Active hook nullifies all guard transfer/module protections | Medium (admin-config fragility) | L2 | Needs framing as design risk |
| RENFT-03 | Medium→QA | Whitelisted delegate fully escapes guard (protocol explicitly assumes restriction) | Medium | L1 (acknowledged in NatSpec) | Likely QA/known |
| RENFT-06 | Low | Cross-fork EIP-712 replay | High | L1 | YES (QA) |
| RENFT-07 | Low/Info | Non-standard typehash encoding (self-consistent) | High | L1 | YES (QA) |
| RENFT-08 | Low | Safe address not pre-computable (global salt counter) | Medium | L1 | YES (QA) |
| RENFT-09 | Info | Fragile hand-rolled accumulator memory invariant | Medium | L1 | YES (QA) |
| RENFT-10 | Info | Validation-last ordering in Stop (currently atomic-safe) | High | L1 | YES (QA) |

## Flagship submission draft — RENFT-01 (High)
**Title:** Renter can permanently brick rental reclaim by disabling the Stop module (Guard validates the wrong
`disableModule` argument).
**Vulnerability detail:** `Guard._checkTransaction` decodes the `disableModule(address prevModule, address module)`
argument at calldata offset `0x24`, which is `prevModule`, not the `module` being removed (offset `0x44`). Its
whitelist gate therefore validates `prevModule`. A renter enables any admin-whitelisted extension `E`
(`SENTINEL→E→Stop`), then calls `disableModule(E, Stop)`; the guard sees `prevModule=E` (whitelisted) and allows the
core, non-whitelisted **Stop** module to be removed.
**Impact:** `Stop.stopRent` reclaims via `safe.execTransactionFromModule`, which now reverts forever (GS104). The
lender can never recover the rented NFT and the escrowed payment is stranded — permanent, irreversible loss of the
lent asset. Permissionless (ordinary renter); precondition is that ≥1 extension is whitelisted (the feature's
intended use, exercised in the protocol's own tests).
**PoC:** `pocs/p235/renft/RENFT01_DisableModuleBypass.t.sol` — 2/2 PASS on real unmodified contracts; asserts
`isModuleEnabled(Stop)` flips true→false and the reclaim primitive then reverts; control shows a direct disable
(`prevModule=SENTINEL`) is correctly blocked.
**Fix:** read the disabled module from offset `0x44` (the `module` arg) in the `disableModule` branch.
