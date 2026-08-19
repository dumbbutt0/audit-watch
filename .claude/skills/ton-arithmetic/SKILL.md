---
name: ton-arithmetic
description: "Run the TON/FunC TVM arithmetic & swap-LP math specialist against the target contract. Pulls muldiv overflow, wrong rounding direction, stableswap convergence, sqrt-of-negative, and precision-scaling patterns from the TON DEX KB (TONCO/FIVA/STON.fi) before scanning. Activate on: /ton-arithmetic, TVM overflow, muldiv overflow, rounding direction, stableswap convergence, sqrt negative input, precision loss, swap math, LP mint rounding."
---

# TON Arithmetic / Swap-LP Math Audit

Targeted scan for TON DEX MATH bugs that move funds: a `muldiv` intermediate that exceeds the 257-bit signed
range (throw/DoS or, unchecked, a corrupted amount), swap-out / LP-mint / fee math rounded in the USER's favor,
a loose stableswap Newton convergence threshold, `sqrt`/`log` fed a value that can go negative, or a
decimals-vs-internal precision scale whose lost units accrue to the user. TVM overflow THROWS (no silent EVM
wrap), so the question is always: *which way does it round, can an intermediate exceed range, and does an edge
input (0, max, negative) return a wrong value that drains the pool?*

## Phase 1: Contract Discovery + Priority Targets

1. Find FunC sources if not provided, and grep the high-signal math patterns:
   ```bash
   find . \( -name "*.fc" -o -name "*.func" \) -not -path "*/node_modules/*" -not -path "*/imports/*" | head -20
   grep -nE "muldiv|mul_div|sqrt|log|>> |<< |/ |reserve|liquidity|amount_out|shares|fee|SCALE|PRECISION" $(find . -name "*.fc" -o -name "*.func")
   ```
   Flag every swap-out / LP-mint / fee / reserve-update computation: note its rounding direction and the widest
   intermediate product.

2. Check `output/attack_surface.json` if present. Filter to handlers with `class: "user"` or
   `moves_funds: true` and `attack_surface_score >= 3`; list the top targets by score (the swap/provide/burn
   `op::` branches whose math an attacker can drive directly).

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py arithmetic "overflow getMaxLiquidity muldiv swap math fund loss TON pool" --top-k 5
python tools/retriever.py arithmetic "rounding direction fee mismatch stableswap convergence sqrt negative" --top-k 5
python tools/immunefi_retriever.py arithmetic "TON DEX swap math overflow rounding" --top-k 5
```

Display summary:
```
TON Arithmetic KB Recon:
  Solodit overflow/muldiv: [top 3]
  Solodit rounding/convergence/sqrt: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — muldiv intermediate overflow (ton-math-overflow): a liquidity↔amount product exceeds 257-bit before
    the divide → throw bricks a shared swap/mint path (DoS), or an unchecked builtin yields a corrupted amount
    that moves funds. (TONCO getMaxLiquidityForAmount0Precise; FIVA cube invariant overflow.)
  ITE-2 — wrong rounding direction (ton-rounding-direction): amount-out / minted shares round UP or a fee
    rounds DOWN in the user's favor → repeated swaps/mints extract value against x*y=k. (TONCO PositionNFT burn
    fee mismatch; TONCO vs Uniswap-v3 amount-delta rounding.)
  ITE-3 — stableswap convergence / sqrt-negative (ton-convergence / ton-signed-int-edge): a loose Newton
    threshold mis-prices the swap, or a negative delta fed to sqrt returns a wrong value. (STON.fi weighted
    stableswap threshold too large; STON.fi math::int::sqrt on negative input.)
```

## Phase 3: Agent Dispatch

Spawn `agents/ton_arithmetic.md` as a Task. Provide:
- Full FunC contract source(s)
- `output/static.json`
- `output/attack_surface.json`
- `output/coverage_manifest.json`
- `audits/<id>/scope.json`  (OOS classes — centralization / slippage / "could be more precise" are OOS)

After the agent writes `output/findings_ton_arithmetic.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_ton_arithmetic.json
```
Stop and report if exit code is non-zero.

## Phase 4: KB Cross-Reference + Novelty Flagging

For each finding in `output/findings_ton_arithmetic.json`, check KB similarity:
```bash
python tools/retriever.py arithmetic "<finding_title> <description_excerpt_100chars>" --top-k 3
python tools/immunefi_retriever.py arithmetic "<finding_title>" --top-k 3
```

- Best `similarity_score` >= 0.4 on Solodit: annotate with matched precedent title + score
- Best score < 0.4 on BOTH Solodit and Immunefi: flag as `[NOVEL]` → route to human review queue

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/ton-arithmetic] scan complete: N findings
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4 — human review required):
  [TAR-001] <title>

KB-matched findings (strong precedent):
  [TAR-002] <title>   — matched: "TONCO getMaxLiquidity overflow fund loss" (score: 0.xx)

Next:
  /confirm TAR-001    — re-run multi-pass on novel finding
  /poc TAR-001        — @ton/sandbox PoC required for any High/Critical math-drain claim
  /human-queue        — review findings requiring manual validation
  /ite-audit          — run full pipeline if not already in progress
```
