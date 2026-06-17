---
name: oracle
description: "Run the oracle manipulation specialist agent. Pulls spot price flash loan, Balancer read-only reentrancy, Chainlink staleness, and TWAP window patterns from Solodit and Immunefi before scanning. Activate on: /oracle, oracle manipulation, spot price, Chainlink stale, TWAP window, getReserves, slot0, latestRoundData, price feed, oracle attack."
---

# Oracle Manipulation Audit

Targeted oracle vulnerability scan covering spot price manipulation, TWAP window attacks, Chainlink staleness, single oracle dependency, Balancer read-only reentrancy via price feed, and price decimal mismatches.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Grep for oracle call sites — every match is a priority target:
   ```bash
   grep -n "getReserves\|slot0\|latestRoundData\|latestAnswer\|getPrice\|consult\|observe\|getPoolTokenInfo\|getPricePerFullShare\|getVirtualPrice\|getAmountsOut" <contract_path>
   ```

3. Check if `output/findings_flash_loan.json` exists — any flash loan finding + liquidation function = potential Critical compound vulnerability.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py oracle-manipulation "spot price getReserves slot0 same transaction flash loan manipulation sandwich" --top-k 5
python tools/retriever.py oracle-manipulation "chainlink latestRoundData updatedAt staleness check missing heartbeat sequencer down" --top-k 5
python tools/immunefi_retriever.py oracle-manipulation "spot price flash loan oracle manipulation exploit critical bounty" --top-k 5
```

Display summary:
```
Oracle KB Recon:
  Solodit spot price: [top 3]
  Solodit Chainlink: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Spot price same-block manipulation
    Intent: inflate collateral value or deflate borrow cost in a single transaction
    Technique: flash loan → dump tokens into Uniswap V2 pair → call getReserves() in same tx → reserves reflect manipulated price → borrow/mint at wrong ratio → repay flash loan
    Evasion: no TWAP; no block delay between price read and financial action; getReserves() used directly in share/collateral calculation
  ITE-2 — Balancer getPoolTokenInfo read-only reentrancy
    Intent: read inflated pool balances to compute wrong collateral value
    Technique: call Balancer remove_liquidity() → during ETH transfer callback → call getPoolTokenInfo() → pool reports pre-withdrawal balances → protocol integrating this view as collateral reads stale/inflated value
    Evasion: Balancer has a reentrancy guard but getPoolTokenInfo() is a view function that bypasses it; no Balancer reentrancy guard check before reading
  ITE-3 — Chainlink staleness not checked
    Intent: use stale price during Chainlink outage to liquidate healthy positions
    Technique: wait for Chainlink heartbeat miss (network congestion or sequencer down) → call latestRoundData() → no require(updatedAt >= block.timestamp - MAX_STALENESS) → stale price returned → protocol liquidates healthy position or mints at wrong rate
    Evasion: only (, int256 price,,,) destructured; updatedAt variable discarded; no staleness check in code path
```

## Phase 3: Agent Dispatch

Spawn `agents/oracle.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/findings_flash_loan.json` (if present — spot price + liquidation = Critical compound)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_oracle.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_oracle.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py oracle-manipulation "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py oracle-manipulation "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/oracle] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [OR-001] <title>

KB-matched findings (strong precedent):
  [OR-002] <title>   — matched: "Chainlink no staleness check" (score: 0.91)
  [OR-003] <title>   — matched: "getReserves spot price manipulation" (score: 0.85)

Cross-reference note: if flash loan findings exist, check for compound oracle+liquidation Critical.

Next:
  /confirm OR-001    — multi-pass confirmation on novel finding
  /flash-loan        — spot price + flash loan = potential Critical compound
  /economic-attack   — oracle manipulation enables sandwich and liquidation profit attacks
  /human-queue       — review human review queue
```
