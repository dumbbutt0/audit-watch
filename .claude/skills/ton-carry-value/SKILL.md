---
name: ton-carry-value
description: "Run the TON/FunC carry-value & gas-accounting specialist against the target contract. Pulls router-balance drain, carry-all sweep, gas-stranding, storage-fee starvation, and excess-misrouting patterns from the TON DEX KB (TONCO/PixelSwap/Crouton/STON.fi) before scanning. Activate on: /ton-carry-value, carry value, gas accounting, raw_reserve, QCARRY_ALL_BALANCE, balance drain, gas stranding, storage fee, value not checked, excesses misrouted."
---

# TON Carry-Value / Gas-Accounting Audit

Targeted scan for the TON value-accounting failure modes: every internal message carries TON coins (gas + value),
and a handler reserves with `raw_reserve`/`reserve_at_most` then carries the rest with a send mode (carry-all =
mode `128`, `QCARRY_ALL_BALANCE`). Two opposite bugs: UNDER-forwarding gas/value → the message chain STALLS and
the user's coins strand; wrong reserve / carry-all → a caller SWEEPS more of the contract's balance than it owes
(a drain).

## Phase 1: Contract Discovery + Priority Targets

1. Find FunC sources if not provided:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" \) -not -path "*/node_modules/*" -not -path "*/imports/*" | head -20
   ```

2. Check `output/attack_surface.json` if present. Filter to handlers with `class: "user"` or
   `moves_funds: true` and `attack_surface_score >= 3`; list top targets by score (these are the `op::`
   branches an attacker can send directly to trigger a send/reserve).

3. Grep the high-signal value/reserve/send patterns:
   ```bash
   grep -nE "raw_reserve|reserve_at_most|QCARRY_ALL_BALANCE|send_raw_message|send_message|msg_value|my_balance|storage_fee|gas_consumption|excesses|response_address" $(find . -name "*.fc" -o -name "*.func")
   ```
   Flag every carry-all (mode 128) send and check the `raw_reserve` that precedes it; flag every `send_raw_message`
   whose `value` is hardcoded/computed without a `msg_value` floor check or a downstream-gas cross-check.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py jetton-theft "proxy TON balance of router can be stolen carry all balance drain" --top-k 5
python tools/retriever.py other "value attached not checked positive gas stranding storage fee TON" --top-k 5 --all
python tools/immunefi_retriever.py jetton-theft "TON balance drain gas value" --top-k 5
```

Display summary:
```
TON Carry-Value KB Recon:
  Solodit router/proxy balance drain: [top 3]
  Solodit gas-stranding / value-not-checked / storage-fee: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Carry-all sweep (raw_reserve doesn't pin the contract's own balance)
    Intent: drain the router/proxy's retained TON balance to the attacker
    Technique: trigger a refund/excesses path that does send mode 128 (QCARRY_ALL_BALANCE) after a
               raw_reserve that under-reserves → the carry-all sweeps the contract's own reserves, not just
               the caller's excess
    Evasion: reserve floor pins less than the rightful balance (storage + funds-owed), or no reserve at all
  ITE-2 — Gas under-forwarded → chain stalls (value stranded)
    Intent: strand a user's coins mid-flow (temporary/permanent freeze)
    Technique: a multi-hop handler forwards a fixed value < the destination's compute + onward sends; the
               next hop can't pay, the chain stops, the user's value is stuck with no payout/refund
    Evasion: forwarded value not cross-checked against gas.fc constants; current balance not checked before send
  ITE-3 — Value not validated / excess misrouted
    Intent: free action (gas avoided) or change/excesses routed away from the original sender
    Technique: op proceeds with zero/insufficient msg_value, or excesses sent to a caller-supplied to_address
    Evasion: no msg_value >= gas_consumption floor; refund recipient read from body, not the verified sender
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_carry_value.md` as a Task. Provide:
- Full FunC contract source(s) (include `gas.fc` / constants headers so forwarded values can be cross-checked)
- `output/static.json`
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json`  (OOS classes — pure gas-optimization and rent-deletion are OOS)

After the agent writes `output/findings_ton_carry_value.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_carry_value.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_carry_value.json`, check KB similarity:
```bash
python tools/retriever.py jetton-theft "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py jetton-theft "<finding_title>" --top-k 3
```

- Best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title + score
- Best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]` → route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/ton-carry-value] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [TCV-001] <title>

KB-matched findings (strong precedent):
  [TCV-002] <title>   — matched: "Proxy TON balance of the router can be stolen" (score: 0.xx)

Next:
  /confirm TCV-001    — re-run multi-pass on novel finding
  /poc TCV-001        — @ton/sandbox PoC required for any High/Critical drain/stranding claim
  /human-queue        — review findings requiring manual validation
  /ite-audit          — run full pipeline if not already in progress
```
