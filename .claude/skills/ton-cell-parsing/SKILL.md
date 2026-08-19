---
name: ton-cell-parsing
description: "Activate on: /ton-cell-parsing, cell parsing, malformed cell, multihop cell, slice underflow, end_parse missing, trailing data, load_ref, cell depth DoS, parser format confusion"
---

# TON Cell / Slice Parsing Audit

Targeted scan for the TON DEX cell-parsing bug class: an attacker-reachable cell (message body, and especially a
multi-hop swap-route ref) crafted/shaped to mis-parse to a WRONG recipient/amount (theft), smuggle extra trailing
bits/refs a downstream handler mis-reads (the STON.fi "custom payload" class), underflow a load (DoS / garbage read),
or nest refs to exhaust gas. TON encodes ALL data — bodies AND storage — as cells; safety rests on each parser
asserting layout, bounding loads, and `end_parse()`-ing what it fully decodes.

## Phase 1: Contract Discovery + Priority Targets

1. Find FunC sources if not provided, and grep the high-signal parse patterns:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" \) -not -path "*/node_modules/*" -not -path "*/imports/*" | head -20
   grep -nE "begin_parse|load_uint|load_int|load_coins|load_msg_addr|load_ref|load_dict|load_bits|slice_bits|slice_refs|slice_empty|end_parse|~load_ref" $(find . -name "*.fc" -o -name "*.func")
   ```
   Flag every `op::` branch that `load_*`s attacker-body fields with NO length guard, forwards a leftover slice/ref
   with NO `end_parse()`, or descends a `~load_ref()` chain in a loop with no depth bound.

2. Check `output/static.json` — note the `has_multihop` flag (a swap-route ref-chain raises the §1 priority).

3. Check `output/attack_surface.json` if present. Filter to handlers with `class: "user"` or `moves_funds: true`
   and `attack_surface_score >= 3`; list top targets by score (the `op::` branches an attacker can send directly).

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py cell-parsing "malformed multihop cell jetton loss wrong recipient TON DEX" --top-k 5
python tools/retriever.py cell-parsing "missing end_parse trailing data custom payload slice underflow" --top-k 5
python tools/immunefi_retriever.py cell-parsing "TON cell parsing jetton loss" --top-k 5
```

Display summary:
```
TON Cell-Parsing KB Recon:
  Solodit multihop misparse: [top 3]
  Solodit trailing-data / underflow: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Malformed multihop cell (ton-multihop-cell-misparse)
    Intent: route a swap's jettons to an attacker address / dead-end → loss
    Technique: craft a route ref-chain whose hop pool/recipient is unverified → router forwards value there
    Evasion: each hop's destination/asset taken from the cell, not validated against known pools
  ITE-2 — Trailing-data smuggling (ton-slice-trailing-data)
    Intent: substitute to_address / op the primary parser never validated (STON.fi "custom payload")
    Technique: append extra bits/refs after the decoded fields → downstream handler parses them
    Evasion: body decoded without end_parse(); leftover slice/ref forwarded onward
  ITE-3 — Slice underflow / format confusion (ton-slice-bounds / ton-cell-format-confusion)
    Intent: brick a shared trading path, or pass one parser while another mis-reads the same cell
    Technique: send a short/empty body that underflows a load on a critical path, or a cell two
               code paths decode with differing layout
    Evasion: load_* with no slice_bits/slice_refs guard; two divergent load_* sequences over one op body
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_cell_parsing.md` as a Task. Provide:
- Full FunC contract source(s)
- `output/static.json`  (note the `has_multihop` flag)
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json`  (OOS classes — gas-optimization and "disguising one asset as another" are OOS)

After the agent writes `output/findings_ton_cell_parsing.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_cell_parsing.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_cell_parsing.json`, check KB similarity:
```bash
python tools/retriever.py cell-parsing "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py cell-parsing "<finding_title>" --top-k 3
```

- Best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title + score
- Best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]` → route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/ton-cell-parsing] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [TCP-001] <title>

KB-matched findings (strong precedent):
  [TCP-002] <title>   — matched: "TONCO malformed multihop cell jetton loss" (score: 0.xx)

Next:
  /confirm TCP-001    — re-run multi-pass on novel finding
  /poc TCP-001        — @ton/sandbox PoC required for any High/Critical misparse/loss claim
  /human-queue        — review findings requiring manual validation
  /ite-audit          — run full pipeline if not already in progress
```
