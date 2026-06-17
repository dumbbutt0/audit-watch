# Getter-vs-State Reconciliation Review

Use for items surfaced by `scripts/getter_state_audit.py`. This lens is about the **correctness of
returned information and helper control flow**, not generic view-function scanning. A getter is dangerous
when downstream logic trusts the **shape, ordering, freshness, or encoding** of its return value.

Read the function body (and every consumer). Answer each question with evidence (file:line):

1. **What state is read?** List the exact storage slots / struct fields / globals the function reads.
2. **What value is returned?** Describe the return type(s) and what each is supposed to mean.
3. **Is the returned value transformed?** (aggregation, scaling, sum/loop, derived) — or a raw read?
4. **Does the return field match the intended field?** (e.g. a "counter" getter returning a different
   stored field, or `blueprintNonce[wrongId]`).
5. **Does return ordering match consumer expectations?** (tuple order, token0/token1, amount/bdv).
6. **Are default branches correct?** (`return 0`, `type(uint).max`, `false`, `address(0)`) — and do
   consumers handle each sentinel?
7. **Is ABI encoding/decoding correct?** Do `abi.decode` types match the struct actually passed
   (e.g. AdvancedPipeCall vs AdvancedFarmCall)?
8. **Are calldata/memory offsets correct?** (clipboard/paste/slice helpers; off-by-word errors).
9. **Are array lengths and indexes correct?** (output sized to the right input; in-bounds indexing).
10. **Is sorting or comparison logic correct?** (pivot/partition/stable order, equal keys) — a broken
    sort corrupts downstream per-element accounting.
11. **Is this getter consumed by a state-changing path?** Name the mutating consumer(s). A wrong/stale
    return that only feeds another view is lower impact than one that drives a mint/transfer/settlement.
12. **Could a stale or incorrect return value cause protocol impact?** Trace the worst-case consumer
    consequence end-to-end (no PoC required for eval classification).

**FP discipline:** do not flag trivial `return s.x` getters, constant-returning views, units-owned pure
math, comment-only mismatches, or event-only ABI words. Require a real return-shape/ordering/encoding/
freshness defect that a consumer can be misled by.

**Classification (pick one):**
`confirmed_eval_finding` | `partial_eval_finding` | `real_world_poc_later` | `duplicate_of_existing` | `false_positive`
