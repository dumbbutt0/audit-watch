---
name: snapshot
description: "Run the snapshot specialist agent. Pulls flash loan vote, buy-before-snapshot, delegation front-running, and missing epoch snapshot patterns from Solodit and Immunefi before scanning. Activate on: /snapshot, snapshot bug, voting power, balanceOf not checkpoint, governance manipulation, stale snapshot, delegation, ERC-20 snapshot."
---

# Snapshot Vulnerability Audit

Targeted snapshot/checkpoint vulnerability scan. Covers governance vote flash loans, buy-before-snapshot attacks, delegation front-running, and missing reward epoch snapshots.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Search for snapshot vulnerability indicators:
   ```bash
   grep -n "balanceOf\|balanceOfAt\|getPriorVotes\|getPastVotes\|snapshot\|checkpoints\|delegate" <contract_path>
   grep -n "epoch\|reward.*balance\|claimRewards\|distributeRewards" <contract_path>
   ```
   List all matches as priority targets.

3. Read latest synthesis from the KB pattern file:
   ```bash
   python -c "import json; data=json.load(open('kb/patterns/snapshot.json')); print(data['cycles'][-1]['synthesis'])" 2>/dev/null || echo "Pattern file not found"
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py logic-error "snapshot balanceOf governance voting power flash loan manipulation checkpoint getPastVotes" --top-k 5
python tools/retriever.py flash-loan "governance token snapshot voting manipulation balance checkpoint same block" --top-k 5
python tools/immunefi_retriever.py --all "snapshot voting power manipulation governance exploit bounty" --top-k 5
```

Display summary:
```
Snapshot KB Recon:
  Solodit: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Flash loan vote theft
    Intent: pass a malicious governance proposal in one transaction
    Technique: flash borrow governance tokens → castVote() with borrowed balance as weight → quorum reached in same tx → if no checkpoint lookback, proposal passes → repay loan
    Evasion: vote weight is balanceOf() not getPastVotes(account, block.number - 1); no block delay between proposal and voting
  ITE-2 — Buy-before-snapshot, sell-after
    Intent: claim rewards or vote with tokens you no longer hold
    Technique: monitor mempool for _snapshot() tx → buy tokens in block N-1 → snapshot records full balance → sell tokens in block N+1 → claim rewards using block N snapshot
    Evasion: snapshot block announced publicly before it lands; no prevention for buy-before-snapshot
  ITE-3 — Missing reward epoch snapshot
    Intent: drain epoch rewards from long-term holders
    Technique: just before claimRewards(): buy tokens → claim pendingRewards * (myBalance/totalSupply) → sell tokens → received rewards without holding during epoch
    Evasion: claimRewards() reads token.balanceOf(msg.sender) at claim time; no balanceOfAt(account, epochStartSnapshot)
```

## Phase 3: Agent Dispatch

Spawn `agents/snapshot.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_snapshot.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_snapshot.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py logic-error "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py --all "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/snapshot] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4):
  [SN-001] <title>

KB-matched findings:
  [SN-002] <title>   — matched: "Governance snapshot flash loan" (score: 0.87)

Next:
  /flash-loan        — snapshot flash vote is a flash loan attack variant
  /economic-attack   — epoch timing attacks may compound with snapshot issues
  /confirm SN-001    — multi-pass confirmation
```
