# 0xMarkets — submission packages (candidates for human review)

Persistent, out-of-/tmp. Each `<ID>/`: `report.md`, `repro.md`, `submission_candidate.json` (schema-valid),
`vulnerable/` (copies of the affected `src/` file(s)). **No runnable PoCs** — 0xMarkets is a full GMX Synthetics fork
and these findings are either a source-confirmed cross-protocol fact (X-1) or need the full GMX build/machinery
(I-1/I-2); each is **code-verified** with exact line refs, and carries an **honest non-reproduced** dashboard status.
**Nothing submitted** — `human_approval_required: true`.

| ID | Severity | Title | PoC | Vulnerable file(s) |
|----|----------|-------|-----|--------------------|
| X-1 | Informational (for 0xM) — confirms Cartha C-1 (High) | `getMarketTokenPrice` can return ≤ 0 | source-confirmed (no runnable PoC) | `MarketUtils.sol` |
| I-1 | Medium (design) | Insurance injection compensates current LP holders → JIT capture | code analysis | `InsuranceFundUtils.sol`, `DecreasePositionCollateralUtils.sol` |
| I-2 | Low (config) | `triggerFactor` unset-default 0 = inject-on-any-drawdown | code analysis | `InsuranceFundUtils.sol` |

## Dashboard
Mirrored into `documentation/research/funnel/synced_findings.generated.json` (namespace `0xmarkets-2026-06-13:`).
Regenerate idempotently:
```bash
python3 reports/0xmarkets-2026-06-13/sync_0xmarkets_to_dashboard.py
python scripts/dashboard.py     # http://localhost:8765  →  /candidates
```
X-1 is GMX-inherited (not a 0xMarkets bug) — recorded to ground Cartha C-1; see
`../cartha-2026-06-13/cartha-C1-reachability.md`.
