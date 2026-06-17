# P285 — IMPLEMENTATION_NOTES

## Files changed (allow-list only)
| File | Change |
|---|---|
| `scripts/research/source_span_guard_extractor.py` | NEW helpers `_match_close`, `_gate_spans`, `_read_context`, `classify_guard_contexts`; `detect()` rewired from token-presence to execution-gate classification; returns `inline_guard_detected` (refined), `inline_guard_ambiguous`, `guard_contexts`. |
| `scripts/research/poc_readiness_evidence_gate.py` | new `NEEDS_GUARD_CONTEXT` status (P285_STATUSES, valid-status set); precedence elif `inline_guard_ambiguous and not _id_deviation`; summary carries `inline_guard_ambiguous` + `guard_contexts`. |

`completion_evidence_deriver.py` unchanged — it already attaches `_ssx.extract(item)` output verbatim, so the refined
fields flow to the gate automatically.

## Gate-span detection
`_gate_spans(body)` returns `(start, end, strength)` ranges that gate execution:
- `require(…)` / `assert(…)` arg span (balanced-paren walk) → STRONG.
- `if (cond)` whose tail (same-line statement, or braced block via balanced-brace walk) contains `revert`/`return` →
  STRONG; `break`/`continue` → MEDIUM.
Modifier (`only[A-Z]…` in signature) and custom-error revert markers are forced EXECUTION_GUARD (they gate regardless of
span math). A token is EXECUTION_GUARD iff ANY of its occurrences lies in a gate span.

## assert() gap (found during the audit, fixed)
The first implementation only covered `require`. `VotingEscrow.withdraw` guards with `assert(_isApprovedOrOwner(
msg.sender, _tokenId))`, which was mis-classified UNKNOWN_READ → the candidate left INLINE_GUARD_REFUTED. Fix: `_RE_REQUIRE`
now matches `\b(require|assert)\s*\(`. After the fix `VotingEscrow.withdraw` is correctly INLINE_GUARD_REFUTED again.

## Statement-scoped read classification
`_read_context` scopes to the STATEMENT (boundary = last `;`/`{`/`}` before the token, up to the next `;`), not the line,
so single-line bodies classify correctly (`return ownerOf(id)` → RETURN_READ).

## Back-compat
Every P281 guard fixture uses `require`/`if-revert`/modifier/`isApprovedForAll`-in-require → still EXECUTION_GUARD
(116 P278–P284 tests green). Prior corpus tests read their own frozen P281–P284 output dirs (unchanged by P285). The
refined output only flips candidates whose "guard" was actually a read — intended.

## No hash-pin cascade beyond the extractor/gate
No test pins the extractor/gate. FROZEN P260–P273 + P283 tracer + P284 deriver/config + reused detector modules +
forbidden 5 are byte-identical (asserted in test_p285 + verification).
