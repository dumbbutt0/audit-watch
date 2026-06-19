# TipRun — submission packages (candidates for human review)

> **Category field:** every `SUBMISSION.md` `# Field: Category` (and `submission_candidate.json` `vrt_category`) is
> chosen verbatim from the canonical list in [`../../SUBMISSION_CATEGORIES.md`](../../SUBMISSION_CATEGORIES.md)
> (HackenProof VRT). Always fill report categories from that list.

Persistent, out-of-/tmp. Each `<ID>/` is self-contained: `report.md` (standalone writeup), `poc/<Name>.t.sol`,
`poc_output.log` (captured passing run), `submission_candidate.json` (schema-conformant), `repro.md`, and
`vulnerable/` (copies of the affected `src/` file(s)). Runnable Foundry harness: `../harness/` (see
`../harness/SETUP.md`). **Nothing here is submitted** — `human_approval_required: true`; human review + KYC +
submission are the operator's responsibility.

**Submittable reports: 8 distinct root causes** (F-1+M-1 are one bug merged into a single report). The N-* findings
are from the 2026-06-18 re-audit (`RE_AUDIT_2026-06-18.md`); all PoCs pass.

| ID | Severity | Title | PoC (in `harness/`) | Vulnerable file(s) in `vulnerable/` |
|----|----------|-------|---------------------|-------------------------------------|
| **F-1 (+M-1)** | Critical (+Medium) | Broken health-transition guard in `Risk.checkValidTransition` — collateral-withdraw bypass (A) + de-risk DoS (B) | `PoC_MarginBypassWithdraw` (A) + `PoC_DeriskDoS` (B) | `Risk.sol`, `PositionManager.sol`, `WithdrawalTransLib.sol` |
| F-2 | High/Critical | Risk-segment freeze → insolvent short un-liquidatable (liquidation lock) | `PoC_RiskSegmentFreeze` (2 tests) | `GeneralConfig.sol`, `Risk.sol` |
| N-1 | High | Privilege escalation to `ALLOW_ADMIN`: any user self-mints admin (caller-named `adminAccountId`) and drains any account | `PoC_PermissionEscalation` | `PermissionsTransLib.sol`, `WithdrawalTransLib.sol` |
| N-2 | Medium (High cond.) | Perp margin checks fail open when `CAP_MARGIN_CHECK` is absent — normal user trade creates bad debt (user-path PoC + negative control) | `PoC_CapabilityRegistryNoop` | `PositionManager.sol`, `TransactionProcessor.sol`, `OrderbookPlugin.sol`, `NullMarginCheck.sol`, `Constants.sol` |
| M-2 | Low | Oracle: no read staleness + monotonic-update guard commented out (defense-in-depth; privileged update path) | `PoC_OracleStaleness` | `Oracle.sol`, `OraclePriceTickTransLib.sol` |
| M-3 | Medium (trust) | Liquidate/Deleverage: no on-chain maintenance-margin precondition | `PoC_NoLiquidatablePrecondition` + `PoC_DeleverageNoConsent` | `LiquidateTransLib.sol`, `DeleverageTransLib.sol` |
| M-4 | Medium/Low | `setSyntheticAssetsInfo` does not bump `configVersion` | `PoC_ConfigVersionNotBumped` | `GeneralConfig.sol`, `MultiTransactionProcessor.sol` |
| N-4 | Low (trust) | Settlement mints collateral at an unconstrained operator price (no oracle/signature/conservation) | `PoC_SettlementUnconstrained` | `SettlementTransLib.sol`, `SettlementPlugin.sol` |

**Merge note:** F-1 and M-1 are two opposite-direction symptoms of a single inverted comparison (`Risk.sol:133`),
so they are submitted as **one combined report** (`F-1/report.md`, with M-1 as "Manifestation B"); the `M-1/` folder
now redirects there and is retained only for reproduction. F-2 is a distinct root cause
(`getRiskFactor`/`getAssetValueAndRisk`).

## Run all PoCs
```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-path 'test/PoC_*.t.sol' -vv     # 9 PoC contracts pass
```

## View on the dashboard (candidates for review)
The six findings are mirrored into the research-only dashboard feed
(`documentation/research/funnel/synced_findings.generated.json`, namespace `tiprun-2026-06-13:`, schema `synced-1`,
`research_only`/`review_only`/`human_review_required`, no submit controls). To (re)generate idempotently:
```bash
python3 reports/tiprun-2026-06-13/sync_tiprun_to_dashboard.py   # upserts only the tiprun namespace; backs up first
```
Then launch the dashboard and open the candidates view:
```bash
python scripts/dashboard.py        # http://localhost:8765  →  /candidates
```
