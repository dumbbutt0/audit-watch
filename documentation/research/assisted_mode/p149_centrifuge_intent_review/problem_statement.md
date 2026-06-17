# P149 — Problem Statement

P147 RUNTIME_CONFIRMED a recipient-provenance **mechanism** in `centrifuge UserEscrow.transferOut`: funds escrowed
for `destination` can be transferred to an unrelated `receiver` when `allowance(destination, receiver) ==
type(uint256).max` (the allowance is never reduced; repeatable — the harness showed 1000e18 then 2000e18 to 0xBEEF
while `destination` received 0). P147 explicitly deferred intent/severity (`requires_human_review=true`,
`submission_ready=false`).

**P149 is a judgment-record phase.** It resolves, from **local source only**, whether that mechanism is *intended
delegation* or an *authorization / economic-recipient weakness*. No new detector, no new bug hunt, no submission
package. The runtime fact is treated as **established**; reportability and severity are **not**.

## Decision: GRIEFING_OR_DESIGN_AMBIGUOUS
The runtime mechanism is real, but local source shows (a) only the **owner** can initiate a withdrawal and chooses
the `receiver` (standard ERC4626), and (b) `transferOut` is ward-only with the allowance check documented as
defense-in-depth "in case of compromized auth." So the source does **not** establish a reportable external-attacker
loss under intended operation — the external-theft framing of P147 is largely **refuted by intent**. What remains
is a genuine ambiguity needing human severity: a functional ERC4626 defect (legitimate `receiver != owner`
withdrawals revert) and a weak compromised-auth proxy. `submission_ready=false`.

## Honesty
`duplicate_status=duplicate_unknown` = "no local duplicate record," **not** novelty. No external docs were used
(local source only). This phase changed no production source, detector, gate, severity, submission, routing, or
prompt baseline; it recorded a judgment on the H1 sidecar row + these deliverables.
