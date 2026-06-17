# P139 — Problem Statement

P138 (CORPUS_VALIDATES_PROMPT) justified promoting the H-03-class deep_pass_value_provenance routing from a
manual recommendation to an **automatic advisory** — NOT automatic finding. P139 implements that: a config-gated,
capped auto path that, for the H-03-class value-provenance recommendations the P135/P136 surfacing layer already
emits, automatically prepares + routes a deep-pass job and surfaces it to review as ADVISORY-ONLY.

Safety boundary (unchanged): auto-run -> attach advisory -> human_review_queue -> advisory_only=true,
submission_ready=false, requires_human_review=true -> human + PoC required. Nothing confirmed/severity/submission.

Primary question: can the surfacing layer auto-run deep_pass_value_provenance on H-03-class recommendations and
safely surface the result to human review, without unsafe promotion or clean-FP inflation?
