# P185 — Mechanism carry-forward ranking patch: VALIDATION

**Goal:** fix the measured P184 failure — a real awarded mechanism (**M-02**) was enumerated but DEMOTED into the
rejection table instead of carried. This phase **preserves plausible mechanisms once enumerated**; it adds no new
families/detectors and claims no new recall.

**Change (production change #6, prompt + checker only):**
- `prompts/deep_trace.md` — **carry-forward ranking rule** (a mechanism MUST stay carried — in
  `selected_mechanisms` or `unresolved_mechanisms`, never buried in `rejected_mechanisms` — if it has source
  evidence / plausible impact / a different actor-or-state-or-auth path / an unproven rejection / could be higher
  severity; "do not demote merely because another is easier to explain or you already found one bug"). New
  schema `selected_mechanisms` (list) / `unresolved_mechanisms` (list) / `rejected_mechanisms` (source-backed
  only). Trivial M-17 menu add: "value exceeds a logical/economic bound (>100% / > cap)".
- `scripts/validate_deep_pass_mechanisms.py` (advisory) — accept `selected_mechanisms`/`chosen_mechanism` as a
  LIST; accept `impact_direction` as structured prose (who-gains + who-loses + impacted state + self-funded/
  admin/dust/timing exclusion); new **`demoted_unresolved_mechanism`** flag (a rejected row with real impact +
  unproven/no-source rejection — the M-02 signal); `selected_count` for noise tracking.

## (A) Checker replay on the P184 blind outputs (`validate_p185.py`, read-only)
| metric | P184 via P183 checker | P184 via P185 checker |
|---|---|---|
| complete | **0/5** (schema false-fails) | **5/5** |
| `demoted_unresolved_mechanism` | n/a (flag didn't exist) | **2/5** (onAfterRemoveLiquidity=M-02, oracle=int216-norm) |
| avg selected / surface | n/a (dict only) | 2.80 |

The schema false-failures are eliminated (5→0), and the new detector **correctly surfaces the M-02 demotion**
plus a second genuine oracle demotion that were invisible before.

## (B) Blind RE-RUN with the UPDATED prompt (decontaminated; source + updated prompt only, no answer key)
| target | P184 | **P185** |
|---|---|---|
| **M-02** (lpTokenDepositValueChange underflow) | enumerated but FOLDED into rejection (demoted) | **CARRIED as `selected_mechanisms` #3** ✓ |
| M-17 (feePerLP > 100%) | not enumerated | **enumerated + carried in `unresolved_mechanisms`** ✓ |
| H-07 (onAfterRemoveLiquidity) | selected | selected (stable) |
| H-03 (onAfterSwap) | selected (loose) | selected (loose) + div-by-zero carried as 2nd |
| `demoted_unresolved` on onAfterRemoveLiquidity | 1 | **0** |
| avg selected / surface (onARL + onAfterSwap) | 2.50 | **2.50 (stable)** |

## Metrics (your guards against list inflation)
- **M-02 carried forward?** YES (rejected/folded → selected).
- **selected_mechanisms list accepted?** YES (checker `mechanism_complete`).
- **unresolved not falsely rejected?** YES (M-17 + 2 others in `unresolved_mechanisms`; only clean source-backed
  rejections remain; `demoted_unresolved` = 0 on the re-run).
- **noise increase?** NONE — `average_selected_mechanisms_per_surface` 2.50 → 2.50 (M-17 went to `unresolved`,
  not padding `selected`).
- **checker false-failures reduced?** 5 → 0.
- **`demoted_unresolved_mechanism` before/after?** P184 = 2/5 detected; P185 re-run onAfterRemoveLiquidity = 0.

## Decision (reviewer's result matrix)
**M-02 carried, noise stable → STRONG SUCCESS → PROMOTE.** The carry-forward rule moved M-02 from demoted to
carried without inflating the selected list, the checker stopped false-failing valid multi-mechanism outputs,
and the new flag both detects past demotions and confirms the re-run no longer demotes.

## Honesty / caveats (no recall claim)
- This is a blind **n=2** demonstration that the rule FIRES (M-02/M-17 carried), not a recall-recovery claim.
- The M-02 carry-forward is partly **self-fulfilling**: the rule explicitly targets M-02's exact shape (impact +
  distinct state-var + unproven rejection), so a blind agent carrying it confirms the rule works, not that it
  generalizes. Same residual same-model-family caveat as P184; firewall-sealed fresh-model run = gold standard.
- H-03 remains a loose near-duplicate of the already-found PARTIAL H-02 (documented, not fixed). M-17 is carried
  as `unresolved`, not a confirmed selection (opportunistic, not claimed).
- `fabrication_rate=0`: raw blind outputs preserved verbatim in `mechanism_ranking_trace.json`.
