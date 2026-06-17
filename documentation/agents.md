# Specialist Agents

All agents are specification files in `agents/`. They are spawned as parallel Claude Code Tasks during Step 2 of the pipeline. Each agent:

- Receives the full contract source as file content
- Reads `output/static.json` and `output/attack_surface.json`
- Calls `tools/retriever.py` and `tools/immunefi_retriever.py` for KB precedent
- Reads `prompts/human_auditor_methodology.md` as base reasoning framework
- Writes exactly one output file: `output/findings_<agent_name>.json`
- Must conform to `schema/findings_schema.json`
- If no findings: writes `{"findings": [], "agent": "<name>"}`

---

## Core Finding Agents (always run)

| Agent | File | Purpose | Finding ID Prefix | Severity Focus |
|-------|------|---------|-------------------|---------------|
| Reentrancy | `agents/reentrancy.md` | CEI violations, read-only reentrancy, ERC-777 hooks, cross-function reentrancy | RE- | Critical/High |
| Access Control | `agents/access_control.md` | Missing guards, privilege escalation, signature replay, ecrecover bypass, tx.origin auth | AC- | Critical/High |
| Arithmetic | `agents/arithmetic.md` | Overflow, underflow, precision loss, rounding errors, unsafe type casting | AR- | High/Medium |
| Oracle | `agents/oracle.md` | Spot price manipulation, TWAP weaknesses, staleness, missing heartbeat checks | OR- | Critical/High |
| Flash Loan | `agents/flash_loan.md` | Flash loan attacks, sandwich surfaces, atomic arbitrage, balanceOf accounting | FL- | Critical/High |
| Logic | `agents/logic.md` | Business logic errors, broken invariants, incorrect state machine transitions | LG- | High/Medium |
| DoS | `agents/dos.md` | Fund lock, gas griefing, unbounded loops, forced revert, frozen contract state | DS- | Medium |
| Snapshot | `agents/snapshot.md` | Flash loan vote, buy-before-snapshot, delegation front-running, missing epoch checkpoint | SN- | High/Medium |
| Economic Attack | `agents/economic_attack.md` | MEV, liquidation arbitrage, governance manipulation, yield drain, incentive exploits | EA- | Critical/High |
| Token Integration | `agents/token_integration.md` | Fee-on-transfer, rebasing tokens, ERC-777, blacklist, decimal mismatch, USDT-style approval | TI- | High/Medium |
| Behavioral State Analysis | `agents/behavioral_state_analysis.md` | NatSpec vs code divergence, documented-but-not-enforced invariants, event misnaming | BSA- | High/Medium |
| Semantic Guard | `agents/semantic_guard.md` | Asymmetric modifiers across function groups, role granting without guards, whenNotPaused missing | SG- | High/Medium |
| Protocol Context | `agents/protocol_context.md` | Protocol classification (lending/AMM/vault/etc), EIP identification, trust model — not a finding agent | PC- | N/A (context only) |

---

## Infrastructure / Synthesis Agents

These agents support the pipeline rather than directly finding vulnerabilities.

