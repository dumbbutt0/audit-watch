# P267 — SETUP (Ranking/Selection Fix for Top-2 Mechanism Misses)

**RESEARCH-ONLY · DEFAULT-OFF · ADVISORY · EXTREMELY NARROW.** P267 builds one new thing — a pairwise mechanism
selector — and touches nothing else. It does NOT modify recall (P260/P262), the shadow harness (P264), the dashboard,
the PoC plumbing, or the completion layer. P266 proved all of those work and are safe; they are not the bottleneck.

## The one bug being fixed (from P266)
`awarded mechanism generated → awarded mechanism in Profile-B top-2 → wrong easier mechanism selected/PoC'd`.
On Phi, the awarded **H-03** curator-enumeration gas-DoS (m1c) was in Profile-B top-2 but lost to an easier,
lower-impact royalty-skim (m1a); the PoC layer then proved the wrong mechanism → 0 exact recovery.

## What P267 adds (allow-list only)
- `scripts/research/mechanism_pairwise_selector.py` — deterministic pairwise selector.
- `config/research_mechanism_pairwise_selector.json` — its config (dimension weights, caps, advisory contract).
- `tests/research/test_p267_mechanism_pairwise_selector.py`.
- `documentation/research/assisted_mode/p267_mechanism_selection_repair/` (8 docs + `outputs/`).

## Design stance (so it stays honest)
The selector is a **deterministic decision function over STRUCTURED inputs**. Each mechanism in a pair carries
**source-derivable, impact-based dimension signals** (impact_class, value_at_risk, victim/gainer clarity, intent
violation, attacker control, persistence, refutation resistance, PoC feasibility) — these are properties an auditor
can state PRE-REVEAL. They are **NOT award labels**. The backtest uses award labels ONLY to *score* whether the
decision preserved the mechanism that turned out awarded; award labels never enter the selector input. No answer key,
no source-reading LLM, no network.

## Frozen baselines (verified unchanged pre-run; must stay byte-identical)
P260 `d6b494bc`/`c61da091` · P262 `a48336275f`/`62e860199` · harness `85f9cbe6`/`e9b74687`. Forbidden 5:
dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9` ·
validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output` (unchanged).

## Backtest inputs (already-scored FROZEN artifacts only — no new answer keys)
P266 (`RANKING_AND_COMPLETION.md` + `REVEAL_AND_SCORE.md`) · P256 (`plaza_PROCEDURE_OUTPUTS.md` +
`plaza_REVEAL_AND_SCORE.md`) · P257 (`notional_MECHANISM_ENUM.md` + `notional_RANKING_ABLATION.md` +
`notional_REVEAL_AND_SCORE.md`) · P255 (`bakerfi_PROCEDURE_OUTPUTS.md` + `bakerfi_REVEAL_AND_SCORE.md`).
