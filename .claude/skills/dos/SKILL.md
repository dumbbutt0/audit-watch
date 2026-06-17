---
name: dos
description: "Run the denial of service specialist agent. Pulls unbounded loop, external call in loop, locked ETH, USDC blacklist, and forced ETH via selfdestruct patterns from Solodit and Immunefi before scanning. Activate on: /dos, denial of service, unbounded loop, gas limit, locked ETH, external call in loop, block stuffing, griefing, USDC blacklist DoS."
---

# Denial of Service Audit

Targeted DoS vulnerability scan covering unbounded loops over user-controlled arrays, external calls in loops, locked ETH with no withdrawal path, USDC blacklist griefing, forced ETH via selfdestruct, and block stuffing.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. From `output/static.json` (if present), list all loop constructs — every loop is a candidate:
   ```bash
   grep -n "for (\|while (\|\.length\b" <contract_path>
   grep -n "payable\|receive()\|fallback()" <contract_path>
   ```

3. Check for push-payment patterns (external call inside loop) — these are the highest severity DoS targets:
   ```bash
   grep -n "\.transfer\|\.send\|\.call{value" <contract_path>
   ```
   Flag any match that appears inside a loop body.

4. Check for strict ETH balance equality (forced ETH vector):
   ```bash
   grep -n "address(this)\.balance ==" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py dos "unbounded loop user controlled array gas limit stakers voters recipients reward distribution" --top-k 5
python tools/retriever.py dos "external call in loop one revert blocks all batch distribute refund USDC blacklist" --top-k 5
python tools/immunefi_retriever.py dos "denial of service griefing locked funds permanent revert unbounded loop" --top-k 5
```

Display summary:
```
DoS KB Recon:
  Solodit unbounded loops: [top 3]
  Solodit external-call-in-loop: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Unbounded loop over user-controlled array
    Intent: permanently block a core protocol function by exhausting block gas
    Technique: attacker creates N wallets → each calls stake() or register() → grows stakers[] array → when distributeRewards() iterates stakers.length, gas cost exceeds 30M block limit → function permanently uncallable
    Evasion: no cap on array length; no pagination; no per-user pull model; test suite only tests with small arrays
  ITE-2 — External call in loop, USDC blacklist
    Intent: permanently block reward/refund distribution for all users
    Technique: get USDC-blacklisted → protocol calls token.transfer(recipients[i]) in loop → USDC reverts on blacklisted address → entire loop reverts → no recipient receives their funds
    Evasion: push-over-pull; no try/catch around each transfer; no skip-on-revert logic; USDC blacklist not considered in design
  ITE-3 — Forced ETH via selfdestruct
    Intent: break an exact balance check to permanently lock the contract
    Technique: contract has require(address(this).balance == expectedAmount) → deploy contract with ETH → selfdestruct(victimAddress) → forces ETH into victim → balance no longer == expectedAmount → check permanently fails
    Evasion: strict equality == on ETH balance instead of >=; selfdestruct ETH injection not considered; no ETH rescue path
```

## Phase 3: Agent Dispatch

Spawn `agents/dos.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_dos.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_dos.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py dos "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py dos "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/dos] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [DS-001] <title>

KB-matched findings (strong precedent):
  [DS-002] <title>   — matched: "Unbounded loop over stakers array" (score: 0.92)
  [DS-003] <title>   — matched: "External call in loop USDC revert" (score: 0.89)

Next:
  /confirm DS-001    — multi-pass confirmation on novel finding
  /token-integration — USDC blacklist DoS intersects with token integration issues
  /logic             — locked ETH bugs may indicate broader accounting invariant violations
  /human-queue       — review human review queue
```
