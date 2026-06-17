# P211 — answer-key scorecard (vs decent _sealed_answer_key, read-only)

decent awarded: 4 High / 5 Medium. H-01 = setRouter→mint (High); M-03 = receiveFromBridge missing-AC (Medium).

| candidate | awarded | blind ceiling | L3 verdict | readiness (flag on) | correct? |
|---|---|---|---|---|---|
| DEC-H-01 | **High** | HIGH | PASS | High readiness CLEARED | ✅ genuine High preserved |
| DEC-M-03 | **Medium** | HIGH (over-rated) | FAIL/demoted | High readiness BLOCKED → Medium | ✅ over-rated High correctly demoted |
| DEC-STATIC (synthetic) | — | HIGH | none | High readiness BLOCKED (fail-closed) | ✅ no PoC ⇒ not High-ready |

## Scoring
- hits (genuine High preserved): 1 (DEC-H-01)
- correct demotions (awarded-Medium/over-rated-High blocked from High): 1 (DEC-M-03)
- false positives (High allowed without material L3): 0
- severity correctness: 2/2 awarded candidates classified correctly (High kept, Medium demoted)
- L3-blocker correctness: 3/3 (clear PASS, block FAIL, block missing)
- package completeness (DEC-H-01): all required fields incl L3 present
