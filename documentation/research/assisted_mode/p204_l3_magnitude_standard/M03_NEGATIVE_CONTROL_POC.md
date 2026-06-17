# P204 — M-03 negative-control PoC

Harness: `pocs/test/M03_receiveFromBridge.t.sol` (real `UTB.sol` + real `UTBExecutor.sol`; owner-registered honest
swapper; mocked external deps only). Run log: `pocs/run_log.txt`.

## Setup (source-valid, honest custody)
- `UTB` (owner=deployer); `UTBExecutor` wired as UTB's executor (`exec.setOwner(UTB)`); an **owner-registered**
  `HonestSwapper` (registerSwapper is `onlyOwner`, so attacker cannot inject a malicious swapper).
- Honest custody: no artificial attacker holdings of victim/UTB tokens; the swap pulls from the caller per source
  (`performSwap`: `transferFrom(msg.sender, ...)`).

## Source fact under test
`receiveFromBridge` is `public` with no access control (capability the static gates rated HIGH). But
`performSwap` pulls `tokenIn` via `transferFrom(msg.sender, address(this), amountIn)` — from the **caller**, never a
victim or pre-existing UTB custody.

## Exploit attempts + measured results
1. `test_M03_cannot_steal_victim_approved_funds`: victim approves UTB for 1e24 tokenA; attacker (0 tokenA) calls
   `receiveFromBridge` trying to route the victim's tokenA → **reverts** (transferFrom pulls from the attacker, who
   has none). Victim balance **unchanged**. → no theft of approved victim funds. **PASS.**
2. `test_M03_no_material_theft_self_funded_only`: UTB holds a 5e23 tokenA treasury (even if it did); attacker funds
   their **own** swap with their own tokenB. UTB's tokenA treasury **untouched**; attacker spends own tokenB and
   receives tokenC 1:1 → **self-funded routing, no profit**. **PASS.**

## L3 verdict: **MEDIUM_OR_LOWER_CALIBRATED (demoted)**
Under source-valid honest custody, no attacker-controlled tx realizes material theft/loss. The proven impact is
**unauthorized/self-funded call** (and the awarded fee/signature-bypass class) — exactly the C4 **Medium** rating.
L3 demotes M-03, fixing the v1/v2 over-confirmation that an executed harness — not a static rule — was needed to
expose. (If a future source-valid flow were shown to leave material funds in UTB at the call point, the verdict
would revisit; no such flow exists in the audited code.)
