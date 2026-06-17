# Recall 2025-02 miss-class replay fixtures (reconstructed)

Minimal reconstructed Solidity for the 8 Recall miss classes the deep-Solidity upgrade targets. These
**prove the new routing/validator behavior** (a lens detects the shape; a thin clear on the special-focus
function is routed to `needs_deep_pass`; a high-risk advisory hit escalates) — they do **not** re-score the
frozen Recall eval and never read it beyond its hash. Each shape ships a **safe-equivalent** counterpart so
the tests also prove no false positive.

| Miss | File | Shape the lens keys on | Lens / rule | Safe equivalent |
|---|---|---|---|---|
| H-03 | `h03_hash_mismatch.sol` | writer keys with `toHash(`, reader looks up with `toTracingId(` | cross_function_invariant: store_key_vs_read_key_divergence | both sides use `toHash` |
| H-04 | `h04_batch_count_overflow.sol` | `commitMsg` increments batch count with no local limit check; limit enforced only in `ensureValid` | cross_function_invariant: counter_limit_divergence | writer checks the limit locally |
| H-05 | `h05_leave_wrong_asset.sol` | pays a `genesisBalance` (supply) amount out of `collateralSource` | asset_source_consistency: source_family_mismatch | pays from `supplySource` |
| H-06 | `h06_cross_function_reentrancy.sol` | `nonReentrant leave()` makes a native transfer; sibling `addBootstrap()` mutates state unguarded | cross_function_invariant: cross_function_reentrancy | all state-mutating siblings guarded |
| H-07 | `h07_compact_index_skip.sol` | `compact()` loop iterates with an absolute index vs pending count | cross_function_invariant + checkpoint_liveness: compaction_skip | index relative to pending range |
| H-08 | `h08_permissionless_register.sol` | `register()` with no caller-authenticity check on a gateway surface | special_focus strong-clear (a thin clear is rejected → needs_deep_pass) | owner/actor-gated register |
| H-09 | `h09_recipient_blocks_checkpoint.sol` | external call inside a checkpoint/batch loop; unbounded returndata | checkpoint_liveness: recipient_blocks_checkpoint / unbounded_returndata | bounded returndata / try-catch skip |
| M-04 | `m04_flooding_confirmchange.sol` | per-call append to a change log on a checkpoint surface, no rate limit | checkpoint_liveness: floodable_state | bounded / paused |

Reconstructed from the public Recall report file/function attributions (post-answer-key); no frozen-eval
source is copied.
