# P274 — DIAGNOSIS (Phase 11)

## Verdict: **A — FULL_PATH_VALIDATED_EXACT_OR_STRONG**
## Bottleneck: **I FULL_PATH_VALIDATED**

### Core question answered
*Does award-class coverage close the "valid non-awarded true positive" mismatch — can the full system recover an
awarded mechanism (exact/strong, runtime-supported) when cross-class coverage prevents triage monoculture?* **Yes, on
this target.** The complete chain (recall → selector → **coverage router** → impact triage → completion → runtime PoC)
recovered **two EXACT awarded High mechanisms pre-reveal, each with a passing runtime PoC, from two distinct award
classes**, with **0 severe false positives**.

### Scorecard
| metric | result |
|---|---|
| EXACT awarded recoveries (pre-reveal, PoC) | **2** — H-03 (Access Control), H-02 (Math/Share) |
| STRONG awarded recoveries | 0 additional (the 2 EXACT also have runtime PoCs) |
| FAMILY / SUBSYSTEM_ONLY | `offers`→H-13 (locus surfaced, mechanism missed); `settleWithBuyout`→H-05/H-06; `mergeTranches`→H-01/H-14; queue→H-07/08/09 |
| NON-AWARDED true positives | 1 (M3 `burnAndWithdraw` stranding — real, QA-adjacent) |
| severe concluded/reportable FP | **0** |
| classes routed → classes with EXACT recovery | 5 → 2 distinct (ACCESS, MATH/SHARE) |

### Why this is A and not B/C/D
- **Not D (STILL_NONAWARDED_TRUE_POSITIVES):** the P272 failure mode is *closed*. In P272 the impact-first accounting
  monoculture spent every slot on accounting and recovered only a non-awarded TP. Here the coverage layer routed
  ACCESS, SHARE, DOS, ACCOUNTING, STATE; the two EXACT recoveries came from **ACCESS_CONTROL** (H-03 `distribute`) and
  **MATH/SHARE** (H-02 WithdrawalQueue) — exactly the non-accounting classes a monoculture would have dropped. We also
  produced a non-awarded TP (M3), but **not at the expense of** the awarded ones.
- **Not C (COVERAGE_MISSED_AWARDED_CLASS):** both recovered awards' classes were routed and converted.
- **Not B (EXACT_STILL_PARTIAL):** the recoveries are EXACT (root cause + locus + fix), not merely class+locus.
- **A requirements met:** ≥1 EXACT awarded mechanism pre-reveal (have 2) · runtime/PoC support (both) · 0 severe FP ·
  advisory/dashboard safe · frozen modules byte-identical · active audit unchanged · no production-authority leakage.

### Per-stage localization (what worked, what leaked)
- **Recall:** surfaced both winning loci (`distribute`, WithdrawalQueue) plus most awarded subsystems. **Worked.**
- **Selector:** anti-easy-PoC KEEP_BOTH preserved the high-impact accounting/order mechanisms. **Worked.**
- **Coverage router (the new stage):** broke the accounting monoculture — only 1 of 5 slots accounting; routed ACCESS,
  SHARE, DOS, STATE. **This is the decisive stage for the A result.**
- **Triage:** kept 4 classes, deferred only the easy dust control. **Worked.**
- **Completion/PoC:** converted ACCESS (H-03) and SHARE (H-02) to EXACT runtime proofs. **Worked.**
- **Remaining gaps (downstream, not the bottleneck):**
  1. **Within-class selection** — the coverage router covers a *class* with one rep and picks the within-class rep by
     score-then-input-order; `settleWithBuyout` (H-05/H-06) lost the STATE slot to `burnAndWithdraw`. A richer awarded
     STATE mechanism was demoted by an input-order tiebreak.
  2. **Exact-mechanism depth on ORDER** — `offers`/H-13 locus was surfaced and examined but the exact missing check
     (`executionData.duration ≤ offer.duration`) was not derived blind.
  3. **PoC-harness depth** — `mergeTranches`/queue-accounting awards (H-01/07/08/09/14) need the full loan stack; not
     pursued under partial-runtime.

### Honest bounds (production authority remains WITHHELD)
- **n = 1 full-path validation.** Two EXACT recoveries on **one** target is a strong signal, not proof of a general
  capability. The arc needs ≥1 more fresh diverse target before any production claim.
- **Training-confound disclosed:** gondi is 2024-04, pre-cutoff, public — the awards may be in training. Mitigated by
  doing all selection/coverage/triage/completion blind pre-reveal and freezing+hashing before opening the key, but not
  eliminated.
- The within-class-selection and ORDER-exactness gaps above are real and bound how many of the 37 awards this path
  converts (2 EXACT of ~6 plausibly-in-reach awarded loci surfaced).
- Coverage **enabled** recovery; it did not **cause** it alone — recall had to surface the loci and completion/PoC had
  to convert them. The claim is "the full path, with coverage, recovers awarded mechanisms," not "coverage recovers."

### The arc
P266 RANKING_GAP → P267 selector → P268 TRIAGE_GAP → P269 triage → P270 routes-onto-awarded-loci (family-level) →
P271 family→exact scaffold → P272 generalizes blind but **AWARD-CLASS mismatch** (non-awarded TP) → P273 coverage
layer breaks the monoculture (backtest) → **P274 the full path with coverage recovers 2 EXACT awarded Highs across 2
classes, blind, runtime-proven, 0 severe FP.** The selection-layer arc that began at P259 is, on this target,
**validated end-to-end.** Next: replicate on ≥1 more fresh diverse target; address within-class selection +
ORDER-exactness before any production-authority decision.
