---
name: semantic-guard
description: "Run the semantic guard analysis agent to find asymmetric and incomplete access control across function groups. Pulls modifier shadowing, role-granting unguarded, and whenNotPaused missing patterns from KB. Activate on: /semantic-guard, modifier asymmetry, guard inconsistency, role granting unprotected, modifier shadowing, whenNotPaused missing, asymmetric guards."
---

# Semantic Guard Analysis Audit

Targeted modifier completeness scan. Finds asymmetric guards across function groups, modifier shadowing in inheritance, unguarded role-granting functions, and missing pause guards.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. From `output/static.json` (if present), collect all functions with their `modifiers` arrays. Group semantically:
   - Withdrawal group: withdraw, emergencyWithdraw, claimRewards, redeem
   - Deposit group: deposit, stake, provide, supply
   - Admin group: setFee, setOracle, pause, unpause, transferOwnership
   - Emergency group: sweep, drain, emergencyExit, recoverToken

3. Identify groups with MIXED guard presence (some functions have guards, others in the same group do not) — these are the highest-priority targets.

4. Also grep for modifier shadowing candidates:
   ```bash
   grep -n "modifier " <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py access-control "asymmetric modifier withdrawal group unguarded emergencyWithdraw bypass pause reentrancy" --top-k 5
python tools/retriever.py access-control "role granting function unguarded grantRole DEFAULT_ADMIN_ROLE revokeRole missing guard" --top-k 5
python tools/immunefi_retriever.py access-control "unguarded privilege escalation modifier missing access control asymmetric guards" --top-k 5
```

Display summary:
```
Semantic Guard KB Recon:
  Solodit: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Asymmetric guards in withdrawal group
    Intent: extract funds bypassing all guards using an unguarded sibling function
    Technique: withdraw() has nonReentrant + whenNotPaused + onlyAllowedCaller → emergencyWithdraw() in same group has no modifiers → call emergencyWithdraw() → bypasses all three guards → drain even when protocol is paused
    Evasion: emergency functions designed to bypass pause but developer forgot to add onlyOwner; no consistency check across function group
  ITE-2 — Modifier shadowing in inheritance
    Intent: bypass an access control modifier via empty child override
    Technique: parent defines modifier onlyOwner() { require(msg.sender == owner); _; } → child defines modifier onlyOwner() { _; } (empty) → all parent functions that use onlyOwner now execute without check
    Evasion: Solidity does not warn on modifier shadowing; IDE shows parent definition on hover; audit of only parent misses child override
  ITE-3 — initialize() callable post-deployment on implementation
    Intent: take over implementation contract and selfdestruct it to brick all proxies
    Technique: call initialize(attackerAddress) directly on implementation contract (not through proxy) → no initializer guard consumed by implementation → attacker becomes owner → call selfdestruct → all proxies pointing to implementation bricked
    Evasion: initializer modifier consumed at proxy init; implementation itself has separate unguarded init path; only proxy init path tested
```

## Phase 3: Agent Dispatch

Spawn `agents/semantic_guard.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_semantic_guard.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_semantic_guard.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py access-control "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py access-control "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/semantic-guard] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4):
  [SG-001] <title>

KB-matched findings:
  [SG-002] <title>   — matched: "Missing whenNotPaused on withdraw" (score: 0.86)

Next:
  /access-control    — semantic guard findings often indicate deeper access control issues
  /behavioral-state  — guard inconsistency may co-occur with NatSpec divergence
  /confirm SG-001    — multi-pass confirmation
```
