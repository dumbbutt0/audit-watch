# Session Status (latest)
_Generated 2026-06-17T16:09:22.047118+00:00_

**Active audit:** `sui-amm-swap-2022-11-eval` — Sui-AMM-swap (OmniBTC constant-product DEX)
**Next action:** Run triage  (`python scripts/triage_findings.py`)

## Calibration (cross-audit)
- FP rate: unmeasured (no ground truth)
- Recall on valid: unmeasured (no ground truth)
- PoC success: 0.857 (n=14)
- Ground-truth records (all audits): 0 across 11 audits

## Backlog (this audit)
- Ground-truth records: 0
- needs_human_review pending: 0
- Unpromoted learning candidates: 0
- Last failed gate: none

## LLM pre-flight
```
LLM pre-flight — API-FREE MODE pinned (config/runtime_policy.json): all stages route to in-session skills
  • deep_analysis: no key → use /deep-analysis (credit-free)
  • cross_agent_connector: no key → SKIP (optional; deterministic artifacts carry the run)
  • synthesize_compound: no key → SKIP (optional; deterministic artifacts carry the run)
  • multi_pass_confirm: no key → SKIP (optional; deterministic artifacts carry the run)
  • triage: no key → use /triage (credit-free)
  • poc: no key → no skill yet; stops with an actionable message
```
