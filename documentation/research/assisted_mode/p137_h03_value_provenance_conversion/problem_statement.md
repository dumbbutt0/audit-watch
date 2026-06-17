# P137 — Problem Statement

P134 found one true residual detector MISS: H-03 `NoyaValueOracle._getValue` (multi-hop value-provenance /
loop-variable bug) — no static taxonomy catches it. P136 routes that class to the existing
`deep_pass_value_provenance` prompt instead of building a detector.

**Primary question:** Can the existing `deep_pass_value_provenance` process discover the H-03 mechanism from
SOURCE, blind (no answer key, no new detector)?

**Blindness method:** I have read the H-03 answer in prior phases, so the blind run is performed by a fresh,
uncontaminated general-purpose subagent given only the prompt + an answer-key-free source packet. I do only the
post-hoc grading. Blind output is separated from informed grading (constraints 7–8). Result is review-evidence
only; nothing submission-ready from prompt reasoning.
