# P183 — Deep-pass mechanism enumeration + exploit framing: VALIDATION

**Goal:** fix the dominant remaining quantamm recall loss (P182): hot surfaces were already deep-read, but the
deep pass selected the first mechanism and stopped, missing the awarded 2nd/3rd bug. **This phase is about not
missing the second/third bug on a function already reached — not finding new functions.**

**Change (production change #5):**
- `prompts/deep_trace.md` (the production deep-trace agent, wired via `run_deep_analysis.py`/`deep_trace.py` —
  the confirmed producer of the single-mechanism findings): additive **STEP 0 Mechanism Inventory** (≥3 from an
  awarded-style menu) + **Rejection Table** (source-fact · who-loses/who-gains · downstream-guard dependency) +
  **Chosen Mechanism + Impact-Direction check** + **Stop Condition** (may not finish if another mechanism affects
  a different actor/state-var or could be higher severity). Existing STEP 1–5 (now 1–7) preserved → recall-safe.
- `scripts/validate_deep_pass_mechanisms.py` — ADVISORY checker (read-only, never blocks): reports per deep-trace
  finding whether it carries the enumeration fields, making missing fields visible. Writer left untouched (the
  standalone validator satisfies "make missing fields visible" without touching the write path).

## Validation (offline — api-free, no in-session LLM)
api-free has no non-interactive LLM, so this **cannot** generate new deep-trace outputs and **cannot** measure
whether the model SELECTS the awarded mechanism. It measures what is deterministic:

| metric | result |
|---|---|
| **awarded_mechanism_enumerated** (awarded mechanism ∈ STEP-0 inventory menu) | **9/9** |
| **stop_condition_would_continue** (fn already had a produced mechanism + awarded differs in actor/state/severity) | **9/9** |
| checker flags single-mechanism output | **yes** (missing inventory/rejection_table/who_loses_gains/impact_direction/stop_condition) |
| checker passes a complete enumerated output | **yes** |

Per-finding (the 9 P182 function-level DEEP_RUN_BUT_WRONG_MECHANISM losses):
| finding | function | awarded mechanism → inventory category | already-produced (the bug that was reported) | stop clause |
|---|---|---|---|---|
| H-07 | onAfterRemoveLiquidity | unauthorized state deletion | H-06 FILO loop underflow (Med) | different actor + higher severity |
| H-03 | onAfterSwap | missing invariant enforcement | H-02 inverted-division fee | different mechanism/severity |
| M-02 | onAfterRemoveLiquidity | precision/packing/normalization edge | H-06 FILO loop underflow | different state variable |
| M-03 | afterUpdate | missing invariant enforcement (100-cap) | H-01 NFT-transfer fee-bypass | different mechanism + state var |
| M-06 | _getData | external-call failure / DoS | (oracle read deep-read) | different actor (all users) + DoS |
| M-10 | afterUpdate | wrong lifecycle ordering | H-01 NFT-transfer fee-bypass | different actor (victim) + impact |
| M-17 | onAfterRemoveLiquidity | missing invariant enforcement (bound) | H-06 FILO loop underflow | different mechanism (bound) |
| L-01 | afterUpdate | stale accounting snapshot | H-01 NFT-transfer fee-bypass | different state variable |
| L-02 | _getData | precision/packing/normalization edge | (oracle read deep-read) | different mechanism |

**noise bound:** every enumerated mechanism must carry a source-fact rejection or be the chosen one (rejection
table), which caps "mechanism spam" by construction.

## NOT measured offline (stated limitation)
- `awarded_mechanism_selected` — whether the in-session model now CHOOSES the awarded mechanism.
- real `noise increase` — whether enumeration adds low-value candidates in practice.
Both require a future **in-session quantamm deep-trace run**. P183 proves the prompt now REQUIRES enumeration
(and the awarded mechanisms are all in the menu, and the stop-condition would have kept tracing), and the
checker makes omissions visible — it does **not** prove recovery.

## Decision: PROMOTE the prompt + advisory checker (recall recovery NOT claimed)
- Enumerability 9/9 + stop-condition 9/9 + checker correct + recall-safe (additive, can only add enumeration) +
  noise bounded by the rejection table → PROMOTE as a low-risk discipline.
- **Claim is limited to mechanism-enumeration coverage.** Recall recovery (awarded_mechanism_selected) is a
  **monitored follow-up** requiring an in-session deep-trace run — explicitly not claimed here.
