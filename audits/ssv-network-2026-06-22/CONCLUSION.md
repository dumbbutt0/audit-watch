# SSV Network v2.0.0 — Immunefi bug bounty — audit conclusion

**Target:** SSV Network (Immunefi $250k; Ethereum DVT staking; theft/permanent-freeze of cluster balances / staked ETH / cSSV). In-scope: SSVNetwork 0xDD9BC35aE942eF0cFa76930954a156B3fF30a4E1 + SSVNetworkViews. Repo github.com/ssvlabs/ssv-network @ HEAD (v2.0.0, squash-merged 2026-04-28). bApps OOS.
**Method: diff-the-audit (softer signal).** SSV audits every version (Quantstamp x5: v1.0.0-rc3 / v1.0.2 / v1.1.0 / v1.2.0 / **v2.0.0 2026-04-10**). HEAD = the audited v2.0.0 (public history squashed → no diffable post-audit delta). But v2.0.0 is a MAJOR fresh rewrite (ETH-based fee accounting, oracle-driven effective-balance (EB) charging, cSSV staking, legacy→ETH migration) with only ONE audit = the thinnest-audited recent surface. Focused deep-read of the new v2 modules + the cluster accounting, deduped vs the in-repo Quantstamp v2.0.0 report.

## Verdict: honest negative — no novel submittable finding

### Staking / cSSV / ETH-accounting / migration — clean (0 findings)
cSSV is a strict 1:1 SSV wrapper (no share/exchange-rate math → no inflation/donation/rounding theft); mint/burn onlySSVStaking. ETH reward accumulator conserves (per-share, floored, guarded ≤ pool). SSV (1e7) and ETH (1e5) ledgers are type+storage segregated (no cross-unit read/write). One-way migration is owner-bound (keccak(msg.sender,operatorIds)) + replay-proof (clusters[hash] deleted, ethClusters[hash] set → IncorrectClusterVersion on replay). CEI + nonReentrant on withdraw/claim.

### Cluster / operator / liquidation accounting — 1 High candidate, KILLED on dedup (CLU-001 = known)
A specialist flagged CLU-001 (High): `removeValidator` (ETH path) subtracts only the baseline (`validatorsRemoved * BPS_DENOMINATOR`) from `ebSnapshot.vUnits` and adjusts the per-validator deviation only when the cluster becomes empty — so removing a high-EB (Pectra) validator from a non-empty cluster strands its deviation → inflated burn rate → over-charge + permissionless wrongful liquidation in the window.
**Verification → NOT novel / OOS:**
- The **"Deviation-only model" is intentional** (code comment: "baseline removed via ethValidatorCount; Do NOT subtract baseline from operatorEthVUnits; deviation cleanup only for explicit-EB clusters"). Deviation is a cluster-AGGREGATE value owned by the oracle, not per-validator.
- **Self-correcting:** `_updateEBSnapshot` writes the merkle-proven `newVUnits` **absolutely** at the next oracle EB update → the stranded deviation is transient (Quantstamp: "Once refreshed, accounting catches up").
- **Heavily audited & known:** the EB-deviation-on-removal/liquidation surface is Quantstamp **SSV-7** (EB inflation on removal — Fixed), **SSV-8** (Double-Accounting of EB Deviation Blocks Validator Removal — Fixed; the deviation-only model IS this fix), **SSV-12** (sub-baseline operatorEthVUnits — Ack), **SSV-17** (Stale Cluster EB Updates — Fixed), **SSV-18** (Direct Liquidations Don't Consider EB Updates — **Acknowledged**). CLU-001's wrongful-liquidation-in-the-window IS the acknowledged SSV-18 behavior.
- Per the bounty, vulnerabilities known to the team / in audit reports are **ineligible** → CLU-001 is OOS.

## Submission
**Nothing submitted (honest negative).** v2.0.0's complex EB/cluster/fee surface was thoroughly covered by Quantstamp (2 High + 7 Medium + Lows, esp. 5 EB-removal/liquidation findings); the one promising lead (CLU-001) is a known variant within that audited space (self-correcting + matches Fixed SSV-8 / Acknowledged SSV-18). Staking/cSSV/migration is clean. (Lesson: an agent over-claimed CLU-001 as a novel High; rigorous code+audit dedup showed it's the intentional, audited deviation-only model.)
