# Pre-submission gate — M-11 `maxSellPercent` self-purchase bypass

Reject-first checklist. A ✅ is a fact established by source/PoC; a ⏳ is a check only a human reviewer can clear.

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Source version pinned | ✅ | commit `6693d9e4`; `SecondSwap_Marketplace.sol` sha256 `80573b863544a3` |
| 2 | In-scope asset confirmed | ⏳ PENDING (human) | contracts are in the project scope list; final in-scope confirmation is the reviewer's call |
| 3 | Duplicate / publicly-known check | ⏳ PENDING (human) | not checked against the program's known-issues / prior submissions |
| 4 | Severity = Medium, rationale supported | ✅ | cap bypass for fee cost; no third-party fund theft proven → Medium (not escalated) |
| 5 | Executable PoC present | ✅ | `M11SelfPurchasePoC.t.sol`; vulnerable test PASS |
| 6 | Patch validation present | ✅ | `test_M11_Patch_SelfPurchaseReverts` PASS; source restored + hash re-verified |
| 7 | No unsupported claims | ✅ | every claim maps to a cited source line or a PoC assertion |
| 8 | No external-report / answer-key dependence | ✅ | derived from in-scope source + executable test only |
| 9 | No internal tooling / scanner language in report body | ✅ | `submission_draft.md` is platform-neutral |
| 10 | Not auto-submitted | ✅ | submission_status stays `NOT_STARTED`; this gate does not submit |
| 11 | Impact not overstated beyond the PoC | ✅ | claims bounded to "cap bypass / full-allocation sale for fees"; no insolvency/theft claim |

## Verdict
**READY_FOR_HUMAN_REVIEW.** The finding is source-backed and PoC-backed; the report is platform-neutral; severity
is conservatively Medium; the minimal patch is validated. The **only** remaining blockers are human-owned:
- in-scope confirmation (#2),
- duplicate / publicly-known check (#3),
- program-specific severity tiering and final wording.

No automated submission occurs. A human must clear #2 and #3 and decide submit / no-submit.
