# P148 — Candidate Selection

## Requirement
A **negative control**: a plausible-but-uncertain candidate the real runtime is expected to **kill** (not a
strawman), in an audit with no local answer key (`duplicate_unknown`), runtime-PoC-able, not already
duplicate-known or runtime-confirmed.

## Selected: velodrome-2022-05-bench `RewardsDistributor` (claim vs claim_many)
| criterion | status |
|---|---|
| plausible suspicion | **yes** — it is the **ancestor** of blackhole's distributor, where B5 (a real claim/claim_many recipient-parity bug) lives; "does the same divergence exist here?" is a genuine question |
| refutes a specific axis | **recipient-divergence** (the B5 axis) |
| no local answer key | yes → `duplicate_unknown` |
| not in corpus / not runtime-confirmed | yes |
| runtime-PoC-able (light deps) | yes — solc 0.8.13, imports only local `Math`/`IERC20`/`IVotingEscrow`, no OZ |
| expected runtime outcome | **REFUTED** — the recipient-resolution branch is architecturally absent |

## Why this is a true negative control (not a strawman)
The same family produced a **real confirmed bug** (B5) one fork downstream. The blackhole fork *added* the
expired-lock external-transfer branch (`ownerOf` + the AVM correction asymmetry) where B5 lives; the velodrome
ancestor never had it — both `claim` and `claim_many` only `deposit_for(_tokenId)`. So the suspicion is
well-motivated and the refutation is meaningful: it shows the panel can distinguish "same family, real bug" (B5,
confirmed) from "same family, no such bug" (velodrome, refuted).

## Rejected alternatives
- Re-using centrifuge UserEscrow (already runtime_confirmed in P147) — would mix statuses on one contract.
- A strawman with no plausible suspicion — fails the "plausible candidate" requirement.
