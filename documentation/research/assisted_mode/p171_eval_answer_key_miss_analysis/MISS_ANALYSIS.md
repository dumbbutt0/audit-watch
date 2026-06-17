# P171 — Eval answer-key miss analysis & taxonomy-gap review

Read-only analysis. No hunting / harnesses / detector / routing / severity / corpus / sidecar / answer-key
mutation. Skepticism rule applied: `MISSED_SHOULD_HAVE_FOUND` only when a source-visible signal existed AND the
pipeline already read that surface; otherwise `MISSED_NEEDS_NEW_TAXONOMY` / `MISSED_LOW_SIGNAL`.

## ⚠ HARD SEPARATION — two measurements, never combined into one recall %
- **Track A — Recall (quantamm only):** quantamm-2024-12-eval got a *full coverage pass*, so a recall % is
  valid. Source: `output/eval_ready/match_matrix.json` (44 findings) + `failure_analysis.md`.
- **Track B — Refutation-correctness (campaign H5–H24):** reject-first hunts of 3–5 leads per corpus — **NOT a
  coverage pass. No recall/coverage % is computed or implied for Track B.** It only asks: did our specific
  candidate touch an awarded surface, and did any refutation wrongly dismiss an awarded bug?

---

## 1. Coverage summary

### Track A — quantamm recall (44 answer-key findings; full coverage pass)
| Category (user scheme) | Count | Answer-key ids |
|---|---|---|
| FOUND_EXACT (HIT) | 3 | H-01, M-01, L-03 |
| FOUND_PARTIAL | 4 | H-02, H-06, L-04, L-05 |
| FOUND_ADJACENT | 1 | M-16 |
| MISSED_SHOULD_HAVE_FOUND | 12 | H-04, H-09, H-10, H-11, M-04, M-07, M-08, M-09, M-12, M-14, L-06, L-09 |
| MISSED_NEEDS_NEW_TAXONOMY | 11 | H-07, M-03, M-05, M-06, M-10, M-11, M-15, M-18, M-19, L-07, L-12 |
| MISSED_LOW_SIGNAL | 9 | H-03, H-05, H-08, M-02, M-13, M-17, L-01, L-02, L-08 |
| OUT_OF_SCOPE_FOR_CURRENT_PIPELINE | 4 | L-10, L-11, L-13, L-14 |
| **Total** | **44** | recall (touched = exact+partial+adjacent) = **8/44 ≈ 18%**; exact = 3/44 |

*Note:* precision on this run was perfect (0 FP). The weak axis is recall, concentrated outside the
hook/fee/oracle layer the pipeline deep-read.

### Track B — campaign refutation-correctness (NOT a coverage measurement — no %)
| Candidate | Corpus | Our target fn | Awarded? | Classification | Refutation correct? |
|---|---|---|---|---|---|
| B5 | blackhole-2025-05-eval | RewardsDistributor.claim_many | **YES — awarded M-04** | **FOUND_EXACT** (runtime-confirmed) | n/a (confirmed, not refuted) |
| H12 | zaros-2025-01-part-2-eval | CreditDelegationBranch._convertAssetsToUsdc (internal) | contract awarded (H-01/H-05/H-06) but a *different* fn | **FOUND_ADJACENT** (right module, wrong fn) | ✅ the internal swap fn we examined genuinely isn't the awarded bug |
| H11 | silo-finance-2025-03-strict-eval | BaseIncentivesController.claimRewards | own-rewards claim (not a foreign-value award) | none / refutation correct | ✅ own-funds, not an awarded theft |
| H1, H3 | centrifuge / decent (runtime-confirmed mechanisms) | UserEscrow.transferOut / UTBFeeCollector | **not analyzed — firewall-sealed** | not_analyzed | preserved blind holdout |
| H6, H13, funnel H-01..03 | pooltogether / predy / vultisig | — | **not analyzed — sealed** | not_analyzed | preserved blind holdout |
| H14–H24 | maia-talos / tokemak / renzo | — | awarded sets not local | not_analyzed | — |

**Track B key result:** across every corpus we *could* check, **no reject-first refutation wrongly dismissed an
awarded bug.** B5 we confirmed (awarded). zaros H12 is an *adjacency/selection* miss (right contract, wrong
function) — not a wrong refutation. This is the central P171 lesson for the campaign: the failure mode is
**function selection within the right module**, not bad refutation.

---

