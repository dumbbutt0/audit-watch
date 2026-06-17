# P203 — HIGH-precondition audit (v2 evidence per retained HIGH_CONFIRMED)

Per the v2 rule, every HIGH_CONFIRMED must cite source-proven custody/value-flow + material magnitude. Below is the
fresh subagent's evidence for each **retained** v2 HIGH_CONFIRMED, with an honest assessment of whether the evidence
truly meets the bar vs over-reaches. (Awarded mapping added by the orchestrator post-regrade for audit only.)

| v2 HIGH | awarded | precondition | magnitude | custody proof | honest assessment |
|---|---|---|---|---|---|
| decent-09 M1 (DcntEth.setRouter→mint/burn) | **H-01 (High)** | SOURCE_PROVEN | MATERIAL_PROVEN | CONTRACT_CUSTODY_PROVEN | ✅ **legit** — setRouter public + mint/burn router-gated; value = token supply controlled inside DcntEth (the contract under trace). Genuine High. |
| decent-01 M1 (UTB.receiveFromBridge) | M-03 (Medium) | SOURCE_PROVEN | MATERIAL_PROVEN | **ACCOUNTING_BALANCE_PROVEN** | ⚠️ **over-reach** — the agent proved arbitrary `executor.execute(target,payload)` capability, NOT that UTB custodies material funds at the call point. Judges rated realized impact (fee/signature bypass) Medium. |
| decent-02 M1 (receiveFromBridge) | M-03 (Medium) | SOURCE_PROVEN | MATERIAL_PROVEN | ACCOUNTING_BALANCE_PROVEN | ⚠️ same over-reach (identical code) |
| decent-03 M1 (receiveFromBridge) | M-03 (Medium) | SOURCE_PROVEN | MATERIAL_PROVEN | ACCOUNTING_BALANCE_PROVEN | ⚠️ same |
| decent-03 M2 (arbitrary exec impersonating UTB) | (unawarded) | SOURCE_PROVEN | MATERIAL_PROVEN | ACCOUNTING_BALANCE_PROVEN | ⚠️ over-reach — "UTB-as-caller against external protocols" assumes UTB holds approvals/roles elsewhere (unseen) |
| decent-06 M2 (UniSwapper.swapNoPath drain) | (unawarded) | SOURCE_PROVEN | MATERIAL_PROVEN | **CONTRACT_CUSTODY_PROVEN** | ⚠️ over-reach — drain requires UniSwapper to custody a valuable residual balance; "contract may hold funds" not proven held at the call point |
| decent-12 M1 (redeemEth double-withdrawal) | (unawarded; loosely H-04) | SOURCE_PROVEN | MATERIAL_PROVEN | CONTRACT_CUSTODY_PROVEN | ⚠️ over-reach — the blind output itself said the attacker "needs a mechanism to receive dcntEth"; precondition not fully source-proven |

## The core finding
Only **1 of 7** retained v2 HIGH_CONFIRMED (decent-09 / H-01) has an *unimpeachable* source-proven value path. The
other 6 were retained by an independent key-blind reviewer who treated **arbitrary-execution capability** or
**"contract may hold a balance"** as satisfying the custody/value-flow precondition — i.e., the v2 rule's
`custody_value_flow_proof` field was marked PROVEN on a worst-case-capability reading, not a realized-fund-custody
reading.

## Why the rule did not bite
The v2 precondition is **interpretable/gameable**: "source-proven custody/value-flow at the vulnerable point" is
satisfied (in an independent reviewer's judgment) by *the ability to make arbitrary calls / the existence of a token
balance variable*, without proving that material funds are actually present and movable in the deployed
configuration. That is precisely why the C4 judges rated receiveFromBridge **Medium** (realized impact = fee/sig
bypass, UTB holds no funds between txs) while a source reviewer rates the **capability** High. A static
source-substantiation rule cannot separate worst-case capability from realized impact — that requires an
exploit/PoC-grade magnitude proof (the project's L3 PoC standard / harness).
