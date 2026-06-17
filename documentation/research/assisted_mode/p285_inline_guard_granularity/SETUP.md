# P285 — SETUP

**Phase:** P285 — D1 Inline-Guard Granularity: Read-vs-Guard Refinement (REPAIR; not blind; production authority WITHHELD).
**Status:** RESEARCH-ONLY · ADVISORY · UN-WIRED · default-off · fail-closed.

## What this phase is
P284's invariant-delta deriver found a real relationship deviation (`blackhole RewardsDistributor.claim_many`,
SIBLING_REFERENCE_FOUND, HIGH, missing `getOriginalOwner` = Blackhole **M-04**) but the READY gate blocked it because
P281 D1 treated the token `ownerOf(` as an inline access guard. In `claim_many`, `ownerOf` is a **recipient READ on the
buggy value path** (`address _nftOwner = …ownerOf(_tokenId)`), not an access guard. P285 makes D1 surgical: a token
counts as an inline guard **only when it sits in an execution-gate construct** (`require`/`assert`, `if (…) revert/
return`, modifier, custom-error revert). The same token used to compute a value/recipient is a READ and must not refute
READY.

## Components
- `scripts/research/source_span_guard_extractor.py` — execution-gate span detection (`require`/`assert` args,
  `if(…){…revert/return…}` blocks, `onlyX` modifier, custom-error reverts) + per-token context taxonomy
  (EXECUTION_GUARD / VALUE_READ / RECIPIENT_READ / EVENT_READ / RETURN_READ / ARITHMETIC_READ / UNKNOWN_READ) +
  refined `inline_guard_detected` / `inline_guard_ambiguous` / `guard_contexts`.
- `scripts/research/poc_readiness_evidence_gate.py` — consumes refined D1; new fail-closed status `NEEDS_GUARD_CONTEXT`
  for ambiguous auth READs that would otherwise reach READY.

## Reproduce the corpus remap
Per audit (12 eval audits): `completion_evidence_deriver.py` (manifest + P278 `evidence_packages.json`) →
`poc_readiness_evidence_gate.py`; aggregate into `outputs/{remap_metrics,guard_context_evidence,audit,guard_report}.json`
+ `claim_many_poc_intent.json` + `l2governor_regression_log.txt`.

## Standing constraints (in force)
Research-only; no production authority / auto-submit / severity / reportable / submission / confirmed. No production or
contest source edits. The reused detector platform + P283/P284 modules are byte-identical. Active audit
`size-credit-2024-06-blind` symlink unchanged. No answer-key / target hard-coding; award titles/bodies never read.
Frozen P260/P262/P264/P267/P269/P271/P273 + P283 tracer + P284 deriver + forbidden 5 byte-identical.
