---
name: arithmetic
description: "Run the arithmetic specialist agent. Pulls decimal mismatch, unchecked block overflow, precision loss, and unsafe casting patterns from Solodit and Immunefi before scanning. Activate on: /arithmetic, overflow, underflow, precision loss, rounding error, unchecked block, decimal mismatch, integer truncation, division precision, mulDiv."
---

# Arithmetic Audit

Targeted arithmetic vulnerability scan covering integer overflow/underflow, precision loss, unsafe unchecked blocks, type casting, decimal mismatches, and rounding direction errors.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Check compiler version from `output/static.json` — if `< 0.8.0`, every arithmetic expression is a candidate and should be flagged as high-priority:
   ```bash
   python -c "import json; d=json.load(open('output/static.json')); print('Compiler:', d.get('compiler_version', 'unknown'))" 2>/dev/null
   ```

3. Grep for high-risk arithmetic patterns:
   ```bash
   grep -n "unchecked\|SafeMath\|uint128\|uint96\|uint64\|int128\|/.*\*\|mulDiv\|WAD\|RAY\|1e18\|1e6\|decimals" <contract_path>
   ```
   List all `unchecked {}` blocks as priority targets.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py arithmetic "decimal mismatch token 6 decimals USDC price calculation 18 decimals normalization" --top-k 5
python tools/retriever.py arithmetic "unchecked block subtraction underflow user controlled input casting uint256 uint128 truncation" --top-k 5
python tools/immunefi_retriever.py arithmetic "overflow underflow precision loss exploit bounty integer arithmetic" --top-k 5
```

Display summary:
```
Arithmetic KB Recon:
  Solodit decimal/casting: [top 3]
  Solodit overflow/unchecked: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Division before multiplication (precision loss)
    Intent: extract value through systematic precision loss in financial calculation
    Technique: (a / b) * c where intermediate division truncates to 0 → fee or reward calculated as 0 → attacker pays zero fees or claims outsized rewards repeatedly
    Evasion: looks like correct math; no mulDiv used; not tested with small numerators where truncation is significant
  ITE-2 — Unsafe uint256 to uint128 cast
    Intent: corrupt financial state via silent truncation
    Technique: large uint256 value passed to function → stored as uint128 via explicit cast → upper 128 bits silently lost → balance or share count becomes wrong by 2^128
    Evasion: Solidity explicit casts (uint128(x)) do not revert on truncation even in 0.8+; no SafeCast used; only tested with small values
  ITE-3 — Decimal mismatch (USDC 6-decimal vs ETH 18-decimal)
    Intent: extract excess tokens due to scale factor error
    Technique: protocol computes amount * price / 1e18 where amount is in 6-decimal USDC and price is in 8-decimal Chainlink → actual value is off by 1e4 → attacker mints/borrows at wrong rate capturing the difference
    Evasion: test suite uses 18-decimal mocks for all tokens; real USDC/USDT decimals never tested; no decimal normalization step
```

## Phase 3: Agent Dispatch

Spawn `agents/arithmetic.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_arithmetic.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_arithmetic.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py arithmetic "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py arithmetic "<finding_title>" --top-k 3
```

Flag `[NOVEL]` if best score < 0.4 on both. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/arithmetic] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [AR-001] <title>

KB-matched findings (strong precedent):
  [AR-002] <title>   — matched: "Decimal mismatch USDC 6 vs 18" (score: 0.89)
  [AR-003] <title>   — matched: "Unchecked subtraction user input" (score: 0.94)

Next:
  /confirm AR-001    — multi-pass confirmation on novel finding
  /oracle            — arithmetic and oracle manipulation often compound
  /erc4626           — rounding direction errors specific to ERC-4626 vaults
  /human-queue       — human review queue
```
