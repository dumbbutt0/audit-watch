# Silo Stalk/Stem Conservation Review

Use for items surfaced by `scripts/silo_stalk_audit.py`. This lens is about **conservation of deposit
amount, BDV, stem, stalk, grown-stalk, roots, and reward scaling** across Silo transfer/reward/germination
flows — not "find stalk words". A Silo helper is dangerous when it silently mints/burns value via rounding,
lets a caller choose a stem, or drops a unit-scale factor.

Read the function body and every caller. Answer each with evidence (file:line):

1. **What deposit/stalk/stem value enters?** (amount, BDV, stem, stalk, grown-stalk, roots, seeds).
2. **What deposit/stalk/stem value leaves?** Compare in vs out.
3. **Is amount, BDV, stem, grown-stalk, and stalk preserved** end-to-end across the operation?
4. **Is rounding direction safe?** Does any roundUp/roundDown favor the user in a way that nets value over
   repeated calls (e.g. `(roots-1)*stalk/totalStalk + 1`)?
5. **Are user totals AND global totals both updated?** (per-account stalk/roots/deposit vs `s.sys.silo.*`).
6. **Are roots/stalk/reward ratios preserved** after mint/burn/transfer and reward distribution?
7. **Does partial transfer recompute stem correctly?** A split must keep the source stem and split BDV
   proportionally — never derive a lower stem.
8. **Does reward scaling use the correct denominator/scale?** (stem-scale 1e6 / PRECISION present; no
   truncation-to-zero; no underflow on `endStem - startStem`).
9. **Can a zero-amount or dust deposit/transfer alter accounting?** (empty deposit record, list griefing).
10. **Is this a duplicate of an existing finding?** (note the finding ID if so).

**FP discipline:** ignore generic ERC20 transfers, comment-only stalk/stem mentions, and plain getters that
just return a stored stalk value. Require a real conservation/rounding/scale defect.

**Classification (pick one):**
`confirmed_eval_finding` | `partial_eval_finding` | `real_world_poc_later` | `duplicate_of_existing` | `false_positive`
