# P291 — IMPLEMENTATION_NOTES

## Files changed (allow-list)
| File | Part | Change |
|---|---|---|
| `completion_evidence_deriver.py` | A | `_integration_deviation_evidence(item, body, pkg)` (auto: low-level call/callback/reentrancy-ordering; explicit operator field for structural bases) attached for EXTERNAL_INTEGRATION candidates; `import re`. |
| `poc_readiness_evidence_gate.py` | A | `_integration_deviation(pkg)` + gate block `elif cls=="EXTERNAL_INTEGRATION" and not _integration_deviation: NEEDS_INTEGRATION_DEVIATION_EVIDENCE`; new status in VALID_STATUSES. |
| `config/research_completion_evidence_deriver.json` | A | integration deviation signal terms (lowlevel/callback/guard markers, state-write regex). |
| `recall_first_harness.py` | B | `_expand_internal_loci(manifest, cands, contest, cfg)` post-sweep pass (imports `source_span_guard_extractor` read-only); appended before harness caps; fail-closed. |
| `config/research_recall_first_harness.json` | B | `internal_locus_recall` block (enabled, caps, class-relevant terms, getter prefixes, skip substrings). |

## Part A — fail-closed deviation requirement
EXTERNAL_INTEGRATION lifts only with a source-backed deviation. AUTO-detect ONLY unambiguous low-level `.call`/
`delegatecall`/callback-interface (and reentrancy-ordering = low-level call + no nonReentrant + state write). Structural
bases (fee-on-transfer/adapter/create2/cross-contract) require an EXPLICIT operator `integration_deviation_evidence`
field — never auto-guessed, because fee-on-transfer is structurally identical to the whitelist-mitigated `Pools.deposit`
(auto-flagging it would re-introduce the P290 false READY). Pools.deposit (nonReentrant + safeTransferFrom, no low-level
call, no explicit evidence) → NEEDS_INTEGRATION_DEVIATION_EVIDENCE.

## Part B — bounded internal-locus expansion
For each surfaced public/external candidate, read its body, resolve internal callees by name (same-contract or unique;
fail-closed), and surface a callee iff internal + has-body + not test/mock + not trivial-getter + class-relevant term +
state write. Caps: ≤3/public entry, ≤15/contest, ranked by class-relevance + state writes. advisory_only:true. Guard
fields preserved (severity None, reportable False, …) so harness guards pass.

## Hash-pin cascade (resolved; per P277/P281/P283/P289 precedent)
The harness/deriver/gate are pinned byte-identical across the P265–P290 history. Bumped: module pins
(`recall_first_harness` 85f9cbe→be428a12, `completion_evidence_deriver` c41eaf9d→bd4994f6,
`poc_readiness_evidence_gate` 9a4e3834→7afdc560) and the harness-config pin (e9b74687→0ea77ea4) across the pinning
tests; extended the blind frozen-stack live-check exclusion (test_p287/p288/p290) to the 3 P291 modules (baseline
hash_manifests preserved truthfully). **All 20 initial cascade failures were hash-pin only — 0 behavioral failures**
(the harness change only APPENDS advisory internal-locus candidates; base candidates + guards unchanged). New hashes:
deriver `bd4994f6aa2a9638`, gate `7afdc560bc4e96cd`, harness `be428a1202c45b1a`, deriver-config `0c7e01d40863ada3`,
harness-config `0ea77ea476450520`.
