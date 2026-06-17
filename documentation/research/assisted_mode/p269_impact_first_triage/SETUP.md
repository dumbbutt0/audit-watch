# P269 — SETUP (Impact-First Triage Fix for PoC Candidate Selection)

**RESEARCH-ONLY · DEFAULT-OFF · ADVISORY · NARROW.** Builds one new thing — an impact-first PoC triage policy — and
touches nothing else. P268 showed recall + the P267 selector work; the binding gap is now **which surfaced candidate
gets routed into the expensive PoC path**. P269 fixes the easy-PoC bias at the *triage* stage.

## The bug being fixed (from P268)
karak's award-dense **NativeVault/slashing/snapshot** subsystem was *surfaced* by recall but *de-scoped at triage*
("needs beacon fixtures → heavy PoC"); the easier ERC20 Vault was routed instead, and all 9 awards lived in the
de-scoped subsystem. Same easy-proof bias P267 fixed for mechanism selection, one level up.

## New principle
Don't route the easiest PoC. Route the **highest award-class-fit** candidate; allow heavier harnesses when the impact
class is stronger. PoC feasibility is a **constraint** (route HEAVY_POC_REQUIRED / PARTIAL_RUNTIME), not a primary
ranking signal — and never a reason to drop an award-class-fit subsystem.

## What P269 adds (allow-list only)
- `scripts/research/impact_first_poc_triage.py` — deterministic impact-first triage runner.
- `config/research_impact_first_poc_triage.json` — impact-fit weights, caps, advisory contract.
- `tests/research/test_p269_impact_first_poc_triage.py`.
- `documentation/research/assisted_mode/p269_impact_first_triage/` (8 docs + `outputs/`).

## Design stance (keeps it honest)
Deterministic decision over STRUCTURED candidate signals (impact_class, recall_delta, subsystem, terminality/value,
selector_outcome, poc_feasibility, feasibility_blockers) — source-derivable pre-reveal, **NOT award labels**. The
backtest uses award labels ONLY to score whether the policy routed the award-carrying subsystem; labels never enter
the policy input. No answer key, no source-reading, no network.

## Frozen baselines (verified unchanged; must stay byte-identical — NO tuning)
P260 `d6b494bc`/`c61da091` · P262 `a48336275f`/`62e860199` · P264 `85f9cbe6`/`e9b74687` · **P267 `b0623b8c`/`9dab060d`**.
Forbidden 5: dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9`
· validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`.

## Backtest inputs (frozen, already-scored — no new answer keys)
P268 (`REVEAL_AND_SCORE.md` + `P268_DIAGNOSIS.md`) · P266 (`REVEAL_AND_SCORE.md`) · P263 (`REVEAL_AND_SCORE.md`) ·
P259 (`VERDICT.md`).
