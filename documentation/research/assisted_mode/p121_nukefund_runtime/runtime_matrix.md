# P121 — Runtime matrix

Command: `forge test --use 0.8.26 --match-contract NukeFundRuntime -vvv`
Project: `/tmp/p121-nukefund-harness` (standalone; traitforge `NukeFund.sol` unmutated via remapping; OZ v4.9.6 via forge install).
Fund per case: 100 ETH sent through `receive()` → `fund == 90 ETH` (10% devShare to dao).

| Case | Scenario (attacker = permissionless caller) | Result | Evidence |
|---|---|---|---|
| **A** | A1 non-owner nukes victim's token; A2 owner but NukeFund not approved; A3 owner+approved but immature | **PASS** | A1 revert "ERC721: caller is not token owner or approved"; A2 revert "Contract must be approved to transfer the NFT."; A3 revert "Token is not mature yet" |
| **B** | owner of mature+approved token, entropy 999999 → `finalNukeFactor > nukeFactorMaxParam` | **PASS** | claim == `fund/2` exactly (45 ETH); fund 90→45; attacker +45; token burned; claim ≤ fund/2 |
| **C** | second `nuke` on the same (now burned) token | **PASS** | reverts "ERC721: caller is not token owner or approved" — no re-nuke |
| **D** | attacker with 2 mature tokens nukes twice | **PASS** | 1st takes exactly 50% (90→45); 2nd takes exactly 50% of remaining (45→22.5); fund stays >0 (no underflow); `address(nf).balance ≥ fund` after each (solvent); 25% of original remains |
| **E** | low factor (entropy 4000, `entropy%10==0` → age term 0 → factor = 100 ≤ 50000) | **PASS** | claim == `fund*factor/MAX_DENOMINATOR` (proportional); ≤ fund/2; fund −= exactly claim |

All 5 tests pass (executed). Full log: `execution_output.txt`.

## Reading
- **A** the three guards (ownership, NukeFund-approval, maturity) are enforced — an arbitrary caller cannot nuke a
  token it doesn't control, nor an immature token.
- **B/E** the claim is exactly the capped (50%) or proportional (`fund*factor/DENOM`) amount, never exceeding
  `fund/2` — `fund -= claim` cannot underflow.
- **C** `burn` + the burned-token check make re-nuke impossible.
- **D** even with multiple aged tokens, each call is bounded to 50% of the *current* fund; the fund never underflows
  and the contract stays solvent (the geometric drain is the designed mechanic, not an exploit).
