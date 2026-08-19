---
name: ton-sender-auth
description: "Run the TON/FunC sender-address verification specialist against the target contract. Pulls jetton transfer_notification spoofing, fake-deposit theft, to_address substitution, and pool-lock owner spoof patterns from the TON DEX KB (STON.fi/TONCO/Swap Coffee) before scanning. Activate on: /ton-sender-auth, sender spoofing, jetton transfer_notification not validated, fake deposit, owner_address spoof, pool lock bypass, to_address substitution, equal_slices missing."
---

# TON Sender-Auth Audit

Targeted scan for the canonical TON DEX theft bug: a message handler that AUTHORIZES or CREDITS off an
unverified / caller-supplied SENDER. TON has no ambient `msg.sender` trust — authority is only the message
SENDER address, and only if the handler binds it (`equal_slices`) to a stored role or to the contract's OWN
jetton wallet derived via state-init.

## Phase 1: Contract Discovery + Priority Targets

1. Find FunC sources if not provided, and grep the high-signal sender/notification patterns:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" \) -not -path "*/node_modules/*" -not -path "*/imports/*" | head -20
   grep -nE "transfer_notification|equal_slices|load_msg_addr|sender_address|calculate_user_jetton|check_workchain|owner_address|to_address" $(find . -name "*.fc" -o -name "*.func")
   ```
   Flag every `op::` branch that does state work but has NO `equal_slices` / `throw_unless` gate on SENDER.

2. Check `output/attack_surface.json` if present. Filter to handlers with `class: "user"` or
   `moves_funds: true` and `attack_surface_score >= 3`; list top targets by score (the `op::` branches an
   attacker can send directly).

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py sender-spoof "jetton transfer notification sender not validated as the router's own wallet fake deposit" --top-k 5
python tools/retriever.py jetton-theft "to_address recipient taken from caller payload steal from lp_account" --top-k 5
python tools/immunefi_retriever.py sender-spoof "TON jetton sender spoofing fake deposit" --top-k 5
```

Display summary:
```
TON Sender-Auth KB Recon:
  Solodit sender-spoof: [top 3]
  Solodit jetton-theft (recipient substitution): [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Fake jetton deposit (transfer_notification sender unbound): attacker sends
    op::ft::transfer_notification(amount) directly; handler skips equal_slices(SENDER, own_jetton_wallet) →
    swap/LP credited from a forged notification with no real tokens → pool reserves drained.
  ITE-2 — Recipient substitution (to_address from caller payload): provide/swap op reads to_address/owner
    from the inbound body → another user's LP/jettons routed to an attacker-chosen lp_account.
  ITE-3 — Pool-lock / owner_address spoof: multi-message swap keys its lock/owner on a body-supplied address
    an attacker reuses/races → reserves corrupted by forged/concurrent swap steps.
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_sender_auth.md` as a Task. Provide:
- Full FunC contract source(s)
- `output/static.json`
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json`  (OOS classes — centralization is OOS)

After the agent writes `output/findings_ton_sender_auth.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_sender_auth.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_sender_auth.json`, check KB similarity:
```bash
python tools/retriever.py sender-spoof "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py sender-spoof "<finding_title>" --top-k 3
```

- Best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title + score
- Best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]` → route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/ton-sender-auth] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [TSA-001] <title>

KB-matched findings (strong precedent):
  [TSA-002] <title>   — matched: "STON.fi steal from lp_account" (score: 0.xx)

Next:
  /confirm TSA-001    — re-run multi-pass on novel finding
  /poc TSA-001        — @ton/sandbox PoC required for any High/Critical spoof claim
  /human-queue        — review findings requiring manual validation
  /ite-audit          — run full pipeline if not already in progress
```
