# P282 — VALUE_FLOW_DERIVER_DESIGN

## Why P281 localized D3
P281 made READY body-aware; 11 candidates blocked NEEDS_VALUE_FLOW_EVIDENCE (accounting/math/oracle/rewards). The
question: can source-span value-flow analysis lift them honestly?

## Extraction (source span only; never award text)
Over the candidate's function body span, detect:
- **state writes** (`=`/`+=`/`-=`/`.push`/`delete`), **asset moves** (transfer/safeTransfer/send/call{value}/mint/burn/
  withdraw/redeem/claim), **share/asset math**, **debt/collateral/oracle/reward** terms.
- **structural anomaly**: division-before-multiplication ordering (`/ … *`) — a source-detectable precision bug class.
- **wrapper/delegation**: a body that just `return _x(...)`/`return a.b(...)` with no in-span write -> value-flow is in
  the callee, OUT of span (`value_flow_out_of_span`).
`value_flow_detected = (value terms present) AND (in-span state-write OR asset-move)` — **naming alone is NOT value-flow.**

## Confidence (precision discipline)
- HIGH: external entry + concrete in-span write/move + class terms + a specific source-backed invariant/assertion
  (e.g. a div-before-mul anomaly).
- MEDIUM: two clear + one bounded assumption.
- LOW: naming-only / no concrete write / wrapper-delegation / inline-guarded.
**A function moving value is not, by itself, >= MEDIUM.**

## Lift rule (gate)
A value class lifts past the D3 block ONLY with `value_flow_detected AND value_anomaly_div_before_mul`. Otherwise
NEEDS_VALUE_FLOW_EVIDENCE with a sharp subreason: value_flow_out_of_span / value_flow_present_but_no_anomaly /
no_value_flow_in_span.

## D1-gap closure (necessary so D3 can't false-lift guarded fns)
P281 D1 patterns were left-biased. P282 adds: msg.sender on EITHER side of ==/!= ; modifier-auth `only[A-Z]\w*`
(onlyOwner/onlyManager/onlyRole/...). This catches inline-guarded functions (commitCheckpoint `!=msg.sender`,
openPosition `onlyManager`) that previously slipped into the value-flow path.

## Forbidden over-inference (examples)
- "function calls transfer" -> NOT READY (no anomaly).
- "function writes a mapping" -> NOT READY.
- wrapper `return _claimFees()` -> NOT READY (value-flow out of span).
Fail-closed: missing span -> NEEDS_SOURCE_SPAN; never sets severity/reportability.
