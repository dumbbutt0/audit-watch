# Pre-submission gate — ILOPool.claim (H-01)

Strict, reject-first checklist. A package is **READY_FOR_HUMAN_REVIEW** only if every machine-checkable item
is ✅ and the only remaining open items are the two **external human checks** (scope/program-rules and
duplicate/public-known). Any other ❌ blocks the package. **This gate does not authorize submission.**

| # | Check | Status | Basis |
|---|---|---|---|
| 1 | **Source version pinned** | ✅ PASS | Commit `befb1b11702a26ad0018308ef6e82b73683fe1d6`; submodules forge-std `52715a2` / oz `04695ae` / v3-core `d8b1c63` (`evidence_bundle.md`). |
| 2 | **Asset / scope verified** | ⏳ PENDING — HUMAN | `ILOPool.sol` is in the audited source tree; a human must confirm it is in the program's in-scope asset list and that the impact class is in-scope. *Allowed open blocker.* |
| 3 | **Duplicate / publicly-known check** | ⏳ PENDING — HUMAN | A human must check the program's known-issues and prior submissions for this finding. No answer key / public report was consulted. *Allowed open blocker.* |
| 4 | **Severity rationale source-backed** | ✅ PASS | Severity argued from source + executable result (fee diversion + later-claim revert), not assumption. See `reviewer_notes.md`. |
| 5 | **Executable PoC present** | ✅ PASS | `H01ClaimFeeSiphon.t.sol`; `forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv` fails on vulnerable source for the stated reason. |
| 6 | **No answer-key dependence** | ✅ PASS | Bug chain, root cause, and PoC are derived from in-scope source and executable behavior only. No findings repo / bot report / public writeup was used as a source of truth. |
| 7 | **No unsupported economic assumptions** | ✅ PASS | Only assumption is that swap fees accrue between launch and claim (normal trading); the PoC demonstrates the loss/revert directly with realistic volume. No price/market assumptions beyond that. |
| 8 | **No scanner/eval claims in the report** | ✅ PASS | `submission_draft.md` references only the contract source and the PoC — no tooling, lens, blind-eval, or internal-phase language. |
| 9 | **No overclaiming beyond the test** | ✅ PASS | The report claims exactly what the test shows: fee diversion to `feeTaker` for non-first claimants, and revert/lock once accrued fees exceed the platform-fee buffer. Below-buffer behavior is described as silent under-payment (not a revert), matching observed runs. |

## Gate verdict
- Machine-checkable items (1, 4–9): **all PASS.**
- Open items: **2 (scope) and 3 (duplicate) — both PENDING external human verification, which are the only
  allowed open blockers.**

➡ **READY_FOR_HUMAN_REVIEW.** Not submission-approved. A human must clear items 2 and 3, confirm program
severity-tier mapping and disclosure format, then make the submission decision. **Do not submit until then.**

## Explicit non-blockers (recorded for transparency)
- Test forks at latest rather than a pinned archive block — does not affect the result (in-scope contracts are
  deployed locally); a reviewer may pin a block via a keyed RPC for determinism.
- The minimal patch is a root-cause discriminator, not the production fix.
