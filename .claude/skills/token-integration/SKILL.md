---
name: token-integration
description: "Run the token integration specialist agent. Pulls fee-on-transfer accounting drift, ERC-777 hook reentrancy, rebasing token, USDC blacklist DoS, and decimal mismatch patterns from Solodit and Immunefi before scanning. Activate on: /token-integration, fee on transfer, rebasing token, ERC-777, USDC blacklist, non-standard token, SafeERC20, decimal mismatch, transfer return value."
---

# Token Integration Audit

Targeted non-standard token vulnerability scan. Covers fee-on-transfer, rebasing, ERC-777 hooks, USDC/USDT blacklists, and decimal mismatches.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. List all tokens mentioned in `output/findings_protocol_context.json`. Classify each:
   - Standard ERC-20 (WETH, DAI): low risk
   - Fee-on-transfer candidate (tokens not in a standard whitelist)
   - Rebasing (stETH, aTokens, rebase mechanisms)
   - Pausable/blacklist (USDC, USDT, BUSD)
   - ERC-777 (has `tokensReceived` or `tokensToSend` hooks)

3. Check `output/coverage_gaps.json` for untested token-handling functions — these are highest priority.

4. Grep for non-standard transfer patterns:
   ```bash
   grep -n "\.transfer\|\.transferFrom\|safeTransfer\|safeTransferFrom" <contract_path>
   grep -n "balanceOf\|amount.*balance\|balance.*amount" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py logic-error "fee on transfer token accounting drift balance tracking deposit amount received" --top-k 5
python tools/retriever.py reentrancy "ERC777 tokensReceived hook reentrant withdraw deposit state update before transfer" --top-k 5
python tools/immunefi_retriever.py --all "fee on transfer non-standard token accounting exploit bounty" --top-k 5
```

Display summary:
```
Token Integration KB Recon:
  Solodit: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Fee-on-transfer accounting drift
    Intent: systematically drain other depositors' funds over many transactions
    Technique: deposit(1000 FOT_token) → protocol records balances[msg.sender] += 1000 → only 990 received (1% fee) → withdraw(1000) → protocol sends 1000 from reserves → 10 tokens drained per tx from other depositors
    Evasion: protocol uses function argument amount not (balanceAfter - balanceBefore) delta; test suite uses standard ERC-20 mock
  ITE-2 — ERC-777 tokensReceived reentrancy
    Intent: drain funds by reentering during token transfer hook
    Technique: implement tokensReceived() → call withdraw(amount) → protocol calls token.transfer(attacker, amount) → ERC-777 triggers tokensReceived before state updated → reenter withdraw() with same balance
    Evasion: no nonReentrant; CEI violated — transfer before balances[msg.sender] -= amount
  ITE-3 — USDC blacklist permanent DoS
    Intent: permanently block reward/liquidation distribution for all users
    Technique: get USDC-blacklisted → distributeRewards() loops token.transfer(recipients[i]) → USDC reverts on blacklisted address → entire loop reverts → all users denied rewards permanently
    Evasion: push payment model; no try/catch; no skip-on-failure; USDC blacklist not in design
```

## Phase 3: Agent Dispatch

Spawn `agents/token_integration.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/coverage_gaps.json` (if present — agent prioritizes untested paths)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_token_integration.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_token_integration.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

Check across three categories — take highest score:
```bash
python tools/retriever.py logic-error "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py reentrancy "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py dos "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py --all "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/token-integration] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4):
  [TI-001] <title>

KB-matched findings:
  [TI-002] <title>   — matched: "Fee-on-transfer deposit accounting" (score: 0.91)

Next:
  /dos               — USDC blacklist loop DoS is a DoS pattern; cross-reference
  /reentrancy        — ERC-777 hook findings may compound with reentrancy
  /confirm TI-001    — multi-pass confirmation
```