| Agent | File | When Used | Purpose |
|-------|------|-----------|---------|
| Report Synthesis | `agents/report_synthesis.md` | Step 3 (called by `report_generator.py`) | Writes the final human-readable audit report from merged findings |
| Attacker Mindset | `agents/attacker_mindset.md` | Step 0.25 | ITE attack surface recon; produces `output/attack_surface.json` with per-function scores |
| Supply Chain Check | `agents/supply_chain_check.md` | Step 1 (parallel with static analysis) | Developer supply chain / patient zero threat model; checks ffi=true, unpinned deps, suspicious scripts | SC- |
| Invariant Extractor | `agents/invariant_extractor.md` | Step 0a | Enumerates all protocol invariants across 6 categories |
| Interaction Mapper | `agents/interaction_mapper.md` | Step 0b | Builds full call graph with trust boundary crossings and danger scoring |
| Deep Trace Agent | `agents/deep_trace_agent.md` | Step 0c | Traces one invariant × one dangerous chain hop-by-hop to verdict | DT- |
| Backward Trace Agent | `agents/backward_trace_agent.md` | Step 0c-bis | Sink-to-source: starts at financial sinks, finds all paths with invariants false | BT- |
| Multi-TX Agent | `agents/multi_tx_agent.md` | Step 0f | Finds bugs requiring multiple separate transactions (TOCTOU, timelock bypass, approval window) | MT- |
| Fuzzing Harness Writer | `agents/fuzzing_harness_writer.md` | Step 0d-fuzz | Writes Echidna Solidity property functions for invariants |
| Compound Synthesis | `agents/compound_synthesis.md` | Step 3 | Finds pairs of Medium/Low findings that together enable Critical/High | CC- |
| Duplicate Risk Agent | `agents/duplicate_risk_agent.md` | Step 5 | Classifies duplicate risk as low/medium/high per finding |
| Exploitability Modeler | `agents/exploitability_modeler.md` | Step 5 | Builds precise attacker model: who can call it, what they need, what they gain |
| Judge Simulator | `agents/judge_simulator.md` | Step 5 | Evaluates finding from 5 judge personas; predicts outcome and severity |
| Severity Calibrator | `agents/severity_calibrator.md` | Step 5 | Chooses final severity most likely to survive judging |
| Runtime PoC Agent | `agents/runtime_poc_agent.md` | Step 6 | Upgrades harness PoC to call real contract code (Levels 0–4) |
| Impact Chain Escalation Agent | `agents/impact_chain_escalation.md` | Step 3.4 manual review | Traces consumer paths for low-confidence ICE findings |
| Reference Diff Agent | `agents/reference_diff_agent.md` | Step 2 post-processing | Compares target implementation against Aave/Compound/Uniswap/Curve reference |

---

## Conditional Agents

These agents are only spawned when their trigger condition is met.

| Agent | File | Trigger Condition |
|-------|------|------------------|
| Cross-Chain | `agents/cross_chain.md` | `output/findings_protocol_context.json` identifies bridge, cross_chain, layer2, relayer, or rollup |
| Upgrade Storage | `agents/upgrade_storage.md` | `output/findings_protocol_context.json` identifies ERC-1967, proxy, UUPS, TransparentProxy, BeaconProxy, or upgradeable |
| ERC-4626 | `agents/erc4626.md` | `output/static.json` has `"is_erc4626": true` OR protocol_context mentions ERC-4626, vault, totalAssets, convertToShares, convertToAssets |
| Transient Storage | `agents/transient_storage.md` | `output/static.json` has `"has_transient_storage": true` OR contract source contains tstore, tload, TSTORE, TLOAD, or ReentrancyGuardTransient |

---

## Agent Output Requirements

Every agent output must:

1. **File path:** `output/findings_<agent_name>.json`
2. **Schema:** Must conform to `schema/findings_schema.json`
3. **Finding ID format:** `<PREFIX>-<THREE_DIGIT_NUMBER>` (e.g., RE-001, AC-002)
4. **Required fields per finding:** `id`, `title`, `severity`, `vuln_type`, `description`, `location`, `impact`, `recommendation`, `confidence`
5. **Empty result:** `{"findings": [], "agent": "<name>"}` (not an error)
6. **No shell metacharacters** in description or recommendation fields (validation gate catches these)

The output validation gate (`scripts/validate_agent_output.py`) checks schema conformance and injection artifacts before merging. Findings with forbidden patterns are excluded from the merged report.

---

## Cross-Agent Data Flow

Agents that benefit from reading each other's output:

- `flash_loan.md` reads `output/findings_oracle.json` (spot prices + flash loans = Critical)
- `logic.md` reads all `output/findings_*.json` for context
- `economic_attack.md` reads `output/findings_oracle.json` and `output/findings_flash_loan.json`
- `cross_chain.md` reads `output/findings_access_control.json` (most bridge bugs are auth-related)
- `upgrade_storage.md` reads `output/findings_access_control.json`

All agents read:
- `data/invariants/protocol_invariants.json` — cross-reference findings against named invariants
- `data/threads/promising_threads.jsonl` — incorporate hop-trace evidence for overlapping threads
- `output/coverage_gaps.json` — flag findings in untested functions with higher confidence
