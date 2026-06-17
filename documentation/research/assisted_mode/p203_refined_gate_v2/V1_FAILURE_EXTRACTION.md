# P203 — v1 failure extraction (from frozen v1 calibration only; NO answer key)

The 8 v1 `HIGH_CONFIRMED` mechanisms (FREEZE 2 `90cf2a4f`) — the v2-regrade targets. Listed with the value-path
claim each makes and whether v1 had **source-proven** custody/value-flow at the vulnerable point (the v2 question).
This is derived from the frozen blind outputs + v1 calibration only; it does not use the answer key.

| v1 HIGH_CONFIRMED | surface | value-path the blind output asserted | source-proven custody/value-flow at vuln point? (v2 question) |
|---|---|---|---|
| decent-01 M1 | UTB.receiveFromBridge | "drain UTB-held funds / arbitrary execution" via missing access control | **doubtful** — claim is AC-bypass; whether UTB custodies funds at the call point is asserted, not shown |
| decent-02 M1 | UTB.receiveFromBridge | same (drain UTB-held funds) | doubtful — same AC-bypass-vs-custody question |
| decent-03 M1 | UTB.receiveFromBridge | same | doubtful |
| decent-03 M2 | UTB (impersonation) | "arbitrary execution using UTB as msg.sender against external protocols" | doubtful — depends on UTB holding approvals/roles elsewhere (unseen) |
| decent-06 M1 | UniSwapper.swapExactIn/Out | "permissionless bypass of onlyUtb; steal tokens held/approved to UniSwapper" | doubtful — depends on UniSwapper holding/approved residual balance (asserted) |
| decent-06 M2 | UniSwapper.swapNoPath | "drain contract's valuable token balance with worthless tokenIn" | doubtful — depends on UniSwapper custodying a valuable balance (asserted) |
| decent-09 M1 | DcntEth.setRouter | "public setRouter → become router → mint/burn arbitrary DcntEth" | **likely source-proven** — setRouter public + mint/burn gated only by router; value = token supply controlled in DcntEth itself |
| decent-12 M1 | DecentEthRouter.redeemEth | "redeemEth doesn't decrement balanceOf → double-withdraw" | doubtful — blind itself noted attacker "needs a mechanism to receive dcntEth"; precondition unproven |

## v2-regrade prediction frame (NOT a backfit; just the rule's logic)
Under the v2 source-substantiation rule, a HIGH is retained only where custody/value-flow + material magnitude are
source-proven at the vulnerable point. The setRouter→mint/burn mechanism (decent-09) directly controls the token
supply in the contract under trace, so its value path is internal/source-proven. The receiveFromBridge cluster
(decent-01/02/03) and the UniSwapper/redeem mechanisms (decent-06/12) all assert theft contingent on the contract
custodying funds that the shown source does not prove are held at the call point → candidates for downgrade. **The
fresh key-blind subagent decides each from source; this table only frames the v1 gap, not the answer.**
