# P137 — Decision

## Decision: **PROMPT_CONVERTS_RESIDUAL**

A genuinely-blind `deep_pass_value_provenance` run (fresh uncontaminated subagent, source only, no answer key)
**identified the exact H-03 mechanism** — the in-loop hop uses the static `asset` instead of the updated
loop-carried `quotingToken` — as a confident, source-cited `finding`. Post-hoc this is a strict match to the
known H-03 (awarded High, value_exit). The residual detector MISS (P134) is converted to a HIT by the existing
prompt, with no new detector and no answer-key knowledge. Controls show acceptable specificity (clean function →
strong_clear; single-hop oracle → needs_human; no false positive on the clean control).

### Rubric
- **PROMPT_CONVERTS_RESIDUAL** ✅ — blind deep-pass identifies the H-03 mechanism with source-grounded reasoning.
- Not PROMPT_PARTIALLY_CONVERTS: it found the *exact* loop-variable mechanism, not just "suspicious".
- Not PROMPT_RECOMMENDATION_ONLY: the blind output is a reviewable candidate on its own (though human + PoC are
  still required before severity/submission — that's the standard discipline, not a weakness of the result).
- Not PROMPT_TOO_NOISY: clean control cleared; uncertain case → needs_human; no invented claim.
- Not BLOCKED_BY_CONTEXT: the function-scoped packet was sufficient.

## Final response

**What this phase tested** — whether the existing `deep_pass_value_provenance` prompt, run blind from source by a
fresh uncontaminated subagent, discovers the H-03 `NoyaValueOracle._getValue` mechanism without a new detector or
the answer key.

**Blind prompt result** — `finding` (high): "in-loop hop conversion uses the static `asset` instead of the updated
loop-carried `quotingToken`" → wrong from-token for every hop after the first; ≥2-hop routes mis-value the asset;
evidence-cited + repro hint. Blind grade: **PROMPT_HIT**.

**Post-hoc H-03 grade** — strict match; mechanism exact; impact correct (multi-hop mis-valuation / value_exit);
consistent with High (pending human + PoC); would have produced a reviewable candidate with zero answer-key access.

**Source evidence** — `_getValue(asset, baseToken, amount, sources)`: loop sets `quotingToken = sources[i]` but
calls `_getValue(asset, sources[i], initialValue)` each hop; `quotingToken` is used only in the post-loop call.

**Safety / routing** — surface H-03-class deep-pass output via the P135/P136 advisory channel to
`human_review_queue` as **advisory_only / submission_ready=false / requires_human_review=true**; review evidence
only; human + PoC required before severity/submission; no new detector; no auto-confirm.

**Controls** — clean `convertCToL` → strong_clear (no over-flag); single-hop oracle `getValue` → needs_human (no
false finding); Morpho TVL → finding (correct H-19 sign error, but aided by a role annotation in the packet → not
counted as clean blind generalization).

**Decision** — PROMPT_CONVERTS_RESIDUAL.

**Tests / integrity** — no code changed (analysis only); active audit unchanged (`quantamm-2024-12-eval`);
`rank_signal_probe --self-test` OK; full `pytest -q` 1607 passed / 2 pre-existing snapshot fails / 4 skipped.

**Deliverables** — `documentation/research/assisted_mode/p137_h03_value_provenance_conversion/` (problem_statement,
prompt_process_map, blind_source_packet, blind_prompt_output, blind_grade, posthoc_answer_key_grade,
routing_recommendation, optional_controls, decision .md + metrics.json + runtime_output.txt).

**Next recommended phase (P138)** — build a small **blind value-provenance corpus** (e.g. 10–15 multi-hop/value-
loop functions across protocols, mix of buggy + clean) and run the prompt blind to measure a real precision/recall
+ FP rate; only if it sustains low FP, consider promoting the H-03-class routing from manual deep-pass rec to an
auto `human_review_queue` advisory. Independently, a PoC/runtime confirm of H-03 (≥2-hop route with distinct
per-pair oracles) would convert this review-evidence HIT into a runtime-confirmed mechanism.
