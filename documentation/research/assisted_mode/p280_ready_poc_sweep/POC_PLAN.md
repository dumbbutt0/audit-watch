# P280 — POC_PLAN

All Tier C (faithful reproduction of the exact guard/state-transition the auto evidence targets), forge-std only.

| candidate | reproduce | expected assertion | control/refutation |
|---|---|---|---|
| V3Vault.transform | inline `if(loanOwner!=msg.sender && !transformApprovals[...]) revert Unauthorized` | unauthorized caller reverts (auto claim refuted) | owner can transform (guard real) |
| IBeanstalk.cancelPodListing | inline `require(plots[lister][fieldId][index]>0)` in LibMarket._cancelPodListing | non-owner reverts (auto claim refuted) | maker can cancel own listing |
| L2Governor.execute | status gate `require(status==Succeeded\|\|Defeated\|\|Expired)`, no caller check | execute permissionless-by-design (auto ACCESS framing benign) + a DEFEATED proposal executes (real anomaly) | only decided proposals execute |

Why Tier C is sufficient: each auto claim is about a SPECIFIC guard/state-transition that is fully captured by
faithfully reproducing that control-flow; the surrounding diamond/governance/vault machinery is irrelevant to whether
the guard refutes the "unauthorized" framing.
