# P121 — Decision: NukeFund.nuke (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness refuted the over-claim / guard-bypass / re-nuke / insolvency hypothesis with executed
assertions — not source-only reasoning.

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| guards cannot be bypassed | Case A: a non-owner/non-approved caller reverts ("caller is not token owner or approved"); an owner without NukeFund approval reverts ("Contract must be approved…"); an immature token reverts ("Token is not mature yet") (PASS). |
| claim cannot exceed the cap | Case B: high `finalNukeFactor` → claim == **exactly `fund/2`**; Case E: low factor → claim == `fund*factor/MAX_DENOMINATOR`, ≤ `fund/2`. `fund -= claim` cannot underflow (PASS). |
| a token cannot be re-nuked | Case C: after a successful nuke the token is burned → a second `nuke` reverts (PASS). |
| accounting stays bounded & solvent | Case D: two nukes each take exactly 50% of the *current* fund; `fund` never underflows; `address(nf).balance ≥ fund` after each call; 25% of the original remains (PASS). |

**Verdict:** the high-ranked, permissionless-flagged `nuke` enforces its ownership/approval/maturity guards, caps
every claim at ≤50% of the fund, blocks re-nuke via `burn`, and keeps the fund accounting non-negative and solvent.
A permissionless caller cannot over-claim, bypass guards, re-nuke, or break solvency → **KILLED_RUNTIME**. A clean
runtime REFUTATION of a NOVEL candidate (the methodology that CONFIRMED P117 and KILLED P118/P120 also KILLS this).

## Out-of-scope (recorded as NEEDS_CONTEXT, not settled here)
The highest-value nuke questions are CROSS-CONTRACT and depend on the real `TraitForgeNft`:
- **maturity bypass** — does mint leave `getTokenLastTransferredTimestamp == 0` so `canTokenBeNuked` is satisfied
  immediately? (a mock NFT cannot honestly settle this — it would only assert the mock's own value).
- **entropy bounds** feeding `calculateNukeFactor`.
These require the real TraitForgeNft mint/entropy machinery (EntropyGenerator + pricing + merkle) — a COMPLEX harness.
The mock-NFT harness decisively answers nuke's INTERNAL claim/guard/accounting integrity only; the cross-contract
questions remain open (NEEDS_CONTEXT) and are not promoted.

## Scope / honesty notes
- The designed mechanic allows up to 50% of the fund per mature token; the multi-token geometric drain is intended
  behavior (bounded, solvent), not an exploit.
- `ageMultiplier` and other params are owner-set; owner mis-configuration is out of the permissionless-attacker scope.
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).

## Hard-stop self-check
- KILLED_RUNTIME claimed only with passing runtime tests (Cases A–E all PASS, executed). ✓
- No source-only reasoning used as runtime proof — guards/claims/solvency are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- traitforge `contracts/` (src) **unmutated** — `NukeFund.sol` (sha f378f93c) imported via remapping; the harness
  lives only in the standalone `/tmp/p121-nukefund-harness/` project. ✓
