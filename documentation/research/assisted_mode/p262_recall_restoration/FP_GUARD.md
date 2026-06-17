# P262 — FP_GUARD (zero CONCLUDED/REPORTABLE false positives — not true 0-FP)
The recall sweep is ADVISORY ONLY. It deliberately WIDENS recall (more candidate loci) — so it will surface many
non-bugs. That is acceptable *because it never concludes*:
- Output flags emits_findings:false / concludes_vulnerability:false; runtime _assert_no_conclusions raises if any
  candidate has severity / concluded:true / vulnerability:true / reportable:true / submission_ready:true.
- Every candidate = RECALL_CANDIDATE_ONLY + needs[NEEDS_RANKING, NEEDS_COMPLETION, NEEDS_REFUTATION].
## Promotion rule (a recall candidate becomes a finding ONLY after a later separate stage proves ALL of):
source-backed mechanism · attacker control · invariant/value delta · victim/gainer · terminal-or-amplifiable impact
· B/C ranking survival · five-operation completion · explicit FP refutation.
## Honest claim
This preserves **0 concluded/reportable false positives** by construction (advisory + promotion-gated). It does NOT
claim true 0 false positives at the candidate stage — recall expansion intentionally trades candidate-precision for
locus-recall, and the downstream ranking/completion/refutation stages are what protect report quality.
