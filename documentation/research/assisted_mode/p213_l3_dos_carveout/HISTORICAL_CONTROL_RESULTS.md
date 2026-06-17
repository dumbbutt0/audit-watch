# P213 — historical control results

All required invariants hold under the repaired mapping:
- **SOPH-03 (P212): medium → High.** ✅ the under-rating is fixed.
- **decent M-03 (P204): not → High** (stays medium; auth-bypass, no deterministic core-path DoS). ✅
- **vultisig M-03 (P207): not → High** (stays medium; cap-bypass, not DoS / not core-path). ✅
- **decent-06 / decent-12 false-Highs: not → High** (medium / needs_harness). ✅
- **Static High without PoC: blocked** (needs_harness; criterion 1 fails). ✅
- **SOPH-01 / SOPH-02 (refuted): unchanged** — their L3 records are FAIL with `source_validity_notes` containing
  "REFUTED", so `decide()` already returns invalid and the carve-out never upgrades invalid. ✅
- **munchables P206 DoS/griefing "Highs": NOT auto-High** — no executed deterministic L3 proof + no control →
  criterion 1/9 fail → stay needs_harness. ✅ (the key over-HIGH guard)
- **Medium path unchanged** unless ALL 10 criteria hold. ✅

Net: the carve-out raises exactly one case (SOPH-03), introduces zero false-Highs, and leaves every validated negative
control below High.