## 2. Miss taxonomy by root-cause family (Track A misses + Track B adjacency; grouped by root cause, not contest)
| Family | Count | Representative ids |
|---|---|---|
| rule/estimator math correctness (overflow/sign/normalization/single-asset) | 6 | H-09, H-11, L-06, L-09, M-07, (H-10 epsilon) |
| dynamic-weight lifecycle (sum/bounds/interval/interpolation/staleness) | 6 | H-04, M-04, M-08, M-09, M-12, M-14 |
| hook lifecycle (Balancer-V3 recovery/register/router-auth/array-griefing) | 7 | H-07, M-03, M-05, M-10, M-11, M-15, M-18 |
| oracle/value-provenance robustness | 5 | M-06, M-19, L-07, L-12, L-02 |
| fee accounting mismatch | 3 | H-03, H-05, M-17 |
| authorization mismatch | 2 | H-08, M-13 |
| recipient/beneficiary misuse | 1 | M-02 (uplift-fee underflow) |
| vault share/accounting + lifecycle hygiene | 4 | L-01, L-08, L-10, L-11 |
| (cross-contract reward parity — Track B) | 1 | blackhole M-04 (found, B5) |

---

## 3. Should-have-found list (STRICT — source-visible signal + pipeline already read the surface)
1. **H-10 epsilon guard-rail violation in weight normalization** — *in reach:* the pipeline explicitly cleared
   rule-math "because `_guardQuantAMMWeights` clamps downstream" — but the guard **is** that function. Signal:
   normalization writes weights without re-checking the epsilon bound. Failed precondition: "guarded-downstream"
   strong-clear when the guard is itself in scope. Fix: forbid that clear → `needs_deep_pass`. FP risk: low.
2. **H-09 integer overflow in QuantAMMMathGuard** — *in reach:* `units_invariant` lens flagged
   division-before-multiplication in `_getWeights` but the flag was cleared in the sweep. Signal: unchecked
   `int128`/scaling math. Fix: escalate lens flags that overlap a cleared item to a candidate. FP risk: low-med.
3. **H-11 incorrect EW-covariance estimation** — *in reach:* same rule-math file the sweep cleared generically.
   Signal: estimator update formula. Fix: estimator-math lens (§4). FP risk: medium (needs a comparand).
4. **H-04 missing `lastUpdateIntervalTime` update → stale interpolation** — *in reach:* setWeights lifecycle was
   read for L-03. Signal: a state var read for interpolation never written on update. Fix: dynamic-weight
   lifecycle invariant. FP risk: low.
5. **M-04 setWeights length-check-mismatch DoS / M-14 missing updateInterval / M-09 post-init minWeight bypass /
   M-12 computeBalance boundary revert** — *in reach:* all on `setWeights`, already read. Signal: missing
   length/interval/bounds checks visible in the signature+body. Fix: dynamic-weight lifecycle family. FP risk: low.
6. **M-08 maxTradeSizeRatio bypass** — *in reach:* the guard was read in `onSwap`; the bypass path wasn't tested.
   Signal: ratio computed on a manipulable input. Fix: test guard bypass, not just guard presence. FP risk: med.
7. **M-07 quantAMMPack32Array precision loss / L-06 negative weights / L-09 single-asset variance underflow** —
   *in reach:* rule-math/pack functions in scope, cleared. Signal: integer-division + signed math edges. Fix:
   estimator-math lens. FP risk: medium.

(These 12 are the honest "should-have-found": the pipeline read the file and a lens or a clear-rationale touched
the exact spot. Everything else is bucketed needs-new-taxonomy / low-signal.)

## 4. New taxonomy needed → see `taxonomy_gap_recommendations.md` (full detail). Summary:
- **F1 dynamic-weight lifecycle** (AMM-with-dynamic-weights) — explains 6 misses.
- **F2 rule/estimator math-correctness** — explains 6 misses; harness-feasible (pure math).
- **F3 Balancer-V3 hook lifecycle** (recovery/onRegister/router-auth/FILO griefing) — explains 7 misses.
- **F4 oracle-integration robustness checklist** (revert-handling/sequencer/deviation/decimals/zero-staleness) —
  explains 5 misses.

## 5. Detector / selector gap map
| Awarded | Should have been caught by | Gap | Proposed improvement |
|---|---|---|---|
| H-10, H-09, L-06 | `units_invariant` lens (it *flagged* div-before-mul + decimals) | flag was **cleared in the sweep**, not escalated | escalate lens flags overlapping a cleared item → candidate; forbid guarded-downstream clear when guard in scope |
| H-11, M-07, L-09 | (none — no estimator-math lens) | missing lens | add F2 estimator-math lens |
| H-04, M-04, M-08, M-09, M-12, M-14 | invariant extractor | no dynamic-weight lifecycle invariant family | add F1 lifecycle invariants (sum/bounds/interval/interpolation/staleness) |
| H-07, M-11, M-15, M-03, M-10, M-18, M-05 | (none — no hook-lifecycle lens) | missing lens | add F3 Balancer-V3 hook-lifecycle lens |
| M-06, L-07, L-12, M-19 | oracle lens (caught one staleness mechanic) | checklist incomplete | extend oracle lens to the F4 robustness checklist |
| zaros H-01/H-05/H-06 (Track B) | hygiene-filtered selector | selector picked the internal swap fn, not the credit-delegation accounting fn in the same contract | family-aware function ranking within a flagged contract (prefer state-mutating accounting fns over internal swap plumbing) |

