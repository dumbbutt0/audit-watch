---
name: erc4626
description: "Run the ERC-4626 vault specialist agent. Only activates when ERC-4626 interface is detected. Pulls inflation attack, wrong rounding direction, and totalAssets flash manipulation patterns from Solodit and Immunefi. Activate on: /erc4626, vault inflation, first depositor, rounding direction, totalAssets, convertToShares, virtual offset, ERC-4626."
---

# ERC-4626 Vault Audit

Conditional audit — only runs when ERC-4626 vault interface is detected.

## Phase 1: Conditional Guard + Discovery

**CONDITIONAL:** Check two sources:
1. `output/static.json` for `"is_erc4626": true`
2. `output/findings_protocol_context.json` for: `ERC-4626`, `vault`, `totalAssets`, `convertToShares`, `convertToAssets`

If neither condition is met:
```
[/erc4626] Skipped: static.json does not flag ERC-4626 and protocol_context has no vault indicators.
Run /surface or /ite-audit first, or pass --force to override.
```
Stop.

If detected: "ERC-4626 vault confirmed. Checking for inflation, rounding, and totalAssets manipulation." Grep:
```bash
grep -n "totalAssets\|convertToShares\|convertToAssets\|previewDeposit\|previewMint\|previewWithdraw\|previewRedeem\|_decimalsOffset" <contract_path>
```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py flash-loan "ERC-4626 inflation attack share price first depositor virtual offset decimals" --top-k 5
python tools/retriever.py arithmetic "ERC-4626 rounding direction mulDiv shares assets deposit withdraw mint redeem" --top-k 5
python tools/immunefi_retriever.py flash-loan "vault inflation first depositor shares price manipulation exploit bounty" --top-k 5
```

Display summary:
```
ERC-4626 KB Recon:
  Solodit flash-loan: [top 3]
  Solodit arithmetic: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — First depositor inflation attack
    Intent: steal the second depositor's entire deposit
    Technique: vault has 0 totalSupply → deposit 1 wei → get 1 share → directly transfer 1e21 tokens to vault → totalAssets=1e21+1, totalSupply=1 → next depositor calls deposit(1e21) → shares = (1e21*1)/(1e21+1) = 0 (rounds down) → depositor gets 0 shares but vault has their tokens
    Evasion: no virtual offset (_decimalsOffset() returns 0); no minimum deposit; direct transfer possible
  ITE-2 — Wrong rounding in mint/withdraw
    Intent: extract fractional value per tx through reversed rounding
    Technique: call mint(shares) repeatedly → convertToAssets(shares) rounds DOWN instead of UP → attacker pays fewer assets per share than correct → vault systematically under-collateralized
    Evasion: plain division always rounds DOWN; Math.mulDiv used without Math.Rounding.Ceil for mint/withdraw paths
  ITE-3 — totalAssets flash loan manipulation
    Intent: cause depositor to receive fewer shares than fair value
    Technique: front-run deposit() → flash loan inflates totalAssets() via donation → victim's shares computed against inflated total → victim receives fewer shares → attacker deflates and profits from delta
    Evasion: totalAssets() reads token.balanceOf(address(this)) not internal accounting; no flash loan protection
```

## Phase 3: Agent Dispatch

Spawn `agents/erc4626.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_erc4626.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_erc4626.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py flash-loan "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py arithmetic "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py flash-loan "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/erc4626] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4):
  [V4-001] <title>

KB-matched findings:
  [V4-002] <title>   — matched: "First depositor inflation attack" (score: 0.93)

Next:
  /flash-loan        — inflation attacks use flash loans; cross-reference
  /arithmetic        — rounding direction findings compound with arithmetic issues
  /confirm V4-001    — multi-pass confirmation
```
