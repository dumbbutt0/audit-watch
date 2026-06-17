# PoC Development

Proof-of-concept tests are the primary evidence for High and Critical findings. The pipeline automates PoC planning, code generation, execution, and verification.

---

## PoC Level Scale

| Level | Description | Sufficient for |
|-------|-------------|---------------|
| L1 | Isolated harness — arithmetic or logic copied from source, no real contract calls | Low finding evidence only |
| L2 | Real buggy function called directly (imported/linked, not copied) | Medium finding evidence; minimum bar for submission |
| L3A | Real public entrypoint called with minimal setup | Confirms call path |
| L3B | Public entrypoint + bug-induced state change proven by assertion | Confirms state corruption |
| L3C | Full exploit chain with financial impact asserted (balance change, unauthorized mint, etc.) | High and Critical evidence |

### Severity ceiling by PoC level and bug class

| Bug class | L3A ceiling | L3B ceiling | L3C ceiling |
|-----------|-------------|-------------|-------------|
| `reentrancy_forced_liquidation` | Medium | Medium | High |
| `close_factor_bypass` | Medium | Medium | High |
| `liquidation_dos` | Medium | **High** | High |
| `missing_auth_allowance_theft` | Medium | Medium | High |

Note: `liquidation_dos` reaches High at L3B because the harm IS the blocked liquidation — no profit assertion is needed to prove severity.

**The permanent rule:** Never finalize severity until the PoC evidence proves the strongest claimed impact. If the report claims forced liquidation, the PoC must execute liquidation. If the report claims direct loss, the PoC must assert balance movement.

---

## PoC Approach by Bug Type

| Approach | When to use | Pattern |
|----------|-------------|---------|
| `pure_arithmetic` | Bug is in a calculation function; can be reproduced without a runtime environment | Duplicate WAD/math functions inline, assert bad output |
| `unit_integration` | Bug is in a contract function with simple dependencies | Mock Soroban/Foundry env, call real function |
| `mock_contract` | Bug requires a malicious external contract (reentrancy, ERC-777 callback) | Stub the external contract, trigger callback |
| `state_machine` | Bug requires a specific sequence of transactions | Sequence of calls proving TOCTOU or accounting drift |

---

## Generation Workflow

### Step 1: Profile the target repo (once per contest)

```bash
python scripts/profile_target_repo.py \
  --repo contracts/ \
  --out data/poc_queue/repo_profile.json
```

Detects language (Solidity/Rust/etc.), framework (Foundry/Hardhat/Soroban), test directories, and helper files.

### Step 2: Generate PoC plan

```bash
python scripts/generate_poc_plan.py --finding-id RE-001
```

Calls `prompts/poc_planner.md`. Produces `data/poc_queue/RE-001_plan.json` conforming to `schemas/poc_plan.schema.json`.

### Step 3: Generate PoC test code

```bash
python scripts/generate_poc_test.py --finding-id RE-001 --max-repair-attempts 3
```

Calls `prompts/poc_writer.md`. Writes the test file (location depends on framework). Attempts up to N repair cycles if compilation fails.

### Step 4: Run tests

```bash
python scripts/run_poc_tests.py --finding-id RE-001
# Re-run all:
python scripts/run_poc_tests.py --all
```

Records results in `data/poc_queue/RE-001_result.json` and `data/runtime_poc/results.jsonl`.

### Step 5: Review results

```bash
python scripts/summarize_poc_results.py --out reports/poc_evidence.md
```

---

## The 7-Question Quality Checklist

After every finding reaches Level 3, answer all 7 questions before submitting. Embed the checklist as a comment block directly above the Level 3 test function.

| # | Question | Passes when |
|---|----------|-------------|
| 1 | Can I prove it with Level 2? | `data/runtime_poc/results.jsonl` has `runtime_level >= 2` AND `status == "proved"` |
| 2 | Can I prove it with Level 3? | Same file, `runtime_level >= 3` AND `status == "proved"` |
| 3 | Is there direct loss? | Fund theft, collateral drain, or DoS of a safety mechanism |
| 4 | Is the exploit permissionless? | No privileged key or pre-existing allowance needed |
| 5 | Is the victim condition realistic? | Arises from normal protocol use or market conditions |
| 6 | Is this likely duplicate? | Check Solodit + root-cause clusters; flag if > 50% similar |
| 7 | Can I write the impact in one sentence? | One sentence, no hedging, names the victim and loss |

A finding that cannot answer ✅ or ⚠️ on questions 1–3 should not be submitted as High/Critical.

### Inline checklist comment format

Embed directly above each Level 3 test function:

```rust
// Checklist:
//   ✅ Proved Level 2: grace period bypass allows self-reinstall of revoked manager
//   ✅ Proved Level 3: XTR001_l3_backdoor_minter_persists
//   ✅  Direct loss: unauthorized minting capability persists after admin revocation
//   ✅  Permissionless: any revoked manager can trigger during grace period
//   ✅  Victim condition realistic: occurs on normal manager rotation
//   ❓  Likely duplicate: no known prior finding on grace period self-reinstall
//   ✅  One-sentence impact: A revoked manager self-reinstalls during the grace period, permanently defeating admin revocation and retaining unauthorized minting rights.
```

Symbols: ✅ = yes, ⚠️ = conditional, ❌ = no, ❓ = unknown (investigate before submitting)

---

## Running the Quality Checklist

```bash
python scripts/run_quality_checklist.py --finding-id RE-001
# All proved findings:
python scripts/run_quality_checklist.py --all
python scripts/generate_status.py
```

Output: `data/quality_checklist/results.jsonl`

---

## PoC Completeness Gate

After the quality checklist passes, run the completeness gate to verify the PoC actually proves the claimed severity:

```bash
python scripts/analyze_poc_completeness.py --all
# Strict mode (exits 1 if any High claim is unsupported):
python scripts/analyze_poc_completeness.py --all --strict
```

If a finding is blocked at a lower PoC level than needed, the gate creates an upgrade task:
`output/poc_upgrade_tasks/<ID>_upgrade.md`

Proof requirement templates live in `templates/proof_requirements/<bug_class>.json`.

---

## Level 3 Naming Convention

```
<finding_id>_l3_<description>
```

Example: `xtr001_l3_backdoor_minter_persists`

Keep the Level 2 test in the same file — both must pass before submission.

---

## Safety Rules

Generated tests MUST NOT contain any of the following:
- `broadcast` or `sendTransaction` — live network calls
- `PRIVATE_KEY` — key references
- `mainnet` or any live network name
- `fs::remove` or `rm -rf` — filesystem destruction
- `curl`, `wget`, `eval`, `exec`, `os.system` — shell execution

The pipeline enforces this. Tests containing these patterns are flagged in the PoC review step and will not be included in the evidence report.

---

## Mock Disclosure Rules

If the PoC uses mock contracts (e.g., a mock ERC-20 that returns incorrect values):
1. Name them clearly: `MockMaliciousERC20`, `MockReentrantReceiver`
2. Include a comment explaining what the mock simulates and why
3. Note in the submission report which external dependencies were mocked
4. Do not claim Level 3C if the financial impact was asserted against a mock balance rather than a real protocol balance

---

## Framework-Specific Notes

**Foundry (EVM Solidity):**
```bash
forge test --match-test xtr001 -vvv
```
Test files: `test/audit/<finding_id>_poc.t.sol`

**Hardhat (EVM Solidity):**
```bash
npx hardhat test test/audit/<finding_id>_poc.js
```

**Rust/Soroban:**
```bash
cargo test <finding_id> -- --nocapture
```
PoC crate: `pocs/<audit_id>/<finding_id>/`
