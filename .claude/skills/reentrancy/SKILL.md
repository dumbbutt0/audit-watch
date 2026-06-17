---
name: reentrancy
description: "Run the reentrancy specialist agent against the target contract. Pulls real-world CEI violation, ERC-777 hook, and read-only reentrancy patterns from Solodit and Immunefi before scanning. Activate on: /reentrancy, reentrancy check, CEI violations, reenter, check for reentrancy, nonReentrant missing, ERC-777 hooks, read-only reentrancy, Curve virtual price."
---

# Reentrancy Audit

Targeted reentrancy scan covering classic CEI violations, cross-function reentrancy, read-only reentrancy (Curve/Balancer), ERC-777/ERC-1155 callback hooks, and proxy delegatecall reentrancy.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Check `output/attack_surface.json` if present. Filter to functions with `class: "user"` or `moves_funds: true` and `attack_surface_score >= 3`. List the top targets by score:
   ```bash
   python -c "
   import json
   try:
       data = json.load(open('output/attack_surface.json'))
       targets = [f for f in data.get('functions', []) if f.get('attack_surface_score', 0) >= 3 and (f.get('class') == 'user' or f.get('moves_funds'))]
       targets.sort(key=lambda x: x.get('attack_surface_score', 0), reverse=True)
       for t in targets[:10]:
           print(f\"  score {t['attack_surface_score']}/5  {t['name']}  [{t['class']}]  moves_funds={t.get('moves_funds', False)}\")
   except FileNotFoundError:
       print('attack_surface.json not found — suggest running /surface first')
   " 2>/dev/null
   ```

3. Grep for external call patterns as supplementary targets:
   ```bash
   grep -n "\.call{value\|\.transfer(\|\.send(\|safeTransfer\|safeTransferFrom" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py reentrancy "read-only reentrancy view function Curve Balancer virtual price getPoolTokenInfo" --top-k 5
python tools/retriever.py reentrancy "CEI violation withdraw deposit external call state update before balance nonReentrant missing" --top-k 5
python tools/immunefi_retriever.py reentrancy "reentrancy exploit drain funds withdraw callback bounty" --top-k 5
```

Display summary:
```
Reentrancy KB Recon:
  Solodit read-only reentrancy: [top 3]
  Solodit CEI violations: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Classic CEI violation (drain ETH/tokens)
    Intent: drain ETH or token balance from any depositor
    Technique: call withdraw() → .call{value:}(recipient) fires → attacker's fallback() re-enters withdraw() before balances[msg.sender] = 0
    Evasion: no ReentrancyGuard; nonReentrant present on deposit() but not withdraw()
  ITE-2 — Balancer/Curve read-only reentrancy
    Intent: borrow against inflated collateral or trigger false rebalance
    Technique: call remove_liquidity() on Curve pool → during ETH callback → call view function get_virtual_price() / getPoolTokenInfo() → returns stale inflated value because Balancer/Curve state is mid-update
    Evasion: view functions cannot carry nonReentrant; no Curve-level reentrancy guard checked before read
  ITE-3 — ERC-777 tokensReceived hook
    Intent: drain funds via hook triggered during token transfer
    Technique: attacker implements tokensReceived() → protocol calls token.transfer(attacker, amount) → hook fires before state updated → reenter deposit/withdraw with unchanged balance
    Evasion: no nonReentrant on withdraw; CEI reversed — transfer before balances[msg.sender] -= amount
```

## Phase 3: Agent Dispatch

Spawn `agents/reentrancy.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_reentrancy.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_reentrancy.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_reentrancy.json`, check KB similarity:
```bash
python tools/retriever.py reentrancy "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py reentrancy "<finding_title>" --top-k 3
```

- If best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title and score
- If best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]`
- `[NOVEL]` findings route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/reentrancy] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [RE-001] <title>

KB-matched findings (strong precedent):
  [RE-002] <title>   — matched: "Curve read-only reentrancy" (score: 0.87)
  [RE-003] <title>   — matched: "Missing nonReentrant on withdraw" (score: 0.91)

Next:
  /confirm RE-001    — re-run multi-pass on novel finding
  /flash-loan        — reentrancy often co-occurs with flash loan attack surfaces
  /human-queue       — review findings requiring manual validation
  /ite-audit         — run full pipeline if not already in progress
```
