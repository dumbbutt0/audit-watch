# P211 — L3 evidence records (reused from P204/P207; no new harness)

Placed at the loader location `output_research/l3_readiness/<candidate_id>.json` (ROOT-relative, audit-independent):

| record | l3_status | poc | actual vs control |
|---|---|---|---|
| `DEC-H-01.json` (PASS) | PASS | P204 `test/H01_setRouter.t.sol` (`forge test --match-contract H01`) | actual: 1e6 ether unbacked mint; control: mint reverts without the setRouter hijack |
| `DEC-M-03.json` (FAIL) | FAIL | P204 `test/M03_receiveFromBridge.t.sol` | actual: 0 (attacker self-funds); control: victim/UTB funds untouched -> demote |
| `VULT-H-01.json` (PASS) | PASS | P207 `test/H01_claimFees.t.sol` | actual: victim B loses 40e18 fees, claim reverts; control: sole investor made whole |

Each record validates against the P208 `L3_READINESS_SCHEMA.json`; all carry `research_only:true`/`routes_in_production:false`.
No new harness was built — P204/P207 forge runs are the evidence (PoC feasibility already demonstrated).
