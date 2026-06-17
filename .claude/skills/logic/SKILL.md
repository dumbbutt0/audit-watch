---
name: logic
description: "Run the logic error specialist agent. Pulls accounting invariant violations, state machine skip, rounding direction, first depositor attacks, and liquidation ratio errors from Solodit and Immunefi before scanning. Activate on: /logic, business logic, invariant violation, accounting bug, state machine, first depositor, rounding error, fee bypass, broken invariant."
---

# Logic Error Audit

Targeted business logic scan covering token accounting invariants, state machine violations, fee/reward calculation errors, liquidation logic, rounding direction, first depositor attacks, and integer division by zero.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Read `output/findings_protocol_context.json` to understand protocol type. This determines which logic sub-classes are most relevant:
   - Lending → liquidation/collateral ratio, health factor, interest accounting
   - DEX/AMM → fee accounting, LP share invariant, swap math
   - Vault/yield → share/asset accounting, reward distribution, epoch logic
   - Governance → proposal state machine, vote counting, timelock

3. List all existing findings from other agents to provide context (logic errors often compound with other vulnerabilities):
   ```bash
   ls output/findings_*.json 2>/dev/null
   ```

4. Grep for invariant-sensitive patterns:
   ```bash
   grep -n "totalSupply\|totalShares\|totalAssets\|healthFactor\|collateralRatio\|_mint\|_burn" <contract_path>
   grep -n "enum.*State\|status\|state\b\|Phase\|stage" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py logic-error "token accounting invariant totalSupply mint burn tracking error balance sum" --top-k 5
python tools/retriever.py logic-error "liquidation collateral ratio health factor calculation wrong math error protocol loss" --top-k 5
python tools/immunefi_retriever.py logic-error "accounting bug logic error state machine invariant exploit bounty" --top-k 5
```

Display summary:
```
Logic Error KB Recon:
  Solodit accounting invariants: [top 3]
  Solodit liquidation/collateral: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Token accounting invariant break
    Intent: mint shares or tokens without equivalent asset backing
    Technique: find a code path where _mint(amount) is called but totalSupply is not updated atomically → invariant sum(balances) == totalSupply breaks → over-minting → existing holders diluted or attacker drains the difference
    Evasion: rare code path not covered in tests; requires multi-tx sequence; internal visibility hides from external auditors; only triggered by unusual input combinations
  ITE-2 — State machine skip
    Intent: claim rewards before vesting or execute action in wrong sequence
    Technique: identify state transitions (PENDING → ACTIVE → CLAIMABLE) → find function callable from PENDING that should only run from CLAIMABLE → call it directly, skipping the ACTIVE state requirement → claim before entitled
    Evasion: state is an enum or uint checked in some functions but not all; missing onlyState(CLAIMABLE) guard on the claim function; developer added guard to most but missed one path
  ITE-3 — Rounding direction favors attacker
    Intent: extract fractional value through reversed rounding per transaction
    Technique: call mint(shares) → convertToAssets(shares) rounds DOWN instead of UP → attacker pays fewer assets per share than correct → after many iterations vault is systematically under-collateralized
    Evasion: plain division always rounds DOWN; mulDiv used without specifying Math.Rounding.Ceil for mint/withdraw caller-pays paths; no rounding direction audit
```

## Phase 3: Agent Dispatch

Spawn `agents/logic.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- ALL existing `output/findings_*.json` files (logic bugs often emerge only in context of other findings)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`
- Any specification documents found: `docs/spec.md`, `README.md`, `SPEC.md`

After agent writes `output/findings_logic.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_logic.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py logic-error "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py logic-error "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4 on both. Note: protocol-specific logic bugs often have low KB similarity because they depend on the exact protocol design. Low similarity should increase (not decrease) scrutiny. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/logic] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — protocol-specific logic; human review required):
  [LG-001] <title>

KB-matched findings (strong precedent):
  [LG-002] <title>   — matched: "Rounding direction vault mint" (score: 0.88)
  [LG-003] <title>   — matched: "State machine skip in claim" (score: 0.84)

Next:
  /confirm LG-001    — multi-pass confirmation essential for novel logic findings
  /economic-attack   — logic errors often enable economic extraction
  /erc4626           — if vault detected, check ERC-4626 specific logic errors
  /human-queue       — protocol-specific logic bugs need human validation
```
