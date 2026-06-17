# P281 — POC_REVALIDATION (the repaired READY set)

1 repaired READY (L2Governor.execute, state-machine). Tier-C reproduction under `pocs/p281/`; `forge test`: **2 passed**
(`outputs/poc_revalidation_log.txt`).

| candidate | framing | result | assertion |
|---|---|---|---|
| L2Governor.execute | STATE_MACHINE (reframed from ACCESS) | **PASS_SUPPORTED** | a DEFEATED proposal (forbidden terminal state) passes the `Succeeded\|\|Defeated\|\|Expired` gate and executes; a Pending/Active proposal is correctly rejected (control) |

The correctly-framed claim is supported: the gate accepts a forbidden state. (This is the state-machine mechanism the
P280 ACCESS framing missed — now the READY label points at the right thing.) Advisory diagnostic, not a confirmed
finding; no severity/reportability.
