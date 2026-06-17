# P280 — INPUT_FREEZE (frozen BEFORE PoC code)

The 3 P279 READY evidence packages, copied to `outputs/frozen_evidence_packages.json` and hashed. Frozen-set hash:
`ce3e99aa8e5bfda7`.

| candidate | class | pkg hash | auto attacker_path | auto poc_assertion | tier |
|---|---|---|---|---|---|
| IBeanstalk.cancelPodListing | ORDER | `24801687d2449e37` | "attacker fills/cancels orders before/instead of intended party" | "attacker-controlled call violates maker/taker/order invariant" | C |
| L2Governor.execute | ACCESS | `23029132f565b670` | "unauthorized EOA calls execute: external state-changing config/param mutator, no auth modifier" | "unauthorized EOA can call execute and change protected state" | C |
| V3Vault.transform | ACCESS | `39f678faf4aef4fb` | "unauthorized EOA calls transform: external state-changing, no auth modifier" | "unauthorized EOA can call transform and change protected state" | C |

Unresolved assumptions (auto): each carries the residue that the value-flow/inline-guard anomaly is unverified. Tier C
(faithful reproduction) chosen for all 3 — heavy stacks (Beanstalk diamond / governance / lending) make full deploy
disproportionate for a diagnostic sweep.
