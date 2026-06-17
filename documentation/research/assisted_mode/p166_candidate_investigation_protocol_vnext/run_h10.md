# P166 Part C — Protocol vNext run: candidate H10 (revert-lend)

**This is the demonstration run; the tooling/protocol (Parts A/B) stand independently of it.**

**Candidate:** `H10-revert-lend-originalowner-libnoise` (audit `revert-lend-2024-03-strict-eval`) ·
**Bucket:** `SOURCE_REFUTED` (G0) · **Decision:** `SOURCE_REFUTED_NO_HARNESS` · **Harness built:** no ·
**Duplicate:** duplicate_unknown.

## Selection
Protocol-vNext booster hunt (correction-layer-first) across fresh vendored corpora. revert-lend showed the
strongest fresh correction-layer grep signal: `originalOwner`. Selected it as the candidate to refute.

## Step 5 — Prediction (logged BEFORE investigation)
`predicted_outcome = static_false_positive` — rationale: "fresh-corpus correction-layer grep signal but
reject-first prior + corpus depletion; must confirm the signal is real protocol code, not vendored-lib noise."
(Logged to `output_research/option_a_campaign/prediction_log.jsonl`.)

## Step 1 — REFUTATION CASE
| Refutation hypothesis | Resolution (source) |
|---|---|
| The `originalOwner` correction layer is vendored-lib noise, not protocol code | **CONFIRMED.** The only `originalOwner` references are `lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol:10` and `lib/permit2/lib/openzeppelin-contracts/contracts/mocks/ERC1271WalletMock.sol:10` — both vendored **test mocks**, out of audit scope. |
| There is some other in-scope correction layer | **REFUTED (absent).** `grep originalOwner` in revert-lend protocol `src/` = **0**. No managed/original-owner/escrow-beneficiary recipient-correction layer exists in scope. |
| (the remaining refutations — permission/recipient/MEV/time/sibling-parity/etc.) | **moot** — there is no candidate mechanism to analyse once G0 fails. |

`sandbox_check.py` on the read source → CLEAN.

## Step 2 — Failure bucket
`SOURCE_REFUTED`, first failed gate **G0 (correction-layer-exists)**. Specific evidence: the correction-layer
signal resolved entirely to vendored library mocks; protocol `src/` has zero occurrences. The candidate's
premise (a recipient/ownership-correction layer with a sibling-divergence) does not exist in scope.

## Step 3 — Converter analysis
Not reached (G0 failed). attacker_recipient_status = n/a, profit_source = none, permission_model = n/a.

## Step 4 — Harness decision
`SOURCE_REFUTED_NO_HARNESS` — a source-level refutation exists (no correction layer in scope), so a harness is
not allowed. **0 harnesses built.**

## Step 5/6 — Prediction vs outcome + learning
- predicted `static_false_positive` → recorded `static_false_positive` ⇒ **calibration: correct (1/1).**
- Ledger row recorded with `rejection_type=source_refuted`, `first_failed_gate=G0`, `harness_built=false`,
  the learning fields, and the lesson.

## Lesson for future campaigns
**The correction-layer grep MUST exclude `lib/` and `*/mocks/*` before a signal is treated as real.** P166's
booster hunt was fooled at the selection stage by vendored-library `originalOwner` mocks; the reject-first
Step-1 caught it immediately (G0), at zero harness cost — exactly the protocol working as intended. Add a
`-not -path '*/lib/*' -not -path '*/mocks/*'` filter to the correction-layer selector's signal scan.

## Outcome vs the success metric
Reportables-per-harness unchanged (1/1); harnesses_avoided +1 (now 5); source_refutations +1 (now 3);
fabrication_rate 0/6; prediction_accuracy 1/1. A clean reject-first demonstration: a candidate selected,
refuted from source at the first gate, logged, with no wasted harness and an honest, correct prediction.
