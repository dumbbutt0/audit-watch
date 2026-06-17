# Cartha Vaults — submission packages (candidates for human review)

Persistent, out-of-/tmp. Each `<ID>/`: `report.md`, `repro.md`, `submission_candidate.json` (schema-valid),
`vulnerable/` (copies of the affected `src/` file(s)), and for PoC'd findings `poc/<Name>.t.sol` + `poc_output.log`.
Runnable harness: `../harness/` (`../harness/SETUP.md`). **Nothing submitted** — `human_approval_required: true`;
human review + KYC + submission are the operator's responsibility.

| ID | Severity | Title | PoC | Vulnerable file(s) |
|----|----------|-------|-----|--------------------|
| C-1 | High (reachability confirmed) | Stale/zero-TVL share mispricing → PnL theft | `PoC_StaleTvlMint` ✅ | `CarthaVault.sol`, `PoolDeployLib.sol` |
| L-1 | Low | Parent withdraw/release full-share burn vs `min(value,balance)` payout (rounding dust) | analysis | `CarthaParentVault.sol` |
| L-2 | Low | Child shares transferable post-lock but redeem is position-bound (orphan shares) | analysis | `CarthaVault.sol` |

## Run the PoC
```bash
cd reports/cartha-2026-06-13/harness
forge test --match-contract PoC_StaleTvlMint -vv     # attacker 100k -> claim 125k; victim 150k -> 125k
```

## View on the dashboard (candidates for review)
Mirrored into `documentation/research/funnel/synced_findings.generated.json` (namespace `cartha-2026-06-13:`, schema
`synced-1`, `research_only`/`review_only`/`human_review_required`, no submit controls). Re-generate idempotently:
```bash
python3 reports/cartha-2026-06-13/sync_cartha_to_dashboard.py   # upserts only the cartha namespace; backs up first
python scripts/dashboard.py        # http://localhost:8765  →  /candidates
```

C-1's `gmPrice ≤ 0` precondition is **confirmed reachable** — auditing 0xMarkets shows `getMarketTokenPrice` returns
`0`/negative when `poolValue ≤ 0` (a real market state), so C-1 is rated **High**. See `../cartha-C1-reachability.md`.
