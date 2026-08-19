---
name: ton-message-flow
description: "Activate on: /ton-message-flow, async race, message ordering, lp_account race, two-deposit race, reserve interleaving, partial execution, message replay, transaction order dependence"
---

# TON / FunC Async Message-Flow Audit

Targeted async-race scan for TON contracts (FunC/Tact): non-atomic multi-step desync, the lp_account two-deposit
accumulation race, reserve-update vs swap interleaving, partial-execution / no-rollback, and replayable /
out-of-order messages. TON has no synchronous reentrancy — the analog is message-ordering / interleaving on shared
mutable state across multiple transactions. MEV-style slippage/frontrun/backrun/sandwich are OUT OF SCOPE; the
in-scope race is protocol-state corruption.

## Phase 1: Contract Discovery + Priority Targets

1. Find TON sources if not provided:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" -o -name "*.tact" \) -not -path "*/node_modules/*" -not -path "*/test*/*" | head -20
   ```

2. Check `output/attack_surface.json` if present. Filter to functions with `class: "user"` or `moves_funds: true`
   and `attack_surface_score >= 3`, and prioritize op handlers that send an outbound message and act on a response:
   ```bash
   python -c "
   import json
   try:
       data = json.load(open('output/attack_surface.json'))
       t = [f for f in data.get('functions', []) if f.get('attack_surface_score',0) >= 3 and (f.get('class')=='user' or f.get('moves_funds'))]
       t.sort(key=lambda x: x.get('attack_surface_score',0), reverse=True)
       for x in t[:10]:
           print(f\"  score {x['attack_surface_score']}/5  {x['name']}  [{x['class']}]  moves_funds={x.get('moves_funds', False)}\")
   except FileNotFoundError:
       print('attack_surface.json not found — suggest running /surface first')
   " 2>/dev/null
   ```

3. Grep for the message-flow primitives that open interleaving windows:
   ```bash
   grep -n "send_raw_message\|send_message\|recv_internal\|bounced\|query_id\|op::\|begin_cell\|load_msg_addr" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py message-race "async race condition between swap and index update loss of funds TON" --top-k 5
python tools/retriever.py message-race "transaction order dependence overwritten balances bounce race" --top-k 5
python tools/immunefi_retriever.py message-race "TON race condition message ordering" --top-k 5
```

Display summary:
```
TON Message-Flow KB Recon:
  Solodit async swap/index race: [top 3]
  Solodit order-dependence / bounce overwrite: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Non-atomic multi-step desync (ton-async-state-desync)
    Intent: desync accounting / double-spend across an interleaved message
    Technique: msg1 optimistically reserves/credits → attacker's message mutates shared state → response re-reads cached value
    Evasion: response trusts the snapshot taken at send time, not current state
  ITE-2 — lp_account two-deposit race (ton-lp-account-race)
    Intent: mint wrong LP / capture another user's partial deposit
    Technique: token A then token B accumulate in separate messages → interleaved deposit/withdraw/reset before mint
    Evasion: accumulation/reset not sender-bound across the two-deposit window
  ITE-3 — Reserve interleave (ton-reserve-interleave)
    Intent: mispricing / over-withdraw off stale reserves
    Technique: swap reads pre-update reserves while a settlement path updates them; two in-flight swaps share one snapshot
    Evasion: no version/seqno guard between reserve update and swap consumption
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_message_flow.md` as a Task. Provide:
- Full contract source (the `.fc`/`.func`/`.tact` files)
- `output/static.json`
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json` (so the agent honors OOS: slippage/frontrun/backrun/sandwich)

After the agent writes `output/findings_ton_message_flow.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_message_flow.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_message_flow.json`, check KB similarity:
```bash
python tools/retriever.py message-race "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py message-race "<finding_title>" --top-k 3
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
[/ton-message-flow] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [TMF-001] <title>

KB-matched findings (strong precedent):
  [TMF-002] <title>   — matched: "Race condition in YT swap and index update" (score: 0.81)
  [TMF-003] <title>   — matched: "Race Condition in Bounce Messages Handling" (score: 0.88)

Next:
  /confirm TMF-001    — re-run multi-pass on novel finding
  /human-queue        — review findings requiring manual validation
  /poc TMF-001        — High/Critical require a runnable @ton/sandbox race PoC (L1 → L2 storage flip → L3 outcome)
  /ite-audit          — run full pipeline if not already in progress
```
