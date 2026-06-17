# Pre-submission gate — Cred._addCredIdPerAddress (P89-H05)

Strict, reject-first checklist. A package is **READY_FOR_HUMAN_REVIEW** only if every machine-checkable item
is ✅ and the only remaining open items are the two **external human checks** (scope/program-rules and
duplicate/public-known). Any other ❌ / TODO blocks the package. **This gate never authorizes submission.**

> **Generated state: this is a freshly scaffolded gate. Every evidence-backed item below is `TODO / UNPROVEN`
> until the PoC reproduces and the source references are filled. The generator NEVER emits a PASS for a
> finding-specific item, and NEVER emits READY_FOR_HUMAN_REVIEW.**

| # | Check | Status | Basis |
|---|---|---|---|
| 1 | **Source version pinned** | ✅ PASS | 2465e04364b759c721f1a0aebace69920411f8aa |
| 2 | **Asset / scope verified** | ⏳ PENDING — HUMAN | A human must confirm `Cred` is in the program's in-scope asset list and the impact class is in scope. *Allowed open blocker.* |
| 3 | **Duplicate / publicly-known check** | ⏳ PENDING — HUMAN | A human must check known-issues and prior submissions. No answer key / public report consulted. *Allowed open blocker.* |
| 4 | **Severity rationale source-backed** | ❌ TODO | Fill from source + executable result (see `reviewer_notes.md`). Must not be assumed. |
| 5 | **Executable PoC present** | ❌ TODO | `CredAddCredIdPerAddressPoC` must fail on vulnerable source for the stated reason via `forge test --match-test test_P89_H05_invariant -vv`. Scaffold is a non-passing stub until implemented. |
| 6 | **No answer-key dependence** | ❌ TODO | Confirm bug chain + PoC derive only from in-scope source and executable behavior. |
| 7 | **No unsupported economic assumptions** | ❌ TODO | List the only assumptions the PoC relies on; no extra price/market assumptions. |
| 8 | **No scanner/eval claims in the report** | ❌ TODO | `submission_draft.md` must reference only contract source + the PoC — no tooling/eval/internal-phase language. |
| 9 | **No overclaiming beyond the test** | ❌ TODO | The report must claim exactly what the test shows, no more. |

## Gate verdict
<!-- VERDICT_TOKEN: DO_NOT_SUBMIT -->
**DO_NOT_SUBMIT — NOT_READY.** Finding-specific items 4–9 are TODO/UNPROVEN (and item 1 may be pending a
pinned commit). The package cannot advance to READY_FOR_HUMAN_REVIEW until those are PASS with only items 2
and 3 (the human checks) open. **Do not submit.**

## Explicit non-blockers (record for transparency)
- TODO — note any environmental caveats (e.g. fork at latest vs pinned block) that do not affect the result.
- The minimal patch is a root-cause discriminator, not the production fix.