## 6. False-positive lesson integration (H10–H21) — filters each new selector MUST keep
The campaign's refutations are the FP guardrails the new lenses must not regress:
- **source-guard-present (H19/H24 + quantamm over-clearance):** the single most important — F1/F2 must verify the
  guard is *actually in scope and unproven* before flagging (this is exactly the quantamm "guarded-downstream"
  clear failure; the fix is symmetrical — don't clear on an unproven in-scope guard, and don't flag if a proven
  guard covers it).
- **vendored/mock noise (H10):** F2 estimator-math must scan protocol_src only (math libs vendored vs protocol).
- **permissioned (H7/H13/H16/H17):** F1 lifecycle must check `setWeights`/update reachability — only flag the
  permissionless update paths (M-08/M-09/L-04 are permissionless; an onlyOwner setter is not a finding).
- **caller-claims-own (H11/H15/H21):** F3 hook/claim selectors must confirm foreign value, not own accrual.
- **dust/MEV/donation + fixed-recipient (H8/H20/H23 + H17):** any recipient/fee selector must require
  attacker-controlled foreign value, not router dust or a fixed feeRecipient.
- **no-sibling-divergence (H14/H18):** parity selectors must confirm one sibling actually omits what another
  applies (B5 had it; H14/H18 didn't).

## 7. Prioritized next taxonomy work (3–5; ranked) → detail in `taxonomy_gap_recommendations.md`
1. **F1 dynamic-weight lifecycle invariants** — most misses explained (6) with the highest source-detectability
   (setWeights/update signatures) and low FP risk. PROMOTE to next campaign.
2. **F2 rule/estimator math-correctness lens** — 6 misses, **harness-feasible** (pure math, deploy-light), medium
   FP risk (needs a corrected-reference comparand). PROMOTE — strong runtime-confirm potential.
3. **F3 Balancer-V3 hook-lifecycle lens** — 7 misses but integration-specific + higher FP risk; KEEP_EXPERIMENTAL.
4. **F4 oracle-integration robustness checklist** — 5 misses, mostly Low severity; lower yield; KEEP_EXPERIMENTAL.
5. **Selection fix (Track B):** family-aware function ranking within a flagged contract (prefer state-mutating
   accounting fns over internal/plumbing) — directly addresses the zaros H12 adjacency miss. PROMOTE (cheap).

## 8. Next campaign recommendation (answer-key-grounded)
- **Target families:** F1 dynamic-weight lifecycle + F2 estimator-math (the two PROMOTE families with the best
  misses-explained × detectability × harness-feasibility).
- **Target corpora:** AMM-with-dynamic-weights / rule-based-rebalancing protocols. Concretely re-run against
  `quantamm-2024-12-strict-eval` (held-out sibling of the analyzed eval — fresh blind set) and similar
  dynamic-weight AMMs; these are exactly where F1/F2 misses concentrated.
- **Selection rules:** hygiene-filtered protocol_src; signatures `setWeights*`/`updateWeight*`/`*MathGuard`/
  `*covariance`/`*gradient`/`pack*Array`; **prefer permissionless update paths + state-mutating accounting fns**
  (Track B fix).
- **Reject-first gates:** the existing 8 gates **plus** the new rule: *do not clear a candidate on a downstream
  guard that is itself in scope and unproven → route to deep-trace* (the #1 should-have-found lesson).
- **Max candidates:** 5. **Stop condition:** after the first corpus, or on the first HARNESS_CANDIDATE that
  converts (then triage it before continuing — P163 soft rule).

---

### Honesty notes
- Track A recall (18% touched / 7% exact) is a *recall-first single-corpus* number; it is **not** combined with
  Track B (which has no %). The campaign was precision-first by design; low recall there is expected, not a
  regression.
- Firewall-sealed holdout keys (centrifuge/decent/pooltogether/predy/vultisig) were **not opened** — preserved
  for blind reuse; their candidates are `not_analyzed`, not graded.
- Every "should-have-found" cites a signal the pipeline demonstrably saw (a lens flag or a read+cleared
  rationale in `failure_analysis.md`); speculative misses were bucketed needs-new-taxonomy / low-signal.
