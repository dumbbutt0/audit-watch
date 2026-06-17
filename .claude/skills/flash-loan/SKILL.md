---
name: flash-loan
description: "Run the flash loan specialist agent. Pulls balance-based accounting inflation, governance flash vote, price manipulation + liquidation, and sandwich attack patterns from Solodit and Immunefi before scanning. Activate on: /flash-loan, flash loan, balanceOf accounting, governance vote manipulation, sandwich attack, minAmountOut zero, ERC-4626 inflation, donation attack."
---

# Flash Loan Audit

Targeted flash loan vulnerability scan covering balance-based accounting exploitable in one transaction, governance attacks via flash-loaned voting power, price manipulation + liquidation combos, callback reentrancy, and ERC-4626 first depositor inflation.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Grep for flash loan attack surface indicators:
   ```bash
   grep -n "balanceOf(address(this))\|balanceOf(address(this)) -\|\.balance\b" <contract_path>
   grep -n "swapExactTokensForTokens\|swapTokensForExactTokens\|exchange\|swap\|amountOutMin.*0\|minAmountOut.*0" <contract_path>
   grep -n "getPastVotes\|getPriorVotes\|balanceOf.*vote\|governance\|proposal\|quorum" <contract_path>
   ```
   Every `balanceOf(address(this))` used in a financial calculation is a high-priority target.

3. Check if `output/findings_oracle.json` exists — flash loan + spot price oracle = Critical compound.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py flash-loan "balance balanceOf share price inflation accounting one transaction flash borrow" --top-k 5
python tools/retriever.py flash-loan "governance flash loan voting power token balance checkpoint quorum same block" --top-k 5
python tools/immunefi_retriever.py flash-loan "flash loan price manipulation liquidation governance exploit critical bounty" --top-k 5
```

Display summary:
```
Flash Loan KB Recon:
  Solodit balance-based: [top 3]
  Solodit governance: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Balance-based accounting inflation
    Intent: drain protocol by inflating balance-derived share price then redeeming
    Technique: flash borrow large amount → donate/transfer to contract → balanceOf(address(this)) returns inflated value → mint shares at deflated price → redeem shares for actual assets → repay flash loan
    Evasion: protocol uses token.balanceOf(address(this)) instead of internal totalDeposited accounting variable; no snapshot of balance before tx
  ITE-2 — Governance via flash-loaned votes
    Intent: pass malicious proposal or drain treasury in one transaction
    Technique: flash borrow governance token → call propose() or castVote() → quorum reached instantly → proposal executes before flash repayment → repay flash loan
    Evasion: vote weight is balanceOf() not getPastVotes(account, block.number - 1); no block delay between proposal and voting; no timelocked execution
  ITE-3 — Price manipulation + liquidation
    Intent: illegitimately liquidate healthy positions for profit
    Technique: flash borrow → dump large amount into AMM to crash collateral token price → call liquidate() on healthy-but-now-priced-as-underwater positions → collect liquidation bonus → repay flash loan
    Evasion: oracle uses spot price (getReserves, slot0) not TWAP; no circuit breaker on collateral price drop percentage
```

## Phase 3: Agent Dispatch

Spawn `agents/flash_loan.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/findings_oracle.json` (if present — flash loan + spot price oracle = Critical compound)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_flash_loan.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_flash_loan.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py flash-loan "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py flash-loan "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/flash-loan] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [FL-001] <title>

KB-matched findings (strong precedent):
  [FL-002] <title>   — matched: "Balance-based accounting flash loan" (score: 0.88)
  [FL-003] <title>   — matched: "Governance flash vote no checkpoint" (score: 0.85)

Cross-reference note: if oracle findings exist, check for FL + OR compound Critical finding.

Next:
  /confirm FL-001    — multi-pass confirmation on novel finding
  /oracle            — flash loan + spot price = compound Critical candidate
  /economic-attack   — flash loan attacks compound with economic manipulation
  /human-queue       — review human review queue
```
