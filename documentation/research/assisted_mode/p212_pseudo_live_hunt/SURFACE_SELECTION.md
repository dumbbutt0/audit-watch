# P212 — surface selection (8 surfaces; bounded, in-scope, non-bridge)

| id | surface | function(s) (SophonFarming.sol) | category |
|---|---|---|---|
| sf-01 | deposit / _deposit | 443-451, 574-624 | custody-in + boost-split accounting |
| sf-02 | withdraw | 699-742 | custody-out + reward/boost accounting |
| sf-03 | increaseBoost / getMaxAdditionalBoost | 631-692 | boost purchase + cap invariant |
| sf-04 | updatePool / _pendingPoints / massUpdatePools | 357-435 | reward accrual scaling (accPointsPerShare) |
| sf-05 | predefined deposits + conversions | 458-566 | units/decimals + boost re-scale + external integ |
| sf-06 | add / set | 153-221 | pool config / allocPoint / poolExists dup |
| sf-07 | setStartBlock / setEndBlock / setPointsPerBlock / setBoosterMultiplier | 272-331 | admin param transitions vs accrual |
| sf-08 | withdrawProceeds + heldProceeds / initialize | 108-152, 863-875 | admin custody + init |

Bridging surfaces (bridgePool/revertFailedBridge) EXCLUDED (out of scope). Views excluded except as accounting refs.
Each surface gets one fresh key-blind Sonnet subagent: production deep_trace.md + verbatim source slice.
