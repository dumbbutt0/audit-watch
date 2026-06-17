---
name: cross-chain
description: "Run the cross-chain bridge specialist agent. Only activates when bridge/layer2/relayer patterns are detected. Pulls message replay, decimal mismatch mint, nonce reordering, and relayer griefing patterns from Solodit and Immunefi. Activate on: /cross-chain, bridge, cross-chain, message replay, relayer, rollup, nonce reorder, token mint inflation, canonical bridge."
---

# Cross-Chain Bridge Audit

Conditional audit — only runs when bridge/cross-chain/layer2 pattern is detected.

## Phase 1: Conditional Guard + Discovery

**CONDITIONAL:** Read `output/findings_protocol_context.json`. Check for any of:
`bridge`, `cross_chain`, `layer2`, `relayer`, `rollup`, `message_passing`, `canonical_bridge`

If NONE are found:
```
[/cross-chain] Skipped: no bridge/cross-chain/layer2 pattern detected in output/findings_protocol_context.json.
Run /surface or /ite-audit first to classify the protocol, or pass --force to override.
```
Stop.

If detected: print which cross-chain pattern was identified (e.g., "LayerZero relayer detected" or "Optimism canonical bridge"). Grep:
```bash
grep -n "chainId\|domainSeparator\|nonce\|messageHash\|bridgeMessage\|relayer\|l1\|l2\|destination" <contract_path>
```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py --all reentrancy "bridge cross-chain message replay nonce domain separator chain id missing validation" --top-k 5
python tools/retriever.py signature-replay "cross-chain domain separator chain id missing replay fork canonical bridge" --top-k 5
python tools/immunefi_retriever.py --all "bridge exploit cross-chain replay nonce double spend token inflation" --top-k 5
```

Display summary:
```
Cross-Chain KB Recon:
  Solodit bridge: [top 3]
  Solodit signature-replay: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Message replay across chains
    Intent: double-mint tokens or replay withdrawal on a second chain
    Technique: obtain valid message/sig on chain A → submit same bytes to bridge on chain B → no chainId in hash → bridge validates → tokens minted on B without burning on A
    Evasion: keccak256(abi.encode(recipient, amount, nonce)) — no block.chainid; nonce is per-sender not per-chain
  ITE-2 — Decimal mismatch on bridge mint
    Intent: receive 1e12x more tokens on destination chain
    Technique: lock 1 USDC (6-decimal, amount=1_000_000) on chain A → bridge passes raw amount to mint on B → destination mints 1_000_000 of 18-decimal token → user receives 1e24 base units instead of 1 token
    Evasion: bridge passes raw amount without normalizing decimals between source and destination token
  ITE-3 — Nonce reordering by relayer
    Intent: grief user by making their message permanently undeliverable
    Technique: relayer withholds message N → delivers N+1 first → strictly sequential nonces → N is now permanently undeliverable → user's funds locked on source chain
    Evasion: no nonce gap tolerance; no user-initiated cancellation; relayer is single trusted point of failure
```

## Phase 3: Agent Dispatch

Spawn `agents/cross_chain.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/findings_access_control.json` (if present — bridge bugs often involve auth/validation failures)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_cross_chain.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_cross_chain.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py --all reentrancy "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py signature-replay "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py arithmetic "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py --all "<finding_title>" --top-k 3
```

Take highest score. Cross-chain is a newer category — expect many findings to come back as NOVEL. Flag `[NOVEL]` if < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/cross-chain] scan complete: N findings (bridge type: <type>)
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — cross-chain is a newer attack surface):
  [CC-001] <title>

KB-matched findings:
  [CC-002] <title>   — matched: "Message replay no chainId" (score: 0.82)

Next:
  /access-control    — bridge validation failures often compound with missing auth
  /confirm CC-001    — multi-pass confirmation on novel finding (expected for cross-chain)
  /human-queue       — cross-chain novel findings require expert review
```
