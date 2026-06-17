# Audit Review Gate — blackhole-2025-05-eval
Generated: 2026-06-04T19:10:28.005434+00:00
Target: Blackhole (Code4rena Eval)

---

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

---

## Validated Findings

| ID | Title | Severity | Entry Point | ICE_C | ICE_E |
|---|---|---|---|---|---|

---

## Finding Details


### Value Provenance Deep-Pass Results — advisory only

> **Advisory only — prompt-derived review evidence, NOT proof, NOT confirmed, NOT submission-ready.** Every row is `advisory_only=true`, `submission_ready=false`, `requires_human_review=true`. **Requires human review and PoC before use in any report.** Excluded from Validated Findings and the confirmed count.

| Status | Location | Decision | Confidence | Next step | Mechanism | Job |
|---|---|---|---|---|---|---|
| completed | `RewardsDistributor.claim_many` | finding — NOT confirmed | high | build_poc | Recipient under-resolved: reward sent to ownerOf(tokenId) ra | VP-RewardsDistributor.claim_many.md |
| completed | `RewardsDistributor.claim` | strong_clear (cleared advisory context) | high | keep_advisory | Single-token claim resolves recipient and amount from the sa | VP-RewardsDistributor.claim.md |
| completed | `RewardsDistributor.claimable` | strong_clear (cleared advisory context) | high | keep_advisory | View accrual calculation for one tokenId; no subject diverge | VP-RewardsDistributor.claimable.md |
