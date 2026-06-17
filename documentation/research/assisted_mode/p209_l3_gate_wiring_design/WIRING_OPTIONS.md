# P209 — wiring placement options (A–F)

Evaluation axes: advantages · risks · recall effect · severity-precision effect · failure mode · complexity ·
can-suppress-investigation? · can-mark-High-ready-without-PoC?

## A. Before `min_confirm_gate`
- **Adv:** earliest signal. **Risk:** gates candidates before fields/reachability even exist; L3 has nothing to read.
- **Recall:** ❌ can suppress candidates pre-confirmation. **Precision:** premature. **Failure:** blocks investigation
  of not-yet-confirmed Highs. **Complexity:** high (new pre-gate stage). **Suppress investigation:** YES. **Mark
  High-ready w/o PoC:** no. → **REJECT** (violates "L3 must not suppress discovery/candidate creation").

## B. Between `min_confirm_gate` and `confirm_gate`
- **Adv:** after field presence. **Risk:** runs before reachability is established, so L3 may be built for unreachable
  candidates (wasted harness cost); ordering couples two deterministic gates with an expensive evidence step.
- **Recall:** neutral-ish. **Precision:** ok but mis-ordered. **Failure:** harness spent on dead paths.
  **Complexity:** medium. **Suppress investigation:** partial (could stall the pipeline). **Mark High-ready w/o PoC:**
  no. → **REJECT** (reachability should be proven first; L3 effort wasted otherwise).

## C. Inside `confirm_gate` as a severity-specific blocker
- **Adv:** single gate. **Risk:** overloads a deterministic, no-LLM reachability gate with a realized-impact/evidence
  concern; `confirm_gate` HARD-FAILs in submission mode → an L3 miss would **hard-block the pipeline** (recall risk on
  the candidate set) and conflate "unreachable" with "impact-unproven". **Recall:** ❌ risk of blocking valid Highs
  awaiting harness. **Precision:** good but brittle. **Failure:** pipeline hard-fail on missing harness. **Complexity:**
  medium (edits a core gate → production behavior change). **Suppress investigation:** YES (hard-fail). **Mark
  High-ready w/o PoC:** no. → **REJECT** (changes core gate behavior; conflates reachability with magnitude).

## D. Inside `submission_readiness_review.py` as a readiness-only blocker
- **Adv:** exactly where readiness already lives; research-only/append-only; never flips canonical flags; new state
  `blocked_by_missing_l3_poc` fits the existing vocabulary. **Risk:** readiness overlay is human-owned, so by itself it
  doesn't surface L3 in dashboards/packages. **Recall:** ✅ none (readiness ≠ discovery). **Precision:** ✅ High
  precision at the readiness layer. **Failure:** fail-open (readiness stays not-ready). **Complexity:** low.
  **Suppress investigation:** NO. **Mark High-ready w/o PoC:** NO. → **Core of the recommendation**, but needs a
  read-only display companion → hence layered.

## E. Dashboard / report-package only
- **Adv:** zero gate risk, pure display. **Risk:** advisory only — a High could still be packaged without L3 because
  nothing blocks readiness. **Recall:** ✅ none. **Precision:** ❌ weak (no enforcement). **Failure:** silent
  High-without-PoC in a package. **Complexity:** low. **Suppress investigation:** NO. **Mark High-ready w/o PoC:** YES
  (no block). → **REJECT as the sole mechanism** (necessary for visibility, insufficient for enforcement) — include as
  a layer.

## F. Layered (D + E, gates unchanged)
- **Adv:** enforcement at the readiness layer (D) where it belongs + read-only visibility (E); discovery and the two
  deterministic gates stay byte-identical; fail-closed for High, fail-open elsewhere. **Risk:** two touch-points to
  keep consistent (mitigated: both read the same `decide()`). **Recall:** ✅ none. **Precision:** ✅ best. **Failure:**
  fail-open (not-ready), never a pipeline hard-fail. **Complexity:** low-medium. **Suppress investigation:** NO. **Mark
  High-ready w/o PoC:** NO. → **RECOMMENDED**.
