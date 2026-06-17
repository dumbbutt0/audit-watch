# P220 — Dashboard update verification

Sync hook: `python scripts/run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace
documentation/research/assisted_mode/p215_full_funnel_rehearsal` → **exit 0**, completion guard **PASS**
(`failures: [] · warnings: [] · reader_failures: [] · card_failures: []`, 12 records, `all_safety_ok: true`).
Mirror `c7166e71 → 33a42431`; per-candidate JSON diff confirms **only ZETA-04 / ZETA-10 / ZETA-11 changed**, the
other 9 records byte-identical.

## Per-target before → after (rendered card fields via `finding_detail.load_unified_detail("funnel:<id>")`)
### ZETA-04
| field | before | after |
|-------|--------|-------|
| l3_status | NEEDS_HARNESS | PASS |
| poc actual | (unknown) | "paused connector still mints via onReceive: totalSupply +100e18 …" |
| poc control | (unknown) | "control test: guarded sibling onRevert (whenNotPaused) REVERTS while paused …" |
| value delta | (unknown) | "executed: onReceive mints the full zetaValue (100e18) during an active pause …" |
| who_loses | (heuristic) | "incident-response/availability: emergency pause does not halt inbound delivery" |
| high_promotion_allowed | false | false (blocker: privileged TSS trigger) |

### ZETA-10
| field | before | after |
|-------|--------|-------|
| l3_status | NEEDS_HARNESS | FAIL |
| poc actual | (unknown) | "reentrancy REACHABLE … but attacker net worth delta == 0 …" |
| poc control | (unknown) | "control: attacker net-worth delta == 0 and consumer residual == 0 …" |
| value delta | (unknown) | "executed: attacker eth_gain(200e18) == zeta_spent(200e18); consumer residual 0" |
| who_loses | (heuristic) | "none realized: the consumer is a pass-through and holds 0 zeta / 0 WETH / 0 ETH" |
| high_promotion_allowed | false | false (blocker: l3_status=FAIL, theft refuted) |

### ZETA-11
| field | before | after |
|-------|--------|-------|
| l3_status | NEEDS_HARNESS | PASS |
| poc actual | (unknown) | "empty getPools() array -> getZetaFromEth reverts at pairPools[0] (Panic 0x32) …" |
| poc control | (unknown) | "control: with a pool present the same getZetaFromEth returns the router output …" |
| value delta | (unknown) | "executed: the empty-array call reverts at pairPools[0]; control returns 1e18" |
| who_loses | (heuristic) | "denial-of-service: users cannot swap ETH->Zeta … when the pair has no Trident pool" |
| high_promotion_allowed | false | false (blocker: attacker_model unknown; DoS not auto-promoted) |

## Safety (all three)
`submission_ready=false`, `routing_allowed=false`, `browser_computes_severity=false`, 15/15 verifier sections render.
PoC actual/expected/control appear **only** where harness evidence exists; the still-NEEDS_HARNESS candidates
(ZETA-01/05/06) and the no-L3 candidates (ZETA-02/09/12) keep those fields explicitly absent.
