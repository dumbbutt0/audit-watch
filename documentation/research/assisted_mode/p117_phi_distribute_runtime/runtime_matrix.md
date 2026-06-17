# P117 — Runtime matrix (forge, local, no fork)

Exact command (from `/tmp/p117-phi-harness`):
`forge test --match-contract CuratorDistributeDoS -vv`  → 4 passed. Full log: `execution_output.txt`.

## Gas vs curator count N (measured, real CuratorRewardsDistributor)
| N (curators) | distribute gas | vs 30M block |
|---|---|---|
| 10 | 61,972 | fits |
| 100 | 350,046 | fits |
| 500 | 1,691,807 | fits |
| 1,000 | 3,443,716 | fits |
| 2,000 | 7,196,555 | fits |
| 4,000 | 15,698,328 | fits |
| 8,000 | **36,686,251** | **EXCEEDS — un-includable** |

Gas grows ~linearly (~4.3–6.2k/curator) + memory-quadratic terms; first N over the 30M block budget = **8,000**.
**This is a conservative LOWER BOUND** — the mock omits the real Cred's per-curator storage reads
(`EnumerableMap.at` + `isShareHolder`), so the real crossover is at FEWER curators (~a few thousand).

## Cases
- **Case A — small N (10):** `distribute` succeeds, 61,972 gas (`test_A_smallN_succeeds` PASS).
- **Case B — large N:** gas strictly increases with N and exceeds the 30M block at N=8,000
  (`test_B_gas_grows_and_exceeds_block_gas` PASS).
- **Case B2 — block-gas-cap revert:** `address(dist).call{gas: 30_000_000}(distribute(credId))` at N=8,000 returns
  `ok = false` → `distribute` cannot complete within a 30M block (`test_B2_distribute_reverts_under_block_gas_cap_at_largeN`
  PASS). Direct un-includability proof.
- **Case C — control:** N=10 again succeeds, 61,972 gas, unchanged (`test_C_control_smallN_still_succeeds` PASS) —
  the failure is caused by curator growth, not the setup.
