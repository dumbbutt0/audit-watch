---
name: access-control
description: "Run the access control specialist agent. Pulls signature replay, ecrecover bypass, missing chainId, and privilege escalation patterns from Solodit and Immunefi before scanning. Activate on: /access-control, missing auth, privilege escalation, unauthorized call, signature replay, ecrecover bypass, who can call this, missing guard, tx.origin."
---

# Access Control Audit

Targeted access control scan covering missing guards, incorrect role assignment, missing two-step ownership, signature-based auth bypass, upgradeable contract auth gaps, and tx.origin auth.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. From `output/attack_surface.json` (if present), list all `admin`-class functions and any `user`-class functions with empty modifier lists — these are the priority targets:
   ```bash
   python -c "
   import json
   try:
       data = json.load(open('output/attack_surface.json'))
       admin = [f for f in data.get('functions', []) if f.get('class') == 'admin']
       unguarded_user = [f for f in data.get('functions', []) if f.get('class') == 'user' and not f.get('modifiers')]
       print('Admin functions:', [f['name'] for f in admin])
       print('Unguarded user functions:', [f['name'] for f in unguarded_user])
   except FileNotFoundError:
       print('attack_surface.json not found — suggest running /surface first')
   " 2>/dev/null
   ```

3. Grep for auth-critical patterns:
   ```bash
   grep -n "ecrecover\|tx\.origin\|initialize\|_authorizeUpgrade\|DEFAULT_ADMIN_ROLE\|transferOwnership" <contract_path>
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py access-control "missing chainId domain separator cross-chain replay ecrecover returns address zero bypass" --top-k 5
python tools/retriever.py signature-replay "nonce not incremented failed transaction replay EIP-712 domain separator hardcoded" --top-k 5
python tools/immunefi_retriever.py access-control "unauthorized access privilege escalation missing guard exploit bounty" --top-k 5
```

Display summary:
```
Access Control KB Recon:
  Solodit access-control: [top 3]
  Solodit signature-replay: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — ecrecover returns address(0) bypass
    Intent: authenticate as any user by forging a signature
    Technique: submit crafted sig where ecrecover returns address(0) → check require(signer == user) passes if user == address(0) is not excluded from the valid set
    Evasion: no require(signer != address(0)) after ecrecover; address(0) is used as a default/unset value elsewhere in the contract
  ITE-2 — Missing chainId in domain separator
    Intent: replay a signed message from chain A on chain B
    Technique: obtain valid EIP-712 signature on mainnet → submit same bytes to bridge/fork where same contract is deployed → signature validates because chainId is not in the domain separator hash
    Evasion: domain separator hardcoded at deploy time; block.chainid not included; EIP-712 DOMAIN_TYPEHASH missing chainId field
  ITE-3 — Failed tx nonce bypass
    Intent: replay a signature after the original transaction reverted
    Technique: craft signed message → original tx reverts mid-execution → nonce not incremented (only incremented on success) → same signature valid for a second submission
    Evasion: nonce increment inside success path only; no nonce burn on failure; replay window open until nonce is consumed by successful tx
```

## Phase 3: Agent Dispatch

Spawn `agents/access_control.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_access_control.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_access_control.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

Check across both access-control and signature-replay categories — take highest score:
```bash
python tools/retriever.py access-control "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/retriever.py signature-replay "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py access-control "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4 across all queries. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/access-control] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [AC-001] <title>

KB-matched findings (strong precedent):
  [AC-002] <title>   — matched: "Missing chainId in EIP-712 domain" (score: 0.88)
  [AC-003] <title>   — matched: "ecrecover zero address bypass" (score: 0.92)

Next:
  /confirm AC-001    — multi-pass confirmation on novel finding
  /semantic-guard    — access control issues often co-occur with guard asymmetry
  /upgrade-storage   — if proxy detected, check upgrade auth gaps
  /human-queue       — review human review queue
```
