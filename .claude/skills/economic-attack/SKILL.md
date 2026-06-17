---
name: economic-attack
description: "Run the economic attack specialist agent. Pulls MEV sandwich, governance manipulation, yield drain, and interest rate spike patterns from Solodit and Immunefi before scanning. Activate on: /economic-attack, MEV, sandwich attack, governance manipulation, yield drain, liquidation profit, interest rate spike, reward epoch, front-run."
---

# Economic Attack Audit

Targeted economic/game-theoretic attack scan. Covers MEV sandwich, governance flash vote, yield drain, reward epoch timing, interest rate spike, and cross-asset arbitrage.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Read `output/findings_protocol_context.json` to determine protocol type, then print the most relevant economic attack classes:
   - Lending protocol → interest rate spike, liquidation griefing, collateral manipulation
   - DEX/AMM → MEV sandwich, slippage attacks, concentrated liquidity manipulation
   - Governance → flash loan vote, voting power front-run, proposal griefing
   - Yield/staking → reward epoch timing, yield drain via deposit/withdraw cycling

3. Check if `output/findings_oracle.json` and `output/findings_flash_loan.json` exist — note their finding IDs as cross-reference context.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py flash-loan "governance flash loan vote manipulation quorum token balance one transaction" --top-k 5
python tools/retriever.py oracle-manipulation "sandwich attack spot price MEV frontrun liquidation profit arbitrage" --top-k 5
python tools/immunefi_retriever.py flash-loan "governance vote flash loan critical exploit economic attack bounty" --top-k 5
```

Display summary:
```
Economic Attack KB Recon:
  Solodit: [top 3 from flash-loan + top 3 from oracle-manipulation]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — MEV sandwich on protocol's own swap
    Intent: extract slippage value from every protocol swap in the mempool
    Technique: monitor mempool for protocol swap() → front-run with large buy → protocol gets worse price → back-run with sell → profit = protocol's slippage loss
    Evasion: amountOutMin=0 or computed on-chain; no deadline; open to public
  ITE-2 — Reward epoch timing
    Intent: claim full-epoch rewards while holding tokens for only fraction of epoch
    Technique: buy staking tokens just before epoch snapshot → claim full epoch rewards → immediately sell → net: trading fees only; net gain: near-full epoch reward
    Evasion: rewards computed from current balance at claim time, not time-weighted average; no snapshot at epoch start
  ITE-3 — Interest rate spike forcing liquidations
    Intent: force competitor positions into liquidation by pushing utilization to 100%
    Technique: borrow maximum from lending pool → utilization = 100% → interest rate jumps to cliff rate (e.g. 1000% APR) → existing borrowers' debt balloons in hours → positions become undercollateralized → liquidate for bonus
    Evasion: no minimum borrow time; no utilization circuit breaker; attacker's cost is interest (paid back from liquidation profits)
```

## Phase 3: Agent Dispatch

Spawn `agents/economic_attack.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/findings_oracle.json` (if present)
- `output/findings_flash_loan.json` (if present)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_economic_attack.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_economic_attack.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

Check across three categories — take highest score:
```bash
python tools/retriever.py flash-loan "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py oracle-manipulation "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py logic-error "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py flash-loan "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4 across all. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/economic-attack] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [EA-001] <title>

KB-matched findings:
  [EA-002] <title>   — matched: "Flash loan governance attack" (score: 0.84)

Next:
  /confirm EA-001    — multi-pass confirmation on novel finding
  /snapshot          — if governance/voting detected, check snapshot vulnerabilities
  /human-queue       — review human queue
```
