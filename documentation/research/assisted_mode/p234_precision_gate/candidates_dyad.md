# P234 blind candidate artifact — DYAD (oracle/accounting stablecoin)

Subject: `audits/dyad-2024-04-fresh` (CDP stablecoin + Kerosene side-token, V2 migration).
Blind Sonnet deep_trace pass (real recall instruments: deep_trace.md + oracle/arithmetic/economic_attack/logic/access_control agents + units/defi_accounting lenses). Report/output/answer-key files NOT opened. Tally: 7 — HIGH 4 · MED 2 · LOW 1 · NOISE 0.

| id | title | class | contract | conf | signal | impact / attacker |
|---|---|---|---|---|---|---|
| DYAD-01 | liquidate() iterates only exo `vaults[id]`, never `vaultsKerosene[id]` → liquidator under-paid → bad debt | logic/invariant | VaultManagerV2 | Confirmed | HIGH | High / permissionless |
| DYAD-02 | setKeroseneManager() guarded only by `initializer` (no msg.sender check) → front-run install malicious registry | access-control | VaultManagerV2 | Confirmed | HIGH | High / permissionless |
| DYAD-03 | UnboundedKerosineVault.assetPrice() `tvl - dyad.totalSupply()` underflow → whole system DoS when undercollateralized | arithmetic/dos | UnboundedKerosineVault | Confirmed | HIGH | High / conditional (price crash) |
| DYAD-04 | no withdrawKerosene path in VaultManagerV2; withdraw() casts kerosene vault to Vault → oracle() reverts → kerosene locked | logic/invariant | VaultManagerV2 / KerosineVault | Confirmed | HIGH | High / permissionless |
| DYAD-05 | assetPrice() missing answeredInRound/answer>0 (IncompleteRound defined-but-unused) | oracle | Vault / VaultWstEth | High | MED | Med / conditional |
| DYAD-07 | kerosene TVL uses `balanceOf(vault)` spot → donation inflation | oracle/accounting | UnboundedKerosineVault | High | MED | Med / conditional |
| DYAD-06 | deposit() uses isValidDNft not isDNftOwner → 1-wei same-block withdraw grief | access-control/dos | VaultManagerV2 | Confirmed | LOW | Low / permissionless |
