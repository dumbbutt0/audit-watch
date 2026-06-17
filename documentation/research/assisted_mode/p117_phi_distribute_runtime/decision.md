# P117 — Decision: CuratorRewardsDistributor.distribute

## Terminal state: **CONFIRMED_RUNTIME**

Runtime decided. The harness answered the one framed question and all four spec conditions for CONFIRMED hold,
each backed by the executed test matrix (`runtime_matrix.md`, `execution_output.txt`) — not by source-only reasoning.

| CONFIRMED condition (spec) | Evidence |
|---|---|
| small-N succeeds | Case A: `distribute` at N=10 → 61,972 gas, completes (PASS). |
| large-N fails / becomes impractical | Case B: gas rises with N to **36,686,251 at N=8,000 > the 30M block limit**; Case B2: `distribute` under a 30M gas cap at N=8,000 **does not complete** (revert/OOG) → un-includable (PASS). |
| curator growth is attacker-controllable / cheaply influenceable | Source: `Cred.buyShareCred` is permissionless → `_addCredIdPerAddress` adds the buyer to the curator set; no cap; `getCuratorAddresses(credId,0,0)` returns ALL curators. N is attacker-growable and also grows organically. |
| failure blocks reward distribution | Source: `distribute` is the only distribution path, processes the entire curator set, and has no paginated variant; once un-includable, `balanceOf[credId]` rewards are permanently undistributable. |

The measured gas is a **conservative lower bound** — the mock omits the real `Cred`'s per-curator storage reads
(`EnumerableMap.at` + `isShareHolder`), so the real `distribute` is more expensive and crosses the block limit at
FEWER curators than 8,000.

## Scope / honesty notes
- This candidate corresponds to phi's **AWARDED H-03** (a known reward-distribution DoS). It is therefore **not a
  novel or submittable finding** — the value here is that the assisted pipeline independently *reached and
  runtime-confirmed a true positive* end-to-end via the P115-corrected ranking → P116 fresh surface → P117 runtime.
  This is the FIRST CONFIRMED_RUNTIME from the fresh-discovery path (P113–P116 were all NEEDS_CONTEXT).
- The secondary hypothesis (royalty-to-caller) is **resolved as NOT a bug**: phi's own test asserts the caller
  receives `depositAmount/100`, i.e. the 1% is an intended keeper fee. Not pursued.
- **No severity is assigned**, no report is written, no submission package is generated, no READY_FOR_HUMAN_REVIEW
  state is created (per the hard stops). This document records a runtime verdict only.

## Hard-stop self-check
- CONFIRMED_RUNTIME is claimed only with a passing runtime test (Cases A/B/B2/C all PASS). ✓
- No source-only reasoning used as runtime proof — the gas blowup + 30M-cap revert are executed. ✓
- No severity / report / submission language; no submission package; no READY state; no production wiring. ✓
- phi `src/` unmutated; harness lives in a standalone `/tmp/p117-phi-harness/` project + `test/audit`-style copy. ✓
