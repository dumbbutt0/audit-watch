# P235 — Shadow Live Contest Scorecard (reNFT 2024-01, Code4rena)

> Blind hunt → freeze → reveal. The hunt and submission drafts were frozen (FROZEN_HUNT.md content hashes) BEFORE
> the answer key was fetched (ANSWER_KEY_revealed.md). Sealed bot/4naly3er/slither artifacts re-verified
> byte-identical = never opened during the hunt.

## Contest scorecard (summary)
| Axis | Result |
|---|---|
| Awarded Highs | 5 (H-01..H-05) |
| Awarded Mediums | ~14 (representative set retrieved) |
| Candidates generated (blind) | 10 |
| Confirmed L3 | 1 (RENFT-01, 2/2 forge, decide()=medium → 0 false-Highs) |
| **High recovered** | **1 / 5 = 20%** (H-04, exact) + 1 partial root-cause (H-02) |
| **Weighted recall** | **≈ 10–16%** (High=3, Med=1; recovered weight 3, total ≈29) |
| Precision (submitted H/M → awarded) | ≈ 1/5 = 20% (clean) / 2/5 = 40% (incl. partial) |
| Dashboard ranking effectiveness | **Excellent** — the one true High (H-04) ranked #1/10 in the frozen queue |
| Proof-conversion | **1/1 = 100%** (the selected candidate harnessed → confirmed) |
| Submission readiness | 1/1 confirmed finding submission-ready without rewrite |
| Severity alignment | 1/1 recovered correct (H-04 predicted High = awarded High) |

## Recall (detail)
- **Strict per-finding High recall:** 1/5 = **20%**.
- **Root-cause-family High recall:** ~1.5/5 = **30%** (H-04 exact; H-02 partial — same "incomplete guard
  selector blocklist" family via RENFT-04, but the specific `setFallbackHandler` vector was not identified).
- **Medium recall:** ≈ 0 clean matches among the retrieved awarded mediums (RENFT-05/02/03 not in awarded set;
  RENFT-10 ≠ M-07). Lower-confidence (full medium set not enumerated).

## Would the dashboard have surfaced each awarded High?
| Awarded High | Surfaced? | Why / failure class |
|---|---|---|
| H-01 malicious-ERC20 tip → permanent lock | **NO** | reasoning error + **taxonomy gap**: I traced the settlement/reentrancy path but dismissed the malicious-token-revert lock as "mitigated by ordering"; no hostile-token-in-settlement griefing lens |
| H-02 `setFallbackHandler` hijack | **MAYBE** | **taxonomy gap**: flagged the root-cause family (RENFT-04, incomplete guard blocklist) but did not enumerate Safe self-management selectors (`setFallbackHandler`, owner mgmt) |
| H-03 ERC1155 reentrancy hijack | **NO** | **harness/reasoning-depth gap**: checked reentrancy, wrongly concluded mitigated; no create-time-ordering reentrancy harness |
| **H-04 disableModule offset → remove Stop** | **YES** | found blind, ICE HIGH, **confirmed L3**, ranked **#1**; exact severity |
| H-05 steal rented NFT + freeze payments | **NO** | **recall gap**: no clean theft path surfaced |

Failure-class tally: ranking failures 0 (ranking was excellent); routing failures 0; **taxonomy failures 2 (H-01,
H-02)**; **harness/reasoning-depth failures 2 (H-01, H-03)**; recall failure 1 (H-05); severity failures 0.

## Top 5 missed findings & why
1. **H-05 (steal rented NFT + freeze payments)** — no theft path surfaced; the deepest miss (direct fund loss).
2. **H-01 (malicious-ERC20 lock)** — analyzed the area but actively reasoned it away; a *reasoning* miss, not a blind spot.
3. **H-03 (ERC1155 reentrancy on create ordering)** — reentrancy considered but dismissed; needed a harness to test, not static reasoning.
4. **H-02 (`setFallbackHandler`)** — right family, wrong specificity; missing a Safe-selector enumeration lens.
5. **M-07 (module upgrade bricks rentals) / M-01 (ERC1155 guard can't differentiate)** — module-lifecycle and ERC1155-identity mediums not modeled.

## Highest-ROI improvement
A **Gnosis-Safe integration recall lens** that, for any Safe-guard-protected protocol, (a) enumerates EVERY Safe
self-management selector (`setFallbackHandler`, `addOwnerWithThreshold`, `swapOwner`, `changeThreshold`, `setGuard`,
`enable/disableModule`, `execTransactionFromModule`, `multiSend`) and asserts each is covered/decoded correctly by
the guard blocklist (this catches H-02 and re-derives H-04), plus a **hostile-token-in-settlement griefing lens**
(malicious/blacklisting ERC20 reverting in the stop/settle path → permanent lock — catches H-01 and several
mediums), plus **create-time reentrancy modeling** (state registered AFTER token movement — catches H-03). These
three lenses target 3–4 of the 4 missed Highs.

## Final Verdict

# C — RECALL_GAPS_REMAIN

Per-finding High recall 20% (1/5) and weighted recall ≈10–16% are below competitive-contest standard, despite the
one recovered High being a subtle, high-quality, blind, runtime-confirmed bug (H-04) that the system also ranked #1.
Precision, proof-conversion (1/1), ranking, and severity-alignment were all strong — the binding constraint is
**recall breadth**, not precision or proof conversion.

This is the honest correction P235 was designed to surface: **P234 measured precision (100%) and P230 judged recall
"generalizes" from candidate *quality* without ground truth; P235, scored against a real answer key, shows
per-finding recall against a hard target is low.** The system would have earned a payout and a correctly-ranked High
in this contest, but would not have been top-tier.

## Recommendation
**Do NOT declare the evaluation arc complete / do NOT move to unsupervised live hunting yet.** The user's completion
condition required *strong weighted recall* — not met. Fix the recall bottleneck first:
1. Build the **Gnosis-Safe integration lens** + **hostile-token-in-settlement lens** + **create-time reentrancy
   modeling** (highest ROI; targets the missed Highs above).
2. Re-run a second shadow contest (different architecture) to confirm recall lift before live hunting.
Strengths to keep: blind candidate quality on subtle logic bugs, ranking (#1 for the true High), 1/1 proof
conversion, 0 false-Highs, exact severity calibration on the recovered High. Supervised live hunting remains viable
for *narrow, high-confidence* finds today, but contest-competitive recall needs the lenses above first.
