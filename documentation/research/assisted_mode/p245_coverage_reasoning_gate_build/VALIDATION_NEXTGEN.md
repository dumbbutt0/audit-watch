# P245 — Validation on nextgen-2023-10

Ran against the **real nextgen coverage manifest** (`audits/nextgen-2023-10-fresh/output/
coverage_manifest.json`, 361 items / 122 in-scope) loaded into a tmp workspace (via `get_audit_root`
redirect) — **zero writes to any audit workspace; the active audit `size-credit-2024-06-blind` was never
switched.** Raw data: `_validation_data.json`, `_triage_demo_data.json`.

## Demo 1 — coverage read-completeness (#3)
Dispositions were synthesized so **every in-scope item is `cleared` with full evidence + strong-clear
fields** — i.e. the base coverage gate is fully satisfied — and the **only** variable is `read_state`:
AuctionDemo critical items = `READ_FULL` (the one contract actually read in P241), all other critical
items = `READ_PARTIAL`. This reproduces the exact P241 situation: *"the auditor cleared everything but
only AuctionDemo was actually read in full."*

| Arm | Flag | Result | Detail |
|---|---|---|---|
| **A (default-off)** | off | **PASS** (rc 0) | base gate satisfied; read-completeness ignored (`enforced:false`). Existing workflow unchanged. |
| **B (enforced)** | `--enforce-read-completeness` | **BLOCK** (rc 1) | 84 of 92 critical in-scope items blocked; only AuctionDemo's 8 (`READ_FULL`) pass. |

Blocked critical items by contract (Arm B):

| Contract | Critical blocked |
|---|---|
| NextGenCore.sol | 33 |
| MinterContract.sol | 24 |
| RandomizerRNG.sol | 8 |
| RandomizerVRF.sol | 8 |
| NextGenAdmins.sol | 6 |
| RandomizerNXT.sol | 5 |
| **Total** | **84** |

The gate blocks triage on **exactly the surface P241 never read** — including the precise loci of the
missed awards: `NextGenCore::mint` + `NextGenCore::_mintProcessing` (H-01 create-time reentrancy),
`MinterContract::mintAndAuction` (H-04), `payArtist` (M-01), `burnToMint` (M-03), `setCollectionPhases` /
`setCollectionCosts` (M-04/M-08), `airDropTokens` (M-08). False blocks: **0** (every blocked item is a
genuine unread critical surface; read-only getters were correctly excluded — `noncritical_unread_warned`
counts the advisory-only non-critical items).

Time overhead: 20 ms (Arm B) vs 5 ms (Arm A) — deterministic regex over the manifest; negligible in
absolute terms (the 3.98× ratio is on a millisecond base).

## `coverage_enforced_recall_gain` (the go/no-go-for-live-hunting metric)
For each item the gate forced to be read, we ask: would it have been triaged under the old (P241) system?
did the gate force additional reading? did that reading produce a new/upgraded candidate? Outcomes are
**answer-key-anchored** (P241/P243 nextgen awards) — with the standing **read ≠ detect** caveat: the gate
forces the *reading* that is the necessary precondition; actual detection still depends on the specialist
pass over the now-readable code (P243 anchors realized recovery at ~60% on a fully-read target).

| Forced-read locus (was `READ_PARTIAL`, now must be `READ_FULL`) | Triaged under old system? | Gate forced reading? | Reading outcome (answer-key) |
|---|---|---|---|
| NextGenCore::mint + _mintProcessing | No (Core unread) | Yes | **new_candidate** → H-01 create-time reentrancy |
| MinterContract::mintAndAuction | No | Yes | **new_candidate** → H-04 |
| MinterContract::payArtist + propose/acceptAddressesAndPercentages | No | Yes | **new_candidate** → M-01 artist payout |
| {NextGenCore,MinterContract}::burnToMint | No | Yes | **new_candidate** → M-03 burn-to-mint |
| MinterContract::setCollectionPhases / setCollectionCosts | No | Yes | **new_candidate** → M-04 / M-08 pricing |
| {NextGenCore,MinterContract}::airDropTokens | No | Yes | **new_candidate** → M-08 airdrop |
| ~70 admin setters / royalties / metadata / randomizer items | No | Yes | no_change (no awarded finding at locus) |

**Finding-level gain:** forcing the read makes ~**2 High (H-01, H-04) + ~4 Medium (M-01, M-03, M-04, M-08)**
loci reachable that the frozen system never opened — i.e. the gate converts the P243 *category-A nextgen
coverage-bound* miss set from "unreadable" to "in front of the specialist." **Under the old system the
recall-gain on these was structurally 0 (the contracts were never read).**

**Item-level ratio:** of 84 forced reads, ~10 map to a distinct awarded-finding locus
(`coverage_enforced_recall_gain ≈ 0.12` at the item level) — the rest are admin/metadata surface with no
award. This is the honest signal: the gate forces a lot of reading, and a meaningful minority of it lands
on real findings — but critically, **the high-value findings (H-01/H-04) are inside the forced set and
were 100% missed without it.** Block count alone (84) would overstate; this metric shows the genuine,
bounded recall payoff.

## Demo 2 — rejection depth-record (#4)
A nextgen-flavored decision set was run through `triage_write.main()` with the policy flag enabled:

| Finding | Area(s) detected | Depth record | Outcome |
|---|---|---|---|
| DT-001 — NextGenCore.mint callback-before-counter (create-time reentrancy) | callbacks/hooks, lifecycle registration | none | **rerouted → human (needs_depth)**; all 6 missing fields named; candidate preserved |
| DT-002 — AuctionDemo oracle staleness | oracle freshness | complete (6/6) | **stays rejected** (allowed) |
| QA-001 — gas: cache loop length | — (non-sensitive) | none | **stays rejected** (unaffected) |

DT-001 is the H-01 anchor that P241 missed by shallow dismissal — the gate refuses to silently reject it
and routes it to human review with the exact missing-depth fields, **without inventing a finding**. The
complete record (DT-002) and the non-sensitive rejection (QA-001) pass through unchanged → no broad noise.

## Conclusion
Both halves behave as specified on real data: #3 blocks the exact unread surface that hid the P241 nextgen
awards; #4 catches the exact shallow rejection that buried H-01. Default-off preserves the workflow.
`coverage_enforced_recall_gain` confirms the blocked work translates into genuine (bounded) recall payoff,
not blocked-work-with-no-payoff. → verdict **A — READY_FOR_DEFAULT_OFF_USE**.
