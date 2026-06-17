# P211 — target selection

## Selected: decent-2024-01-holdout

| criterion | decent |
|---|---|
| source availability | ✅ `audits/decent-2024-01-holdout/contracts` |
| answer key availability | ✅ `_sealed_answer_key/report.md` (4 High / 5 Medium) |
| dependency manageability | ✅ light; P204 harnesses are forge-std-free, real contracts + mocked external deps |
| known High/Medium mix | ✅ H-01 setRouter→mint (genuine permissionless High), M-03 receiveFromBridge (awarded Medium, blind-rated High) |
| expected PoC feasibility | ✅ already executed in P204 (H-01 PASS 1e6-ether unbacked mint; M-03 demoted, no theft) |
| no live submission risk | ✅ historical C4 corpus, sealed key, no live bounty |

## Why decent over alternatives
- **vultisig** (P207) is also viable (H-01 claim-fee-loss PASS, M-03 cap-bypass demoted) and is used as a secondary
  L3 record; decent is primary because its H-01/M-03 map 1:1 to the awarded set and the P204 harnesses are the
  lightest.
- The active audit **quantamm-2024-12-eval** is a blind eval in progress — deliberately NOT used (must not score/
  disturb it).
- decent/munchables etc. were screened earlier; decent is the cleanest known corpus with both a genuine High and an
  over-rated Medium plus executed L3 evidence.

## Rehearsal-shape constraint (honest)
decent has its answer key but **no `output/` pipeline artifacts** (no merged_findings/triage/confirm), so a literal
full-discovery replay is not available and is out of scope for a workflow rehearsal. P211 therefore rehearses the
**L3-relevant wired surface end-to-end** — submission readiness → dashboard panel → report package — by driving the
REAL P210 functions (`evaluate`/`l3_evaluate`/`detail_overlay`/`record_review`, the dashboard L3 path) with decent
candidate fixtures + the real P204/P207 L3 records. Discovery/`min_confirm_gate`/`confirm_gate` are unchanged and were
validated in P209/P210; they are not re-exercised here.
