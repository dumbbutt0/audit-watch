# P212 — discovery log (blind deep_trace per surface)

8 fresh key-blind Sonnet subagents, each = production `deep_trace.md` + verbatim source slice. Outputs JSON-only,
token-scan CLEAN (no `_sealed`/finding-id leakage). Raw outputs frozen: `raw_outputs/sf-*.json`, FREEZE hash `c14b2421`.

| surface | verdict (ceiling) | lead → candidate |
|---|---|---|
| sf-01 deposit | HIGH | boost inflates pool.amount reward denominator → SOPH-04 |
| sf-02 withdraw | HIGH | withdraw omits boostAmount decrement (conservation) → **SOPH-01** |
| sf-03 increaseBoost | HIGH(→Med) | boost synthetic weight (by-design) → SOPH-04 |
| sf-04 reward accrual | HIGH | accPointsPerShare 1e18 scaling mismatch + truncation → **SOPH-02** |
| sf-05 conversions | HIGH | depositStEth wraps full _amount vs received (stETH off-by-one) → **SOPH-03** |
| sf-06 add/set | MEDIUM | admin _withUpdate=false retroactive dilution → SOPH-06 (privileged) |
| sf-07 admin params | HIGH(priv) | setEndBlock withdrawalBlocks=0 withdrawal lock → SOPH-05 (privileged) |
| sf-08 proceeds/init/proxy | HIGH(→Med) | heldProceeds under-withdraw → SOPH-07 (privileged, benign) |

Threat-ceiling tally: 6 HIGH + 2 MEDIUM (over-HIGH skew, consistent with P199 — ceiling ≠ final severity).
