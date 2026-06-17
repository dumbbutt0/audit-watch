# P205 — blind threat-ceiling results (vultisig-2024-06, src/ ILO surfaces)

Production `deep_trace.md` (`ef93a6c2`) unchanged. One fresh key-blind Sonnet subagent per surface; prompt =
deep_trace.md + verbatim source only (no key/PCS hints). Prompts + outputs token-scanned: **CLEAN** (no
`[H-0`/`[M-0`/`code-423n4`/severity-criteria leakage). **FREEZE 1** raw-outputs hash = `fa1afe1b`
(`raw_outputs/v-01.json … v-08.json`). Raw outputs are structured distillations (verdict + selected/unresolved/
rejected mechanisms preserved verbatim in substance); full subagent reasoning is in the session transcript.

| id | surface | blind verdict | core mechanism (blind) |
|---|---|---|---|
| v-01 | ILOPool.buy | **HIGH** | recipient≠msg.sender custody split; per-user-cap bypass via NFT transfer (raiseAmount=0 fresh tokenId) |
| v-02 | ILOPool.claim | **HIGH** | shared single V3 position fee accounting — first claimer absorbs others' fees |
| v-03 | ILOPool.launch | **HIGH** | reverting ERC721 recipient / liquidity over-allocation DoS |
| v-04 | ILOPool.claimRefund | MEDIUM | 0-raiseAmount NFT permanent burn (edge) |
| v-05 | ILOManager.initialize | **CRITICAL** | no access control → frontrun seize ownership + malicious pool impl; missing upper-range check |
| v-06 | ILOManager.launch/setPlatformFee | **HIGH** | permissionless slot0 price-peg DoS; fee no upper-bound cap |
| v-07 | base/ILOWhitelist | **HIGH** | `openToAll` bypasses whitelist; unbounded batch DoS |
| v-08 | base/LiquidityManagement | **HIGH** | mint-callback drain via cached pool addr / no in-flight guard |

**Threat ceiling: 7/8 ≥ HIGH (1 CRITICAL + 6 HIGH + 1 MEDIUM).** This reproduces the P199
`SEVERITY_FRONTIER_CONFIRMED` over-HIGH skew on a 3rd-architecture corpus (RWA-tranche centrifuge P198 →
launchpad/ILO vultisig). The deep_trace verdict is a **threat ceiling by design**, not a calibrated severity — as
documented since P199.
