---
name: ton-bounce-handling
description: "Activate on: /ton-bounce-handling, bounce, bounced message, IS_BOUNCED ignored, fund stranding, non-bounceable, bounce rollback, lost deposit, mint_shares bounce"
---

# TON Bounce-Handling Audit

Targeted scan for the canonical TON fund-loss bug: a contract that commits value-bearing state OPTIMISTICALLY
(debits a balance, reserves liquidity, credits an accumulator, mints LP, advances a rate) BEFORE sending a
*bounceable* internal message, then IGNORES or fails to ROLL BACK that state when the message bounces. A
bounceable send that fails on the callee (throw / non-existent contract / out-of-gas) returns to the sender
with the bounced flag set and the remaining value; if `recv_internal` drops it, the user's funds/reservation
are stranded, double-counted, or the protocol's derived accounting desyncs. Severity per program: permanent
freeze = Critical, temporary freeze = High.

## Phase 1: Contract Discovery + Priority Targets

1. Find FunC sources if not provided, and grep the high-signal bounce + commit-before-send patterns:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" \) -not -path "*/node_modules/*" -not -path "*/imports/*" | head -20
   grep -nE "IS_BOUNCED|bounced|flags & 1|send_raw_message|store_uint\(0x18|store_uint\(0x10|mint_shares|reserve|store_coins" $(find . -name "*.fc" -o -name "*.func")
   ```
   Flag every `recv_internal` that does `if (... IS_BOUNCED ...) { return (); }` (or has no bounce branch) on
   a contract that mutates value-bearing state, and every bounceable send (`store_uint(0x18, 6)` header) that
   follows a debit/reserve/credit/mint.

2. Check `output/attack_surface.json` if present. Filter to handlers with `class: "user"` or
   `moves_funds: true` and `attack_surface_score >= 3`; list top targets by score (the value paths whose
   downstream send can bounce).

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py bounce-stranding "ignored bounced message strands user deposit lost funds TON" --top-k 5
python tools/retriever.py bounce-stranding "bounce handler does not roll back reserved state rate desync" --top-k 5
python tools/immunefi_retriever.py bounce-stranding "TON bounce message loss of funds" --top-k 5
```

Display summary:
```
TON Bounce-Handling KB Recon:
  Solodit ignored-bounce stranding / missing-rollback / rate-desync: [top 3 each]   Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Ignored bounce on a value path (ton-bounce-ignored)
    debit/reserve/credit → bounceable send → callee throws → bounce hits `if (IS_BOUNCED) { return (); }`
    → committed state never reversed. STON.fi router.fc + lp_account.fc; Crouton mint_shares() lost deposits
  ITE-2 — Bounce handled but state not rolled back (ton-bounce-no-rollback)
    bounce branch only logs/forwards excesses, never un-reserves/re-credits the debited slot (not the inverse)
  ITE-3 — Non-bounceable loss (ton-non-bounceable-send) / rate desync (ton-bounce-rate-desync)
    value sent non-bounceable to a missing/throwing callee (Bemo jetton deploy), OR a mint/transfer bounces
    but the derived LP rate/reserves/supply is not corrected with the user balance (Storm Trade)
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_bounce_handling.md` as a Task. Provide:
- Full FunC contract source(s)
- `output/static.json`  (note the `bounce_ignored` flag for handlers that early-return on IS_BOUNCED)
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json`  (OOS classes — rent/storage-rent deletion is OOS; pure gas-optimization is OOS)

After the agent writes `output/findings_ton_bounce_handling.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_bounce_handling.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_bounce_handling.json`, check KB similarity:
```bash
python tools/retriever.py bounce-stranding "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py bounce-stranding "<finding_title>" --top-k 3
```

- Best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title + score
- Best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]` → route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/ton-bounce-handling] scan complete: N findings   Critical: N  High: N  Medium: N  Low: N

Novel (KB < 0.4 — human review):  [TBH-001] <title>
KB-matched:  [TBH-002] <title> — "STON.fi ignored bounce strands deposit" (score: 0.xx)

Next:
  /confirm TBH-001     — re-run multi-pass on novel finding
  /poc TBH-001         — @ton/sandbox PoC required for any High/Critical stranding claim
  /ton-sender-auth     — bounce stranding often co-occurs with sender-auth on the same value path
  /human-queue         — review findings requiring manual validation
```
