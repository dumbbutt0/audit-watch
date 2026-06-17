# P211 — final submission package rehearsal (DEC-H-01)

`final_submission_pack.py` is NOT modified (hash `57cba16d` unchanged). This is the "equivalent" package: its existing
fields + the L3 overlay fields, assembled for the decent H-01 candidate to verify the High package carries L3 evidence
and shows NO auto-submit.

## Package (rehearsal)
- **Finding:** H-01 — Anyone can update the DcntEth Router and mint unbacked tokens.
- **Affected functions:** `DcntEth.setRouter`, `DcntEth.mint`.
- **Attacker model:** permissionless EOA (no privileged setup).
- **Exploit steps:** attacker calls `setRouter(attacker)`; then `mint(attacker, 1e6 ether)`.
- **Source references:** real `DcntEth` (P204 `realsrc/`), `setRouter` is public.
- **Impact path:** unbacked supply inflation → dilutes every holder / breaks 1:1 backing.
- **L3 status:** `PASS` (L3_REAL_CONTRACT_POC).
- **PoC path:** `p204_l3_magnitude_standard/pocs/test/H01_setRouter.t.sol`.
- **PoC command:** `forge test --match-contract H01`.
- **Actual result:** 1,000,000 ether minted to attacker, unbacked.
- **Expected/control result:** mint reverts without the setRouter hijack.
- **Mitigation:** restrict `setRouter` to owner/governance.
- **Assumptions/limitations:** external deps mocked (OFTV2 base); honest custody.
- **Human review note:** REQUIRED before any submission — package is a draft only.
- **Auto-submit:** NONE. `submission_ready`/`routing_allowed` not set; readiness is advisory.

## Verification
The package contains all required fields INCLUDING L3 evidence (status/poc_path/poc_command/actual/expected-control).
For a High lacking L3 (e.g. DEC-STATIC) the package would be marked "not High-ready: blocked_by_missing_l3_poc".
Follow-up (not P211): render these L3 fields directly inside `final_submission_pack.py`.
